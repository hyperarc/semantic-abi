import {FileUtil} from 'test/common/FileUtil';
import {SemanticTransformer} from 'semanticabi/transform/SemanticTransformer';
import {EvmChain} from 'semanticabi/metadata/EvmChain';
import {EthBlock} from 'semanticabi/metadata/EthBlock';

const fileUtil = new FileUtil('test/semanticabi/resources/contracts/seaport');

test('matching schemas', () => {
    const transformer = new SemanticTransformer(fileUtil.loadJson('abis/transform/primary_items_schema_equal.json'));

    expect(transformer.schema.columns.map(c => c.name)).toEqual([
        'chain', 'blockHash', 'blockNumber', 'blockTimestamp', 'transactionHash', 'transactionFrom', 'transactionTo',
        'contractAddress', 'status', 'gasUsed', 'itemType', 'internalIndex', 'parameters_offerer', 'parameters_zone',
        'parameters_orderType', 'parameters_startTime', 'parameters_zoneHash', 'parameters_salt', 'fulfilled',
        'fulfill_orderHash', 'fulfill_offerer', 'fulfill_recipient', 'transfer_fromAddress', 'transfer_toAddress',
        'transfer_value', 'transfer_tokenId', 'transfer_tokenType', 'explodeIndex', 'transform_error'
    ]);
});

/**
 * Test that different sets of columns create a unioned schema. The first item excludes the `fulfilled` output param
 * and the second item excludes the 'parameters_salt' input param.
 */
test('different columns', () => {
    const transformer = new SemanticTransformer(fileUtil.loadJson('abis/transform/primary_items_schema_diff_columns.json'));

    expect(transformer.schema.columns.map(c => c.name)).toEqual([
        'chain', 'blockHash', 'blockNumber', 'blockTimestamp', 'transactionHash', 'transactionFrom', 'transactionTo',
        'contractAddress', 'status', 'gasUsed', 'itemType', 'internalIndex', 'parameters_offerer', 'parameters_zone',
        'parameters_orderType', 'parameters_startTime', 'parameters_zoneHash', 'parameters_salt', 'explodeIndex',
        'transform_error', 'fulfilled'
    ]);
});

test('invalid different column types', () => {
    expect(() => {
        new SemanticTransformer(fileUtil.loadJson('abis/transform/primary_items_schema_diff_column_types.json'));
    }).toThrow('Column with name \'parameters_startTime\' already exists and is a different type.');
});

test('seaport block', async() => {
    const transformer = new SemanticTransformer(fileUtil.loadJson('abis/transform/primary_items_schema_equal.json'));
    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19072200.json.gz'));

    expect(transformer.transform(block)).toStrictEqual([{
        'blockHash': '0xb6dc49e1ec28f2847a6b6e0d2159e3f04c539fc5af78d7a1451cb9e4250f28c9',
        'blockNumber': 19072200,
        'blockTimestamp': 1706047259,
        'chain': 'ethereum',
        'contractAddress': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'explodeIndex': 0,
        'fulfill_offerer': '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428',
        'fulfill_orderHash': '841b8210183ab8e77633eb01e2b61d8ea99877ed02710d1cc37b1eb36589e1b2',
        'fulfill_recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'fulfilled': true,
        'gasUsed': 309515,
        'internalIndex': '',
        'itemType': 'function',
        'parameters_offerer': '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428',
        'parameters_orderType': BigInt(0),
        'parameters_salt': BigInt('51951570786726798460324975021501917861654789585098516727729696327573800411544'),
        'parameters_startTime': BigInt(1706047181),
        'parameters_zone': '0x004c00500000ad104d7dbd00e3ae0a5c00560c00',
        'parameters_zoneHash': '0000000000000000000000000000000000000000000000000000000000000000',
        'status': 1,
        'transactionFrom': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transactionHash': '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0',
        'transactionTo': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'transfer_fromAddress': '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428',
        'transfer_toAddress': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transfer_tokenId': '207',
        'transfer_tokenType': 'Erc721',
        'transfer_value': 1,
        'transform_error': null
    }, {
        'blockHash': '0xb6dc49e1ec28f2847a6b6e0d2159e3f04c539fc5af78d7a1451cb9e4250f28c9',
        'blockNumber': 19072200,
        'blockTimestamp': 1706047259,
        'chain': 'ethereum',
        'contractAddress': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'explodeIndex': 1,
        'fulfill_offerer': '0x492bd7462b4c9f391aaa38f328b7220229d67802',
        'fulfill_orderHash': '420f28ae360d4f13a4cc18505b3fff1729642eef26220d4c225460fc08643010',
        'fulfill_recipient': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'fulfilled': true,
        'gasUsed': 309515,
        'internalIndex': '',
        'itemType': 'function',
        'parameters_offerer': '0x492bd7462b4c9f391aaa38f328b7220229d67802',
        'parameters_orderType': BigInt(0),
        'parameters_salt': BigInt('51951570786726798460324975021501917861654789585098516727716053568646066475044'),
        'parameters_startTime': BigInt('1706047217'),
        'parameters_zone': '0x004c00500000ad104d7dbd00e3ae0a5c00560c00',
        'parameters_zoneHash': '0000000000000000000000000000000000000000000000000000000000000000',
        'status': 1,
        'transactionFrom': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transactionHash': '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0',
        'transactionTo': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'transfer_fromAddress': '0x492bd7462b4c9f391aaa38f328b7220229d67802',
        'transfer_toAddress': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transfer_tokenId': '6290',
        'transfer_tokenType': 'Erc721',
        'transfer_value': 1,
        'transform_error': null
    }]);
});

