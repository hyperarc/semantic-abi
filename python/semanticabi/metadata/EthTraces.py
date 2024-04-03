from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from functools import cached_property
from typing import Optional, List, Literal, Set

from semanticabi.metadata.EthTransferable import EthTransferable
from semanticabi.metadata.EthTransferType import EthTransferType
from semanticabi.common.ObjectMetadata import ObjectMetadata

TraceType = Literal[
    'call',
    'reward'
]

CallType = Literal[
    'call',
    'delegatecall',
    'staticcall',
    'callcode',
    # erigon will always be create, while geth might be create or create2
    'create',
    # https://ethereum.stackexchange.com/questions/101336/what-is-the-benefit-of-using-create2-to-create-a-smart-contract
    'create2'
]


class EthTraces(ObjectMetadata, ABC):
    """
    All traces in a block.

    @author zuyezheng
    """

    @property
    @abstractmethod
    def transactions(self) -> List[EthTransactionTraces]:
        pass

    @property
    @abstractmethod
    def transaction_hashes(self) -> Set[str]:
        pass

    @abstractmethod
    def traces(self, transaction_hash: str) -> Optional[EthTransactionTraces]:
        """ Get the traces for the given transaction hash. """
        pass


class EthTransactionTraces:
    """
    Container for all traces in a transaction.
    """

    # main trace representing the top level transaction
    root_trace: EthTrace
    # traces by the trace address "hash"
    sub_traces: OrderedDict[str, EthTrace]

    def __init__(self, root_trace: EthTrace):
        self.root_trace = root_trace
        self.sub_traces = OrderedDict()

    @property
    def hash(self) -> str:
        return self.root_trace.transaction_hash

    @property
    def from_address(self) -> str:
        return self.root_trace.from_address

    @property
    def to_address(self) -> str:
        return self.root_trace.to_address

    @property
    def traces(self) -> List[EthTrace]:
        ### Return all traces as a list. ###
        return [
            self.root_trace,
            *self.sub_traces.values()
        ]

    @property
    def value(self) -> int:
        """ Value of the main/root transaction which does not include internal transactions. """
        return self.root_trace.value

    @cached_property
    def internal_transactions(self) -> List[EthTrace]:
        """
        Return all "internal" transactions that moved eth due to internal contract calls that only show up in traces.
        """
        return list(
            filter(
                # only care if value is > 0 and it's if type call (vs delegatecall)
                lambda t: t.call_type == 'call' and t.value is not None and t.value > 0,
                self.sub_traces.values()
            )
        )

    @cached_property
    def errors(self) -> Optional[List[str]]:
        """ Return a list of errors if any. """
        errors = []
        if self.root_trace.error:
            errors.append(self.root_trace.error)
        for trace in self.sub_traces.values():
            if trace.error:
                errors.append(trace.error)

        return None if len(errors) == 0 else errors

    def add_trace(self, trace: EthTrace):
        self.sub_traces[trace.trace_hash] = trace

    def trace_by_address(self, address: List[int]) -> EthTrace:
        """ Return a trace by its address. """
        if len(address) == 0:
            return self.root_trace

        return self.sub_traces[EthTrace.hash_trace_address(address)]

    def call_stack(self, address: List[int]) -> List[EthTrace]:
        """ Return all traces in the call stack of trace for the given address. """
        cur_trace = self.trace_by_address(address)
        stack = [cur_trace]

        while not cur_trace.is_root:
            cur_trace = self.trace_by_address(cur_trace.parent_trace_address)
            stack.append(cur_trace)

        stack.reverse()
        return stack

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, item):
        return getattr(self, item)


class EthTrace(EthTransferable, ABC):
    """
    Individual traces.
    """

    @staticmethod
    def hash_trace_address(trace_address: List[int]) -> str:
        """ "Hashes" the trace address [0, 3, 1] into '0_3_1'. """
        return '_'.join(map(lambda v: str(v), trace_address))

    @property
    def transfer_type(self) -> EthTransferType:
        return EthTransferType.INTERNAL

    @cached_property
    def parent_trace_address(self) -> List[int]:
        if self.is_root:
            raise Exception('No parent for root trace.')

        return self.trace_address[:-1]

    @property
    @abstractmethod
    def is_root(self) -> bool:
        pass

    @property
    @abstractmethod
    def block_hash(self) -> str:
        pass

    @property
    @abstractmethod
    def transaction_hash(self) -> str:
        pass

    @property
    @abstractmethod
    def trace_address(self) -> List[int]:
        pass

    @property
    @abstractmethod
    def trace_hash(self) -> str:
        pass

    @property
    @abstractmethod
    def signature(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def error(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def type(self) -> TraceType:
        """
        Specific to erigon, where geth only has "calls".
        """
        pass

    @property
    @abstractmethod
    def call_type(self) -> CallType:
        """
        The "type" in geth and "call type" in erigon.
        """
        pass

    @property
    @abstractmethod
    def input(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def output(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def gas(self) -> Optional[int]:
        pass

    @property
    @abstractmethod
    def gas_used(self) -> Optional[int]:
        pass
