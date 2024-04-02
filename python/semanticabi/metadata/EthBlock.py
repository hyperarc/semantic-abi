from functools import cached_property
from typing import Dict, Tuple, Iterator, List, Optional

from semanticabi.common.ValueConverter import ValueConverter
from semanticabi.metadata.ErigonTraces import ErigonTraces
from semanticabi.metadata.EthBlockJson import EthBlockJson
from semanticabi.metadata.EthReceipt import EthReceipt
from semanticabi.metadata.EthTraces import EthTraces
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.GethTraces import GethTraces
from semanticabi.common.ObjectMetadata import ObjectMetadata
from semanticabi.metadata.EvmChain import EvmChain

BURN_ADDRESS = '0x0000000000000000000000000000000000000000'


class EthBlock(ObjectMetadata):
    """
    @author zuyezheng
    """

    chain: EvmChain
    block_json: EthBlockJson
    _transactions: Optional[List[EthTransaction]]

    def __init__(self, chain: EvmChain, block_json: Dict[str, any]):
        self.chain = chain
        self.block_json = block_json
        self._transactions = None

    @property
    def number(self) -> int:
        return ValueConverter.hex_to_int(self.block['number'])

    @property
    def timestamp(self) -> int:
        return ValueConverter.hex_to_int(self.block['timestamp'])

    @property
    def block(self) -> Dict[str, any]:
        return self.block_json['block']

    @property
    def has_traces(self) -> bool:
        return 'traces' in self.block_json

    @property
    def transactions_and_receipts(self) -> Iterator[Tuple[Dict[str, any], EthReceipt]]:
        """
        Legacy iterator of tuples of transactions with receipts.
        """
        if 'transactions_and_receipts' in self.block_json:
            # legacy extracted transactions and receipts as separate requests from the block and pushed them into a
            # single object
            return map(
                lambda d: (d['transaction'], d['receipt']),
                self.block_json['transactions_and_receipts']
            )
        else:
            # new extract pulled all transaction data in the block request
            if len(self.block_json['block']['transactions']) != len(self.block_json['receipts']):
                raise Exception(
                    f'differing number of transactions and receipts for block: {self.number}'
                )

            return zip(
                self.block_json['block']['transactions'],
                self.block_json['receipts']
            )

    @cached_property
    def transactions(self) -> List[EthTransaction]:
        """
        Instead of an iterator of tuples return a list of objects with traces if there are any.
        """
        traces: Optional[EthTraces] = None
        traces_hashes = set()
        if 'traces' in self.block_json:
            if len(self.block_json['traces']) == 0:
                # if traces is an empty array, can deserialize as either
                traces = ErigonTraces(self.chain, self.number, self.block_json['traces'])
            elif 'traceAddress' in self.block_json['traces'][0]:
                # only erigon will have fields like 'traceAddress' at the root
                traces = ErigonTraces(self.chain, self.number, self.block_json['traces'])
            else:
                traces = GethTraces(self.chain, self.number, self.block_json)

            # store the traces hashes for validation
            traces_hashes = traces.transaction_hashes

        transaction_hashes = set()
        transactions = []
        for transaction_and_receipt in self.transactions_and_receipts:
            transaction_hash = transaction_and_receipt[0]['hash'].lower()

            if transaction_hash != transaction_and_receipt[1]['transactionHash']:
                raise Exception(
                    f'Transaction and receipt hash mismatch: {self.number} ({transaction_hash}).'
                )

            transaction_hashes.add(transaction_hash)
            eth_transaction = EthTransaction(
                self.chain,
                transaction_and_receipt[0],
                transaction_and_receipt[1],
                None if traces is None else traces.traces(transaction_hash)
            )
            transactions.append(eth_transaction)

            # for polygon, chain state syncs don't have a traces which is expected to add it to the set for validation
            if (
                self.chain == EvmChain.POLYGON and
                eth_transaction.from_address == BURN_ADDRESS and
                eth_transaction.to_address == BURN_ADDRESS
            ):
                traces_hashes.add(transaction_hash)

        # if there are traces, verify the traces
        if traces:
            if transaction_hashes != traces_hashes:
                raise Exception(
                    f'differing transactions in the receipts and traces for block: {self.number}'
                )

        return transactions
