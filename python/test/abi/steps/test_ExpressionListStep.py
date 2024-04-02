import gzip
import json
from typing import List, Dict

import pytest as pytest

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.ExpressionListStep import ExpressionListStep
from semanticabi.steps.FlattenParametersStep import FlattenParametersStep
from semanticabi.steps.InitStep import InitStep
from semanticabi.steps.Step import Step


def test_seaport_function():
    with open('test/resources/contracts/seaport/abis/expression/expressions.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    with gzip.open('test/resources/contracts/seaport/blocks/18937419.json.gz') as file:
        seaport_block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')

    # The 'fulfillOrder' function
    item: SemanticAbiItem = seaport_abi.functions_by_hash.get('b3a34c4c')

    step: Step = InitStep(seaport_abi, item)
    step = FlattenParametersStep(step)
    step = ExpressionListStep(step, item.properties.expressions)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 5
    offerer_column: DatasetColumn = columns[0]
    assert offerer_column.name == 'order_parameters_offerer'
    assert offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    # The order type column gets overwritten by one of the expressions
    order_type_column: DatasetColumn = columns[1]
    assert order_type_column.name == 'order_parameters_orderType'
    assert order_type_column.type_metadata == {'ingestType': 'long', 'expectedType': 'long'}
    offerer_expr_column: DatasetColumn = columns[2]
    assert offerer_expr_column.name == 'offerer_expr'
    assert offerer_expr_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_expr_column.extended_metadata == {'higherOrderType': 'none'}
    order_type_expr_column: DatasetColumn = columns[3]
    assert order_type_expr_column.name == 'orderType_expr'
    assert order_type_expr_column.type_metadata == {'ingestType': 'long', 'expectedType': 'long'}
    # We should be able to use a previously defined expression column
    order_type_expr_use_column: DatasetColumn = columns[4]
    assert order_type_expr_use_column.name == 'orderType_expr_use'
    assert order_type_expr_use_column.type_metadata == {'ingestType': 'long', 'expectedType': 'long'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_order_transaction)

    assert len(rows) == 1
    row: Dict[str, any] = rows[0]
    assert row['order_parameters_offerer'] == '0xed7df6066bda2256efbf1f48f536c1e5c7776172'
    # This gets overwritten by an expression
    assert row['order_parameters_orderType'] == 5
    assert row['offerer_expr'] == 'offerer_0xed7df6066bda2256efbf1f48f536c1e5c7776172'
    assert row['orderType_expr'] == 1
    assert row['orderType_expr_use'] == 2


def test_seaport_invalid_expression():
    with open('test/resources/contracts/seaport/abis/expression/expressions_invalid.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    # The 'fulfillOrder' function
    item: SemanticAbiItem = seaport_abi.functions_by_hash.get('b3a34c4c')

    step: Step = InitStep(seaport_abi, item)
    step = FlattenParametersStep(step)

    with pytest.raises(InvalidAbiException) as e:
        ExpressionListStep(step, item.properties.expressions)

    assert str(e.value) == 'Unknown columns referenced in expression \'\'offerer_\' || offerer\': offerer'
