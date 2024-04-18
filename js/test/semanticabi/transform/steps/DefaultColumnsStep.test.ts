import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {InitStep} from "semanticabi/transform/steps/InitStep";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {FileUtil} from "@test/common/FileUtil";
import {DefaultColumnsStep} from "semanticabi/transform/steps/DefaultColumnsStep";

const fileUtil = new FileUtil('test/semanticabi/resources/contracts/uniswap');

test('default columns event', async () => {
    const semanticAbi = new SemanticAbi(fileUtil.loadJson('abis/FactoryV3.json'));
    const testBlock = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadJson('blocks/FactoryV3.json'));

    let step = new InitStep(semanticAbi, semanticAbi.events.get('783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118'));
    step = new DefaultColumnsStep(step);

    // transaction without the function trace we care about
    expect(step.transform(testBlock, testBlock.transactions[0])).toEqual([{
        chain: 'ethereum',
        blockHash: '0xd3e60acfc6fff75c5eb2ddae2618cbc07cc7c0be0a6d69ff5ce722828758e895',
        blockNumber: 18578531,
        blockTimestamp: 1700066351,
        transactionHash: '0x65773c0937a12b6cc0435fb025c0920aeb16a15b1c397b559dda6f26dbbe4f29',
        transactionFrom: '0x130b0a18b6bd98c00133600d8095aaaaeb1cfb5b',
        transactionTo: '0x1f98431c8ad98523631ae4a59f267346ea31f984',
        contractAddress: '0x1f98431c8ad98523631ae4a59f267346ea31f984',
        status: 1,
        gasUsed: 4558970,
        itemType: 'event',
        internalIndex: '161'
    }]);
});

test('default columns function', async () => {
    const semanticAbi = new SemanticAbi(fileUtil.loadJson('abis/FactoryV3.json'));
    const testBlock = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadJson('blocks/FactoryV3.json'));

    let step = new InitStep(semanticAbi, semanticAbi.functions.get('a1671295'));
    step = new DefaultColumnsStep(step);

    // transaction without the function trace we care about
    expect(step.transform(testBlock, testBlock.transactions[0])).toEqual([{
        chain: 'ethereum',
        blockHash: '0xd3e60acfc6fff75c5eb2ddae2618cbc07cc7c0be0a6d69ff5ce722828758e895',
        blockNumber: 18578531,
        blockTimestamp: 1700066351,
        transactionHash: '0x65773c0937a12b6cc0435fb025c0920aeb16a15b1c397b559dda6f26dbbe4f29',
        transactionFrom: '0x130b0a18b6bd98c00133600d8095aaaaeb1cfb5b',
        transactionTo: '0x1f98431c8ad98523631ae4a59f267346ea31f984',
        contractAddress: '0x1f98431c8ad98523631ae4a59f267346ea31f984',
        status: 1,
        gasUsed: 4558970,
        itemType: 'function',
        internalIndex: ''
    }]);
});
