from abc import ABC, abstractmethod


class ObjectMetadata(ABC):
    """
    Holds metadata about an object that can be transformed.

    @author zuyezheng
    """

    @abstractmethod
    def __init__(self, raw: any):
        pass
