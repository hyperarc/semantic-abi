import {FileUtil} from "test/common/FileUtil";
import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {InitStep} from "semanticabi/transform/steps/InitStep";
import {Step} from "semanticabi/transform/steps/Step";
import {ExplodeIndexStep} from "semanticabi/transform/steps/ExplodeIndexStep";
import {FlattenStep} from "semanticabi/transform/steps/FlattenStep";

const fileUtil = new FileUtil('test/semanticabi/resources/contracts');

test('uniswap event', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('uniswap/abis/FactoryV3.json'));
    let step: Step = new InitStep(abi, abi.events.get('783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118'));
    step = new FlattenStep(step);
    step = new ExplodeIndexStep(step);

    const columns = step.schema.columns;
    expect(columns.map(c => c.name)).toEqual([
        'token0',
        'fee',
        'tickSpacing',
        'pool',
        'explodeIndex'
    ]);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadJson('uniswap/blocks/FactoryV3.json'));
    const rows = step.transform(block, block.transactions[0]);
    expect(rows).toEqual([{
        'token0': '0x96ac8b252e1a9b75418964849f1985aef3798db0',
        'fee': BigInt(3000),
        'tickSpacing': BigInt(60),
        'pool': '0xa6656d691a80b01126d23ef9268212b74abcfaf5',
        'explodeIndex': 0
    }]);
});


test('seaport function', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('seaport/abis/Seaport1.5.json'));
    let step: Step = new InitStep(abi, abi.functions.get('b3a34c4c'));
    step = new FlattenStep(step);

    const columns = step.schema.columns;
    expect(columns.map(c => c.name)).toEqual([
        'order_parameters_offerer',
        'order_parameters_orderType',
        'order_parameters_startTime',
        'order_parameters_zoneHash',
        'order_signature',
        'fulfillerConduitKey',
        'fulfilled'
    ]);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('seaport/blocks/18937419.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')
    );
    expect(rows).toEqual([{
        'order_parameters_offerer': '0xed7df6066bda2256efbf1f48f536c1e5c7776172',
        'order_parameters_orderType': BigInt(0),
        'order_parameters_startTime': BigInt(1704411678),
        'order_parameters_zoneHash': '0000000000000000000000000000000000000000000000000000000000000000',
        'order_signature': '972ad99ba757983e2f2c28f48eeeec33819cd295cb6ffacc65eb5f58934cff35e42e0a43823b982838f7f4820c7a21ab3734115db3b6655fc28af7fea0ce520f00000a528a3e884473607e158111b86d27a5eac5cea6f46e1d23bf313ccc216eaf87970192bb5fbfc95abb002baa829d265042917f216996b13e3e9ae89b2c667943dca7b21727a1760cd8220b2c93408c85679a7707835008be3cee8879aa12bd03f34a383253bf26758d08a3814fbe3d76c5fdc204493666d79251fd837c979318f421957ec43ce2c5f9e87edf1057b34a0348c31dc7f9be3d03e8e26d6ef5e6ad9f',
        'fulfillerConduitKey': '0000000000000000000000000000000000000000000000000000000000000000',
        'fulfilled': true
    }]);
});

test('seaport function param transform', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('seaport/abis/flatten/param_transform.json'));
    let step: Step = new InitStep(abi, abi.functions.get('b3a34c4c'));
    step = new FlattenStep(step);

    const columns = step.schema.columns;
    expect(columns.map(c => c.name)).toEqual([
        'orderOfferer',
        'order_parameters_orderType',
        'isFulfilled'
    ]);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('seaport/blocks/18937419.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')
    );
    expect(rows).toEqual([{
        'orderOfferer': '0xed7df6066bda2256efbf1f48f536c1e5c7776172',
        'order_parameters_orderType': BigInt(0),
        'isFulfilled': true
    }]);
});