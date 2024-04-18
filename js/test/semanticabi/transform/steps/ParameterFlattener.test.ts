import {SemanticAbi} from "semanticabi/abi/SemanticAbi";
import {FileUtil} from "@test/common/FileUtil";
import {DataType} from "semanticabi/transform/column/DataType";
import {ParameterFlattener} from "semanticabi/transform/steps/ParameterFlattener";
import {zip} from "common/Collections";
import {ExplodeFlattenPredicate} from "semanticabi/transform/steps/ExplodeStep";

const fileUtil = new FileUtil('test/semanticabi/resources/contracts');

class EF {

    constructor(
        public readonly expectedName: string,
        public readonly expectedIsInput: boolean,
        public readonly expectedDataType: DataType,
        public readonly expectedPathNames: string[] = [],
        public readonly expectedColumnName: string = expectedName,
    ) {}

}

const assertFlattenedParameters = (flattener: ParameterFlattener, expected: EF[]) => {
    expect(flattener.flattened.length).toBe(expected.length);
    zip(flattener.flattened, expected).forEach(([param, expected]) => {
        expect(param.semanticParameter.name).toBe(expected.expectedName);
        expect(param.path.map((p) => p.name)).toEqual(expected.expectedPathNames);
        expect(param.finalColumnName).toBe(expected.expectedColumnName);
        expect(param.isInput).toBe(expected.expectedIsInput);
        expect(param.finalDatasetColumn.dataType).toEqual(expected.expectedDataType);
    });
};

test('flatten event params', () => {
    const abiItem = new SemanticAbi(fileUtil.loadJson('uniswap/abis/FactoryV3.json')).events.get('783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118');
    const flattener = new ParameterFlattener(abiItem);

    assertFlattenedParameters(flattener, [
        new EF(
            'token0',
            true,
            DataType.STRING
        ),
        new EF(
            'fee',
            true,
            DataType.NUMBER
        ),
        new EF(
            'tickSpacing',
            true,
            DataType.NUMBER
        ),
        new EF(
            'pool',
            true,
            DataType.STRING
        )
    ]);
});

test('flatten function params', () => {
    const abiItem = new SemanticAbi(fileUtil.loadJson('uniswap/abis/FactoryV3.json')).functions.get('a1671295')!;
    const flattener = new ParameterFlattener(abiItem);

    assertFlattenedParameters(flattener, [
        new EF(
            'tokenB',
            true,
            DataType.STRING
        ),
        new EF(
            'fee',
            true,
            DataType.NUMBER
        ),
        new EF(
            'pool',
            false,
            DataType.STRING
        )
    ]);
});

test('flatten tuple', () => {
    const abiItem = new SemanticAbi(fileUtil.loadJson('seaport/abis/Seaport1.5.json')).functions.get('b3a34c4c')!;
    const flattener = new ParameterFlattener(abiItem);

    assertFlattenedParameters(flattener, [
        new EF(
            'offerer',
            true,
            DataType.STRING,
            ['order', 'parameters'],
            'order_parameters_offerer'
        ),
        new EF(
            'orderType',
            true,
            DataType.NUMBER,
            ['order', 'parameters'],
            'order_parameters_orderType'
        ),
        new EF(
            'startTime',
            true,
            DataType.NUMBER,
            ['order', 'parameters'],
            'order_parameters_startTime'
        ),
        new EF(
            'zoneHash',
            true,
            DataType.STRING,
            ['order', 'parameters'],
            'order_parameters_zoneHash'
        ),
        new EF(
            'signature',
            true,
            DataType.STRING,
            ['order'],
            'order_signature'
        ),
        new EF(
            'fulfillerConduitKey',
            true,
            DataType.STRING
        ),
        new EF(
            'fulfilled',
            false,
            DataType.STRING
        )
    ]);
});

test('function with transforms', () => {
    const abiItem = new SemanticAbi(fileUtil.loadJson('seaport/abis/flatten/param_transform.json')).functions.get('b3a34c4c')!;
    const flattener = new ParameterFlattener(abiItem);

    assertFlattenedParameters(flattener, [
        new EF(
            'offerer',
            true,
            DataType.STRING,
            ['order', 'parameters'],
            'orderOfferer'
        ),
        new EF(
            'orderType',
            true,
            DataType.STRING,
            ['order', 'parameters'],
            'order_parameters_orderType'
        ),
        new EF(
            'fulfilled',
            false,
            DataType.STRING,
            [],
            'isFulfilled',
        )
    ]);
});


test('flattened array primitive', () => {
    const abiItem = new SemanticAbi(fileUtil.loadJson('seaport/abis/explode/primitive.json')).functions.get('ed98a574');
    const flattener = new ParameterFlattener(
        abiItem,
        new ExplodeFlattenPredicate(abiItem.properties.explode.get().pathParts)
    );

    assertFlattenedParameters(flattener, [
        new EF(
            'fulfilled',
            false,
            DataType.STRING
        )
    ]);
});

test('flattened array tuple', () => {
    const abiItem = new SemanticAbi(fileUtil.loadJson('seaport/abis/explode/tuple.json')).functions.get('ed98a574');
    const flattener = new ParameterFlattener(
        abiItem,
        new ExplodeFlattenPredicate(abiItem.properties.explode.get().pathParts)
    );

    assertFlattenedParameters(flattener, [
        new EF(
            'offerer',
            true,
            DataType.STRING,
            ['orders', 'parameters'],
            'orders_parameters_offerer',
        ),
        new EF(
            'orderType',
            true,
            DataType.NUMBER,
            ['orders', 'parameters'],
            'orders_parameters_orderType',
        ),
        new EF(
            'startTime',
            true,
            DataType.NUMBER,
            ['orders', 'parameters'],
            'orders_parameters_startTime',
        ),
        new EF(
            'signature',
            true,
            DataType.STRING,
            ['orders'],
            'orders_signature',
        )
    ]);
});

test('flattened array nested tuple', () => {
    const abiItem = new SemanticAbi(fileUtil.loadJson('seaport/abis/explode/nested_tuple.json')).functions.get('00000000');
    const flattener: ParameterFlattener = new ParameterFlattener(
        abiItem,
        new ExplodeFlattenPredicate(abiItem.properties.explode.get().pathParts)
    );

    assertFlattenedParameters(flattener, [
        new EF(
            'amount',
            true,
            DataType.NUMBER,
            ['parameters', 'additionalRecipients'],
            'parameters_additionalRecipients_amount'
        ),
        new EF(
            'recipient',
            true,
            DataType.STRING,
            ['parameters', 'additionalRecipients'],
            'parameters_additionalRecipients_recipient'
        )
    ]);
});