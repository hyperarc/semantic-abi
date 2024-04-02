import gzip
import json
from typing import Dict, Tuple, List

import pytest as pytest

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.item.Matches import Match
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.ExplodeIndexStep import ExplodeIndexStep
from semanticabi.steps.ExplodeStep import ExplodeStep
from semanticabi.steps.FlattenParametersStep import FlattenParametersStep
from semanticabi.steps.InitStep import InitStep
from semanticabi.steps.MatchStep import MatchStep, AbiMatchSteps
from semanticabi.steps.Step import Step


@pytest.fixture(scope='module')
def seaport_block() -> EthBlock:
    with gzip.open('test/resources/contracts/seaport/blocks/19044839.json.gz') as file:
        return EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))


def _build_matches_and_steps(semantic_abi: SemanticAbi, item: SemanticAbiItem) -> List[Tuple[Match, Step]]:
    return AbiMatchSteps.from_abi(semantic_abi, [item]).steps_for_match_list(item.properties.matches.matches)


def test_match_event_onlyone(seaport_block: EthBlock):
    with open('test/resources/contracts/seaport/abis/match/event_onlyone.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_basic_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0x1d43365c4b76e9ef6689c0204479fdc98c9ca0107093a7b7e89269776c71e3f0')

    # The 'fulfillBasicOrder_efficient_6GL6yc' function
    item: SemanticAbiItem = semantic_abi.functions_by_hash.get('00000000')

    matches_and_steps: List[Tuple[Match, Step]] = _build_matches_and_steps(semantic_abi, item)

    step: Step = InitStep(semantic_abi, item)
    step = FlattenParametersStep(step)
    step = MatchStep(step, matches_and_steps)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 4
    offerer_column: DatasetColumn = columns[0]
    assert offerer_column.name == 'parameters_offerer'
    assert offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_order_hash_column: DatasetColumn = columns[1]
    assert fulfill_order_hash_column.name == 'fulfill_orderHash'
    assert fulfill_order_hash_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    fulfill_offerer_column: DatasetColumn = columns[2]
    assert fulfill_offerer_column.name == 'fulfill_offerer'
    assert fulfill_offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_recipient_column: DatasetColumn = columns[3]
    assert fulfill_recipient_column.name == 'fulfill_recipient'
    assert fulfill_recipient_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_recipient_column.extended_metadata == {'higherOrderType': 'addressHash'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_basic_order_transaction)

    assert len(rows) == 1
    row = rows[0]
    assert row['parameters_offerer'] == '0xf3a635117e050b6abe6b7502e12323addad5503e'
    assert row['fulfill_orderHash'] == '603816a107c27139ec3f867c70aaa1008f42db389c7be0b4807464505ad5c699'
    assert row['fulfill_offerer'] == '0xf3a635117e050b6abe6b7502e12323addad5503e'
    assert row['fulfill_recipient'] == '0x7a558b543f18ce7257bd469e24bbb31e5ec4f1e8'


def test_match_function_onlyone(seaport_block: EthBlock):
    with open('test/resources/contracts/seaport/abis/match/function_onlyone.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_basic_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0x1d43365c4b76e9ef6689c0204479fdc98c9ca0107093a7b7e89269776c71e3f0')

    # The 'OrderFulfilled' event
    item: SemanticAbiItem = semantic_abi.events_by_hash.get('9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31')

    matches_and_steps: List[Tuple[Match, Step]] = _build_matches_and_steps(semantic_abi, item)

    step: Step = InitStep(semantic_abi, item)
    step = FlattenParametersStep(step)
    step = MatchStep(step, matches_and_steps)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 4
    fulfill_order_hash_column: DatasetColumn = columns[0]
    assert fulfill_order_hash_column.name == 'orderHash'
    assert fulfill_order_hash_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    fulfill_offerer_column: DatasetColumn = columns[1]
    assert fulfill_offerer_column.name == 'offerer'
    assert fulfill_offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_recipient_column: DatasetColumn = columns[2]
    assert fulfill_recipient_column.name == 'recipient'
    assert fulfill_recipient_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_recipient_column.extended_metadata == {'higherOrderType': 'addressHash'}
    offerer_column: DatasetColumn = columns[3]
    assert offerer_column.name == 'basicOrder_parameters_offerer'
    assert offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_basic_order_transaction)

    assert len(rows) == 1
    row = rows[0]
    assert row['orderHash'] == '603816a107c27139ec3f867c70aaa1008f42db389c7be0b4807464505ad5c699'
    assert row['offerer'] == '0xf3a635117e050b6abe6b7502e12323addad5503e'
    assert row['recipient'] == '0x7a558b543f18ce7257bd469e24bbb31e5ec4f1e8'
    assert row['basicOrder_parameters_offerer'] == '0xf3a635117e050b6abe6b7502e12323addad5503e'


