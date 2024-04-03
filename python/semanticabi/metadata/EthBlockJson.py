from __future__ import annotations
from typing import TypedDict, List, Dict, Optional

from semanticabi.metadata.EthReceipt import EthReceipt


class EthBlockJson(TypedDict):

    block: BlockInfoJson
    receipts: List[EthReceipt]
    traces: List[ErigonTraceJson, GethTraceRootJson]


BlockTransactionJson = TypedDict(
    'BlockTransactionJson',
    {
        'blockHash': str,
        'blockNumber': str,
        'from': str,
        'gas': str,
        'gasPrice': str,
        'maxPriorityFeePerGas': str,
        'maxFeePerGas': str,
        'hash': str,
        'input': str,
        'nonce': str,
        'to': str,
        'transactionIndex': str,
        'value': str,
        'type': str,
        'accessList': str,
        'chainId': str
    }
)


BlockInfoJson = TypedDict(
    'BlockInfoJson',
    {
        'baseFeePerGas': str,
        'difficulty': str,
        'extraData': str,
        'gasLimit': str,
        'gasUsed': str,
        'hash': str,
        'logsBloom': str,
        'miner': str,
        'mixHash': str,
        'nonce': str,
        'number': str,
        'parentHash': str,
        'receiptsRoot': str,
        'sha3Uncles': str,
        'size': str,
        'stateRoot': str,
        'timestamp': str,
        'totalDifficulty': str,
        'transactionsRoot': str,
        'withdrawalsRoot': str,

        'transactions': List[BlockTransactionJson],
        'uncles': List[any],
        'withdrawals': List[Dict[str, any]]
    }
)


ErigonTraceJson = TypedDict(
    'ErigonTraceJson',
    {
        'action': Dict[str, any],
        'blockHash': str,
        'blockNumber': int,
        'subtraces': int,
        'traceAddress': List[int],
        'transactionHash': str,
        'transactionPosition': int,
        'type': str,

        'result': Dict[str, any]
    }
)


GethTraceJson = TypedDict(
    'GethTraceJson',
    {
        'from': str,
        'gas': str,
        'gasUsed': str,
        'to': str,
        'input': str,
        'output': str,
        'value': str,
        'error': str,
        'type': str,

        'calls': Optional[List['GethTraceJson']]
    }
)


GethTraceRootJson = TypedDict(
    'GethTraceRootJson',
    {
        'result': GethTraceJson,
        'error': Optional[str]
    }
)