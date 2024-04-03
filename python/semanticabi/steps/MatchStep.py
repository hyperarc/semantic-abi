from __future__ import annotations
from typing import Tuple, List, Dict

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.item.Matches import Match, AssertType, MatchItemType
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem
from semanticabi.common.TransformException import TransformException
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.FlattenParametersStep import FlattenParametersStep
from semanticabi.steps.InitStep import InitStep
from semanticabi.steps.Step import Step, TransformItem
from semanticabi.steps.SubsequentStep import SubsequentStep
from semanticabi.steps.TokenTransferStep import TokenTransferStep


class AbiMatchSteps:
    """
    A precomputed collection of steps for use in a MatchStep so that if there are multiple matches against the same
    item, we only generate the step for that item once. Each matched item simply just flattens the parameters
    and does not include any transform error to avoid appending additional transform error columns
    """
    _event_match_steps_by_signature: Dict[str, Step]
    _function_match_steps_by_signature: Dict[str, Step]

    @staticmethod
    def from_abi(abi: SemanticAbi, primary_items: List[SemanticAbiItem]) -> AbiMatchSteps:
        event_match_steps_by_signature: Dict[str, Step] = {}
        function_match_steps_by_signature: Dict[str, Step] = {}

        for item in primary_items:
            if item.properties.matches is not None:
                for match in item.properties.matches.matches:
                    if match.type == MatchItemType.EVENT and match.signature not in event_match_steps_by_signature:
                        event_match_steps_by_signature[match.signature] = FlattenParametersStep(InitStep(abi, abi.events_by_signature[match.signature]))
                    elif match.type == MatchItemType.FUNCTION and match.signature not in function_match_steps_by_signature:
                        function_match_steps_by_signature[match.signature] = FlattenParametersStep(InitStep(abi, abi.functions_by_signature[match.signature]))

        return AbiMatchSteps(event_match_steps_by_signature, function_match_steps_by_signature)

    def __init__(self, event_match_steps_by_signature: Dict[str, Step], function_match_steps_by_signature: Dict[str, Step]):
        self._event_match_steps_by_signature = event_match_steps_by_signature
        self._function_match_steps_by_signature = function_match_steps_by_signature

    def steps_for_match_list(self, matches: List[Match]) -> List[Tuple[Match, Step]]:
        """
        Builds a list of steps for the set of matches that can be passed into MatchStep
        """
        matches_and_steps: List[Tuple[Match, Step]] = []
        for match in matches:
            match match.type:
                case MatchItemType.EVENT:
                    matched_step = self._event_match_steps_by_signature.get(match.signature)
                    matches_and_steps.append((match, matched_step))
                case MatchItemType.FUNCTION:
                    matched_step = self._function_match_steps_by_signature.get(match.signature)
                    matches_and_steps.append((match, matched_step))
                case MatchItemType.TRANSFER:
                    matches_and_steps.append((match, TokenTransferStep()))
        return matches_and_steps


class MatchStep(SubsequentStep):
    """
    Step that "joins" the current item with other items based on the match predicates
    """
    _matches_and_steps: List[Tuple[Match, Step]]
    _schema: AbiSchema

    def __init__(self, previous_step: Step, matches_and_steps: List[Tuple[Match, Step]]):
        super().__init__(previous_step)
        self._matches_and_steps = matches_and_steps
        self._schema = MatchStep._build_schema(previous_step.schema, matches_and_steps)

    @staticmethod
    def _build_schema(previous_schema: AbiSchema, matches_and_steps: List[Tuple[Match, Step]]) -> AbiSchema:
        new_schema = previous_schema
        for match, step in matches_and_steps:
            MatchStep._validate_predicates(match, new_schema, step.schema)
            new_schema = new_schema.append_schema_with_rename(step.schema, match.make_prefixed_column_name)

        return new_schema

    @staticmethod
    def _validate_predicates(match: Match, source_schema: AbiSchema, matched_schema: AbiSchema) -> None:
        for predicate in match.predicates:
            for source_column_name in predicate.source_column_names():
                if not source_schema.has_column(source_column_name):
                    raise InvalidAbiException(f'Unknown source column referenced in match predicate of prefix \'{match.prefix}\': {source_column_name}')

            for matched_column_name in predicate.matched_column_names():
                if not matched_schema.has_column(matched_column_name):
                    raise InvalidAbiException(f'Unknown matched column referenced in match predicate of prefix \'{match.prefix}\': {matched_column_name}')

    @property
    def schema(self) -> AbiSchema:
        return self._schema

    def _should_transform(self):
        return self._abi_item.properties.matches is not None

    def _inner_transform_item(
        self,
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previous_data: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        current_data: List[Dict[str, any]] = previous_data
        for item_match, step in self._matches_and_steps:
            # Sanity check that we aren't getting into combinatorics
            if item_match.assert_type == AssertType.MANY and len(current_data) > 1:
                raise TransformException('Only a single row of data can be matched with a "many" match')

            # Get the decoded data for the items to match against
            transformed_match_rows: List[Dict[str, any]] = step.transform(block, transaction)
            next_data: List[Dict[str, any]] = []
            for row in current_data:
                matched_rows: List[Dict[str, any]] = []

                for transformed_match_row in transformed_match_rows:
                    is_matched: bool = True
                    for predicate in item_match.predicates:
                        if not predicate.matches(row, transformed_match_row):
                            is_matched = False
                            break

                    # Collect the rows that match all of the predicates
                    if is_matched:
                        matched_rows.append(transformed_match_row)

                next_data += MatchStep._handle_matches(row, matched_rows, item_match, step)

            # Use the updated data for the next match
            current_data = next_data

        return current_data

    @staticmethod
    def _handle_matches(
        data: Dict[str, any],
        matched_rows: List[Dict[str, any]],
        item_match: Match,
        step: Step
    ) -> List[Dict[str, any]]:
        updated_data: List[Dict[str, any]] = []
        match item_match.assert_type:
            case AssertType.ONLY_ONE:
                if len(matched_rows) == 0:
                    raise MatchStep._match_assert_error(f'No match found for \'onlyOne\' match', item_match)
                elif len(matched_rows) > 1:
                    raise MatchStep._match_assert_error('Multiple matches found for \'onlyOne\' match', item_match)

                MatchStep._append_matched_data(data, matched_rows[0], item_match)

                updated_data.append(data)
            case AssertType.MANY:
                if len(matched_rows) == 0:
                    raise MatchStep._match_assert_error('No match found for \'many\' match', item_match)

                for matched_row in matched_rows:
                    data_copy = data.copy()

                    MatchStep._append_matched_data(data_copy, matched_row, item_match)

                    updated_data.append(data_copy)
            case AssertType.OPTIONAL_ONE:
                if len(matched_rows) > 1:
                    raise MatchStep._match_assert_error('Multiple matches found for \'optionalOne\' match', item_match)

                if len(matched_rows) == 1:
                    MatchStep._append_matched_data(data, matched_rows[0], item_match)
                else:
                    for column in step.schema.columns():
                        data[item_match.make_prefixed_column_name(column.name)] = None

                updated_data.append(data)

        return updated_data

    @staticmethod
    def _append_matched_data(data: Dict[str, any], matched_row: Dict[str, any], item_match: Match) -> None:
        for column_name, value in matched_row.items():
            data[item_match.make_prefixed_column_name(column_name)] = value

    @staticmethod
    def _match_assert_error(error: str, match: Match) -> TransformException:
        error += f' of type \'{match.type}\''
        if match.signature is not None:
            error += f' with signature \'{match.signature}\''
        return TransformException(error)
