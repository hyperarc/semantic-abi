from dataclasses import dataclass
from typing import Optional, Dict

from semanticabi.common.column.DatasetColumnTransform import DatasetColumnTransform


@dataclass
class ToString(DatasetColumnTransform):
    """
    Coerces a value to a string after applying a base transform
    """

    base_transform: Optional[DatasetColumnTransform]

    def transform(self, blob: Dict[str, any], key: str) -> any:
        if key in blob and blob[key] is not None:
            value = blob[key]
            if self.base_transform is not None:
                value = self.base_transform.transform(blob, key)

            if isinstance(value, str):
                return value

            return str(value)
        else:
            return None
