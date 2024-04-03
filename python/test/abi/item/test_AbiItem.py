import unittest

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.item.DataType import DataType
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiEvent, SemanticAbiFunction


class AbiItem(unittest.TestCase):
    def test_invalid_parameter_name(self):
        item_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiFunction.from_json(item_json)

    def test_invalid_non_primary_abi_explode(self):
        item_json = {
            "name": "Transfer",
            "type": "event",
            "@isPrimary": False,
            "@explode": {
                "paths": [
                    "value"
                ]
            },
            "inputs": [
                {
                    "internalType": "address",
                    "name": "from",
                    "type": "address"
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(item_json)

    def test_invalid_non_primary_abi_matches(self):
        item_json = {
            "name": "Transfer",
            "type": "event",
            "@isPrimary": False,
            "@matches": [
                {
                    "name": "someFunc",
                    "type": "function",
                    "prefix": "prefix",
                    "assert": "onlyone",
                    "predicates": [
                        {
                            "type": "exact",
                            "source": "from",
                            "matched": "from"
                        }
                    ]
                }
            ],
            "inputs": [
                {
                    "internalType": "address",
                    "name": "from",
                    "type": "address"
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(item_json)

    def test_invalid_non_primary_abi_expressions(self):
        abi_json = {
            "name": "Transfer",
            "type": "event",
            "@isPrimary": False,
            "@expressions": [
                {
                    "name": "someExpr",
                    "expression": "some expression"
                }
            ],
            "inputs": [
                {
                    "internalType": "address",
                    "name": "from",
                    "type": "address"
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)

    def test_invalid_tuple_input_with_transforms(self):
        abi_json = {
            "name": "Transfer",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "tuple",
                    "components": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        }
                    ],
                    "@transform": {
                        "name": "someName"
                    }
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)

    def test_event(self):
        abi_json = {
            "name": "Transfer",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address"
                },
                {
                    "name": "to",
                    "type": "address",
                    "@exclude": True
                },
                {
                    "name": "value",
                    "type": "uint256",
                    "@transform": {
                        "name": "someName",
                        "expression": "1 * this",
                        "type": "string"
                    }
                },
                {
                    "name": "blah",
                    "type": "tuple",
                    "components": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        },
                        {
                            "internalType": "uint256",
                            "name": "value",
                            "type": "uint256"
                        }
                    ]
                }
            ],
        }

        abi_item = SemanticAbiEvent.from_json(abi_json)

        self.assertEqual(abi_item.raw_item.name, 'Transfer')
        self.assertEqual(abi_item.input_parameters.parameter('from').exclude, False)
        self.assertEqual(abi_item.input_parameters.parameter('from').transform, None)
        self.assertEqual(abi_item.input_parameters.parameter('from').components, None)
        self.assertEqual(abi_item.input_parameters.parameter('to').exclude, True)
        self.assertEqual(abi_item.input_parameters.parameter('value').exclude, False)
        self.assertEqual(abi_item.input_parameters.parameter('value').transform.name, 'someName')
        self.assertEqual(abi_item.input_parameters.parameter('value').transform.expression, '1 * this')
        self.assertEqual(abi_item.input_parameters.parameter('value').transform.type, DataType.STRING)
        self.assertEqual(abi_item.input_parameters.parameter('blah').components.parameter('from').exclude, False)
        self.assertEqual(abi_item.input_parameters.parameter('blah').components.parameter('value').exclude, False)

    def test_function(self):
        abi_json = {
            "name": "someFunction",
            "type": "function",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address"
                }
            ],
            "outputs": [
                {
                    "name": "other",
                    "type": "address",
                    "@transform": {
                        "name": "someName",
                        "expression": "'a' || this",
                        "type": "string"
                    }
                },
                {
                    "name": "to",
                    "type": "address",
                    "@exclude": True
                },
                {
                    "name": "blah",
                    "type": "tuple",
                    "components": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        }
                    ]
                }
            ],
        }

        abi_item = SemanticAbiFunction.from_json(abi_json)

        self.assertEqual(abi_item.raw_item.name, 'someFunction')
        self.assertEqual(abi_item.input_parameters.parameter('from').exclude, False)
        self.assertEqual(abi_item.input_parameters.parameter('from').transform, None)
        self.assertEqual(abi_item.input_parameters.parameter('from').components, None)
        self.assertEqual(abi_item.output_parameters.parameter('other').exclude, False)
        self.assertEqual(abi_item.output_parameters.parameter('other').transform.name, 'someName')
        self.assertEqual(abi_item.output_parameters.parameter('other').transform.expression, "'a' || this")
        self.assertEqual(abi_item.output_parameters.parameter('other').transform.type, DataType.STRING)
        self.assertEqual(abi_item.output_parameters.parameter('other').components, None)
        self.assertEqual(abi_item.output_parameters.parameter('to').exclude, True)
        self.assertEqual(abi_item.output_parameters.parameter('blah').components.parameter('from').exclude, False)

    def test_explode_path_not_found(self):
        abi_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address"
                }
            ],
            "@explode": {
                "paths": [
                    "blah"
                ]
            }
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)

    def test_explode_path_not_array(self):
        abi_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address"
                }
            ],
            "@explode": {
                "paths": [
                    "from"
                ]
            }
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)

    def test_explode_path_excluded(self):
        abi_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address",
                    "@exclude": True
                }
            ],
            "@explode": {
                "paths": [
                    "from"
                ]
            }
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)

    def test_explode_path_not_array_of_arrays(self):
        abi_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address[][]"
                }
            ],
            "@explode": {
                "paths": [
                    "from"
                ]
            }
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)

    def test_explode_path_nested_arrays(self):
        abi_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "tuple[]",
                    "components": [
                        {
                            "name": "addr",
                            "type": "address[]"
                        }
                    ]
                }
            ],
            "@explode": {
                "paths": [
                    "from.addr"
                ]
            }
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)

    def test_explode(self):
        abi_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address"
                },
                {
                    "name": "blah",
                    "type": "tuple",
                    "components": [
                        {
                            "internalType": "address",
                            "name": "from",
                            "type": "address"
                        },
                        {
                            "internalType": "uint256[]",
                            "name": "value",
                            "type": "uint256[]"
                        }
                    ]
                },
                {
                    "name": "value",
                    "type": "uint256[]"
                }
            ],
            "@explode": {
                "paths": [
                    "blah.value",
                    "value"
                ]
            }
        }

        abi_item = SemanticAbiEvent.from_json(abi_json)

        self.assertEqual(abi_item.raw_item.name, 'someEvent')

    def test_explode_output_field(self):
        abi_json = {
            "name": "someFunction",
            "type": "function",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address"
                }
            ],
            "outputs": [
                {
                    "name": "value",
                    "type": "uint256[]"
                }
            ],
            "@explode": {
                "paths": [
                    "value"
                ]
            }
        }

        abi_item = SemanticAbiFunction.from_json(abi_json)

        self.assertEqual(abi_item.raw_item.name, 'someFunction')

    def test_duplicate_input_parameters(self):
        abi_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "from",
                    "type": "address"
                },
                {
                    "name": "from",
                    "type": "address"
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)

    def test_duplicate_output_parameters(self):
        abi_json = {
            "name": "someFunction",
            "type": "function",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "to",
                    "type": "address"
                }
            ],
            "outputs": [
                {
                    "name": "from",
                    "type": "address"
                },
                {
                    "name": "from",
                    "type": "address"
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiFunction.from_json(abi_json)

    def test_duplicate_input_and_output_parameters(self):
        abi_json = {
            "name": "someFunction",
            "type": "function",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "to",
                    "type": "address"
                },
                {
                    "name": "from",
                    "type": "address"
                }
            ],
            "outputs": [
                {
                    "name": "from",
                    "type": "address"
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiFunction.from_json(abi_json)

    def test_parameter_invalid_expression_columns(self):
        abi_json = {
            "name": "someEvent",
            "type": "event",
            "@isPrimary": True,
            "inputs": [
                {
                    "name": "count",
                    "type": "int8",
                    "@transform": {
                        "expression": "a + b",
                        "type": "int"
                    }
                }
            ]
        }

        with self.assertRaises(InvalidAbiException):
            SemanticAbiEvent.from_json(abi_json)
