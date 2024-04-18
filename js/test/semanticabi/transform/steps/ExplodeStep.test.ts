import {FileUtil} from "@test/common/FileUtil";
import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {InitStep} from "semanticabi/transform/steps/InitStep";
import {ExplodeStep} from "semanticabi/transform/steps/ExplodeStep";
import {Step} from "semanticabi/transform/steps/Step";
import {ExplodeIndexStep} from "semanticabi/transform/steps/ExplodeIndexStep";

const fileUtil = new FileUtil('test/semanticabi/resources/contracts/seaport');

test('explode multiple', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('abis/explode/multiple.json'));
    let step: Step = new InitStep(abi, abi.functions.get('ed98a574'));
    step = new ExplodeStep(step);
    step = new ExplodeIndexStep(step);

    expect(step.schema.columns.map(c => c.name)).toEqual([
        'orders_parameters_offerer',
        'orders_parameters_zone',
        'orders_signature',
        'fulfilled',
        'explodeIndex'
    ]);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19029959.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0x35343c5b809fc2a1c9e1c15fe854c8f07ba815fa58764373c5f949ffc08d9d6f')
    );
    expect(rows).toEqual([{
        'orders_parameters_offerer': '0x48d67bf72c47d748ca7c23fd54981a7875a0282e',
        'orders_parameters_zone': '0x004c00500000ad104d7dbd00e3ae0a5c00560c00',
        'orders_signature': '747dbe9266ec5b43e167e68f033fe2f079eae133b9f1a3bd5c3116a813672b247dab08d158e9daaabf0dedf6fddf65da00f27c734ce0b7cd27ba366b39cb2cc1',
        'fulfilled': true,
        'explodeIndex': 0
    }, {
        'orders_parameters_offerer': '0x2ff895e051f7a1c29c2d3bdab35c4960e3e1ec72',
        'orders_parameters_zone': '0x004c00500000ad104d7dbd00e3ae0a5c00560c00',
        'orders_signature': 'ebeba3501a325b6ac776dd1b17a757ca73ad9d9a1748348b25500c0205ed8cc99149f3e9113b98ee0520083f4711258b831544297925622ec56fe3b6f09d7b2a',
        'fulfilled': true,
        'explodeIndex': 1
    }]);
});
