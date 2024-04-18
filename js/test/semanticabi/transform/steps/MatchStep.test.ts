import {FileUtil} from '@test/common/FileUtil';
import {SemanticAbi} from 'semanticabi/abi/SemanticAbi';
import {Step} from 'semanticabi/transform/steps/Step';
import {InitStep} from 'semanticabi/transform/steps/InitStep';
import {AbiMatchSteps, MatchStep} from 'semanticabi/transform/steps/MatchStep';
import {FlattenStep} from 'semanticabi/transform/steps/FlattenStep';
import {EthBlock} from 'semanticabi/metadata/EthBlock';
import {EvmChain} from 'semanticabi/metadata/EvmChain';
import {ExplodeIndexStep} from 'semanticabi/transform/steps/ExplodeIndexStep';
import {ExplodeStep} from 'semanticabi/transform/steps/ExplodeStep';

const fileUtil = new FileUtil('test/semanticabi/resources/contracts/seaport');

test('match event only one', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('abis/match/event_onlyone.json'));

    const abiItem = abi.functions.get('00000000');
    const stepsForMatches = AbiMatchSteps.fromAbi(abi, [abiItem]).stepsForMatch(abiItem.properties.matches.get().matches);

    let step: Step = new InitStep(abi, abiItem);
    step = new FlattenStep(step);
    step = new MatchStep(step, stepsForMatches);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19044839.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0x1d43365c4b76e9ef6689c0204479fdc98c9ca0107093a7b7e89269776c71e3f0')
    );
    expect(rows).toEqual([{
        'parameters_offerer': '0xf3a635117e050b6abe6b7502e12323addad5503e',
        'fulfill_orderHash': '603816a107c27139ec3f867c70aaa1008f42db389c7be0b4807464505ad5c699',
        'fulfill_offerer': '0xf3a635117e050b6abe6b7502e12323addad5503e',
        'fulfill_recipient': '0x7a558b543f18ce7257bd469e24bbb31e5ec4f1e8'
    }]);
});

test('match function only one', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('abis/match/function_onlyone.json'));

    const abiItem = abi.events.get('9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31');
    const stepsForMatches = AbiMatchSteps.fromAbi(abi, [abiItem]).stepsForMatch(abiItem.properties.matches.get().matches);

    let step: Step = new InitStep(abi, abiItem);
    step = new FlattenStep(step);
    step = new MatchStep(step, stepsForMatches);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19044839.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0x1d43365c4b76e9ef6689c0204479fdc98c9ca0107093a7b7e89269776c71e3f0')
    );
    expect(rows).toEqual([{
        'orderHash': '603816a107c27139ec3f867c70aaa1008f42db389c7be0b4807464505ad5c699',
        'offerer': '0xf3a635117e050b6abe6b7502e12323addad5503e',
        'recipient': '0x7a558b543f18ce7257bd469e24bbb31e5ec4f1e8',
        'basicOrder_parameters_offerer': '0xf3a635117e050b6abe6b7502e12323addad5503e'
    }]);
});

test('match event optional one', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('abis/match/event_optionalone.json'));

    const abiItem = abi.functions.get('00000000');
    const stepsForMatches = AbiMatchSteps.fromAbi(abi, [abiItem]).stepsForMatch(abiItem.properties.matches.get().matches);

    let step: Step = new InitStep(abi, abiItem);
    step = new FlattenStep(step);
    step = new MatchStep(step, stepsForMatches);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19044839.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0x1d43365c4b76e9ef6689c0204479fdc98c9ca0107093a7b7e89269776c71e3f0')
    );
    expect(rows).toEqual([{
        'parameters_offerer': '0xf3a635117e050b6abe6b7502e12323addad5503e',
        'fulfill_orderHash': null,
        'fulfill_offerer': null,
        'fulfill_recipient': null
    }]);
});

test('match event many', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('abis/match/event_many.json'));

    const abiItem = abi.functions.get('87201b41');
    const stepsForMatches = AbiMatchSteps.fromAbi(abi, [abiItem]).stepsForMatch(abiItem.properties.matches.get().matches);

    let step: Step = new InitStep(abi, abiItem);
    step = new FlattenStep(step);
    step = new MatchStep(step, stepsForMatches);
    step = new ExplodeIndexStep(step);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19072200.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0')
    );
    expect(rows).toEqual([{
        'recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'fulfill_orderHash': '841b8210183ab8e77633eb01e2b61d8ea99877ed02710d1cc37b1eb36589e1b2',
        'fulfill_offerer': '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428',
        'fulfill_recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'explodeIndex': 0
    }, {
        'recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'fulfill_orderHash': '420f28ae360d4f13a4cc18505b3fff1729642eef26220d4c225460fc08643010',
        'fulfill_offerer': '0x492bd7462b4c9f391aaa38f328b7220229d67802',
        'fulfill_recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'explodeIndex': 1
    }]);
});

