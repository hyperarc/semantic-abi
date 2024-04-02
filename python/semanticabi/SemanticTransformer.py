from __future__ import annotations

from functools import cached_property
from typing import Dict, List, Tuple

from pyarrow import DataType

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.SemanticAbi import SemanticAbi, TypedSemanticAbi
from semanticabi.abi.item.Expressions import Expressions
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthLog import EthLog
from semanticabi.metadata.EthTraces import EthTrace
from semanticabi.metadata.EvmChain import EvmChain
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.DefaultColumnsStep import DefaultColumnsStep
from semanticabi.steps.ExplodeIndexStep import ExplodeIndexStep
from semanticabi.steps.ExplodeStep import ExplodeStep
from semanticabi.steps.ExpressionListStep import ExpressionListStep
from semanticabi.steps.FlattenParametersStep import FlattenParametersStep
from semanticabi.steps.InitStep import InitStep
from semanticabi.steps.MatchStep import AbiMatchSteps, MatchStep
from semanticabi.steps.Step import Step
from semanticabi.steps.TransformErrorStep import TransformErrorStep


class SemanticTransformer:
    """
    Given a Semantic ABI definition, this will build the necessary transformation pipeline to transform a block with
    transactions that contains a log or trace that is marked as a primary item in the ABI, and then transform those
    transactions
    """
    _abi: SemanticAbi
    _pipeline_by_topic: Dict[str, Step]
    _schema: AbiSchema

    def __init__(self, abi_json: TypedSemanticAbi):
        """
        Constructs a SemanticTransformer given a JSON representation of a Semantic ABI. Throws an InvalidAbiException
        if there are any problems with the ABI that would prevent it from being able to construct a valid schema
        """
        self._abi = SemanticAbi(abi_json)

        primary_items: List[SemanticAbiItem] = \
            SemanticTransformer._get_primary_items(self._abi.events_by_hash) \
            + SemanticTransformer._get_primary_items(self._abi.functions_by_hash)

        match_steps: AbiMatchSteps = AbiMatchSteps.from_abi(self._abi, primary_items)

        self._pipeline_by_topic: Dict[str, Step] = {
            item.raw_item.hash: SemanticTransformer._build_pipeline(self._abi, item, match_steps)
            for item in primary_items
        }

        self._schema = SemanticTransformer._union_schemas([step.schema for step in self._pipeline_by_topic.values()])

    @staticmethod
    def _get_primary_items(items_by_topic: Dict[str, SemanticAbiItem]) -> List[SemanticAbiItem]:
        return [item for item in items_by_topic.values() if item.properties.is_primary]

    @staticmethod
    def _build_pipeline(abi: SemanticAbi, item: SemanticAbiItem, match_steps: AbiMatchSteps) -> Step:
        """
        Construct the set of steps for transforming a primary abi item
        """
        step: Step = InitStep(abi, item)
        step = DefaultColumnsStep(step)
        step = FlattenParametersStep(step)
        step = ExplodeStep(step)
        step = MatchStep(step, match_steps.steps_for_match_list(item.properties.matches.matches) if item.properties.matches is not None else [])
        step = ExplodeIndexStep(step)
        step = ExpressionListStep(step, item.properties.expressions if item.properties.expressions is not None else Expressions([]))
        step = ExpressionListStep(step, abi.expressions)
        step = TransformErrorStep(step)
        return step

    @staticmethod
    def _union_schemas(schemas: List[AbiSchema]) -> AbiSchema:
        columns: List[DatasetColumn] = schemas[0].columns().copy()
        columns_by_name: Dict[str, DatasetColumn] = {column.name: column for column in columns}

        for schema in schemas[1:]:
            for column in schema.columns():
                if column.name in columns_by_name:
                    if columns_by_name[column.name] != column:
                        raise InvalidAbiException(f'Column \'{column.name}\' has conflicting types in schemas: {columns_by_name[column.name]} and {column}')
                else:
                    columns_by_name[column.name] = column
                    columns.append(column)

        return AbiSchema(columns)

    @property
    def schema(self) -> AbiSchema:
        """
        Get the schema for the ABI.
        """
        return self._schema

    def transform(self, block: EthBlock) -> List[Dict[str, any]]:
        """
        Given a block, goes through each transaction, finding any that have logs or traces that match any of the
        primary item topics, and transforms those primary items into rows
        """
        results: List[Dict[str, any]] = []

        if not self.is_valid_for_chain(block.chain):
            return results

        for transaction in block.transactions:
            logs_by_topic: Dict[str, List[EthLog]] = transaction.logs_by_topic
            traces_by_topic: Dict[str, List[EthTrace]] = transaction.traces_by_topic

            for topic, step in self._pipeline_by_topic.items():
                if topic not in logs_by_topic and topic not in traces_by_topic:
                    continue

                step_result: List[Dict[str, any]] = step.transform(block, transaction)
                if len(step_result) > 0:
                    for row in step_result:
                        # Pad out any missing columns with None
                        for column in self._schema.columns():
                            if column.name not in row:
                                row[column.name] = None
                    results.extend(step_result)

        return results

    def is_valid_for_chain(self, chain: EvmChain) -> bool:
        """
        Does this ABI apply to the given chain?
        """
        return chain in self._abi.chains

    @cached_property
    def metadata(self) -> List[Tuple[str, DataType]]:
        """
        Returns the metadata required for constructing a pyarrow schema
        """
        return list(map(
            lambda c: (c.name, c.data_type),
            self.schema.columns()
        ))
