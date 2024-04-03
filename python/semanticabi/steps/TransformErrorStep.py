from typing import List, Dict

from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.Step import Step, TransformItem, TRANSFORM_ERROR_COLUMN
from semanticabi.steps.SubsequentStep import SubsequentStep


class TransformErrorStep(SubsequentStep):
    """
    Special step that adds a column to the schema for holding errors that occurred during the transform. This doesn't
    actually add the error to the data, but only informs the final transform process that it should include any errors
    in the data
    """

    _schema: AbiSchema

    def __init__(self, previous_step: Step):
        super().__init__(previous_step)
        self._schema = previous_step.schema.with_columns([TRANSFORM_ERROR_COLUMN])

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
        return previous_data
