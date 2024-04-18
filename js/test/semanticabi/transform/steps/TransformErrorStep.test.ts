import {SubsequentStep} from 'semanticabi/transform/steps/SubsequentStep';
import {Step} from 'semanticabi/transform/steps/Step';
import {AbiSchema} from 'semanticabi/transform/steps/AbiSchema';
import {SemanticAbiExecutionError} from 'semanticabi/abi/item/semantic/SemanticAbiExecutionError';
import {FileUtil} from 'test/common/FileUtil';
import {SemanticAbi} from 'semanticabi/abi/SemanticAbi';
import {EthBlock} from 'semanticabi/metadata/EthBlock';
import {EvmChain} from 'semanticabi/metadata/EvmChain';
import {InitStep} from 'semanticabi/transform/steps/InitStep';
import {DefaultColumnsStep} from 'semanticabi/transform/steps/DefaultColumnsStep';
import {TransformErrorStep} from 'semanticabi/transform/steps/TransformErrorStep';

class FakeErrorStep extends SubsequentStep {

    constructor(previousStep: Step) {
        super(previousStep);
    }

    get schema(): AbiSchema {
        return this.previousStep.schema;
    }

    protected innerTransformItem(
        block: any,
        transaction: any,
        item: any,
        previousData: any[]
    ): any[] {
        throw new SemanticAbiExecutionError('Fake error');
    }

}

const fileUtil = new FileUtil('test/semanticabi/resources/contracts/seaport');

test('step with transform error', async () => {
    const semanticAbi = new SemanticAbi(fileUtil.loadJson('abis/Seaport1.5.json'));

    let step = new InitStep(semanticAbi, semanticAbi.functions.get('b3a34c4c'));
    step = new DefaultColumnsStep(step);
    step = new FakeErrorStep(step);
    step = new TransformErrorStep(step);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/18937419.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace')
    );
    expect(rows).toEqual([{
        'blockHash': '0x805a62aaf25fd971f223660f919fdaa591463f1fa12204ac495c94e3b31d067f',
        'blockNumber': 18937419,
        'blockTimestamp': 1704413267,
        'chain': 'ethereum',
        'contractAddress': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'gasUsed': 159666,
        'internalIndex': '',
        'itemType': 'function',
        'status': 1,
        'transactionFrom': '0x057f18b59fbd0cb8b78ab3421cf29c8d046bcb7c',
        'transactionHash': '0xb305d44fd60ea8a92d11c2cd342a850a911ee8a2043c41f0e1ec0507e8e51ace',
        'transactionTo': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'transform_error': 'Error: Fake error'
    }]);
});