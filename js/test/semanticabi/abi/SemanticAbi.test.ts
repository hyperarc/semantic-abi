import {SemanticAbi} from 'semanticabi/abi/SemanticAbi';
import {EvmChain} from 'semanticabi/metadata/EvmChain';
import {SemanticAbiEvent} from 'semanticabi/abi/item/semantic/SemanticAbiEvent';
import {MatchType} from "semanticabi/abi/item/semantic/MatchType";
import {MatchCardinality} from "semanticabi/abi/item/semantic/MatchCardinality";
import {EqualMatchPredicate} from "semanticabi/abi/item/semantic/EqualMatchPredicate";
import {BoundMatchPredicate} from "semanticabi/abi/item/semantic/BoundMatchPredicate";
import {SemanticAbiFunction} from "semanticabi/abi/item/semantic/SemanticAbiFunction";

test('valid', () => {
    const abi = new SemanticAbi({
        'metadata': {
            'chains': [
                'ethereum'
            ],
            'contractAddresses': [
                '0x1234567890123456789012345678901234567890'
            ],
            'expressions': [
                {
                    'name': 'someExpr',
                    'expression': 'some expression',
                    'type': 'string'
                }
            ]
        },
        'abi': [
            {
                'name': 'Transfer',
                'type': 'event',
                '@isPrimary': true,
                '@explode': {
                    'paths': [
                        'some.path.to.something'
                    ]
                },
                '@matches': [
                    {
                        'signature': 'someFunction(address)',
                        'type': 'function',
                        'prefix': 'prefix',
                        'assert': 'onlyOne',
                        'predicates': [
                            {
                                'type': 'equal',
                                'source': 'fromS',
                                'matched': 'fromM'
                            },
                            {
                                'type': 'bound',
                                'source': 'toS',
                                'matched': 'toM',
                                'lower': 0.5,
                                'upper': 1.5
                            }
                        ]
                    }
                ],
                '@expressions': [
                    {
                        'name': 'someExpr',
                        'expression': 'some expression',
                        'type': 'string'
                    }
                ],
                'inputs': [
                    {
                        'internalType': 'address',
                        'name': 'from',
                        'type': 'address'
                    },
                    {
                        'internalType': 'address',
                        'name': 'to',
                        'type': 'address'
                    },
                    {
                        'internalType': 'uint256[]',
                        'name': 'value',
                        'type': 'uint256[]'
                    }
                ],
            },
            {
                'name': 'someFunction',
                'type': 'function',
                'inputs': [
                    {
                        'internalType': 'address',
                        'name': 'other',
                        'type': 'address'
                    }
                ],
                'outputs': [
                    {
                        'internalType': 'address',
                        'name': 'from',
                        'type': 'address'
                    }
                ]
            }
        ]
    });

    expect(abi.chains).toEqual(new Set([EvmChain.ETHEREUM]));
    expect(abi.contractAddresses).toEqual(new Set(['0x1234567890123456789012345678901234567890']));

    // TODO ZZ assert expressions
    //expect(abi.expressions.expressions).toBe(1);
    expect(abi.events.size).toBe(1);
    expect(abi.functions.size).toBe(1);

    const abiEvent: SemanticAbiEvent = abi.events.values().next().value;
    expect(abiEvent.rawItem.name).toBe('Transfer');
    expect(abiEvent.properties.isPrimary).toBeTruthy();
    expect(abiEvent.rawItem.inputs.parameters().length).toBe(3);
    expect(abiEvent.properties.explode.get().paths.length).toBe(1);
    expect(abiEvent.properties.explode.get().pathParts.get('some.path.to.something'))
        .toStrictEqual(['some', 'path', 'to', 'something']);

    const match = abiEvent.properties.matches.get().matches[0];
    expect(match.signature.get()).toBe('someFunction(address)');
    expect(match.type).toBe(MatchType.FUNCTION);
    expect(match.prefix).toBe('prefix');
    expect(match.cardinality).toBe(MatchCardinality.ONLY_ONE);
    expect(match.predicates.length).toBe(2);

    const exactMatch = match.predicates[0] as EqualMatchPredicate;
    // Assuming there's a way to check the instance type
    expect(exactMatch instanceof EqualMatchPredicate).toBeTruthy();
    expect(exactMatch.sourceColumnNames).toEqual(new Set(['fromS']));
    expect(exactMatch.matchedColumnNames).toEqual(new Set(['fromM']));

    const boundMatch = match.predicates[1] as BoundMatchPredicate;
    // Assuming there's a way to check the instance type
    expect(boundMatch instanceof BoundMatchPredicate).toBeTruthy();
    expect(boundMatch.sourceColumnNames).toEqual(new Set(['toS']));
    expect(boundMatch.matchedColumnNames).toEqual(new Set(['toM']));
    expect(boundMatch.lower).toBe(0.5);
    expect(boundMatch.upper).toBe(1.5);

    const abiFunction = abi.functions.values().next().value as SemanticAbiFunction;
    expect(abiFunction.rawItem.name).toBe('someFunction');
    expect(abiFunction.properties.isPrimary).toBeFalsy();
    expect(abiFunction.rawItem.inputs.parameters().length).toBe(1);
    expect(abiFunction.rawItem.outputs.parameters().length).toBe(1);
});