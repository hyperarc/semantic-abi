from dataclasses import dataclass
from typing import Dict

from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform


@dataclass
class HexNormalize(DatasetColumnTransform):
    """
    Lowercase hex strings.

    @author zuyezheng
    """

    # provide to rename
    source_col: str = None

    @staticmethod
    def normalize(hex: str) -> str:
        return hex.lower()

    def transform(self, blob: Dict[str, any], key: str) -> any:
        key = key if self.source_col is None else self.source_col

        if key in blob and blob[key] is not None:
            value = blob[key]
            if isinstance(value, list):
                return [HexNormalize.normalize(v) for v in value]
            else:
                return HexNormalize.normalize(value)
        else:
            return None
