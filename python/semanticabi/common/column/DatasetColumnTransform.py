from abc import ABC, abstractmethod

from typing import Dict


class DatasetColumnTransform(ABC):
    """
    @author zuyezheng
    """

    @abstractmethod
    def transform(self, blob: Dict[str, any], key: str) -> any:
        """
        Main entry point for transformation given a blob.
        """
        pass