test('seaport block union schema', async() => {
    const transformer = new SemanticTransformer(fileUtil.loadJson('abis/transform/primary_items_schema_diff_columns.json'));
    const block = new EthBlock(EvmChain.ETHEREUM, await fileUtil.loadZippedJson('blocks/19072200.json.gz'));

    expect(transformer.transform(block)).toStrictEqual([{
        'blockHash': '0xb6dc49e1ec28f2847a6b6e0d2159e3f04c539fc5af78d7a1451cb9e4250f28c9',
        'blockNumber': 19072200,
        'blockTimestamp': 1706047259,
        'chain': 'ethereum',
        'contractAddress': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'explodeIndex': 0,
        'fulfilled': null,
        'gasUsed': 309515,
        'internalIndex': '',
        'itemType': 'function',
        'parameters_offerer': '0x47c47bde4cdc40a04e812a2417a5b7a5a2aea428',
        'parameters_orderType': BigInt(0),
        'parameters_salt': BigInt('51951570786726798460324975021501917861654789585098516727729696327573800411544'),
        'parameters_startTime': BigInt(1706047181),
        'parameters_zone': '0x004c00500000ad104d7dbd00e3ae0a5c00560c00',
        'parameters_zoneHash': '0000000000000000000000000000000000000000000000000000000000000000',
        'status': 1,
        'transactionFrom': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transactionHash': '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0',
        'transactionTo': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'transform_error': null
    }, {
        'blockHash': '0xb6dc49e1ec28f2847a6b6e0d2159e3f04c539fc5af78d7a1451cb9e4250f28c9',
        'blockNumber': 19072200,
        'blockTimestamp': 1706047259,
        'chain': 'ethereum',
        'contractAddress': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'explodeIndex': 1,
        'fulfilled': null,
        'gasUsed': 309515,
        'internalIndex': '',
        'itemType': 'function',
        'parameters_offerer': '0x492bd7462b4c9f391aaa38f328b7220229d67802',
        'parameters_orderType': BigInt(0),
        'parameters_salt': BigInt('51951570786726798460324975021501917861654789585098516727716053568646066475044'),
        'parameters_startTime': BigInt(1706047217),
        'parameters_zone': '0x004c00500000ad104d7dbd00e3ae0a5c00560c00',
        'parameters_zoneHash': '0000000000000000000000000000000000000000000000000000000000000000',
        'status': 1,
        'transactionFrom': '0xd41fcbb0e58cbeae68b151e07bd8f991afc5e1af',
        'transactionHash': '0xda8f8d02c5afc00304f8db14ebe2e00a671e2cffa17867323c091e418a6156d0',
        'transactionTo': '0x00000000000000adc04c56bf30ac9d3c0aaf14dc',
        'transform_error': null
    }]);
});
