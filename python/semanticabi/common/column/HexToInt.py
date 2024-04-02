from dataclasses import dataclass
from typing import Dict

from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform
from semanticabi.common.ValueConverter import ValueConverter


@dataclass
class HexToInt(DatasetColumnTransform):
    """
    Transform a possible hex value to an int. If the value is a string, it will be treated as a hex to be converted,
    otherwise as an int that does not need conversion.

    @author zuyezheng
    """

    # provide to rename
    source_col: str = None
    default_value: int = None
    max_value: int = None

    def transform(self, blob: Dict[str, any], key: str) -> any:
        key = key if self.source_col is None else self.source_col

        if key in blob and blob[key] is not None:
            converted = ValueConverter.hex_to_int(blob[key])
            if self.max_value and converted > self.max_value:
                return self.default_value
            else:
                return converted
        else:
            return self.default_value
