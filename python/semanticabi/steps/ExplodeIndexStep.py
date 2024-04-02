from typing import List, Dict

from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.common.column.NumericDatasetColumn import NumericDatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.Step import Step, TransformItem
from semanticabi.steps.SubsequentStep import SubsequentStep

# If we explode more than 65,535 rows, then that's a crazy amount of data in that transaction
_EXPLODE_INDEX_COLUMN: DatasetColumn = NumericDatasetColumn.uint16('explodeIndex')


class ExplodeIndexStep(SubsequentStep):
    """
    After the Explode and Match steps, adds a unique index for each row of exploded or "many" matched data
    """
    _schema: AbiSchema

    def __init__(self, previous_step: Step):
        super().__init__(previous_step)
        self._schema = previous_step.schema.with_columns([_EXPLODE_INDEX_COLUMN])

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
        for i, row in enumerate(previous_data):
            # Just use the index of the exploded row as the explode index
            row[_EXPLODE_INDEX_COLUMN.name] = i
            new_data.append(row)

        return new_data

