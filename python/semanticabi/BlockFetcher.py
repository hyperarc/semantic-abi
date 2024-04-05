from __future__ import annotations

import json
from contextlib import AsyncExitStack
from enum import Enum
from typing import Dict, List

import aiohttp
from aiohttp import ClientSession

from semanticabi.metadata.EthBlockJson import EthBlockJson, BlockInfoJson
from semanticabi.metadata.EthReceipt import EthReceipt


class BlockFetcher:
    """
    Fetches a block with receipts and traces from an EVM-based blockchain node in the format used by the
    SemanticTransformer
    """
    _node_url: str
    _node_type: NodeType

    _exit_stack: AsyncExitStack
    _session: ClientSession

    def __init__(self, node_url: str, node_type: NodeType):
        self._node_url = node_url
        self._node_type = node_type
        self._exit_stack = AsyncExitStack()

    async def __aenter__(self) -> BlockFetcher:
        self._session = await self._exit_stack.enter_async_context(ClientSession(
            # eth RPC calls are usually fast, small queries and will run up against rate limiters so default to 1
            connector=aiohttp.TCPConnector(limit=1)
        ))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.__aexit__(exc_type, exc_val, exc_tb)

    async def fetch_block(self, block_number: int) -> EthBlockJson:
        """
        Fetch a block with receipts and traces from the node
        """
        async with self._session.post(self._node_url, data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'eth_getBlockByNumber',
            'params': [hex(block_number), True],
            'id': 1
        })) as response:
            if not response.ok:
                raise Exception(f'Failed to fetch block {block_number}: {response.status} {response.reason}')

            response_json = await response.json()
            block_info_json: BlockInfoJson = response_json['result']

            receipts = await self._get_block_receipts(block_number) if self._node_type == NodeType.ERIGON else \
                await self._get_transaction_receipts(block_info_json)

            traces = await self.trace_block_erigon(block_number) if self._node_type == NodeType.ERIGON else \
                await self._trace_block_geth(block_number)

            return EthBlockJson(
                block=block_info_json,
                receipts=receipts,
                traces=traces
            )

    async def _get_transaction_receipts(
        self,
        block: BlockInfoJson
    ) -> List[EthReceipt]:
        """ Get the individual receipt for every transaction in the block """
        receipts: List[EthReceipt] = []
        for transaction in block['transactions']:
            receipt = await self._get_transaction_receipt(transaction['hash'])
            receipts.append(receipt)

        return receipts

    async def _get_transaction_receipt(
        self,
        transaction_hash: str
    ) -> EthReceipt:
        """
        Get a receipt for a single transaction
        """
        async with self._session.post(
            self._node_url,
            headers={'content-type': 'application/json'},
            data=json.dumps({
                'jsonrpc': '2.0',
                'method': 'eth_getTransactionReceipt',
                'params': [transaction_hash],
                'id': 1
            })
        ) as response:
            if not response.ok:
                raise Exception(f'Failed to transaction receipt for transaction {transaction_hash}: {response.status} {response.reason}')

            receipt = await response.json()

            return receipt['result']

    async def _get_block_receipts(self, block_number: int) -> List[EthReceipt]:
        """
        Get all receipts for a block in a single call, this is only supported on erigon clients.
        """
        async with self._session.post(
            self._node_url,
            headers={'content-type': 'application/json'},
            data=json.dumps({
                'jsonrpc': '2.0',
                'method': 'eth_getBlockReceipts',
                'params': [hex(block_number)],
                'id': 1
            })
        ) as response:
            if not response.ok:
                raise Exception(f'Failed to fetch block receipts for {block_number}: {response.status} {response.reason}')

            receipts = await response.json()

            return receipts['result']

    async def _trace_block_geth(self, block_number: int) -> List[Dict[str, any]]:
        """
        Gets the transaction trace with the "callTracer" for a block.
        """
        async with self._session.post(
            self._node_url,
            headers={'content-type': 'application/json'},
            data=json.dumps({
                'jsonrpc': '2.0',
                'method': 'debug_traceBlockByNumber',
                'params': [hex(block_number), {'tracer': 'callTracer', 'timeout': '500s'}],
                'id': 1
            })
        ) as response:
            if not response.ok:
                raise Exception(f'Failed to fetch block traces for {block_number}: {response.status} {response.reason}')

            traces = await response.json()

            return traces['result']

    async def trace_block_erigon(self, block_number: int) -> List[Dict[str, any]]:
        """
        Call the erigon `trace_block` function.
        """
        async with self._session.post(
            self._node_url,
            headers={'content-type': 'application/json'},
            data=json.dumps({
                'jsonrpc': '2.0',
                'method': 'trace_block',
                'params': [hex(block_number)],
                'id': 1
            })
        ) as response:
            if not response.ok:
                raise Exception(f'Failed to fetch block traces for {block_number}: {response.status} {response.reason}')

            traces = await response.json()

            return traces['result']


class NodeType(Enum):
    """
    Enum to represent the different types of EVM-based blockchain nodes
    """
    ERIGON = 'erigon'
    GETH = 'geth'
