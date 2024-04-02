from dataclasses import dataclass
from typing import Dict, Optional

from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform


@dataclass
class HexToFloat(DatasetColumnTransform):

    # provide to rename
    source_col: str = None

    @staticmethod
    def convert(value: str | int) -> Optional[float]:
        if value is None:
            return None

        if isinstance(value, str):
            return float(int(value, 16))
        else:
            return float(value)

    def transform(self, blob: Dict[str, any], key: str) -> any:
        key = key if self.source_col is None else self.source_col

        if key in blob:
            return HexToFloat.convert(blob[key])
        else:
            return None
