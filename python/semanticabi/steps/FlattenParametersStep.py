from typing import List, Dict

from semanticabi.abi.item.SemanticAbiItem import DecodedResult
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.ParameterFlattener import ParameterFlattener
from semanticabi.steps.Step import Step, TransformItem
from semanticabi.steps.SubsequentStep import SubsequentStep


class FlattenParametersStep(SubsequentStep):
    """
    Adds all included parameters from the abi item to the schema and results
    """

    _parameter_flattener: ParameterFlattener
    _schema: AbiSchema

    def __init__(self, previous_step: Step):
        super().__init__(previous_step)
        self._parameter_flattener = ParameterFlattener(self._previous_step._abi_item)
        self._schema = self._previous_step.schema.with_columns(self._parameter_flattener.dataset_columns())

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
        decoded_result: DecodedResult = item.decoded_result

        new_data: List[Dict[str, any]] = []
        for row in previous_data:
            for parameter in self._parameter_flattener.parameter_list():
                row[parameter.final_column_name] = parameter.flattened_value(decoded_result)

            new_data.append(row)

        return new_data