def test_match_event_optionalone(seaport_block: EthBlock):
    with open('test/resources/contracts/seaport/abis/match/event_optionalone.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_basic_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0x1d43365c4b76e9ef6689c0204479fdc98c9ca0107093a7b7e89269776c71e3f0')

    # The 'fulfillBasicOrder_efficient_6GL6yc' function
    item: SemanticAbiItem = semantic_abi.functions_by_hash.get('00000000')

    matches_and_steps: List[Tuple[Match, Step]] = _build_matches_and_steps(semantic_abi, item)

    step: Step = InitStep(semantic_abi, item)
    step = FlattenParametersStep(step)
    step = MatchStep(step, matches_and_steps)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 4
    offerer_column: DatasetColumn = columns[0]
    assert offerer_column.name == 'parameters_offerer'
    assert offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_order_hash_column: DatasetColumn = columns[1]
    assert fulfill_order_hash_column.name == 'fulfill_orderHash'
    assert fulfill_order_hash_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    fulfill_offerer_column: DatasetColumn = columns[2]
    assert fulfill_offerer_column.name == 'fulfill_offerer'
    assert fulfill_offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_recipient_column: DatasetColumn = columns[3]
    assert fulfill_recipient_column.name == 'fulfill_recipient'
    assert fulfill_recipient_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_recipient_column.extended_metadata == {'higherOrderType': 'addressHash'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_basic_order_transaction)

    assert len(rows) == 1
    row = rows[0]
    assert row['parameters_offerer'] == '0xf3a635117e050b6abe6b7502e12323addad5503e'
    assert row['fulfill_orderHash'] is None
    assert row['fulfill_offerer'] is None
    assert row['fulfill_recipient'] is None


