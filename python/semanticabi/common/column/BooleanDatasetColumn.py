from typing import Optional, Dict

import pyarrow

from semanticabi.common.column.DatasetColumn import DatasetColumn, TypeMetadata, AnalyticalType, IndexType
from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform


class BooleanDatasetColumn(DatasetColumn):
    """
    @author zuyezheng
    """

    def __init__(
        self,
        name: str,
        transform_f: Optional[DatasetColumnTransform] = None
    ):
        super().__init__(
            name=name,
            data_type=pyarrow.bool_(),
            index_types={IndexType.INVERTED},
            transform_f=transform_f
        )

    @property
    def type_metadata(self) -> TypeMetadata:
        return {
            'ingestType': 'boolean',
            'expectedType': 'boolean'
        }

    @property
    def extended_metadata(self) -> Dict[str, any]:
        return {}

    @property
    def analytical_type(self) -> AnalyticalType:
        return AnalyticalType.DIMENSION
