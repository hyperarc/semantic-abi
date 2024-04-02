from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TypedDict, List, Optional, Dict

from semanticabi.abi.Decoded import DecodedTuple
from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.item.AbiItem import AbiItem, AbiEvent, AbiFunction
from semanticabi.abi.item.Explode import TypedExplode, Explode
from semanticabi.abi.item.Expressions import TypedExpression, Expressions
from semanticabi.abi.item.Matches import TypedMatch, Matches, AssertType
from semanticabi.abi.item.SemanticParameter import SemanticParameters
from semanticabi.metadata.EthLog import EthLog
from semanticabi.metadata.EthTraces import EthTrace

IS_PRIMARY_NAME = '@isPrimary'
EXPLODE_NAME = '@explode'
MATCHES_NAME = '@matches'
EXPRESSIONS_NAME = '@expressions'


TypedSemanticAbiItemProperties = TypedDict('TypedSemanticAbiItemProperties', {
    IS_PRIMARY_NAME: bool,
    EXPLODE_NAME: TypedExplode,
    MATCHES_NAME: List[TypedMatch],
    EXPRESSIONS_NAME: List[TypedExpression]
}, total=False)


@dataclass
class SemanticAbiItemProperties:
    # If this is a primary event that will produce a row
    is_primary: bool
    # The set of paths to explode if this is a primary item type
    explode: Optional[Explode]
    # The item matches to try to join with
    matches: Optional[Matches]
    # The expressions to run for each row
    expressions: Optional[Expressions]

    @staticmethod
    def from_json(json: TypedSemanticAbiItemProperties) -> SemanticAbiItemProperties:
        return SemanticAbiItemProperties(
            json.get(IS_PRIMARY_NAME, False),
            Explode.from_json(json[EXPLODE_NAME]) if EXPLODE_NAME in json else None,
            Matches.from_json(json[MATCHES_NAME]) if MATCHES_NAME in json else None,
            Expressions.from_json(json[EXPRESSIONS_NAME]) if EXPRESSIONS_NAME in json else None
        )

    def __post_init__(self):
        if not self.is_primary and (self.explode is not None or self.matches is not None or self.expressions is not None):
            raise InvalidAbiException('Non-primary ABI item may not have "explode", "matches", or "expressions".')

        if self.explode is not None and self.matches is not None:
            for match in self.matches.matches:
                if match.assert_type == AssertType.MANY:
                    raise InvalidAbiException(f'Cannot have a match that asserts "many" and an explode on the same item.')


@dataclass
class DecodedResult:
    """
    Result of decoding an item.
    """
    # The decoded inputs
    inputs: DecodedTuple
    # The decoded outputs, if this item is a function
    outputs: Optional[DecodedTuple]

    @cached_property
    def decoded_input_json(self) -> Dict[str, any]:
        return self.inputs.to_json()

    @cached_property
    def decoded_output_json(self) -> Dict[str, any]:
        if self.outputs is None:
            return {}
        else:
            return self.outputs.to_json()


@dataclass
class SemanticAbiItem(ABC):
    properties: SemanticAbiItemProperties
    input_parameters: SemanticParameters

    def __post_init__(self):
        if self.properties.explode is not None:
            self.properties.explode.validate(self.all_parameters())

    @property
    @abstractmethod
    def raw_item(self) -> AbiItem:
        """
        Returns the original AbiItem
        """
        pass

    @property
    @abstractmethod
    def output_parameters(self) -> Optional[SemanticParameters]:
        pass

    @abstractmethod
    def all_parameters(self) -> List[SemanticParameters]:
        pass

    @abstractmethod
    def decode(self, event_or_trace: EthLog | EthTrace) -> DecodedResult:
        pass


@dataclass
class SemanticAbiEvent(SemanticAbiItem):
    event: AbiEvent

    @staticmethod
    def from_json(json: Dict[str, any]) -> SemanticAbiEvent:
        event: AbiEvent = AbiEvent.from_json(json)
        return SemanticAbiEvent(
            SemanticAbiItemProperties.from_json(json),
            SemanticParameters.from_parameters(event.inputs.parameters(), json['inputs']),
            event
        )

    @property
    def raw_item(self) -> AbiItem:
        return self.event

    def all_parameters(self) -> List[SemanticParameters]:
        return [self.input_parameters]

    @property
    def output_parameters(self) -> Optional[SemanticParameters]:
        return None

    def decode(self, event: EthLog) -> DecodedResult:
        # Can't do isinstance(event, EthLog) because isinstance doesn't work on TypedDicts, which EthLog is
        if isinstance(event, EthTrace):
            raise Exception("Can only decode logs")

        return DecodedResult(
            self.event.decode(event),
            None
        )


@dataclass
class SemanticAbiFunction(SemanticAbiItem):
    function: AbiFunction
    _output_parameters: SemanticParameters

    @staticmethod
    def from_json(json: Dict[str, any]) -> SemanticAbiFunction:
        function: AbiFunction = AbiFunction.from_json(json)
        return SemanticAbiFunction(
            SemanticAbiItemProperties.from_json(json),
            SemanticParameters.from_parameters(function.inputs.parameters(), json['inputs']),
            function,
            SemanticParameters.from_parameters(function.outputs.parameters(), json['outputs'])
        )

    def __post_init__(self):
        super().__post_init__()

        top_level_input_parameter_names = set(self.input_parameters.parameters().keys())
        top_level_output_parameter_names = set(self.output_parameters.parameters().keys())

        # TODO ZZ I think this compares the raw parameter names which won't account for renames that would prevent dupes
        duplicate_names = top_level_input_parameter_names.intersection(top_level_output_parameter_names)
        if len(duplicate_names) > 0:
            duplicate_names_str = ', '.join(duplicate_names)
            raise InvalidAbiException(f'Parameters are duplicated in inputs and outputs: {duplicate_names_str}')

    @property
    def raw_item(self) -> AbiItem:
        return self.function

    def all_parameters(self) -> List[SemanticParameters]:
        return [self.input_parameters, self._output_parameters]

    @property
    def output_parameters(self) -> Optional[SemanticParameters]:
        return self._output_parameters

    def decode(self, trace: EthTrace) -> DecodedResult:
        if not isinstance(trace, EthTrace):
            raise Exception("Can only decode traces")

        output = trace.output
        decoded_output = None
        # output is only valid and non-empty if more than 2 characters since the first 2 are 0x
        if output is not None and len(output) > 2:
            decoded_output = self.function.decode_output(output)

        return DecodedResult(
            self.function.decode(trace.input),
            decoded_output
        )
