import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {InitStep} from "semanticabi/transform/steps/InitStep";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {FileUtil} from "@test/common/FileUtil";

const fileUtil = new FileUtil('test/semanticabi/resources/contracts/seaport');

test('filtered contract address', async () => {
    const semanticAbi = new SemanticAbi(fileUtil.loadJson('abis/init/FilteredContractAddress.json'));
    const step = new InitStep(semanticAbi, semanticAbi.functions.get('b3a34c4c'));
    const testBlock = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/18937419.json.gz'));

    // transaction with the function trace we care about
    expect(step.transform(
        testBlock,
        testBlock.transactions.find(t => t.hash === '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')
    ).length).toBe(1);

    // transaction without the function trace we care about
    expect(step.transform(
        testBlock,
        testBlock.transactions.find(t => t.hash === '0x79207b3fb00a5f3c89342bc0d34a6db88106fb824d26c2c4e4bd73ac38348e7c')
    ).length).toBe(0);
});