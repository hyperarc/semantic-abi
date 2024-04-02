from __future__ import annotations
from typing import List, Dict, Callable

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.common.column.RenamedColumn import RenamedColumn


class AbiSchema:
    """
    The column schema from parsing a semantic abi
    """

    _columns: List[DatasetColumn]
    _column_indices: Dict[str, int]

    def __init__(self, columns: List[DatasetColumn] = None):
        if columns is None:
            columns = []
        self._columns = columns
        self._column_indices = {column.name: index for index, column in enumerate(columns)}

    def columns(self) -> List[DatasetColumn]:
        return self._columns

    def column(self, name: str) -> DatasetColumn:
        return self._columns[self._column_indices[name]]

    def has_column(self, name: str) -> bool:
        return name in self._column_indices

    def with_columns(self, columns: List[DatasetColumn], allow_overwrite: bool = False) -> AbiSchema:
        """
        Append the list of columns to the existing columns
        """
        new_columns: List[DatasetColumn] = self._columns.copy()
        for column in columns:
            if column.name in self._column_indices and not allow_overwrite:
                raise InvalidAbiException(f'Column \'{column.name}\' already exists in schema')

            if column.name in self._column_indices:
                new_columns[self._column_indices[column.name]] = column
            else:
                new_columns.append(column)

        return AbiSchema(new_columns)

    def append_schema_with_rename(self, schema: AbiSchema, column_rename_fn: Callable[[str], str]) -> AbiSchema:
        """
        Append the schema to this schema while renaming each column using the given rename function
        """
        new_columns: List[DatasetColumn] = self._columns.copy()
        for column in schema.columns():
            new_column_name = column_rename_fn(column.name)
            if new_column_name in self._column_indices:
                raise InvalidAbiException(f'Column \'{new_column_name}\' already exists in schema')

            new_columns.append(RenamedColumn(column, new_column_name))

        return AbiSchema(new_columns)

    def __eq__(self, other: AbiSchema) -> bool:
        return self._columns == other._columns

    def __ne__(self, other: AbiSchema) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._columns)

    def __str__(self):
        return f'AbiSchema({",".join([str(column) for column in self._columns])})'
