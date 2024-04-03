from typing import List, Dict, Optional

from semanticabi.abi.item.SemanticAbiItem import DecodedResult
from semanticabi.abi.item.SemanticParameter import SemanticParameter
from semanticabi.common.TransformException import TransformException
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.FlattenedParameter import FlattenedParameter
from semanticabi.steps.ParameterFlattener import FlattenPredicate, ParameterFlattener
from semanticabi.steps.Step import Step, TransformItem
from semanticabi.steps.SubsequentStep import SubsequentStep


class ExplodeFlattenPredicate(FlattenPredicate):
    _explode_paths: Dict[str, List[str]]

    def __init__(self, explode_paths: Dict[str, List[str]]):
        self._explode_paths = explode_paths

    def should_flatten(self, parameter: SemanticParameter, path: List[SemanticParameter]) -> bool:
        """
        Only flatten if the parameter's path begins with any of the explode paths
        """
        full_path = path + [parameter]
        for explode_path, explode_path_parts in self._explode_paths.items():
            path_matches = True
            for i, path_part_param in enumerate(full_path):
                if i >= len(explode_path_parts):
                    # If the current path is a subpath of the explode path, then it's a component of an exploded tuple,
                    # which we want to include, unless it's another array
                    if path_part_param.parameter.is_array:
                        path_matches = False
                        break
                else:
                    # Otherwise make sure the current path at least starts with the appropriate params
                    if explode_path_parts[i] != path_part_param.name:
                        path_matches = False
                        break

            if path_matches:
                return True

        return False


class ExplodeStep(SubsequentStep):
    """
    Explodes an array parameter into a row for each element in the array
    """
    _parameter_flattener: ParameterFlattener
    _schema: AbiSchema

    def __init__(self, previous_step: Step):
        super().__init__(previous_step)
        explode_path_parts: Dict[str, List[str]] = {}
        if previous_step._abi_item.properties.explode is not None:
            explode_path_parts = previous_step._abi_item.properties.explode.path_parts
        self._parameter_flattener = ParameterFlattener(self._previous_step._abi_item, ExplodeFlattenPredicate(explode_path_parts))
        self._schema = self._previous_step.schema.with_columns(self._parameter_flattener.dataset_columns())

    @property
    def schema(self) -> AbiSchema:
        return self._schema

    def _should_transform(self):
        return self._abi_item.properties.explode is not None

    def _inner_transform_item(
        self,
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previous_data: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        decoded_result: DecodedResult = item.decoded_result

        # Sanity check that we aren't getting into combinatorics
        if len(previous_data) > 1:
            raise TransformException('Can only explode a single row of data')

        new_data: List[Dict[str, any]] = []
        flattened_parameters: List[FlattenedParameter] = self._parameter_flattener.parameter_list()
        for row in previous_data:
            flattened_arrays: List[List[str]] = []
            array_length: Optional[int] = None
            # Get the flattened array of values for each parameter
            for parameter in flattened_parameters:
                flattened_array: List[any] = parameter.flattened_array(decoded_result)

                if array_length is None:
                    array_length = len(flattened_array)
                else:
                    if array_length != len(flattened_array):
                        raise TransformException(f'Parameter \'{parameter.final_column_name}\' has a different number of elements than the other exploded parameters')

                flattened_arrays.append(flattened_array)

            # Zip the flattened arrays into tuples that get turned into rows
            for zipped_data in zip(*flattened_arrays):
                new_data_map = row.copy()
                for index, param_value in enumerate(zipped_data):
                    new_data_map[flattened_parameters[index].final_column_name] = param_value

                new_data.append(new_data_map)

        return new_data
