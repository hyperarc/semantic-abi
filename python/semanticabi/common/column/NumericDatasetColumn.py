from __future__ import annotations

from enum import Enum
from typing import Optional, Dict, Set

import pyarrow
from pyarrow import DataType

from semanticabi.common.column.DatasetColumn import DatasetColumn, TypeMetadata, AnalyticalType, IndexType
from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform


class DecimalTypeMetadata(TypeMetadata):
    precision: int
    scale: int


class NumericType(Enum):
    NONE = (None, False)
    # token or coin value
    CURRENCY = ('currency', False)
    # scale of a decimal value represented as an integer
    SCALE = ('scale', False)
    COUNT = ('count', False)

    """ Numerical Dimensions"""
    # incrementing index
    INDEX = ('index', True)
    # enumeration like status, should be treated as a dimension
    ENUM = ('enum', True, {IndexType.INVERTED})

    code: str
    is_dimension: bool
    index_types: Set[IndexType]

    def __init__(
        self,
        code: str,
        is_dimension: bool,
        # default index type will be range, specify another if needed
        index_types: Set[IndexType] = None
    ):
        self.code = code
        self.is_dimension = is_dimension
        self.index_types = {IndexType.RANGE} if index_types is None else index_types


class NumericDatasetColumn(DatasetColumn):
    """
    @author zuyezheng
    """

    @staticmethod
    def int8(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.int8(), 'byte', **kwargs)

    @staticmethod
    def uint8(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.uint8(), 'short', **kwargs)

    @staticmethod
    def int16(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.int16(), 'short', **kwargs)

    @staticmethod
    def uint16(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.uint16(), 'integer', **kwargs)

    @staticmethod
    def int32(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.int32(), 'integer', **kwargs)

    @staticmethod
    def uint32(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.uint32(), 'long', **kwargs)

    @staticmethod
    def int64(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.int64(), 'long', **kwargs)

    @staticmethod
    def float32(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.float32(), 'float', **kwargs)

    @staticmethod
    def float64(name: str, **kwargs) -> NumericDatasetColumn:
        return NumericDatasetColumn(name, pyarrow.float64(), 'double', **kwargs)

    @staticmethod
    def uint64(name: str, **kwargs) -> NumericDatasetColumn:
        return DecimalDatasetColumn(name, 20, 0, **kwargs)

    @staticmethod
    def int128(name: str, **kwargs) -> NumericDatasetColumn:
        """
        This is the max precision decimal/integer that can be ingested natively into spark, although EVMs use uint256
        for values, this is likely sufficient with most supplies in the billions and up to 18 decimal places.
        """
        return DecimalDatasetColumn(name, 38, 0, **kwargs)

    @staticmethod
    def int256(name: str, **kwargs) -> NumericDatasetColumn:
        return CoercedNumericSilverColumn(name, 78, 0, **kwargs)

    @staticmethod
    def unscaled_int64(name: str, scale: int, **kwargs) -> NumericDatasetColumn:
        """
        For currently unscaled int64s with known scales that can be applied during ingest. Signs don't really matter
        since stored as decimals/bigdecimals.
        """
        return DecimalDatasetColumn(name, 20, scale, data_type=pyarrow.decimal128(20, 0), **kwargs)

    @staticmethod
    def unscaled_int128(name: str, scale: int, **kwargs) -> NumericDatasetColumn:
        """ For currently unscaled int128s with known scales that can be applied during ingest. """
        return DecimalDatasetColumn(name, 38, scale, data_type=pyarrow.decimal128(38, 0), **kwargs)

    @staticmethod
    def unscaled_int(name: str, precision: int, scale: int, **kwargs) -> NumericDatasetColumn:
        """
        For something more custom which will either use a decimal (supports up to 38 digits of precision) or a string
        if greater.
        """
        if precision <= 38:
            return DecimalDatasetColumn(name, precision, scale, data_type=pyarrow.decimal128(precision, 0), **kwargs)
        else:
            return CoercedNumericSilverColumn(name, precision, scale, **kwargs)

    ingest_type: str
    expected_type: str
    higher_order_type: NumericType
    is_dimension: bool

    def __init__(
        self,
        name: str,
        data_type: DataType,
        ingest_type: str,
        expected_type: str = None,
        *,
        # total number of digits
        transform_f: Optional[DatasetColumnTransform] = None,
        higher_order_type: NumericType = NumericType.NONE,
        # if it should be considered a numerical dimension, will default to that of the higher order type
        is_dimension: bool = None
    ):
        super().__init__(
            name=name,
            data_type=data_type,
            index_types=higher_order_type.index_types,
            transform_f=transform_f
        )

        self.ingest_type = ingest_type
        self.expected_type = ingest_type if expected_type is None else expected_type
        self.higher_order_type = higher_order_type
        self.is_dimension = self.higher_order_type.is_dimension if is_dimension is None else is_dimension

    @property
    def type_metadata(self) -> TypeMetadata:
        return {
            'ingestType': self.ingest_type,
            'expectedType': self.expected_type
        }

    @property
    def extended_metadata(self) -> Dict[str, any]:
        return {
            'higherOrderType': self.higher_order_type.code
        }

    @property
    def analytical_type(self) -> AnalyticalType:
        return AnalyticalType.DIMENSION if self.is_dimension else AnalyticalType.MEASURE


class DecimalDatasetColumn(NumericDatasetColumn):
    """
    Numeric column that needs to be stored into a string for storage.

    @author zuyezheng
    """

    precision: int
    scale: int

    def __init__(
        self,
        name: str,
        # total number of digits
        precision: int,
        # number of decimal places
        scale: int,
        *,
        data_type: Optional[DataType] = None,
        ingest_type: Optional[str] = 'decimal',
        expected_type: Optional[str] = 'decimal',
        transform_f: Optional[DatasetColumnTransform] = None,
        higher_order_type: NumericType = NumericType.NONE
    ):
        self.precision = precision
        self.scale = scale

        if data_type is None:
            data_type = pyarrow.decimal128(precision, scale)

        super().__init__(
            name,
            data_type=data_type,
            ingest_type=ingest_type,
            expected_type=expected_type,
            transform_f=transform_f,
            higher_order_type=higher_order_type
        )

    @property
    def type_metadata(self) -> DecimalTypeMetadata:
        return {
            'ingestType': self.ingest_type,
            'expectedType': self.expected_type,
            'precision': self.precision,
            'scale': self.scale
        }


class CoercedNumericSilverColumn(DecimalDatasetColumn):
    """
    Numeric column that needs to be stored into a string for storage.

    @author zuyezheng
    """

    def __init__(
        self,
        name: str,
        # total number of digits
        precision: int,
        # number of decimal places
        scale: int,
        transform_f: Optional[DatasetColumnTransform] = None,
        higher_order_type: NumericType = NumericType.NONE
    ):
        super().__init__(
            name,
            precision,
            scale,
            data_type=pyarrow.string(),
            ingest_type='string',
            expected_type='decimal',
            transform_f=transform_f,
            higher_order_type=higher_order_type
        )

    def post_transform_value(self, value: any) -> any:
        """
        For coerced numbers, they should be represented as strings
        """
        if value is not None:
            return str(value)

        return None
