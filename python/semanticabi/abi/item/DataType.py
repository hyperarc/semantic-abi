from __future__ import annotations

from enum import Enum
from typing import Optional, Callable

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform
from semanticabi.common.column.ToString import ToString
from semanticabi.common.column.NumericDatasetColumn import NumericDatasetColumn
from semanticabi.common.column.StringDatasetColumn import StringType


class DataType(Enum):
    """
    The output data type of a field or expression
    """

    INT = ('int', lambda name, transform_f: NumericDatasetColumn.int64(name))
    DOUBLE = ('double', lambda name, transform_f: NumericDatasetColumn.float64(name))
    STRING = ('string', lambda name, transform_f: StringType.NONE(
        name, transform_f=ToString(transform_f if transform_f is not None else None)
    ))

    type_name: str
    build_dataset_column: Callable[[str, Optional[DatasetColumnTransform]], DatasetColumn]

    def __init__(self, type_name: str, dataset_column_type_fn: Callable[[str, Optional[DatasetColumn]], DatasetColumn]):
        self.type_name = type_name
        self.build_dataset_column = dataset_column_type_fn

    @staticmethod
    def get(type_name: str) -> DataType:
        """
        Returns the DataType for the given string value.
        """
        try:
            return next(data_type for data_type in DataType if data_type.type_name == type_name)
        except StopIteration:
            raise InvalidAbiException(f'Invalid value for "type": {type_name}')

    def dataset_column(self, name: str, transform_f: Optional[DatasetColumnTransform] = None) -> DatasetColumn:
        """
        Returns the DatasetColumn for this data type with the given name.
        """
        return self.build_dataset_column(name, transform_f)
