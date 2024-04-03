import gzip
import json
from typing import List, Dict

import pytest

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.ExplodeIndexStep import ExplodeIndexStep
from semanticabi.steps.FlattenParametersStep import FlattenParametersStep
from semanticabi.steps.InitStep import InitStep
from semanticabi.steps.Step import Step


@pytest.fixture(scope='module')
def uniswap_abi() -> SemanticAbi:
    with open('test/resources/contracts/uniswap/FactoryV3.json') as file:
        return SemanticAbi(json.loads(file.read()))


@pytest.fixture(scope='module')
def uniswap_block() -> EthBlock:
    with open('test/resources/contracts/uniswap/blocks/FactoryV3_block.json') as file:
        return EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))


@pytest.fixture(scope='module')
def seaport_abi() -> SemanticAbi:
    with open('test/resources/contracts/seaport/abis/Seaport1.5.json') as file:
        return SemanticAbi(json.loads(file.read()))


@pytest.fixture(scope='module')
def seaport_block() -> EthBlock:
    with gzip.open('test/resources/contracts/seaport/blocks/18937419.json.gz') as file:
        return EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))


def test_uniswap_event(uniswap_abi: SemanticAbi, uniswap_block: EthBlock):
    v3_transaction: EthTransaction = uniswap_block.transactions[0]

    step: Step = InitStep(uniswap_abi, uniswap_abi.events_by_hash.get('783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118'))
    step = FlattenParametersStep(step)
    step = ExplodeIndexStep(step)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 5
    token_0_column: DatasetColumn = columns[0]
    assert token_0_column.name == 'token0'
    assert token_0_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert token_0_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fee_column: DatasetColumn = columns[1]
    assert fee_column.name == 'fee'
    assert fee_column.type_metadata == {'ingestType': 'long', 'expectedType': 'long'}
    tick_spacing_column: DatasetColumn = columns[2]
    assert tick_spacing_column.name == 'tickSpacing'
    assert tick_spacing_column.type_metadata == {'ingestType': 'integer', 'expectedType': 'integer'}
    pool_column: DatasetColumn = columns[3]
    assert pool_column.name == 'pool'
    assert pool_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert pool_column.extended_metadata == {'higherOrderType': 'addressHash'}
    explode_index_column: DatasetColumn = columns[4]
    assert explode_index_column.name == 'explodeIndex'
    assert explode_index_column.type_metadata == {'ingestType': 'integer', 'expectedType': 'integer'}

    rows: List[Dict[str, any]] = step.transform(uniswap_block, v3_transaction)

    assert len(rows) == 1
    row = rows[0]
    assert row['token0'] == '0x96ac8b252e1a9b75418964849f1985aef3798db0'
    assert row['fee'] == 3000
    assert row['tickSpacing'] == 60
    assert row['pool'] == '0xa6656d691a80b01126d23ef9268212b74abcfaf5'
    # Even non-exploded rows should have an explodeIndex of 0
    assert row['explodeIndex'] == 0


def test_seaport_function(seaport_abi: SemanticAbi, seaport_block: EthBlock):
    fulfill_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')

    step: FlattenParametersStep = FlattenParametersStep(
        InitStep(seaport_abi, seaport_abi.functions_by_hash.get('b3a34c4c'))
    )

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 7
    offerer_column: DatasetColumn = columns[0]
    assert offerer_column.name == 'order_parameters_offerer'
    assert offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    order_type_column: DatasetColumn = columns[1]
    assert order_type_column.name == 'order_parameters_orderType'
    assert order_type_column.type_metadata == {'ingestType': 'short', 'expectedType': 'short'}
    start_time_column: DatasetColumn = columns[2]
    assert start_time_column.name == 'order_parameters_startTime'
    assert start_time_column.type_metadata == {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0}
    zone_hash_column: DatasetColumn = columns[3]
    assert zone_hash_column.name == 'order_parameters_zoneHash'
    assert zone_hash_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert zone_hash_column.extended_metadata == {'higherOrderType': 'none'}
    signature_column: DatasetColumn = columns[4]
    assert signature_column.name == 'order_signature'
    assert signature_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert signature_column.extended_metadata == {'higherOrderType': 'none'}
    fulfiller_conduit_key_column: DatasetColumn = columns[5]
    assert fulfiller_conduit_key_column.name == 'fulfillerConduitKey'
    assert fulfiller_conduit_key_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfiller_conduit_key_column.extended_metadata == {'higherOrderType': 'none'}
    fulfilled_column: DatasetColumn = columns[6]
    assert fulfilled_column.name == 'fulfilled'
    assert fulfilled_column.type_metadata == {'ingestType': 'boolean', 'expectedType': 'boolean'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_order_transaction)

    assert len(rows) == 1
    row = rows[0]
    assert row['order_parameters_offerer'] == '0xed7df6066bda2256efbf1f48f536c1e5c7776172'
    assert row['order_parameters_orderType'] == 0
    # uint256 values are represented as a string
    assert row['order_parameters_startTime'] == '1704411678'
    # 'bytes' parameter values will not be prefixed with '0x'
    assert row['order_parameters_zoneHash'] == '0000000000000000000000000000000000000000000000000000000000000000'
    assert row['order_signature'].startswith('972ad99b') and row['order_signature'].endswith('f5e6ad9f')
    assert row['fulfillerConduitKey'] == '0000000000000000000000000000000000000000000000000000000000000000'
    assert row['fulfilled'] is True


def test_seaport_function_param_transforms(seaport_block: EthBlock):
    with open('test/resources/contracts/seaport/abis/flatten/param_transform.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')

    step: FlattenParametersStep = FlattenParametersStep(
        InitStep(seaport_abi, seaport_abi.functions_by_hash.get('b3a34c4c'))
    )

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 3
    offerer_column: DatasetColumn = columns[0]
    assert offerer_column.name == 'orderOfferer'
    assert offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    order_type_column: DatasetColumn = columns[1]
    assert order_type_column.name == 'order_parameters_orderType'
    assert order_type_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    fulfilled_column: DatasetColumn = columns[2]
    assert fulfilled_column.name == 'isFulfilled'
    assert fulfilled_column.type_metadata == {'ingestType': 'boolean', 'expectedType': 'boolean'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_order_transaction)

    assert len(rows) == 1
    row = rows[0]
    assert row['orderOfferer'] == '0xed7df6066bda2256efbf1f48f536c1e5c7776172'
    # The orderType value should be a string rather than an int due to the type transform
    assert row['order_parameters_orderType'] == '0'
    assert row['isFulfilled'] is True


def test_seaport_function_param_expression(seaport_block: EthBlock):
    with open('test/resources/contracts/seaport/abis/flatten/param_expression.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')

    step: FlattenParametersStep = FlattenParametersStep(
        InitStep(seaport_abi, seaport_abi.functions_by_hash.get('b3a34c4c'))
    )

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 2
    order_type_column: DatasetColumn = columns[0]
    assert order_type_column.name == 'order_parameters_orderType'
    assert order_type_column.type_metadata == {'ingestType': 'short', 'expectedType': 'short'}
    consideration_items_column: DatasetColumn = columns[1]
    assert consideration_items_column.name == 'invertedTotalConsiderationItems'
    assert consideration_items_column.type_metadata == {'ingestType': 'long', 'expectedType': 'long'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_order_transaction)

    assert len(rows) == 1
    row = rows[0]
    assert row['order_parameters_orderType'] == 5
    assert row['invertedTotalConsiderationItems'] == -3
