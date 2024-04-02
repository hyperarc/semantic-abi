from typing import TypedDict, List, Optional

from semanticabi.metadata.EthLog import EthLog


"""
Definition of a persisted receipt as JSON, can't define it as a class due to reserved keywords as keys.

@author zuyezheng
"""
EthReceipt = TypedDict(
    'EthReceipt',
    {
        'blockHash': str,
        'blockNumber': int,
        'contractAddress': Optional[str],
        'cumulativeGasUsed': int,
        'effectiveGasPrice': int,
        'from': str,
        'gasUsed': int,
        'logs': List[EthLog],
        'logsBloom': str,
        'status': int,
        'to': str,
        'transactionHash': str,
        'transactionIndex': int,
        'type': int,
        'error': Optional[str]
    }
)
