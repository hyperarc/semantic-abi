from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, TypedDict, Set

from pyarrow import DataType

from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform


@dataclass
class DatasetColumn(ABC):
    """
    @author zuyezheng
    """

    name: str
    data_type: DataType
    index_types: Set[IndexType]
    transform_f: Optional[DatasetColumnTransform] = None

    @property
    @abstractmethod
    def type_metadata(self) -> TypeMetadata:
        """ Metadata about data type and storage. """
        pass

    @property
    @abstractmethod
    def extended_metadata(self) -> Dict[str, any]:
        """ Extended metadata with column type specifics. """
        pass

    @property
    @abstractmethod
    def analytical_type(self) -> AnalyticalType:
        pass

    def transform(self, data: Dict[str, any]) -> any:
        if self.transform_f is None:
            if self.name in data:
                value = data[self.name]
            else:
                value = None
        else:
            value = self.transform_f.transform(data, self.name)

        return self.post_transform_value(value)

    def post_transform_value(self, value: any) -> any:
        """
        After the transformation is applied to the value, any other post-processing that a particular column type
        needs to do can be done here
        """
        return value

    def __eq__(self, other: DatasetColumn) -> bool:
        return self.name == other.name \
               and self.data_type == other.data_type \
               and self.index_types == other.index_types \
               and self.type_metadata == other.type_metadata \
               and self.extended_metadata == other.extended_metadata \
               and self.analytical_type == other.analytical_type

    def __ne__(self, other: DatasetColumn) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.data_type, self.index_types, self.type_metadata, self.extended_metadata, self.analytical_type))

    def __str__(self):
        return f'Column({self.name}, {self.type_metadata["ingestType"]})'


class AnalyticalType(Enum):
    DIMENSION = 'dimensions'
    MEASURE = 'measures'
    DATE = 'dates'

    plural: str

    def __init__(self, plural: str):
        self.plural = plural


class IndexType(Enum):
    INVERTED = 'inverted'
    TEXT = 'text'
    NATIVE = 'native'
    TIMESTAMP = 'timestamp'
    RANGE = 'range'


class TypeMetadata(TypedDict):
    ingestType: str
    expectedType: str