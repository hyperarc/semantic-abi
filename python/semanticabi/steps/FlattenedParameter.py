from dataclasses import dataclass
from functools import cached_property
from typing import List, Dict, Optional

from semanticabi.abi.item.Parameter import PrimitiveParameter, Parameter
from semanticabi.abi.item.SemanticAbiItem import DecodedResult
from semanticabi.abi.item.SemanticParameter import SemanticParameter
from semanticabi.common.TransformException import TransformException
from semanticabi.common.ValueConverter import ValueConverter
from semanticabi.common.column.BooleanDatasetColumn import BooleanDatasetColumn
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.common.column.HexNormalize import HexNormalize
from semanticabi.common.column.NumericDatasetColumn import NumericDatasetColumn
from semanticabi.common.column.StringDatasetColumn import StringType


@dataclass
class FlattenedParameter:

    # The parameter that this flattened parameter represents.
    semantic_parameter: SemanticParameter
    # The path to the parameter if the parameter is nested within a tuple.
    path: List[SemanticParameter]
    # The name of the column in the dataset for this parameter based on the path to this parameter.
    raw_column_name: str
    # If this is an input or output parameter.
    is_input: bool

    @cached_property
    def final_column_name(self) -> str:
        """
        The final column name for this parameter, which is the raw column name if there is no transform, or the
        transform name if there is a transform
        """
        if self.semantic_parameter.transform is None or self.semantic_parameter.transform.name is None:
            return self.raw_column_name
        else:
            return self.semantic_parameter.transform.name

    @cached_property
    def final_dataset_column(self) -> DatasetColumn:
        """
        The final column type for this parameter, which is the raw column type if there is no transform, or the
        transform type if there is a transform
        """
        column_name: str = self.final_column_name
        raw_column: DatasetColumn = FlattenedParameter.build_column(self.semantic_parameter.parameter, column_name)
        if self.semantic_parameter.transform is None or self.semantic_parameter.transform.type is None:
            return raw_column
        else:
            return self.semantic_parameter.transform.type.dataset_column(column_name, raw_column.transform_f)

    def flattened_value(self, decoded_result: DecodedResult) -> any:
        """
        Get the decoded and transformed parameter value for this flattened parameter
        """
        full_path = self.path + [self.semantic_parameter]
        # First get the raw decoded value
        if self.is_input:
            value = self._navigate_path(full_path, decoded_result.decoded_input_json)
        else:
            value = self._navigate_path(full_path, decoded_result.decoded_output_json)

        if value is None:
            raise TransformException(f'Could not find value at path {full_path}')

        return self._apply_transforms(value)

    def flattened_array(self, decoded_result: DecodedResult) -> List[any]:
        """
        Get the decoded and transformed array values for this flattened parameter
        """
        full_path = self.path + [self.semantic_parameter]
        # First get the raw decoded value
        if self.is_input:
            value = self._navigate_array_path(full_path, decoded_result.decoded_input_json)
        else:
            value = self._navigate_array_path(full_path, decoded_result.decoded_output_json)

        if value is None:
            raise TransformException(f'Could not find value at path {full_path}')

        return [self._apply_transforms(v) for v in value]

    @staticmethod
    def build_column(parameter: Parameter, column_name: str) -> DatasetColumn:
        """
        Derive the appropriate column type from the type of the parameter
        """
        if not isinstance(parameter, PrimitiveParameter):
            raise Exception('Can only build column type for primitive parameter')

        primitive_type: str = parameter.signature
        if parameter.is_array:
            # Remove the trailing []
            primitive_type = primitive_type[:-2]

        # Mapping the various types listed here: https://docs.soliditylang.org/en/latest/abi-spec.html#types
        if primitive_type == 'bool':
            return BooleanDatasetColumn(column_name)
        elif primitive_type == 'address':
            return StringType.ADDRESS_HASH(column_name)
        elif primitive_type == 'string':
            return StringType.NONE(column_name)
        elif primitive_type.startswith('bytes'):
            if primitive_type == 'bytes':
                return StringType.NONE(column_name)

            # bytes are just decoded as strings
            return StringType.NONE(column_name)
        elif primitive_type.startswith('int'):
            if primitive_type == 'int':
                return NumericDatasetColumn.int256(column_name)

            size = int(primitive_type[3:])
            if size > 128:
                return NumericDatasetColumn.int256(column_name)
            elif size > 64:
                return NumericDatasetColumn.int128(column_name)
            elif size > 32:
                return NumericDatasetColumn.int64(column_name)
            elif size > 16:
                return NumericDatasetColumn.int32(column_name)
            elif size > 8:
                return NumericDatasetColumn.int16(column_name)
            else:
                return NumericDatasetColumn.int8(column_name)
        elif primitive_type.startswith('uint'):
            if primitive_type == 'uint':
                return NumericDatasetColumn.int256(column_name)

            size = int(primitive_type[4:])
            if size > 64:
                # Use int256 as it is coerced into a string anyway
                return NumericDatasetColumn.int256(column_name)
            elif size > 32:
                return NumericDatasetColumn.uint64(column_name)
            elif size > 16:
                return NumericDatasetColumn.uint32(column_name)
            elif size > 8:
                return NumericDatasetColumn.uint16(column_name)
            else:
                return NumericDatasetColumn.uint8(column_name)
        else:
            # TODO: support fixed and ufixed
            raise Exception(f'Unsupported primitive type {primitive_type} for parameter {parameter.name}')

    def _apply_transforms(self, value: any) -> any:
        primitive_type: str = self.semantic_parameter.parameter.signature
        if primitive_type.startswith('int') or primitive_type.startswith('uint'):
            value = ValueConverter.hex_to_int(value)
        elif primitive_type.startswith('address'):
            # Make sure all addresses get normalized before they might happen to get used in a match
            value = HexNormalize.normalize(value)

        # Finally evaluate any expression transformations
        if self.semantic_parameter.transform is not None:
            value = self.semantic_parameter.transform.evaluate_expression(value)

        return value

    @staticmethod
    def _navigate_path(full_path: List[SemanticParameter], decoded_json: Dict[str, any]) -> Optional[any]:
        """
        Return the value at the nested path, or None if any part of the path doesn't exist
        """
        json = decoded_json
        for param in full_path:
            if param.name not in json:
                return None

            json = json[param.name]

        return json

    @staticmethod
    def _navigate_array_path(full_path: List[SemanticParameter], decoded_json: Dict[str, any]) -> Optional[List[any]]:
        """
        Return the array values at the nested path, or None if any part of the path doesn't exist
        """
        json = decoded_json
        array_param_index = next((i for i, param in enumerate(full_path) if param.parameter.is_array), None)
        if array_param_index is None:
            return None

        # Navigate through the array param
        for param in full_path[0:array_param_index + 1]:
            if param.name not in json:
                return None

            json = json[param.name]

        # Then navigate through each array item the rest of the way
        return [FlattenedParameter._navigate_path(full_path[array_param_index + 1:], value) for value in json]
