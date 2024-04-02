import gzip
import json
from typing import List, Dict

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.common.TransformException import TransformException
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.DefaultColumnsStep import DefaultColumnsStep
from semanticabi.steps.InitStep import InitStep
from semanticabi.steps.Step import Step, TransformItem
from semanticabi.steps.SubsequentStep import SubsequentStep
from semanticabi.steps.TransformErrorStep import TransformErrorStep


class FakeErrorStep(SubsequentStep):
    _previous_step: Step

    def __init__(self, previous_step: Step):
        super().__init__(previous_step)

    @property
    def schema(self) -> AbiSchema:
        return self._previous_step.schema

    def _inner_transform_item(
        self,
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previous_data: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        raise TransformException('Fake error')


def test_step_with_transform_error():
    with open('test/resources/contracts/seaport/abis/Seaport1.5.json') as file:
        seaport_abi: SemanticAbi = SemanticAbi(json.loads(file.read()))

    with gzip.open('test/resources/contracts/seaport/blocks/18937419.json.gz') as file:
        seaport_block: EthBlock = EthBlock(EvmChain.ETHEREUM, json.loads(file.read()))

    fulfill_order_transaction: EthTransaction = \
        next(t for t in seaport_block.transactions if t.hash == '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')

    step: Step = InitStep(seaport_abi, seaport_abi.functions_by_hash.get('b3a34c4c'))
    step = DefaultColumnsStep(step)
    step = FakeErrorStep(step)
    step = TransformErrorStep(step)

    schema: AbiSchema = step.schema
    columns: List[DatasetColumn] = schema.columns()

    assert len(columns) == 13
    transform_error_column: DatasetColumn = columns[12]
    assert transform_error_column.name == 'transform_error'
    assert transform_error_column.type_metadata == {'ingestType': 'string', 'expectedType': 'string', 'isArray': False}
    assert transform_error_column.extended_metadata == {'higherOrderType': 'none'}

    rows: List[Dict[str, any]] = step.transform(seaport_block, fulfill_order_transaction)

    assert len(rows) == 1
    row = rows[0]
    # Quick check that the default column values still got filled
    assert row['chain'] == 'ethereum'
    assert row['blockNumber'] == 18937419
    # Check that the transform_error column got filled
    assert row['transform_error'] == 'Fake error'