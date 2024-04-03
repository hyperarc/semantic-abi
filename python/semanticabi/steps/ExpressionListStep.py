from typing import List, Dict, Set

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.item.Expressions import Expressions
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.Step import Step, TransformItem
from semanticabi.steps.SubsequentStep import SubsequentStep


class ExpressionListStep(SubsequentStep):
    """
    Applies a list of expressions to the current item
    """

    _expressions: Expressions
    _schema: AbiSchema

    def __init__(self, previous_step: Step, expressions: Expressions):
        super().__init__(previous_step)
        self._expressions = expressions
        self._schema = ExpressionListStep._build_schema(previous_step.schema, expressions)

    @staticmethod
    def _build_schema(previous_schema: AbiSchema, expressions: Expressions) -> AbiSchema:
        if len(expressions.expressions) == 0:
            return previous_schema

        new_schema = previous_schema
        for expression in expressions.expressions:
            expression_columns: Set[str] = expression.column_names()
            unknown_columns: Set[str] = set()
            for column_name in expression_columns:
                if not new_schema.has_column(column_name):
                    unknown_columns.add(column_name)

            if len(unknown_columns) > 0:
                raise InvalidAbiException(f'Unknown columns referenced in expression \'{expression.expression}\': {",".join(unknown_columns)}')

            new_schema = new_schema.with_columns([expression.type.dataset_column(expression.name)], True)

        return new_schema

    @property
    def schema(self) -> AbiSchema:
        return self._schema

    def _should_transform(self):
        return len(self._expressions.expressions) > 0

    def _inner_transform_item(
        self,
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previous_data: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        new_data: List[Dict[str, any]] = []
        for row in previous_data:
            for expression in self._expressions.expressions:
                # Make sure we pass in the updated row to evaluate the next expression
                row[expression.name] = expression.evaluate(row)

            new_data.append(row)

        return new_data
