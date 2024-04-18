import {ErigonTraces} from "semanticabi/metadata/ErigonTraces";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {FileUtil} from "test/common/FileUtil";

const fileUtil = new FileUtil('test/semanticabi/resources/blocks/');

test('load', async () => {
    const traces = ErigonTraces.fromStandalone(
        EvmChain.ETHEREUM, await fileUtil.loadZippedJson('17133218_erigon.json.gz')
    );

    expect(traces.blockNumber).toBe(17133218);
    expect(traces.rewards.length).toBe(1);
    expect(traces.transactions.length).toBe(144);

    const internalTransactions = traces.transactions.flatMap(t => t.internalTransactions);
    expect(internalTransactions.length).toBe(58);

    const errors = traces.transactions.filter(t => t.errors.isPresent);
    expect(errors.length).toBe(8);
});

test('callStack', async () => {
    const traces = ErigonTraces.fromStandalone(
        EvmChain.ETHEREUM, await fileUtil.loadZippedJson('17133218_erigon.json.gz')
    );

    const transaction = traces.transactions[0];
    const stack = transaction.callStack([2, 7, 1, 0, 0]);
    expect(stack.map(t => t.traceHash)).toEqual(['', '2', '2_7', '2_7_1', '2_7_1_0', '2_7_1_0_0']);
});