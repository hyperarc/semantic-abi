import json
from typing import Dict, List

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.DefaultColumnsStep import DefaultColumnsStep
from semanticabi.steps.InitStep import InitStep


def test_default_columns_event():
    with open('test/resources/contracts/uniswap/blocks/FactoryV3_block.json') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    with open('test/resources/contracts/uniswap/FactoryV3.json') as file:
        abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    v3_transaction: EthTransaction = block.transactions[0]

    default_columns_step: DefaultColumnsStep = DefaultColumnsStep(
        InitStep(abi, abi.events_by_hash.get('783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118'))
    )

    rows: List[Dict[str, any]] = default_columns_step.transform(block, v3_transaction)

    assert len(rows) == 1
    row = rows[0]
    # 12 default columns
    assert len(row) == 12
    assert row['chain'] == 'ethereum'
    assert row['blockHash'] == '0xd3e60acfc6fff75c5eb2ddae2618cbc07cc7c0be0a6d69ff5ce722828758e895'
    assert row['blockNumber'] == 18578531
    assert row['blockTimestamp'] == 1700066351
    assert row['transactionHash'] == '0x65773c0937a12b6cc0435fb025c0920aeb16a15b1c397b559dda6f26dbbe4f29'
    assert row['transactionFrom'] == '0x130b0a18b6bd98c00133600d8095aaaaeb1cfb5b'
    assert row['transactionTo'] == '0x1f98431c8ad98523631ae4a59f267346ea31f984'
    assert row['contractAddress'] == '0x1f98431c8ad98523631ae4a59f267346ea31f984'
    assert row['status'] == 1
    assert row['gasUsed'] == 4558970.0
    assert row['itemType'] == 'event'
    assert row['internalIndex'] == '161'


def test_default_columns_function():
    with open('test/resources/contracts/uniswap/blocks/FactoryV3_block.json') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    with open('test/resources/contracts/uniswap/FactoryV3.json') as file:
        abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    v3_transaction: EthTransaction = block.transactions[0]

    default_columns_step: DefaultColumnsStep = DefaultColumnsStep(
        InitStep(abi, abi.functions_by_hash.get('a1671295'))
    )

    rows: List[Dict[str, any]] = default_columns_step.transform(block, v3_transaction)

    assert len(rows) == 1
    row = rows[0]
    # 12 default columns
    assert len(row) == 12
    assert row['chain'] == 'ethereum'
    assert row['blockHash'] == '0xd3e60acfc6fff75c5eb2ddae2618cbc07cc7c0be0a6d69ff5ce722828758e895'
    assert row['blockNumber'] == 18578531
    assert row['blockTimestamp'] == 1700066351
    assert row['transactionHash'] == '0x65773c0937a12b6cc0435fb025c0920aeb16a15b1c397b559dda6f26dbbe4f29'
    assert row['transactionFrom'] == '0x130b0a18b6bd98c00133600d8095aaaaeb1cfb5b'
    assert row['transactionTo'] == '0x1f98431c8ad98523631ae4a59f267346ea31f984'
    assert row['contractAddress'] == '0x1f98431c8ad98523631ae4a59f267346ea31f984'
    assert row['status'] == 1
    assert row['gasUsed'] == 4558970.0
    assert row['itemType'] == 'function'
    # The top-level function call in a trace has no hash
    assert row['internalIndex'] == ''
