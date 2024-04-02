import gzip
import json
from typing import List, Dict

from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.Step import Step
from semanticabi.steps.TokenTransferStep import TokenTransferStep


def test_token_transfers():
    with gzip.open('test/resources/contracts/seaport/blocks/18937419.json.gz') as file:
        block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in block.transactions if t.hash == '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')

    # Token transfers are Semantic ABI-agnostic
    step: Step = TokenTransferStep()

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 5
    from_address_column: DatasetColumn = columns[0]
    assert from_address_column.name == 'fromAddress'
    assert from_address_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert from_address_column.extended_metadata == {'higherOrderType': 'addressHash'}
    to_address_column: DatasetColumn = columns[1]
    assert to_address_column.name == 'toAddress'
    assert to_address_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert to_address_column.extended_metadata == {'higherOrderType': 'addressHash'}
    value_column: DatasetColumn = columns[2]
    assert value_column.name == 'value'
    assert value_column.type_metadata == {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0}
    token_id_column: DatasetColumn = columns[3]
    assert token_id_column.name == 'tokenId'
    assert token_id_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert token_id_column.extended_metadata == {'higherOrderType': 'id'}
    token_type_column: DatasetColumn = columns[4]
    assert token_type_column.name == 'tokenType'
    assert token_type_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert token_type_column.extended_metadata == {'higherOrderType': 'enum'}

    rows: List[Dict[str, any]] = step.transform(block, fulfill_order_transaction)

    assert len(rows) == 1
    row: Dict[str, any] = rows[0]
    assert row['fromAddress'] == '0xed7df6066bda2256efbf1f48f536c1e5c7776172'
    assert row['toAddress'] == '0x057f18b59fbd0cb8b78ab3421cf29c8d046bcb7c'
    assert row['value'] == '1'
    assert row['tokenId'] == '4340'
    assert row['tokenType'] == 'Erc721'
