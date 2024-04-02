import json
from typing import Optional, List, Dict

import pytest

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem
from semanticabi.steps.ExplodeStep import ExplodeFlattenPredicate
from semanticabi.steps.FlattenedParameter import FlattenedParameter
from semanticabi.steps.ParameterFlattener import ParameterFlattener


@pytest.fixture(scope='module')
def uniswap_abi() -> SemanticAbi:
    with open('test/resources/contracts/uniswap/FactoryV3.json') as file:
        return SemanticAbi(json.loads(file.read()))


@pytest.fixture(scope='module')
def seaport_abi() -> SemanticAbi:
    with open('test/resources/contracts/seaport/abis/Seaport1.5.json') as file:
        return SemanticAbi(json.loads(file.read()))


def assert_flattened_parameter(
    param: FlattenedParameter,
    expected_name: str,
    expected_path_names: List[str],
    expected_column_name: str,
    expected_dataset_column_type: Dict[str, any],
    expected_is_input: bool,
    expected_dataset_column_extended_metadata: Optional[Dict[str, any]] = None
):
    assert param.semantic_parameter.name == expected_name
    assert [p.name for p in param.path] == expected_path_names
    assert param.final_column_name == expected_column_name
    dataset_column = param.final_dataset_column
    assert dataset_column.type_metadata == expected_dataset_column_type
    assert param.is_input == expected_is_input
    if expected_dataset_column_extended_metadata is not None:
        assert dataset_column.extended_metadata == expected_dataset_column_extended_metadata


def test_flatten_event_params(uniswap_abi: SemanticAbi):
    abi_item: SemanticAbiItem = uniswap_abi.events_by_hash.get('783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118')
    flattener: ParameterFlattener = ParameterFlattener(abi_item)

    params = flattener.parameter_list()
    assert len(params) == 4

    token0_param: FlattenedParameter = params[0]
    assert_flattened_parameter(
        token0_param,
        'token0',
        [],
        'token0',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'addressHash'}
    )

    fee_param: FlattenedParameter = params[1]
    assert_flattened_parameter(
        fee_param,
        'fee',
        [],
        'fee',
        {'ingestType': 'long', 'expectedType': 'long'},
        True
    )

    tick_spacing_param: FlattenedParameter = params[2]
    assert_flattened_parameter(
        tick_spacing_param,
        'tickSpacing',
        [],
        'tickSpacing',
        {'ingestType': 'integer', 'expectedType': 'integer'},
        True
    )

    pool_param: FlattenedParameter = params[3]
    assert_flattened_parameter(
        pool_param,
        'pool',
        [],
        'pool',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'addressHash'}
    )


def test_flatten_function_params(uniswap_abi: SemanticAbi):
    abi_item: SemanticAbiItem = uniswap_abi.functions_by_hash.get('a1671295')
    flattener: ParameterFlattener = ParameterFlattener(abi_item)

    params = flattener.parameter_list()
    assert len(params) == 3

    token_b_param: FlattenedParameter = params[0]
    assert_flattened_parameter(
        token_b_param,
        'tokenB',
        [],
        'tokenB',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'addressHash'}
    )

    fee_param: FlattenedParameter = params[1]
    assert_flattened_parameter(
        fee_param,
        'fee',
        [],
        'fee',
        {'ingestType': 'long', 'expectedType': 'long'},
        True
    )

    pool_param: FlattenedParameter = params[2]
    assert_flattened_parameter(
        pool_param,
        'pool',
        [],
        'pool',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        False,
        {'higherOrderType': 'addressHash'}
    )


def test_flatten_tuple(seaport_abi: SemanticAbi):
    # Get the 'fulfillOrder' function
    abi_item: SemanticAbiItem = seaport_abi.functions_by_hash.get('b3a34c4c')
    flattener: ParameterFlattener = ParameterFlattener(abi_item)

    params = flattener.parameter_list()
    assert len(params) == 7

    offerer_param: FlattenedParameter = params[0]
    assert_flattened_parameter(
        offerer_param,
        'offerer',
        ['order', 'parameters'],
        'order_parameters_offerer',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'addressHash'}
    )

    order_type_param: FlattenedParameter = params[1]
    assert_flattened_parameter(
        order_type_param,
        'orderType',
        ['order', 'parameters'],
        'order_parameters_orderType',
        {'ingestType': 'short', 'expectedType': 'short'},
        True
    )

    start_time_param: FlattenedParameter = params[2]
    assert_flattened_parameter(
        start_time_param,
        'startTime',
        ['order', 'parameters'],
        'order_parameters_startTime',
        {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0},
        True
    )

    zone_hash_param: FlattenedParameter = params[3]
    assert_flattened_parameter(
        zone_hash_param,
        'zoneHash',
        ['order', 'parameters'],
        'order_parameters_zoneHash',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'none'}
    )

    signature_param: FlattenedParameter = params[4]
    assert_flattened_parameter(
        signature_param,
        'signature',
        ['order'],
        'order_signature',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'none'}
    )

    fulfiller_conduit_key_param: FlattenedParameter = params[5]
    assert_flattened_parameter(
        fulfiller_conduit_key_param,
        'fulfillerConduitKey',
        [],
        'fulfillerConduitKey',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'none'}
    )

    fulfilled_param: FlattenedParameter = params[6]
    assert_flattened_parameter(
        fulfilled_param,
        'fulfilled',
        [],
        'fulfilled',
        {'ingestType': 'boolean', 'expectedType': 'boolean'},
        False
    )


