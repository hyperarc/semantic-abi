from __future__ import annotations

from functools import cached_property
from typing import Dict, List, Optional, Set

from semanticabi.common.ValueConverter import ValueConverter
from semanticabi.metadata.EthBlockJson import EthBlockJson, GethTraceJson, GethTraceRootJson
from semanticabi.metadata.EthTraces import EthTrace, CallType, EthTransactionTraces, EthTraces, TraceType
from semanticabi.metadata.EvmChain import EvmChain


class GethTraces(EthTraces):
    """
    High level parsing to make erigon trace files easier to navigate.

    @author zuyezheng
    """

    chain: EvmChain
    block_number: int
    # traces grouped by transaction and indexed by transaction hash
    _transactions: Dict[str, EthTransactionTraces]

    @staticmethod
    def from_standalone(chain: EvmChain, block_json: EthBlockJson) -> GethTraces:
        """
        From a full block json with the "block info" since geth traces often don't include important things like the
        transaction hash which needs to be matched by index with the transactions from the block
        """
        return GethTraces(chain, ValueConverter.hex_to_int(block_json['block']['number']), block_json)

    def __init__(self, chain: EvmChain, block_number: int, block_json: EthBlockJson):
        self.chain = chain
        self.block_number = block_number
        self._transactions = dict()

        if len(block_json['block']['transactions']) != len(block_json['traces']):
            raise Exception(f'Have {len(block_json["block"]["transactions"])} transactions for {len(block_json["traces"])} traces.')

        block_hash = block_json['block']['hash'].lower()
        for trace_i, trace_json in enumerate(block_json['traces']):
            transaction = GethTraces._parse_transaction_tree(
                self.chain, block_hash, block_json['block']['transactions'][trace_i]['hash'].lower(), trace_json
            )
            self._transactions[transaction.hash] = transaction

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

    @staticmethod
    def _parse_transaction_tree(
        chain: EvmChain, block_hash: str, transaction_hash: str, root_json: GethTraceRootJson
    ) -> EthTransactionTraces:
        if 'result' not in root_json:
            raise Exception(f'Missing trace results in transaction {transaction_hash}.')

        # flatten out the trace tree to normalize with erigon representation
        trace_json = root_json['result']
        transaction = EthTransactionTraces(
            GethTrace(chain, block_hash, transaction_hash, [], trace_json)
        )

        def dfs(node: GethTraceJson, address: List[int]):
            # not the root, add the current node
            if len(address) > 0:
                transaction.add_trace(GethTrace(chain, block_hash, transaction_hash, address, node))

            if 'calls' in node:
                for child_i, child in enumerate(node['calls']):
                    dfs(child, [*address, child_i])

        dfs(trace_json, [])
        return transaction


class GethTrace(EthTrace):

    trace_json: GethTraceJson

    chain: EvmChain
    _block_hash: str
    _transaction_hash: str
    _trace_address: List[int]

    def __init__(
        self,
        chain: EvmChain,
        block_hash: str,
        transaction_hash: str,
        trace_address: List[int],
        trace_json: GethTraceJson
    ):
        """ Create a new Trace object from a copy of the trace json. """
        self.trace_json = {k: trace_json[k] for k in trace_json.keys() - {'calls'}}

        self.chain = chain
        self._block_hash = block_hash
        self._transaction_hash = transaction_hash
        self._trace_address = trace_address

    @cached_property
    def contract_address(self) -> str:
        """
        This is the "token" contract address represented by the trace, not the address of the contract that emitted the
        trace which will be the to address. This is only valid for internal transfers which will always be in the native
        token of the chain.
        """
        return self.chain.native_token_address

    @cached_property
    def from_address(self) -> str:
        return self.trace_json['from'].lower()

    @cached_property
    def to_address(self) -> Optional[str]:
        # geth will always have a to address that is either the actual to address or the address of the contract
        # being created
        return self.trace_json['to'].lower()

    @property
    def value(self) -> Optional[int]:
        return self._result_hex_int('value')

    @property
    def is_root(self) -> bool:
        return len(self.trace_address) == 0

    @property
    def block_hash(self) -> str:
        return self._block_hash

    @property
    def transaction_hash(self) -> str:
        return self._transaction_hash

    @property
    def trace_address(self) -> List[int]:
        return self._trace_address

    @cached_property
    def trace_hash(self) -> str:
        """ Cached version of the trace hash. """
        return EthTrace.hash_trace_address(self.trace_address)

    @property
    def signature(self) -> Optional[str]:
        """ Function signature hash. """
        # first 10 characters of the input including the 0x
        return self.input[:10] if self.input else None

    @property
    def error(self) -> Optional[str]:
        return self.trace_json.get('error')

    @property
    def input(self) -> Optional[str]:
        return self.trace_json['input']

    @property
    def output(self) -> Optional[str]:
        return self.trace_json.get('output')

    @property
    def type(self) -> TraceType:
        return 'call'

    @property
    def call_type(self) -> CallType:
        return self.trace_json['type'].lower()

    @property
    def gas(self) -> Optional[int]:
        return self._result_hex_int('gas')

    @property
    def gas_used(self) -> Optional[int]:
        return self._result_hex_int('gasUsed')

    def _result_hex_int(self, key: str) -> Optional[int]:
        v = self.trace_json.get(key)
        if v is None:
            return None
        else:
            return int(v, 16)

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, item):
        return getattr(self, item)
