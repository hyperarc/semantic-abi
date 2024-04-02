from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List, Set, TypedDict

from semanticabi.abi.InvalidAbiException import InvalidAbiException


class MatchItemType(Enum):
    """
    The type of abi item to match
    """

    # Match an event
    EVENT = 'event'
    # Match a function
    FUNCTION = 'function'
    # Special type to match against a transfer-type of event that has a fromAddress, toAddress, and value
    TRANSFER = 'transfer'


class AssertType(Enum):
    """
    The type of assertion to make after applying the predicates to the candidate items.
    """

    # Assert that there is exactly one match
    ONLY_ONE = 'onlyOne'
    # Assert that there is at least one match
    MANY = 'many'
    # Assert that there is either 0 or 1 match
    OPTIONAL_ONE = 'optionalOne'


class TypedPredicate(TypedDict):
    type: str


class TypedEqualPredicate(TypedPredicate):
    source: str
    matched: str


class TypedBoundPredicate(TypedPredicate):
    source: str
    matched: str
    lower: Optional[float]
    upper: Optional[float]


class TypedExactInSetPredicate(TypedPredicate):
    source: str
    matched: List[str]


class MatchType(ABC):
    @abstractmethod
    def matches(self, source_row: Dict[str, any], matched_row: Dict[str, any]) -> bool:
        """
        Returns True if the source_row matches the matched_row for this particular type of match
        """
        pass

    @abstractmethod
    def source_column_names(self) -> Set[str]:
        """
        Returns the set of source column names that are used by this match type
        """
        pass

    @abstractmethod
    def matched_column_names(self) -> Set[str]:
        """
        Returns the set of matched column names that are used by this match type
        """
        pass


@dataclass
class EqualMatch(MatchType):
    """
    Matches the exact value.
    """

    @staticmethod
    def from_json(json: TypedEqualPredicate) -> EqualMatch:
        return EqualMatch(
            json['source'],
            json['matched']
        )

    source: str
    matched: str

    def matches(self, source_row: Dict[str, any], matched_row: Dict[str, any]) -> bool:
        return source_row[self.source] == matched_row[self.matched]

    def source_column_names(self) -> Set[str]:
        return {self.source}

    def matched_column_names(self) -> Set[str]:
        return {self.matched}


@dataclass
class BoundMatch(MatchType):
    """
    Matches the value within the specified bounds
    """

    @staticmethod
    def from_json(json: TypedBoundPredicate) -> BoundMatch:
        return BoundMatch(
            json['source'],
            json['matched'],
            json.get('lower'),
            json.get('upper')
        )

    source: str
    matched: str
    lower: Optional[float]
    upper: Optional[float]

    def __post_init__(self):
        if self.lower is None and self.upper is None:
            raise InvalidAbiException('Bound match must specify at least one of "lower" or "upper"')

        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise InvalidAbiException('Bound match "lower" must be less than "upper"')

    def matches(self, source_row: Dict[str, any], matched_row: Dict[str, any]) -> bool:
        value = source_row[self.source]
        matched_value = matched_row[self.matched]

        if self.lower is not None and matched_value < self.lower * value:
            return False

        if self.upper is not None and matched_value > self.upper * value:
            return False

        return True

    def source_column_names(self) -> Set[str]:
        return {self.source}

    def matched_column_names(self) -> Set[str]:
        return {self.matched}


@dataclass
class ExactInSetMatch(MatchType):
    """
    Matches the source value if found in the set of matched values.
    """

    @staticmethod
    def from_json(json: TypedExactInSetPredicate) -> ExactInSetMatch:
        return ExactInSetMatch(
            json['source'],
            set(json['matched'])
        )

    source: str
    matched: Set[str]

    def matches(self, source_row: Dict[str, any], matched_row: Dict[str, any]) -> bool:
        value = source_row[self.source]
        for matched_column in self.matched:
            if matched_row[matched_column] == value:
                return True

        return False

    def source_column_names(self) -> Set[str]:
        return {self.source}

    def matched_column_names(self) -> Set[str]:
        return self.matched


TypedMatchBase = TypedDict('TypedMatchBase', {
    'type': str,
    'prefix': str,
    'assert': str,
    'predicates': List[TypedPredicate]
})


class TypedMatch(TypedMatchBase, total=False):
    # signature is optional, as it is not needed for a type = "transfer"
    signature: str


@dataclass
class Match:
    """
    Defines the match criteria for a row.
    """

    @staticmethod
    def from_json(json: TypedMatch) -> Match:
        try:
            match_item_type = MatchItemType(json['type'])
        except ValueError:
            raise InvalidAbiException(f'Invalid value for "type": {json["type"]}')

        try:
            assert_type = AssertType(json['assert'])
        except ValueError:
            raise InvalidAbiException(f'Invalid value for "assert": {json["assert"]}')

        return Match(
            json.get('signature'),
            match_item_type,
            json['prefix'],
            assert_type,
            [Match.parse_predicate(predicate) for predicate in json['predicates']]
        )

    @staticmethod
    def parse_predicate(json: TypedPredicate) -> MatchType:
        predicate_type = json['type']
        if predicate_type == 'equal':
            return EqualMatch.from_json(json)
        elif predicate_type == 'bound':
            return BoundMatch.from_json(json)
        elif predicate_type == 'in':
            return ExactInSetMatch.from_json(json)
        else:
            raise InvalidAbiException(f'Unknown predicate type: {predicate_type}')

    signature: Optional[str]
    type: MatchItemType
    prefix: str
    assert_type: AssertType
    predicates: List[MatchType]

    def __post_init__(self):
        if self.signature is None and self.type != MatchItemType.TRANSFER:
            raise InvalidAbiException('Match must specify "signature" unless it is a "transfer" match')

    def make_prefixed_column_name(self, name: str) -> str:
        """
        Return the column name with the match's prefix prepended
        """
        return f'{self.prefix}_{name}'


@dataclass
class Matches:
    """
    The list of matches to apply to each row.
    """

    @staticmethod
    def from_json(json: List[Dict[str, any]]) -> Matches:
        return Matches([Match.from_json(match) for match in json])

    matches: List[Match]

    def __post_init__(self):
        has_many_assert = False
        for match in self.matches:
            if match.assert_type == AssertType.MANY:
                if has_many_assert:
                    raise InvalidAbiException('Cannot have multiple matches that assert "many"')
                has_many_assert = True

        prefixes_by_signature: Dict[str, Set[str]] = {}
        for match in self.matches:
            if match.signature is not None:
                if match.signature not in prefixes_by_signature:
                    prefixes_by_signature[match.signature] = set()

                if match.prefix in prefixes_by_signature[match.signature]:
                    raise InvalidAbiException(f'Cannot have multiple matches of the same signature \'{match.signature}\' with the same prefix \'{match.prefix}\'')

                prefixes_by_signature[match.signature].add(match.prefix)