def test_match_event_many():
    with gzip.open('test/resources/contracts/seaport/blocks/19072200.json.gz') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    with open('test/resources/contracts/seaport/abis/match/event_many.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_available_advanced_orders_transaction: EthTransaction = \
        next(t for t in block.transactions if t.hash == '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0')

    # The 'fulfillAvailableAdvancedOrders' function
    item: SemanticAbiItem = semantic_abi.functions_by_hash.get('87201b41')

    matches_and_steps: List[Tuple[Match, Step]] = _build_matches_and_steps(semantic_abi, item)

    step: Step = InitStep(semantic_abi, item)
    step = FlattenParametersStep(step)
    step = MatchStep(step, matches_and_steps)
    step = ExplodeIndexStep(step)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 5
    recipient_column: DatasetColumn = columns[0]
    assert recipient_column.name == 'recipient'
    assert recipient_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert recipient_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_order_hash_column: DatasetColumn = columns[1]
    assert fulfill_order_hash_column.name == 'fulfill_orderHash'
    assert fulfill_order_hash_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    fulfill_offerer_column: DatasetColumn = columns[2]
    assert fulfill_offerer_column.name == 'fulfill_offerer'
    assert fulfill_offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_recipient_column: DatasetColumn = columns[3]
    assert fulfill_recipient_column.name == 'fulfill_recipient'
    assert fulfill_recipient_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_recipient_column.extended_metadata == {'higherOrderType': 'addressHash'}
    explode_index_column: DatasetColumn = columns[4]
    assert explode_index_column.name == 'explodeIndex'
    assert explode_index_column.type_metadata == {'ingestType': 'integer', 'expectedType': 'integer'}

    rows: List[Dict[str, any]] = step.transform(block, fulfill_available_advanced_orders_transaction)

    assert len(rows) == 2
    row = rows[0]
    assert row['recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['fulfill_orderHash'] == '841b8210183ab8e77633eb01e2b61d8ea99877ed02710d1cc37b1eb36589e1b2'
    assert row['fulfill_offerer'] == '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428'
    assert row['fulfill_recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['explodeIndex'] == 0
    row = rows[1]
    assert row['recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['fulfill_orderHash'] == '420f28ae360d4f13a4cc18505b3fff1729642eef26220d4c225460fc08643010'
    assert row['fulfill_offerer'] == '0x492bd7462b4c9f391aaa38f328b7220229d67802'
    assert row['fulfill_recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['explodeIndex'] == 1


def test_match_event_multiple_with_transfer():
    """
    Test that we can match against multiple things, including a transfer event
    """
    with gzip.open('test/resources/contracts/seaport/blocks/19072200.json.gz') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    with open('test/resources/contracts/seaport/abis/match/event_multiple_with_transfer.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_available_advanced_orders_transaction: EthTransaction = \
        next(t for t in block.transactions if t.hash == '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0')

    # The 'fulfillAvailableAdvancedOrders' function
    item: SemanticAbiItem = semantic_abi.functions_by_hash.get('87201b41')

    matches_and_steps: List[Tuple[Match, Step]] = _build_matches_and_steps(semantic_abi, item)

    step: Step = InitStep(semantic_abi, item)
    step = FlattenParametersStep(step)
    step = MatchStep(step, matches_and_steps)
    step = ExplodeIndexStep(step)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 10
    recipient_column: DatasetColumn = columns[0]
    assert recipient_column.name == 'recipient'
    assert recipient_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert recipient_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_order_hash_column: DatasetColumn = columns[1]
    assert fulfill_order_hash_column.name == 'fulfill_orderHash'
    assert fulfill_order_hash_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    fulfill_offerer_column: DatasetColumn = columns[2]
    assert fulfill_offerer_column.name == 'fulfill_offerer'
    assert fulfill_offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_recipient_column: DatasetColumn = columns[3]
    assert fulfill_recipient_column.name == 'fulfill_recipient'
    assert fulfill_recipient_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_recipient_column.extended_metadata == {'higherOrderType': 'addressHash'}
    from_column: DatasetColumn = columns[4]
    assert from_column.name == 'transfer_fromAddress'
    assert from_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert from_column.extended_metadata == {'higherOrderType': 'addressHash'}
    to_column: DatasetColumn = columns[5]
    assert to_column.name == 'transfer_toAddress'
    assert to_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert to_column.extended_metadata == {'higherOrderType': 'addressHash'}
    value_column: DatasetColumn = columns[6]
    assert value_column.name == 'transfer_value'
    assert value_column.type_metadata == {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0}
    token_id_column: DatasetColumn = columns[7]
    assert token_id_column.name == 'transfer_tokenId'
    assert token_id_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert token_id_column.extended_metadata == {'higherOrderType': 'id'}
    token_type_column: DatasetColumn = columns[8]
    assert token_type_column.name == 'transfer_tokenType'
    assert token_type_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert token_type_column.extended_metadata == {'higherOrderType': 'enum'}
    explode_index_column: DatasetColumn = columns[9]
    assert explode_index_column.name == 'explodeIndex'
    assert explode_index_column.type_metadata == {'ingestType': 'integer', 'expectedType': 'integer'}

    rows: List[Dict[str, any]] = step.transform(block, fulfill_available_advanced_orders_transaction)

    assert len(rows) == 2
    row = rows[0]
    assert row['recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['fulfill_orderHash'] == '841b8210183ab8e77633eb01e2b61d8ea99877ed02710d1cc37b1eb36589e1b2'
    assert row['fulfill_offerer'] == '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428'
    assert row['fulfill_recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['transfer_fromAddress'] == '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428'
    assert row['transfer_toAddress'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['transfer_value'] == '1'
    assert row['transfer_tokenId'] == '207'
    assert row['transfer_tokenType'] == 'Erc721'
    assert row['explodeIndex'] == 0
    row = rows[1]
    assert row['recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['fulfill_orderHash'] == '420f28ae360d4f13a4cc18505b3fff1729642eef26220d4c225460fc08643010'
    assert row['fulfill_offerer'] == '0x492bd7462b4c9f391aaa38f328b7220229d67802'
    assert row['fulfill_recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['transfer_fromAddress'] == '0x492bd7462b4c9f391aaa38f328b7220229d67802'
    assert row['transfer_toAddress'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['transfer_value'] == '1'
    assert row['transfer_tokenId'] == '6290'
    assert row['transfer_tokenType'] == 'Erc721'
    assert row['explodeIndex'] == 1


def test_match_event_onlyone_with_exploded():
    """
    Test that we can match onlyOne event with each row of an exploded primary item
    """
    with gzip.open('test/resources/contracts/seaport/blocks/19029959.json.gz') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    with open('test/resources/contracts/seaport/abis/match/event_onlyone_with_exploded.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in block.transactions if t.hash == '0x35343c5b809fc2a1c9e1c15fe854c8f07ba815fa58764373c5f949ffc08d9d6f')

    item: SemanticAbiItem = semantic_abi.functions_by_hash.get('ed98a574')

    step: Step = InitStep(semantic_abi, item)
    step = FlattenParametersStep(step)
    step = ExplodeStep(step)
    step = MatchStep(step, _build_matches_and_steps(semantic_abi, item))
    step = ExplodeIndexStep(step)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 6
    offerer_column: DatasetColumn = columns[0]
    assert offerer_column.name == 'orders_parameters_offerer'
    assert offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    start_time_column: DatasetColumn = columns[1]
    assert start_time_column.name == 'orders_parameters_startTime'
    assert start_time_column.type_metadata == {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0}
    fulfill_order_hash_column: DatasetColumn = columns[2]
    assert fulfill_order_hash_column.name == 'fulfill_orderHash'
    assert fulfill_order_hash_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    fulfill_offerer_column: DatasetColumn = columns[3]
    assert fulfill_offerer_column.name == 'fulfill_offerer'
    assert fulfill_offerer_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_offerer_column.extended_metadata == {'higherOrderType': 'addressHash'}
    fulfill_recipient_column: DatasetColumn = columns[4]
    assert fulfill_recipient_column.name == 'fulfill_recipient'
    assert fulfill_recipient_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert fulfill_recipient_column.extended_metadata == {'higherOrderType': 'addressHash'}
    explode_index_column: DatasetColumn = columns[5]
    assert explode_index_column.name == 'explodeIndex'
    assert explode_index_column.type_metadata == {'ingestType': 'integer', 'expectedType': 'integer'}

    rows: List[Dict[str, any]] = step.transform(block, fulfill_order_transaction)

    assert len(rows) == 2
    row = rows[0]
    assert row['orders_parameters_offerer'] == '0x48d67bf72c47d748ca7c23fd54981a7875a0282e'
    assert row['orders_parameters_startTime'] == '1705393997'
    assert row['fulfill_orderHash'] == 'cfaff8419f2c662c4d5c066743109aee7ede3f14b3a899d4ba46f410e724b041'
    assert row['fulfill_offerer'] == '0x48d67bf72c47d748ca7c23fd54981a7875a0282e'
    assert row['fulfill_recipient'] == '0x99732e448bb615dbef5cf529da864d0cb51eb0fc'
    assert row['explodeIndex'] == 0
    row = rows[1]
    assert row['orders_parameters_offerer'] == '0x2ff895e051f7a1c29c2d3bdab35c4960e3e1ec72'
    assert row['orders_parameters_startTime'] == '1705535000'
    assert row['fulfill_orderHash'] == '5acfda362b60a511a6b2a2856bf23d37acb774785cb59fefd374490cb3f78fd9'
    assert row['fulfill_offerer'] == '0x2ff895e051f7a1c29c2d3bdab35c4960e3e1ec72'
    assert row['fulfill_recipient'] == '0x99732e448bb615dbef5cf529da864d0cb51eb0fc'
    assert row['explodeIndex'] == 1


def test_match_invalid_column():
    with open('test/resources/contracts/seaport/abis/match/invalid_column.json') as file:
        semantic_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    # The 'OrderFulfilled' event
    item: SemanticAbiItem = semantic_abi.events_by_hash.get('9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31')

    matches_and_steps: List[Tuple[Match, Step]] = _build_matches_and_steps(semantic_abi, item)

    step: Step = InitStep(semantic_abi, item)
    step = FlattenParametersStep(step)

    with pytest.raises(InvalidAbiException) as e:
        MatchStep(step, matches_and_steps)

    assert str(e.value) == "Unknown matched column referenced in match predicate of prefix 'basicOrder': blargh"
