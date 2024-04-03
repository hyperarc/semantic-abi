from __future__ import annotations

from functools import cached_property
from typing import Dict, List, Optional, Set

from semanticabi.metadata.EthTraces import EthTrace, TraceType, CallType, EthTransactionTraces, EthTraces
from semanticabi.metadata.EvmChain import EvmChain


class ErigonTraces(EthTraces):
    """
    High level parsing to make erigon trace files easier to navigate.

    @author zuyezheng
    """

    chain: EvmChain
    block_number: int
    # traces grouped by transaction and indexed by transaction hash
    _transactions: Dict[str, EthTransactionTraces]
    # mining rewards
    rewards: List[ErigonTrace]

    @staticmethod
    def from_standalone(chain: EvmChain, block_json: Dict[str, any]) -> ErigonTraces:
        """
        From the payload of the standalone extractor of just erigon traces.
        """
        if 'result' not in block_json['traces']:
            raise Exception('Invalid trace file.')

        return ErigonTraces(chain, block_json['slot'], block_json['traces']['result'])

    def __init__(self, chain: EvmChain, block_number: int, traces: List[Dict[str, any]]):
        self.chain = chain
        self.block_number = block_number
        self._transactions = dict()
        self.rewards = []

        current_transaction: Optional[EthTransactionTraces] = None

        for trace_json in traces:
            trace = ErigonTrace(self.chain, trace_json)

            if trace.type == 'reward':
                self.rewards.append(trace)
            else:
                if current_transaction is None or trace.transaction_hash != current_transaction.hash:
                    # traces are ordered by transaction hash starting with a root, if hash changed, start a new
                    current_transaction = EthTransactionTraces(trace)
                    self._transactions[current_transaction.hash] = current_transaction
                else:
                    # otherwise add it as a sub trace of existing
                    current_transaction.add_trace(trace)

    @property
    def transactions(self) -> List[EthTransactionTraces]:
        return list(self._transactions.values())

    @property
    def transaction_hashes(self) -> Set[str]:
        return set(self._transactions.keys())

    def traces(self, transaction_hash: str) -> Optional[EthTransactionTraces]:
        """ Get the traces for the given transaction hash. """
        return self._transactions.get(transaction_hash)

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, item):
        return getattr(self, item)

    def __len__(self):
        return len(self._transactions)


class ErigonTrace(EthTrace):

    chain: EvmChain
    trace_json: Dict[str, any]

    def __init__(self, chain: EvmChain, trace_json: Dict[str, any]):
        self.chain = chain
        self.trace_json = trace_json

    @cached_property
    def contract_address(self) -> str:
        """
        This is the "token" contract address represented by the trace, not the address of the contract that emitted the
        trace which will be the to address. This is only valid for internal transfers which will always be in the native
        token of the chain.
        """
        return self.chain.native_token_address

    @property
    def trace_address(self) -> List[int]:
        return self.trace_json.get('traceAddress')

    @cached_property
    def trace_hash(self) -> str:
        """ Cached version of the trace hash. """
        return EthTrace.hash_trace_address(self.trace_address)

    @property
    def signature(self) -> Optional[str]:
        """ Function signature hash. """
        # first 10 characters of the input including the 0x
        return self.input[:10] if self.input else None

    @cached_property
    def parent_trace_address(self) -> List[int]:
        if self.is_root:
            raise Exception('No parent for root trace.')

        return self.trace_address[:-1]

    @property
    def error(self) -> Optional[str]:
        return self.trace_json.get('error')

    @property
    def block_hash(self) -> str:
        return self.trace_json['blockHash']

    @property
    def transaction_hash(self) -> str:
        return self.trace_json['transactionHash'].lower()

    @property
    def is_root(self) -> bool:
        return len(self.trace_json['traceAddress']) == 0

    @property
    def type(self) -> TraceType:
        return self.trace_json['type']

    @property
    def call_type(self) -> CallType:
        return self._action.get('callType')

    @property
    def input(self) -> Optional[str]:
        return self._action.get('input')

    @property
    def output(self) -> Optional[str]:
        return self._result('output')

    @cached_property
    def from_address(self) -> str:
        return self._action['from'].lower()

    @cached_property
    def to_address(self) -> Optional[str]:
        # use the presence of init to determine if it is a contract creation trace
        if 'init' in self._action:
            # to address is often used for the contract address being created in geth, in erigon we have to look
            # elsewhere
            contract_address = self._result('address')
            if contract_address is None:
                # contract creation failure or something else
                return '0x0000000000000000000000000000000000000000'
            else:
                contract_address.lower()
        else:
            return self._action['to'].lower()

    @property
    def value(self) -> Optional[int]:
        return self._action_hex_int('value')

    @property
    def gas(self) -> Optional[int]:
        return self._action_hex_int('gas')

    @property
    def gas_used(self) -> Optional[int]:
        v = self._result('gasUsed')
        if v is None:
            return None
        else:
            return int(v, 16)

    @property
    def _action(self) -> Dict[str, any]:
        return self.trace_json['action']

    def _action_hex_int(self, key: str) -> Optional[int]:
        v = self._action.get(key)
        if v is None:
            return None
        else:
            return int(v, 16)

    def _result(self, key: str) -> Optional[any]:
        """ Optionally get a value in a result since result does not exist if there is an error."""
        if self.trace_json.get('result') is not None:
            return self.trace_json['result'].get(key)

        return None

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, item):
        return getattr(self, item)
