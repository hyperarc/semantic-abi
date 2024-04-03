import unittest

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.item.Matches import Match, EqualMatch, BoundMatch, ExactInSetMatch, Matches, MatchItemType, \
    AssertType


class MatchTest(unittest.TestCase):
    def test_equal_match(self):
        assert Match.parse_predicate({
            'type': 'equal',
            'source': 'from',
            'matched': 'from'
        }) == EqualMatch('from', 'from')

    def test_bound_match(self):
        assert Match.parse_predicate({
            'type': 'bound',
            'source': 'to',
            'matched': 'to',
            'lower': 0.5,
            'upper': 1.5
        }) == BoundMatch('to', 'to', 0.5, 1.5)

    def test_bound_match_lower_only(self):
        assert Match.parse_predicate({
            'type': 'bound',
            'source': 'to',
            'matched': 'to',
            'lower': 0.5
        }) == BoundMatch('to', 'to', 0.5, None)

    def test_exact_in_set_match(self):
        assert Match.parse_predicate({
            'type': 'in',
            'source': 'from',
            'matched': ['from', 'to']
        }) == ExactInSetMatch('from', {'from', 'to'})

    def test_invalid_match_type(self):
        with self.assertRaises(InvalidAbiException):
            Match.parse_predicate({
                'type': 'invalid',
                'source': 'from',
                'matched': 'from'
            })

    def test_invalid_bound_match_missing_bounds(self):
        with self.assertRaises(InvalidAbiException):
            Match.parse_predicate({
                'type': 'bound',
                'source': 'to',
                'matched': 'to'
            })

    def test_invalid_bound_match_lower_greater_than_upper(self):
        with self.assertRaises(InvalidAbiException):
            Match.parse_predicate({
                'type': 'bound',
                'source': 'to',
                'matched': 'to',
                'lower': 1.5,
                'upper': 0.5
            })

    def test_invalid_match_no_signature(self):
        with self.assertRaises(InvalidAbiException):
            Match.from_json({
                'type': 'event',
                'prefix': 'prefix',
                'assert': 'onlyOne',
                'predicates': [
                    {
                        'type': 'equal',
                        'source': 'from',
                        'matched': 'from'
                    }
                ]
            })

    def test_invalid_multiple_many_matches(self):
        with self.assertRaises(InvalidAbiException):
            Matches.from_json([
                {
                    'type': 'event',
                    'signature': 'sig1',
                    'prefix': 'blah',
                    'assert': 'many',
                    'predicates': []
                },
                {
                    'type': 'event',
                    'signature': 'sig2',
                    'prefix': 'blah2',
                    'assert': 'many',
                    'predicates': []
                }
            ])

    def test_invalid_multiple_same_prefix(self):
        with self.assertRaises(InvalidAbiException):
            Matches.from_json([
                {
                    'type': 'event',
                    'signature': 'sig1',
                    'prefix': 'prefix',
                    'assert': 'onlyOne',
                    'predicates': []
                },
                {
                    'type': 'event',
                    'signature': 'sig1',
                    'prefix': 'prefix',
                    'assert': 'onlyOne',
                    'predicates': []
                }
            ])

    def test_transfer_match(self):
        assert Match.from_json({
            'type': 'transfer',
            'prefix': 'prefix',
            'assert': 'onlyOne',
            'predicates': [
                {
                    'type': 'equal',
                    'source': 'from',
                    'matched': 'from'
                }
            ]
        }) == Match(None, MatchItemType.TRANSFER, 'prefix', AssertType.ONLY_ONE, [EqualMatch('from', 'from')])
