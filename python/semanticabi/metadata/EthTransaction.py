from __future__ import annotations

from functools import cached_property
from typing import List, Dict, Optional

import importlib_resources

from semanticabi.abi.Abi import Abi
from semanticabi.abi.decoded.TokenTransferDecoded import TokenTransferDecoded
from semanticabi.metadata.EthLog import EthLog
from semanticabi.metadata.EthReceipt import EthReceipt
from semanticabi.common.ValueConverter import ValueConverter
from semanticabi.metadata.EthTraces import EthTransactionTraces, EthTrace
from semanticabi.metadata.EthTransferable import EthTransferable
from semanticabi.metadata.EthTransferType import EthTransferType
from semanticabi.metadata.EvmChain import EvmChain

TRANSFER_ABI = Abi.from_json(
    'Transfer',
    importlib_resources.files('resources').joinpath('Transfer.json').absolute()
)


class EthTransaction(EthTransferable):
    """
    Encapsulate all information about an EVM transaction including the transaction, receipts, and traces.

    @author zuyezheng
    """

    chain: EvmChain
    raw: Dict[str, any]
    receipt: EthReceipt
    traces: EthTransactionTraces

    def __init__(
        self,
        chain: EvmChain,
        raw: Dict[str, any],
        receipt: EthReceipt,
        traces: EthTransactionTraces
    ):
        self.chain = chain
        self.raw = raw
        self.receipt = receipt
        self.traces = traces

        EthTransaction.fix_status(self)

    @staticmethod
    def fix_status(transaction: EthTransaction):
        """
        Fix the status of a transaction by checking the receipt status and setting it if it's not present. This is due
        status being a later addition after the byzantium fork.
        """
        if 'status' not in transaction.receipt or transaction.receipt['status'] is None:
            if transaction.has_traces:
                # if there's traces, check the root for an error, if the root has no error and it's children do
                # indicative of a partial failure vs entire transaction failure
                transaction.receipt['status'] = (1 if transaction.traces.root_trace.error is None else 0)
            else:
                # otherwise assume success
                transaction.receipt['status'] = 1

    @property
    def hash(self) -> str:
        return self.raw['hash'].lower()

    @cached_property
    def status_enum(self) -> str:
        return 'error' if self.receipt['status'] == 0 else 'success'

    @cached_property
    def contract_address(self) -> str:
        return self.chain.native_token_address

    @cached_property
    def from_address(self) -> str:
        return self.raw['from'].lower()

    @cached_property
    def to_address(self) -> Optional[str]:
        if self.raw.get('to') is not None:
            # if there's a to address use it
            return self.raw['to'].lower()
        elif self.receipt.get('contractAddress') is not None:
            # otherwise it's a contract creation
            return self.receipt['contractAddress'].lower()
        else:
            raise Exception(f'transaction missing to and receipt contract address: {self.hash}')

    @property
    def is_contract_creation(self) -> bool:
        return self.receipt.get('contractAddress') is not None

    @property
    def value(self) -> Optional[int]:
        if 'value' in self.raw:
            return ValueConverter.hex_to_int(self.raw['value'])
        else:
            return None

    @property
    def transfer_type(self) -> EthTransferType:
        return EthTransferType.PRIMARY

    @property
    def logs(self) -> List[EthLog]:
        return self.receipt['logs']

    @cached_property
    def transfers(self) -> List[TokenTransferDecoded]:
        """ Return all token transfers by lazily decoding logs and caching results. """
        transfers = []

        for log_i, log in enumerate(self.logs):
            if TokenTransferDecoded.is_a(log):
                try:
                    if decoded_log := TRANSFER_ABI.decode_log(log):
                        for transfer_decoded in TokenTransferDecoded.of(log, log_i, decoded_log):
                            transfers.append(transfer_decoded)
                except Exception as e:
                    # decoding failed, likely a bad transfer
                    pass

        return transfers

    @cached_property
    def positive_transferables(self) -> List[EthTransferable]:
        """
        Return all positive (and a little more) transferables (root, internal, token transfers) in this transaction
        and cache the result.

        All token transfers from logs will be returned without any filtering, while only positive (non zero) root
        and internal transactions will be returned since not all transactions are transfers (such as contract calls).
        """
        transferables: List[EthTransferable] = self.transfers + self.traces.internal_transactions

        if self.value is not None and self.value > 0:
            transferables.append(self)

        return transferables + self.transfers

    @property
    def has_traces(self) -> bool:
        return self.traces is not None

    @cached_property
    def logs_by_topic(self) -> Dict[str, List[EthLog]]:
        """
        Return all logs by topic.
        """
        logs_by_topic: Dict[str, List[EthLog]] = {}
        for log in self.logs:
            if len(log['topics']) == 0:
                continue

            topic = log['topics'][0][2:]
            if topic not in logs_by_topic:
                logs_by_topic[topic] = []
            logs_by_topic[topic].append(log)

        return logs_by_topic

    @cached_property
    def traces_by_topic(self) -> Dict[str, List[EthTrace]]:
        """
        Return all traces by topic.
        """
        traces_by_topic: Dict[str, List[EthTrace]] = {}
        if self.traces is None:
            return traces_by_topic

        for trace in self.traces.traces:
            if trace.signature is not None:
                topic = trace.signature[2:]
                if topic == '':
                    continue
                if topic not in traces_by_topic:
                    traces_by_topic[topic] = []
                traces_by_topic[topic].append(trace)

        return traces_by_topic
