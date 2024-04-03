from typing import Dict, Set

from semanticabi.abi.item.DataType import DataType
from semanticabi.common.column.DatasetColumn import DatasetColumn, AnalyticalType, TypeMetadata, IndexType


class RenamedColumn(DatasetColumn):
    """
    Renames an existing column
    """
    _original_column: DatasetColumn
    _name: str

    def __init__(self, original_column: DatasetColumn, name: str):
        self._original_column = original_column
        self._name = name

    @property
    def data_type(self) -> DataType:
        return self._original_column.data_type

    @property
    def index_types(self) -> Set[IndexType]:
        return self._original_column.index_types

    @property
    def type_metadata(self) -> TypeMetadata:
        return self._original_column.type_metadata

    @property
    def extended_metadata(self) -> Dict[str, any]:
        return self._original_column.extended_metadata

    @property
    def analytical_type(self) -> AnalyticalType:
        return self._original_column.analytical_type

    @property
    def name(self) -> str:
        """
        Override the 'name' property to return the new name
        """
        return self._name
