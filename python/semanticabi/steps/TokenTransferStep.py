from typing import List, Dict, Tuple

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.decoded.TokenTransferDecoded import TokenTransferDecoded
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem
from semanticabi.common.column.NumericDatasetColumn import NumericDatasetColumn, NumericType
from semanticabi.common.column.StringDatasetColumn import StringType
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.Step import Step, TransformItem


_SCHEMA: AbiSchema = AbiSchema([
    StringType.ADDRESS_HASH('fromAddress'),
    StringType.ADDRESS_HASH('toAddress'),
    NumericDatasetColumn.int256('value', higher_order_type=NumericType.CURRENCY),
    StringType.ID('tokenId'),
    StringType.ENUM('tokenType')
])


class TokenTransferTransformItem(TransformItem):
    _token_transfer: TokenTransferDecoded

    def __init__(self, token_transfer: TokenTransferDecoded):
        # We don't have a DecodedResult that we need to pass down
        super().__init__(None)
        self._token_transfer = token_transfer

    @property
    def contract_address(self) -> str:
        return self._token_transfer.contract_address

    @property
    def internal_index(self) -> str:
        return str(self._token_transfer.internal_index)

    @property
    def item_type(self) -> str:
        return 'transfer'


class TokenTransferStep(Step):
    """
    Special step to handle token transfer matches. This takes all the various transfer events from the transaction and
    generates a single row for each transfer event, with the from, to, value, tokenId, and tokenType fields
    """

    @property
    def _abi(self) -> SemanticAbi:
        raise Exception('Method not implemented.')

    @property
    def _abi_item(self) -> SemanticAbiItem:
        raise Exception('Method not implemented.')

    @property
    def schema(self) -> AbiSchema:
        return _SCHEMA

    def _inner_transform(self, block: EthBlock, transaction: EthTransaction) -> List[Tuple[TransformItem, List[Dict[str, any]]]]:
        results: List[Tuple[TransformItem, List[Dict[str, any]]]] = []

        for transfer in transaction.transfers:
            results.append((TokenTransferTransformItem(transfer), [{
                'fromAddress': transfer.from_address,
                'toAddress': transfer.to_address,
                'value': transfer.value,
                'tokenId': str(transfer.token_id),
                'tokenType': transfer.token_type.code
            }]))

        return results