test('match event multiple with transfer', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('abis/match/event_multiple_with_transfer.json'));

    const abiItem = abi.functions.get('87201b41');
    const stepsForMatches = AbiMatchSteps.fromAbi(abi, [abiItem]).stepsForMatch(abiItem.properties.matches.get().matches);

    let step: Step = new InitStep(abi, abiItem);
    step = new FlattenStep(step);
    step = new MatchStep(step, stepsForMatches);
    step = new ExplodeIndexStep(step);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19072200.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0')
    );
    expect(rows).toEqual([{
        'explodeIndex': 0,
        'fulfill_offerer': '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428',
        'fulfill_orderHash': '841b8210183ab8e77633eb01e2b61d8ea99877ed02710d1cc37b1eb36589e1b2',
        'fulfill_recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transfer_fromAddress': '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428',
        'transfer_toAddress': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transfer_tokenId': '207',
        'transfer_tokenType': 'Erc721',
        'transfer_value': 1
    }, {
        'explodeIndex': 1,
        'fulfill_offerer': '0x492bd7462b4c9f391aaa38f328b7220229d67802',
        'fulfill_orderHash': '420f28ae360d4f13a4cc18505b3fff1729642eef26220d4c225460fc08643010',
        'fulfill_recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transfer_fromAddress': '0x492bd7462b4c9f391aaa38f328b7220229d67802',
        'transfer_toAddress': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transfer_tokenId': '6290',
        'transfer_tokenType': 'Erc721',
        'transfer_value': 1
    }]);
});

test('match event only one with exploded', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('abis/match/event_onlyone_with_exploded.json'));

    const abiItem = abi.functions.get('ed98a574');
    const stepsForMatches = AbiMatchSteps.fromAbi(abi, [abiItem]).stepsForMatch(abiItem.properties.matches.get().matches);

    let step: Step = new InitStep(abi, abiItem);
    step = new FlattenStep(step);
    step = new ExplodeStep(step);
    step = new MatchStep(step, stepsForMatches);
    step = new ExplodeIndexStep(step);

    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19029959.json.gz'));
    const rows = step.transform(
        block,
        block.transactions.find(t => t.hash === '0x35343c5b809fc2a1c9e1c15fe854c8f07ba815fa58764373c5f949ffc08d9d6f')
    );
    expect(rows).toEqual([  {
        'explodeIndex': 0,
        'fulfill_offerer': '0x48d67bf72c47d748ca7c23fd54981a7875a0282e',
        'fulfill_orderHash': 'cfaff8419f2c662c4d5c066743109aee7ede3f14b3a899d4ba46f410e724b041',
        'fulfill_recipient': '0x99732e448bb615dbef5cf529da864d0cb51eb0fc',
        'orders_parameters_offerer': '0x48d67bf72c47d748ca7c23fd54981a7875a0282e',
        'orders_parameters_startTime': BigInt(1705393997)
    }, {
        'explodeIndex': 1,
        'fulfill_offerer': '0x2ff895e051f7a1c29c2d3bdab35c4960e3e1ec72',
        'fulfill_orderHash': '5acfda362b60a511a6b2a2856bf23d37acb774785cb59fefd374490cb3f78fd9',
        'fulfill_recipient': '0x99732e448bb615dbef5cf529da864d0cb51eb0fc',
        'orders_parameters_offerer': '0x2ff895e051f7a1c29c2d3bdab35c4960e3e1ec72',
        'orders_parameters_startTime': BigInt(1705535000)
    }]);
});

test('match invalid column', async () => {
    const abi = new SemanticAbi(fileUtil.loadJson('abis/match/invalid_column.json'));

    const abiItem = abi.events.get('9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31');
    const stepsForMatches = AbiMatchSteps.fromAbi(abi, [abiItem]).stepsForMatch(abiItem.properties.matches.get().matches);

    let step: Step = new InitStep(abi, abiItem);
    step = new FlattenStep(step);
    expect(() => new MatchStep(step, stepsForMatches)).toThrow('Unknown matched column referenced in match predicate of prefix \'basicOrder\': blargh.');
});

