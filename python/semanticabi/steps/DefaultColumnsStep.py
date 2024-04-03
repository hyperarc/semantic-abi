from typing import List, Tuple, Dict, Callable

from semanticabi.common.column.HexToFloat import HexToFloat
from semanticabi.common.ValueConverter import ValueConverter
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.common.column.HexNormalize import HexNormalize
from semanticabi.common.column.NumericDatasetColumn import NumericDatasetColumn, NumericType
from semanticabi.common.column.StringDatasetColumn import StringType
from semanticabi.common.column.TimestampDatasetColumn import TimestampDatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.Step import Step, TransformItem
from semanticabi.steps.SubsequentStep import SubsequentStep

DEFAULT_COLUMNS: List[Tuple[DatasetColumn, Callable[[EthBlock, EthTransaction, TransformItem], any]]] = [
    (StringType.ENUM('chain'), lambda block, transaction, result_item: block.chain.value),
    (StringType.BLOCK_HASH('blockHash'), lambda block, transaction, result_item: HexNormalize.normalize(block.block['hash'])),
    (NumericDatasetColumn.uint32('blockNumber', higher_order_type=NumericType.INDEX), lambda block, transaction, result_item: ValueConverter.hex_to_int(block.number)),
    (TimestampDatasetColumn.timestamp('blockTimestamp', is_time_sort_column=True), lambda block, transaction, result_item: ValueConverter.hex_to_int(block.timestamp)),
    (StringType.TRANSACTION_HASH('transactionHash'), lambda block, transaction, result_item: HexNormalize.normalize(transaction.hash)),
    (StringType.ADDRESS_HASH('transactionFrom'), lambda block, transaction, result_item: HexNormalize.normalize(transaction.from_address)),
    (StringType.ADDRESS_HASH('transactionTo'), lambda block, transaction, result_item: HexNormalize.normalize(transaction.to_address)),
    (StringType.ADDRESS_HASH('contractAddress'), lambda block, transaction, result_item: HexNormalize.normalize(result_item.contract_address)),
    (NumericDatasetColumn.uint8('status', higher_order_type=NumericType.ENUM), lambda block, transaction, result_item: ValueConverter.hex_to_int(transaction.receipt['status'])),
    (NumericDatasetColumn.float64('gasUsed', higher_order_type=NumericType.CURRENCY), lambda block, transaction, result_item: HexToFloat.convert(transaction.receipt['gasUsed'])),
    (StringType.ENUM('itemType'), lambda block, transaction, result_item: result_item.item_type),
    # This index needs to be a string as function calls don't have an integer index that we can use to uniquely identify
    # them within a transaction, and so we use the trace_hash instead
    (StringType.NONE('internalIndex'), lambda block, transaction, result_item: result_item.internal_index)
]


class DefaultColumnsStep(SubsequentStep):
    """
    Adds a set of default columns to the output
    """

    _schema: AbiSchema

    def __init__(self, previous_step: Step):
        super().__init__(previous_step)
        self._schema = previous_step.schema.with_columns([el[0] for el in DEFAULT_COLUMNS])

    @property
    def schema(self) -> AbiSchema:
        return self._schema

    def _inner_transform_item(
        self,
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previous_data: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        new_data: List[Dict[str, any]] = []
        for row in previous_data:
            # Add the default columns to the existing data
            for column, extractor_fn in DEFAULT_COLUMNS:
                row[column.name] = extractor_fn(block, transaction, item)

            new_data.append(row)

        return new_data
