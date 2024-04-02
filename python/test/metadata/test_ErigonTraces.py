import json
from functools import reduce

import pytest

from semanticabi.metadata.ErigonTraces import ErigonTraces
from semanticabi.metadata.EvmChain import EvmChain


@pytest.fixture(scope='module')
def traces() -> ErigonTraces:
    with open('test/resources/ethereum_traces/17133218_erigon.json') as file:
        return ErigonTraces.from_standalone(EvmChain.ETHEREUM, json.loads(file.read()))


def test_load(traces: ErigonTraces):
    assert traces.block_number == 17133218
    assert len(traces.rewards) == 1
    assert len(traces.transactions) == 144

    # count all internal transactions
    internal_transactions = reduce(
        lambda a, b: a + b,
        map(
            lambda t: t.internal_transactions,
            traces.transactions
        )
    )
    assert len(internal_transactions) == 58

    # count all errors
    errors = list(
        filter(
            lambda t: t.errors is not None,
            traces.transactions
        )
    )
    assert len(errors) == 8


def test_call_stack(traces: ErigonTraces):
    transaction = traces.transactions[0]
    stack = transaction.call_stack([2, 7, 1, 0, '0'])

    assert ['', '2', '2_7', '2_7_1', '2_7_1_0', '2_7_1_0_0'] == list(map(lambda t: t.trace_hash, stack))
