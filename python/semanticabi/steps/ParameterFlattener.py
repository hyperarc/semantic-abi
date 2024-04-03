from abc import ABC, abstractmethod
from typing import List

from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem
from semanticabi.abi.item.SemanticParameter import SemanticParameters, SemanticParameter
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.steps.FlattenedParameter import FlattenedParameter


class FlattenPredicate(ABC):
    """
    Predicate to determine what parameters to flatten
    """

    @abstractmethod
    def should_flatten(self, parameter: SemanticParameter, path: List[SemanticParameter]) -> bool:
        """
        Whether to flatten the components of the parameter
        """
        pass


class DefaultFlattenPredicate(FlattenPredicate):
    """
    Default predicate that flattens all non-array parameters
    """
    def should_flatten(self, parameter: SemanticParameter, path: List[SemanticParameter]) -> bool:
        """
        Don't flatten any array parameters
        """
        return not parameter.parameter.is_array


class ParameterFlattener:
    """
    Iterates through the parameters of an abi, flattening any tuple components to individual columns, and returning
    a list of the parameters that can be used to build the schema.

    For primitive parameters, we just create a column with the parameter name as the column name. For tuple parameters,
    we recursively go through the components, and create a column for each primitive component with a name that
    combines the parent parameter name and the individual parameter's name to ensure uniqueness.
    """
    _abi_item: SemanticAbiItem
    _predicate: FlattenPredicate
    _flattened_parameters: List[FlattenedParameter]

    @staticmethod
    def build_column_name(path: List[SemanticParameter], name: str) -> str:
        """
        Create a flattened column name for a parameter that is nested in a tuple
        """
        return '_'.join([p.name for p in path] + [name])

    def __init__(self, abi_item: SemanticAbiItem, predicate: FlattenPredicate = DefaultFlattenPredicate()):
        self._abi_item = abi_item
        self._predicate = predicate
        self._flattened_parameters = self._build_parameter_list()

    def parameter_list(self) -> List[FlattenedParameter]:
        """
        Get the list of flattened parameters for this abi item
        """
        return self._flattened_parameters

    def dataset_columns(self) -> List[DatasetColumn]:
        """
        Get the list of dataset columns for this abi item
        """
        return [parameter.final_dataset_column for parameter in self._flattened_parameters]

    def _build_parameter_list(self) -> List[FlattenedParameter]:
        parameters = self._flatten_parameters(self._abi_item.input_parameters, True)

        if self._abi_item.output_parameters is not None:
            parameters += self._flatten_parameters(self._abi_item.output_parameters, False)

        return parameters

    def _flatten_parameters(
        self,
        semantic_parameters: SemanticParameters,
        is_input: bool,
        path: List[SemanticParameter] = None
    ) -> List[FlattenedParameter]:
        if path is None:
            path = []

        flattened_parameters: List[FlattenedParameter] = []
        for semantic_trace_parameter in semantic_parameters.parameters().values():
            if semantic_trace_parameter.exclude:
                continue

            if not self._predicate.should_flatten(semantic_trace_parameter, path):
                continue

            flattened_parameters += self._flatten_parameter(semantic_trace_parameter, is_input, path)

        return flattened_parameters

    def _flatten_parameter(
        self,
        semantic_parameter: SemanticParameter,
        is_input: bool,
        path: List[SemanticParameter]
    ) -> List[FlattenedParameter]:
        if semantic_parameter.components is not None:
            # If we have a tuple, recursively flatten the components
            return self._flatten_parameters(
                semantic_parameter.components,
                is_input,
                path + [semantic_parameter]
            )
        else:
            return [FlattenedParameter(
                semantic_parameter,
                path,
                ParameterFlattener.build_column_name(path, semantic_parameter.name),
                is_input
            )]
