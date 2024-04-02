from typing import Optional, Dict, Literal

import pyarrow
from pyarrow import DataType, TimestampType

from semanticabi.common.column.DatasetColumn import DatasetColumn, TypeMetadata, AnalyticalType, IndexType
from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform


class TimestampTypeMetadata(TypeMetadata):
    grain: str


class TimestampDatasetColumn(DatasetColumn):
    """
    @author zuyezheng
    """

    @staticmethod
    def epoch(name: str, transform_f: Optional[DatasetColumnTransform] = None, is_time_sort_column: bool = False):
        return TimestampDatasetColumn(name, 's', pyarrow.int64(), transform_f, is_time_sort_column)

    @staticmethod
    def timestamp(
        name: str,
        grain: Literal['s', 'ms'] = 's',
        transform_f: Optional[DatasetColumnTransform] = None,
        is_time_sort_column: bool = False
    ):
        return TimestampDatasetColumn(name, grain, pyarrow.timestamp(grain, tz='UTC'), transform_f, is_time_sort_column)

    grain: str
    is_time_sort_column: bool

    def __init__(
        self,
        name: str,
        grain: Literal['s', 'ms'],
        data_type: DataType,
        transform_f: Optional[DatasetColumnTransform],
        is_time_sort_column: bool
    ):
        self.grain = grain
        self.is_time_sort_column = is_time_sort_column
        super().__init__(
            name=name, 
            data_type=data_type,
            index_types={IndexType.TIMESTAMP},
            transform_f=transform_f
        )

    @property
    def type_metadata(self) -> TimestampTypeMetadata:
        return {
            # either a full timestamp or epoch
            'ingestType': 'timestamp' if isinstance(self.data_type, TimestampType) else 'long',
            'expectedType': 'timestamp',
            'grain': self.grain
        }

    @property
    def analytical_type(self) -> AnalyticalType:
        return AnalyticalType.DATE

    @property
    def extended_metadata(self) -> Dict[str, any]:
        return {
            "isTimeSortColumn": self.is_time_sort_column
        }
