import gzip
import json
from typing import List, Dict

import pytest as pytest

from semanticabi.SemanticTransformer import SemanticTransformer
from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.SemanticAbi import TypedSemanticAbi
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EvmChain import EvmChain


def test_matching_schemas():
    with open('test/resources/contracts/seaport/abis/transform/primary_items_schema_equal.json') as file:
        semantic_transformer: SemanticTransformer = SemanticTransformer(json.loads(file.read()))

    columns: List[DatasetColumn] = semantic_transformer.schema.columns()
    assert len(columns) == 29
    expected_column_names = [
        'chain', 'blockHash', 'blockNumber', 'blockTimestamp', 'transactionHash', 'transactionFrom', 'transactionTo',
        'contractAddress', 'status', 'gasUsed', 'itemType', 'internalIndex', 'parameters_offerer', 'parameters_zone',
        'parameters_orderType', 'parameters_startTime', 'parameters_zoneHash', 'parameters_salt', 'fulfilled',
        'fulfill_orderHash', 'fulfill_offerer', 'fulfill_recipient', 'transfer_fromAddress', 'transfer_toAddress',
        'transfer_value', 'transfer_tokenId', 'transfer_tokenType', 'explodeIndex', 'transform_error'
    ]
    assert [column.name for column in columns] == expected_column_names


def test_different_columns():
    """
    Test that different sets of columns create a unioned schema. The first item excludes the `fulfilled` output param
    and the second item excludes the 'parameters_salt' input param
    """
    with open('test/resources/contracts/seaport/abis/transform/primary_items_schema_diff_columns.json') as file:
        semantic_transformer: SemanticTransformer = SemanticTransformer(json.loads(file.read()))

    columns: List[DatasetColumn] = semantic_transformer.schema.columns()

    assert len(columns) == 21
    expected_column_names = [
        'chain', 'blockHash', 'blockNumber', 'blockTimestamp', 'transactionHash', 'transactionFrom', 'transactionTo',
        'contractAddress', 'status', 'gasUsed', 'itemType', 'internalIndex', 'parameters_offerer', 'parameters_zone',
        'parameters_orderType', 'parameters_startTime', 'parameters_zoneHash', 'parameters_salt', 'explodeIndex',
        'transform_error', 'fulfilled'
    ]
    assert [column.name for column in columns] == expected_column_names


def test_invalid_different_column_types():
    """
    Test that different column types for the same column name throw. The first item transforms the 'startTime' uint256
    to an int, while the second item does not
    """
    with open('test/resources/contracts/seaport/abis/transform/primary_items_schema_diff_column_types.json') as file:
        abi_json: TypedSemanticAbi = json.loads(file.read())

    with pytest.raises(InvalidAbiException) as e:
        SemanticTransformer(abi_json)

    assert 'Column \'parameters_startTime\' has conflicting types in schemas' in str(e.value)
    assert 'Column(parameters_startTime, long)' in str(e.value)
    assert 'Column(parameters_startTime, string)' in str(e.value)


def test_seaport_block():
    with open('test/resources/contracts/seaport/abis/transform/primary_items_schema_equal.json') as file:
        semantic_transformer: SemanticTransformer = SemanticTransformer(json.loads(file.read()))

    with gzip.open('test/resources/contracts/seaport/blocks/19072200.json.gz') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    rows: List[Dict[str, any]] = semantic_transformer.transform(block)

    assert len(rows) == 3
    # The fb2 transaction is a 'fulfillBasicOrder_efficient_6GL6yc' transaction with a single order that is fulfilled
    row = rows[0]
    assert row['transactionHash'] == '0xfb2e222fe2650533ab27b7354f9c8dfdd210625dd4eaaee7cae6e6ccd0a953bf'
    assert row['parameters_offerer'] == '0xe9b814a3cf21e36563d17820aa47f886cd6a6541'
    assert row['fulfill_orderHash'] == '2a9bb46a64e7620201e27a21143ebc9da61a116a14ddbc6a35496b663c62b9af'
    assert row['fulfill_recipient'] == '0xbea780f985790a0441c55efbd8b68f9e73c6893c'
    assert row['transfer_tokenId'] == '209'
    # The da8 transaction is a 'fulfillAvailableAdvancedOrders' transaction with a pair of orders that are fulfilled
    row = rows[1]
    assert row['transactionHash'] == '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0'
    assert row['parameters_offerer'] == '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428'
    assert row['fulfill_orderHash'] == '841b8210183ab8e77633eb01e2b61d8ea99877ed02710d1cc37b1eb36589e1b2'
    assert row['fulfill_recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['transfer_tokenId'] == '207'
    row = rows[2]
    assert row['transactionHash'] == '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0'
    assert row['parameters_offerer'] == '0x492bd7462b4c9f391aaa38f328b7220229d67802'
    assert row['fulfill_orderHash'] == '420f28ae360d4f13a4cc18505b3fff1729642eef26220d4c225460fc08643010'
    assert row['fulfill_recipient'] == '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af'
    assert row['transfer_tokenId'] == '6290'


def test_seaport_block_union_schema():
    with open('test/resources/contracts/seaport/abis/transform/primary_items_schema_diff_columns.json') as file:
        semantic_transformer: SemanticTransformer = SemanticTransformer(json.loads(file.read()))

    with gzip.open('test/resources/contracts/seaport/blocks/19072200.json.gz') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    rows: List[Dict[str, any]] = semantic_transformer.transform(block)

    assert len(rows) == 3
    assert rows[0]['fulfilled'] is True
    assert rows[1]['fulfilled'] is None
    assert rows[2]['fulfilled'] is None

    assert rows[0]['parameters_salt'] is None
    assert rows[1]['parameters_salt'] == '51951570786726798460324975021501917861654789585098516727729696327573800411544'
    assert rows[2]['parameters_salt'] == '51951570786726798460324975021501917861654789585098516727716053568646066475044'