def test_function_with_transforms():
    with open('test/resources/contracts/seaport/abis/flatten/param_transform.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    # The 'fulfillOrder' function
    abi_item: SemanticAbiItem = seaport_abi.functions_by_hash.get('b3a34c4c')
    flattener: ParameterFlattener = ParameterFlattener(abi_item)

    params = flattener.parameter_list()
    assert len(params) == 3

    offerer_param: FlattenedParameter = params[0]
    assert_flattened_parameter(
        offerer_param,
        'offerer',
        ['order', 'parameters'],
        'orderOfferer',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'addressHash'}
    )

    order_type_param: FlattenedParameter = params[1]
    assert_flattened_parameter(
        order_type_param,
        'orderType',
        ['order', 'parameters'],
        'order_parameters_orderType',
        # This is just a string rather than a short type since it has a 'string' type transform
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True
    )

    fulfilled_param: FlattenedParameter = params[2]
    assert_flattened_parameter(
        fulfilled_param,
        'fulfilled',
        [],
        'isFulfilled',
        {'ingestType': 'boolean', 'expectedType': 'boolean'},
        False
    )


def test_flattened_array_primitive():
    with open('test/resources/contracts/seaport/abis/explode/primitive.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    # The 'fulfillAvailableOrders' function
    abi_item: SemanticAbiItem = seaport_abi.functions_by_hash.get('ed98a574')
    flattener: ParameterFlattener = ParameterFlattener(abi_item, ExplodeFlattenPredicate(abi_item.properties.explode.path_parts))

    params = flattener.parameter_list()
    assert len(params) == 1

    fulfilled_param: FlattenedParameter = params[0]
    assert_flattened_parameter(
        fulfilled_param,
        'fulfilled',
        [],
        'fulfilled',
        {'ingestType': 'boolean', 'expectedType': 'boolean'},
        False
    )


def test_flattened_array_tuple():
    with open('test/resources/contracts/seaport/abis/explode/tuple.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    # The 'fulfillAvailableOrders' function
    abi_item: SemanticAbiItem = seaport_abi.functions_by_hash.get('ed98a574')
    flattener: ParameterFlattener = ParameterFlattener(abi_item, ExplodeFlattenPredicate(abi_item.properties.explode.path_parts))

    params = flattener.parameter_list()
    assert len(params) == 4

    offerer_param: FlattenedParameter = params[0]
    assert_flattened_parameter(
        offerer_param,
        'offerer',
        ['orders', 'parameters'],
        'orders_parameters_offerer',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'addressHash'}
    )

    order_type_param: FlattenedParameter = params[1]
    assert_flattened_parameter(
        order_type_param,
        'orderType',
        ['orders', 'parameters'],
        'orders_parameters_orderType',
        {'ingestType': 'short', 'expectedType': 'short'},
        True
    )

    start_time_param: FlattenedParameter = params[2]
    assert_flattened_parameter(
        start_time_param,
        'startTime',
        ['orders', 'parameters'],
        'orders_parameters_startTime',
        {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0},
        True
    )

    signature_param: FlattenedParameter = params[3]
    assert_flattened_parameter(
        signature_param,
        'signature',
        ['orders'],
        'orders_signature',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'none'}
    )


def test_flattened_array_nested_tuple():
    with open('test/resources/contracts/seaport/abis/explode/nested_tuple.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    # The 'fulfillBasicOrder_efficient_6GL6yc' function
    abi_item: SemanticAbiItem = seaport_abi.functions_by_hash.get('00000000')
    flattener: ParameterFlattener = ParameterFlattener(abi_item, ExplodeFlattenPredicate(abi_item.properties.explode.path_parts))

    params = flattener.parameter_list()
    assert len(params) == 2

    amount_param: FlattenedParameter = params[0]
    assert_flattened_parameter(
        amount_param,
        'amount',
        ['parameters', 'additionalRecipients'],
        'parameters_additionalRecipients_amount',
        {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0},
        True
    )

    recipient_param: FlattenedParameter = params[1]
    assert_flattened_parameter(
        recipient_param,
        'recipient',
        ['parameters', 'additionalRecipients'],
        'parameters_additionalRecipients_recipient',
        {'ingestType': 'string', 'expectedType': 'string', 'isArray': False},
        True,
        {'higherOrderType': 'addressHash'}
    )
