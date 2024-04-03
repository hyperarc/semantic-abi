from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from semanticabi.metadata.EthTransferType import EthTransferType


class EthTransferable(ABC):
    """
    Interface for things that can be transferred including root transaction, internal transaction, and token transfers.

    @author zuyezheng
    """

    @property
    @abstractmethod
    def contract_address(self) -> str:
        """ Contract address for the transfer. """
        pass

    @property
    @abstractmethod
    def from_address(self) -> str:
        pass

    @property
    @abstractmethod
    def to_address(self) -> str:
        pass

    @property
    @abstractmethod
    def value(self) -> Optional[int]:
        pass

    @property
    @abstractmethod
    def transfer_type(self) -> EthTransferType:
        pass
