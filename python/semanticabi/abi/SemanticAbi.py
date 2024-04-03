from typing import Dict, Set, TypedDict, List

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.item.Expressions import TypedExpression, Expressions
from semanticabi.abi.item.Matches import MatchItemType
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiEvent, SemanticAbiFunction, SemanticAbiItem
from semanticabi.abi.item.ItemType import ItemType
from semanticabi.abi.item.Parameter import TupleParameter
from semanticabi.common.column.HexNormalize import HexNormalize
from semanticabi.metadata.EvmChain import EvmChain


class TypedMetadataBase(TypedDict):
    chains: List[str]


class TypedMetadata(TypedMetadataBase, total=False):
    contractAddresses: List[str]
    expressions: List[TypedExpression]


class TypedSemanticAbi(TypedDict):
    metadata: TypedMetadata
    abi: List[Dict[str, any]]


class SemanticAbi:
    """
    The semantic ABI for a smart contract. This contains all the details needed to decode the logs
    and transforms them into individual rows.
    """

    abi_json: TypedSemanticAbi

    # The chains this ABI is deployed on
    chains: Set[EvmChain]
    # Any specific contract addresses to filter on
    contract_addresses: Set[str]
    # Table-level expressions to evaluate for each row
    expressions: Expressions

    # events and functions by their hashes/topic
    events_by_hash: Dict[str, SemanticAbiEvent]
    functions_by_hash: Dict[str, SemanticAbiFunction]
    # events and functions by their signatures
    events_by_signature: Dict[str, SemanticAbiEvent]
    functions_by_signature: Dict[str, SemanticAbiFunction]

    def __init__(
        self,
        abi_json: TypedSemanticAbi
    ):
        self.abi_json = abi_json

        chains_list = abi_json['metadata'].get('chains', [])
        if len(chains_list) == 0:
            raise InvalidAbiException('No chains specified in metadata')
        self.chains = set(map(lambda chain: EvmChain(chain), chains_list))

        contract_addrs = abi_json['metadata'].get('contractAddresses', [])
        self.contract_addresses = set([HexNormalize.normalize(address) for address in contract_addrs])

        self.expressions = Expressions.from_json(abi_json['metadata'].get('expressions', []))

        self.events_by_hash = {}
        self.functions_by_hash = {}
        self.events_by_signature = {}
        self.functions_by_signature = {}

        has_primary_item: bool = False
        all_items: List[SemanticAbiItem] = []
        for item in self.abi_json['abi']:
            # skip if there are no inputs
            if 'inputs' not in item:
                continue

            item_type = ItemType(item['type'])
            if item_type == ItemType.EVENT:
                abi_item = SemanticAbiEvent.from_json(item)
                if abi_item.raw_item.hash in self.events_by_hash:
                    raise InvalidAbiException(f'Multiple events with the same topic: {abi_item.raw_item.name} and {self.events_by_hash[abi_item.raw_item.hash].raw_item.name}')
                self.events_by_hash[abi_item.raw_item.hash] = abi_item
                self.events_by_signature[abi_item.raw_item.signature] = abi_item
            elif item_type == ItemType.FUNCTION:
                abi_item = SemanticAbiFunction.from_json(item)
                if abi_item.raw_item.hash in self.functions_by_hash:
                    raise InvalidAbiException(f'Multiple functions with the same topic: {abi_item.raw_item.signature} and {self.functions_by_hash[abi_item.raw_item.hash].raw_item.signature}')
                self.functions_by_hash[abi_item.raw_item.hash] = abi_item
                self.functions_by_signature[abi_item.raw_item.signature] = abi_item
            # TODO ZZ if we don't care about the rest, why not skip all vs detecting unknown?
            elif ItemType.is_function_type(item_type) or item_type == ItemType.ERROR:
                # Ignore any other types
                continue
            else:
                raise InvalidAbiException(f'Unknown ABI item type {item_type}')

            has_primary_item = has_primary_item or abi_item.properties.is_primary
            all_items.append(abi_item)

        if not has_primary_item:
            raise InvalidAbiException('At least one primary ABI item must be specified')

        # validation
        for item in all_items:
            if item.properties.matches is not None:
                for match in item.properties.matches.matches:
                    if match.type == MatchItemType.EVENT:
                        if match.signature not in self.events_by_signature:
                            raise InvalidAbiException(f'Unknown event signature to match: {match.signature}')
                    elif match.type == MatchItemType.FUNCTION:
                        if match.signature not in self.functions_by_signature:
                            raise InvalidAbiException(f'Unknown function signature to match: {match.signature}')

                    # TODO ZZ the following 2 validations can be pushed down to item
                    if match.signature is not None and match.signature == item.raw_item.signature:
                        raise InvalidAbiException(f'Cannot match an item to itself: {match.signature}')

                    if match.prefix is not None:
                        for parameters_set in item.all_parameters():
                            if parameters_set.has_parameter(match.prefix) and isinstance(parameters_set.parameter(match.prefix).parameter, TupleParameter):
                                raise InvalidAbiException(f'Prefix "{match.prefix}" cannot be the name of a tuple parameter.')

    def should_consider(self, contract_address: str) -> bool:
        """
        If a set of contract address are specified on the ABI, then the contract address of an emitted log or trace
        must be in that set, otherwise we will skip transforming it
        """
        return len(self.contract_addresses) == 0 or HexNormalize.normalize(contract_address) in self.contract_addresses
