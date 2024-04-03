from __future__ import annotations
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Dict

import eth_abi
from Crypto.Hash import keccak

from semanticabi.abi.Decoded import DecodedTuple
from semanticabi.abi.item.Parameter import Parameters
from semanticabi.abi.item.ItemType import ItemType


class AbiItem(ABC):
    """
    Item in an ABI definition.

    @author zuyezheng
    """

    name: str
    # all of the inputs
    inputs: Parameters
    # signature of the item such as `fn(address,uint256)`.
    signature: str
    # any extra metadata to help disambiguate the log since ambiguity like indexed vs unindexed parameters could cause
    # hash collisions
    extra: Dict[str, any]

    def __init__(
        self,
        name: str,
        inputs: Parameters,
        extra: Dict[str, any]
    ):
        self.name = name
        self.inputs = inputs
        self.extra = extra

        self.signature = f'{self.name}({",".join(self.inputs.signatures())})'

    @property
    @abstractmethod
    def hash(self) -> str:
        """
        Hash used to match encoded data to this item.
        """
        pass

    @abstractmethod
    def decode(self, item_json: Dict[str, any]) -> DecodedTuple:
        pass


class AbiFunction(AbiItem):

    @staticmethod
    def from_json(item_json: Dict[str, any]) -> AbiFunction:
        return AbiFunction(
            item_json['name'],
            ItemType(item_json['type']),
            Parameters.from_json(item_json['inputs']),
            # traces also have outputs
            Parameters.from_json(item_json['outputs']),
            item_json.get('extra')
        )

    def __init__(
        self,
        name: str,
        function_type: ItemType,
        inputs: Parameters,
        outputs: Parameters,
        # any extra metadata
        extra: Dict[str, any]
    ):
        super().__init__(name, inputs, extra)
        self.function_type = function_type
        self.outputs = outputs

    @cached_property
    def hash(self) -> str:
        item_hash = keccak.new(digest_bits=256)
        item_hash.update(str.encode(self.signature))
        # functions only use the first 8 hex digits
        return item_hash.hexdigest()[0:8]

    def decode(self, input: str) -> DecodedTuple:
        return DecodedTuple.from_parameters_and_values(
            None,
            self.inputs.parameters(),
            eth_abi.decode(
                # build out the signatures to decode
                self.inputs.signatures(),
                # use input encoded as hex stripping the 0x and function signature
                bytearray.fromhex(input[10:])
            )
        )

    def decode_output(self, output: str) -> DecodedTuple:
        return DecodedTuple.from_parameters_and_values(
            None,
            self.outputs.parameters(),
            eth_abi.decode(
                # build out the signatures to decode
                self.outputs.signatures(),
                # use output encoded as hex stripping the 0x
                bytearray.fromhex(output[2:])
            )
        )


class AbiEvent(AbiItem):

    @staticmethod
    def from_json(item_json: Dict[str, any]) -> AbiEvent:
        return AbiEvent(
            item_json['name'],
            Parameters.from_json(item_json['inputs']),
            item_json.get('extra')
        )

    @cached_property
    def hash(self) -> str:
        item_hash = keccak.new(digest_bits=256)
        item_hash.update(str.encode(self.signature))
        return item_hash.hexdigest()

    @cached_property
    def num_indexed(self) -> int:
        return len(self.inputs.parameters(True))

    def is_of(self, log: Dict[str, any], check_num_indexed: bool = True) -> bool:
        """
        Check if the log is of the event, optionally checking the right number of indexed parameters in addition to hash.
        """
        if log['topics'][0][2:] != self.hash:
            return False

        if check_num_indexed and (len(log['topics']) - 1) != self.num_indexed:
            return False

        return True

    def decode(self, item: Dict[str, any]) -> DecodedTuple:
        # we'll be decoding out of order due to indexed vs unindexed parameters, map them so we can reorder at the end
        decoded = {}

        # events/logs are split between indexed and unindexed parameters, start with the indexed first
        indexed_data = bytearray.fromhex(''.join(
            map(
                # need to strip '0x' off all the hex strings
                lambda s: s[2:],
                # first topic is event hash, use the rest
                item['topics'][1:]
            )
        ))
        decoded_values = eth_abi.decode(self.inputs.signatures(True), indexed_data)
        for parameter_i, parameter in enumerate(self.inputs.parameters(True)):
            decoded[parameter.name] = decoded_values[parameter_i]

        # decode the rest of the data blob
        decoded_values = eth_abi.decode(self.inputs.signatures(False), bytearray.fromhex(item['data'][2:]))
        for parameter_i, parameter in enumerate(self.inputs.parameters(False)):
            decoded[parameter.name] = decoded_values[parameter_i]

        return DecodedTuple.from_parameters_and_values(
            None,
            self.inputs.parameters(),
            # reorder decoded values to match the signature
            [decoded[parameter.name] for parameter in self.inputs.parameters()]
        )

