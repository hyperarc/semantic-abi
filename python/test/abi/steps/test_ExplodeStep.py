import gzip
import json
from typing import List, Dict

import pytest as pytest

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.ExplodeIndexStep import ExplodeIndexStep
from semanticabi.steps.ExplodeStep import ExplodeStep
from semanticabi.steps.InitStep import InitStep
from semanticabi.steps.Step import Step


@pytest.fixture(scope='module')
def seaport_block() -> EthBlock:
    with gzip.open('test/resources/contracts/seaport/blocks/19029959.json.gz') as file:
        return EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))


def test_explode_multiple(seaport_block: EthBlock):
    with open('test/resources/contracts/seaport/abis/explode/multiple.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0x35343c5b809fc2a1c9e1c15fe854c8f07ba815fa58764373c5f949ffc08d9d6f')

    step: Step = InitStep(semantic_abi, semantic_abi.functions_by_hash.get('ed98a574'))
    step = ExplodeStep(step)
    step = ExplodeIndexStep(step)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 5
    offerer_column: DatasetColumn = columns[0]
    assert offerer_column.name == 'orders_parameters_offerer'
    assert offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    zone_column: DatasetColumn = columns[1]
    assert zone_column.name == 'orders_parameters_zone'
    assert zone_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert zone_column.extended_metadata == {'higherOrderType': 'addressHash'}
    signature_column: DatasetColumn = columns[2]
    assert signature_column.name == 'orders_signature'
    assert signature_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert signature_column.extended_metadata == {'higherOrderType': 'none'}
    fulfilled_column: DatasetColumn = columns[3]
    assert fulfilled_column.name == 'fulfilled'
    assert fulfilled_column.type_metadata == {'ingestType': 'boolean', 'expectedType': 'boolean'}
    explode_index_column: DatasetColumn = columns[4]
    assert explode_index_column.name == 'explodeIndex'
    assert explode_index_column.type_metadata == {'ingestType': 'integer', 'expectedType': 'integer'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_order_transaction)

    assert len(rows) == 2
    row = rows[0]
    assert row['orders_parameters_offerer'] == '0x48d67bf72c47d748ca7c23fd54981a7875a0282e'
    assert row['orders_parameters_zone'] == '0x004c00500000ad104d7dbd00e3ae0a5c00560c00'
    assert row['orders_signature'].startswith('747dbe92')
    assert row['fulfilled'] is True
    assert row['explodeIndex'] == 0
    row = rows[1]
    assert row['orders_parameters_offerer'] == '0x2ff895e051f7a1c29c2d3bdab35c4960e3e1ec72'
    assert row['orders_parameters_zone'] == '0x004c00500000ad104d7dbd00e3ae0a5c00560c00'
    assert row['orders_signature'].startswith('ebeba350')
    assert row['fulfilled'] is True
    assert row['explodeIndex'] == 1
