from enum import Enum
from typing import Optional, Dict, Set

import pyarrow

from semanticabi.common.column.HexNormalize import HexNormalize
from semanticabi.common.column.DatasetColumn import DatasetColumn, TypeMetadata, AnalyticalType, IndexType
from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform


class StringTypeMetadata(TypeMetadata):
    isArray: bool


class StringType(Enum):
    NONE = ('none', None, {IndexType.INVERTED, IndexType.TEXT}, {IndexType.INVERTED, IndexType.TEXT})

    # low cardinality dimension
    ENUM = ('enum', None, {IndexType.INVERTED, IndexType.TEXT}, {IndexType.INVERTED, IndexType.TEXT})

    # large text blob that we want to enable text search and likely no others
    BLOB = ('blob', None, {IndexType.INVERTED, IndexType.TEXT}, {IndexType.INVERTED, IndexType.TEXT})

    # high cardinality hashes or ids where a text index isn't that useful
    BLOCK_HASH = ('blockHash', 'hash', {IndexType.INVERTED})
    TRANSACTION_HASH = ('transactionHash', 'hash', {IndexType.INVERTED})
    ADDRESS_HASH = ('addressHash', 'hash', {IndexType.INVERTED})
    HASH = ('hash', 'hash', {IndexType.INVERTED})
    SIGNATURE = ('signature', 'hash', {IndexType.INVERTED})
    ID = ('id', 'id', {IndexType.INVERTED})

    # generated system fields like for errors during processing
    SYSTEM = ('system', None, {})

    code: str
    category: str
    _index_types: Set[IndexType]
    # if there are separate index types if it's an array
    _array_index_types: Set[IndexType]

    def __init__(self, code: str, category: str, index_types: Set[IndexType], array_index_types: Set[IndexType] = None):
        self.code = code
        self.category = category
        self._index_types = index_types
        self._array_index_types = array_index_types

    def __call__(self, name: str, **kwargs):
        if self.category == 'hash' and 'transform_f' not in kwargs:
            kwargs['transform_f'] = HexNormalize()

        return StringDatasetColumn(
            name,
            higher_order_type=self,
            **kwargs
        )

    def index_types(self, is_array: bool):
        if is_array and self._array_index_types is not None:
            return self._array_index_types
        else:
            return self._index_types


class StringDatasetColumn(DatasetColumn):
    """
    @author zuyezheng
    """

    higher_order_type: StringType
    is_array: bool
    # If the column is nullable, write empty strings as nulls
    is_nullable: bool

    def __init__(
        self,
        name: str,
        *,
        transform_f: Optional[DatasetColumnTransform] = None,
        higher_order_type: StringType = StringType.NONE,
        is_array: bool = False,
        is_nullable: bool = False
    ):
        super().__init__(
            name=name,
            data_type=pyarrow.list_(pyarrow.string()) if is_array else pyarrow.string(),
            index_types=higher_order_type.index_types(is_array),
            transform_f=transform_f
        )

        self.higher_order_type = higher_order_type
        self.is_array = is_array
        self.is_nullable = is_nullable

    @property
    def type_metadata(self) -> StringTypeMetadata:
        return {
            'ingestType': 'string',
            'expectedType': 'string',
            'isArray': self.is_array
        }

    @property
    def extended_metadata(self) -> Dict[str, any]:
        return {
            'higherOrderType': self.higher_order_type.code,
        }

    @property
    def analytical_type(self) -> AnalyticalType:
        return AnalyticalType.DIMENSION

    def post_transform_value(self, value: any) -> any:
        # coerce into a string if not none
        if self.is_array:
            return value
        elif value is not None and not isinstance(value, str):
            return str(value)
        elif self.is_nullable and value == '':
            return None
        else:
            return value
