import unittest

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiEvent, SemanticAbiFunction
from semanticabi.abi.item.DataType import DataType
from semanticabi.abi.item.Matches import Match, AssertType, EqualMatch, MatchType, BoundMatch, MatchItemType
from semanticabi.metadata.EvmChain import EvmChain


class SemanticAbiTest(unittest.TestCase):
    def test_valid_abi(self):
        abi_json = {
            "metadata": {
                "chains": [
                    "ethereum"
                ],
                "contractAddresses": [
                    "0x1234567890123456789012345678901234567890"
                ],
                "expressions": [
                    {
                        "name": "someExpr",
                        "expression": "some expression",
                        "type": "string"
                    }
                ]
            },
            "abi": [
                {
                    "name": "Transfer",
                    "type": "event",
                    "@isPrimary": True,
                    "@explode": {
                        "paths": [
                            "value"
                        ]
                    },
                    "@matches": [
                        {
                            "signature": "someFunction(address)",
                            "type": "function",
                            "prefix": "prefix",
                            "assert": "onlyOne",
                            "predicates": [
                                {
                                    "type": "equal",
                                    "source": "from",
                                    "matched": "from"
                                },
                                {
                                    "type": "bound",
                                    "source": "to",
                                    "matched": "to",
                                    "lower": 0.5,
                                    "upper": 1.5
                                }
                            ]
                        }
                    ],
                    "@expressions": [
                        {
                            "name": "someExpr",
                            "expression": "some expression",
                            "type": "string"
                        }
                    ],
                    "inputs": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        },
                        {
                            "internalType": "address",
                            "name": "to",
                            "type": "address"
                        },
                        {
                            "internalType": "uint256[]",
                            "name": "value",
                            "type": "uint256[]"
                        }
                    ],
                },
                {
                    "name": "someFunction",
                    "type": "function",
                    "inputs": [
                        {
                            "internalType": "address",
                            "name": "other",
                            "type": "address"
                        }
                    ],
                    "outputs": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        }
                    ]
                }
            ]
        }

        abi = SemanticAbi(abi_json)

        assert abi.chains == {EvmChain.ETHEREUM}
        assert abi.contract_addresses == {'0x1234567890123456789012345678901234567890'}
        assert len(abi.expressions.expressions) == 1

        assert len(abi.events_by_hash) == 1
        assert len(abi.functions_by_hash) == 1

        abi_event: SemanticAbiEvent = list(abi.events_by_hash.values())[0]
        assert abi_event.event.name == 'Transfer'
        assert abi_event.properties.is_primary
        assert len(abi_event.event.inputs.parameters()) == 3
        assert len(abi_event.properties.explode.paths) == 1
        assert abi_event.properties.explode.paths[0] == 'value'

        assert len(abi_event.properties.matches.matches) == 1
        match: Match = abi_event.properties.matches.matches[0]
        assert match.signature == 'someFunction(address)'
        assert match.type == MatchItemType.FUNCTION
        assert match.prefix == 'prefix'
        assert match.assert_type == AssertType.ONLY_ONE
        assert len(match.predicates) == 2

        exact_match: MatchType = match.predicates[0]
        assert isinstance(exact_match, EqualMatch)
        assert exact_match.source == 'from'
        assert exact_match.matched == 'from'

        bound_match: MatchType = match.predicates[1]
        assert isinstance(bound_match, BoundMatch)
        assert bound_match.source == 'to'
        assert bound_match.matched == 'to'
        assert bound_match.lower == 0.5
        assert bound_match.upper == 1.5

        assert len(abi_event.properties.expressions.expressions) == 1
        expression = abi_event.properties.expressions.expressions[0]
        assert expression.name == 'someExpr'
        assert expression.expression == 'some expression'
        assert expression.type == DataType.STRING

        abi_func: SemanticAbiFunction = list(abi.functions_by_hash.values())[0]
        assert abi_func.function.name == 'someFunction'
        assert not abi_func.properties.is_primary
        assert len(abi_func.function.inputs.parameters()) == 1
        assert len(abi_func.function.outputs.parameters()) == 1

    def test_invalid_abi_no_chains(self):
        abi_json = {
            "metadata": {
                "contractAddresses": [
                    "0x1234567890123456789012345678901234567890"
                ],
                "chains": []
            },
            "abi": []
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbi(abi_json)

    def test_invalid_abi_no_primary_items(self):
        abi_json = {
            "metadata": {
                "contractAddresses": [],
                "chains": [
                    "ethereum"
                ]
            },
            "abi": [
                {
                    "name": "someFunction",
                    "type": "function",
                    "inputs": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        }
                    ],
                    "outputs": [
                        {
                            "internalType": "address",
                            "name": "to",
                            "type": "address"
                        }
                    ]
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbi(abi_json)

    def test_invalid_abi_match_unknown_event(self):
        abi_json = {
            "metadata": {
                "contractAddresses": [],
                "chains": [
                    "ethereum"
                ]
            },
            "abi": [
                {
                    "name": "someFunction",
                    "type": "function",
                    "@isPrimary": True,
                    "inputs": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        }
                    ],
                    "outputs": [
                        {
                            "internalType": "address",
                            "name": "to",
                            "type": "address"
                        }
                    ],
                    "@matches": [
                        {
                            "signature": "someEvent(address)",
                            "type": "event",
                            "prefix": "prefix",
                            "assert": "onlyOne",
                            "predicates": []
                        }
                    ]
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbi(abi_json)

    def test_invalid_abi_match_unknown_function(self):
        abi_json = {
            "metadata": {
                "contractAddresses": [],
                "chains": [
                    "ethereum"
                ]
            },
            "abi": [
                {
                    "name": "someEvent",
                    "type": "event",
                    "@isPrimary": True,
                    "inputs": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        }
                    ],
                    "@matches": [
                        {
                            "signature": "someFunction(address)",
                            "type": "function",
                            "prefix": "prefix",
                            "assert": "onlyOne",
                            "predicates": []
                        }
                    ]
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbi(abi_json)

    def test_invalid_abi_same_match_prefix_tuple_name(self):
        abi_json = {
            "metadata": {
                "contractAddresses": [],
                "chains": [
                    "ethereum"
                ]
            },
            "abi": [
                {
                    "name": "someEvent",
                    "type": "event",
                    "@isPrimary": True,
                    "inputs": [
                        {
                            "internalType": "tuple",
                            "name": "from",
                            "type": "tuple",
                            "components": [
                                {
                                    "internalType": "address",
                                    "name": "blah",
                                    "type": "address"
                                }
                            ]
                        }
                    ],
                    "@matches": [
                        {
                            "signature": "someOtherEvent(address)",
                            "type": "event",
                            "prefix": "from",
                            "assert": "onlyOne",
                            "predicates": []
                        }
                    ]
                },
                {
                    "name": "someOtherEvent",
                    "type": "event",
                    "inputs": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        }
                    ]
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbi(abi_json)

    def test_invalid_abi_item_matches_self(self):
        abi_json = {
            "metadata": {
                "contractAddresses": [],
                "chains": [
                    "ethereum"
                ]
            },
            "abi": [
                {
                    "name": "someEvent",
                    "type": "event",
                    "@isPrimary": True,
                    "inputs": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        }
                    ],
                    "@matches": [
                        {
                            "signature": "someEvent(address)",
                            "type": "event",
                            "prefix": "prefix",
                            "assert": "onlyOne",
                            "predicates": []
                        }
                    ]
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbi(abi_json)
