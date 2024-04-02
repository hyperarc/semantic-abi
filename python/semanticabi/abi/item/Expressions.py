from __future__ import annotations
from dataclasses import dataclass
from typing import List, TypedDict, Set, Dict

from semanticabi.abi.item.DataType import DataType
from semanticabi.common.expression.ExpressionEvaluator import ExpressionEvaluator

TYPE_NAME = 'type'


class TypedExpression(TypedDict):
    name: str
    expression: str
    type: str


@dataclass
class Expression:
    """
    Defines the expression to evaluate for each row.
    """

    @staticmethod
    def from_json(json: TypedExpression) -> Expression:
        data_type = DataType.get(json[TYPE_NAME]) if TYPE_NAME in json else None

        return Expression(json['name'], json['expression'], data_type)

    name: str
    expression: str
    type: DataType

    def __post_init__(self):
        self._expression_evaluator: ExpressionEvaluator = ExpressionEvaluator(self.expression)
        self._column_names: Set[str] = self._expression_evaluator.column_names()

    def column_names(self) -> Set[str]:
        """
        Get the names of the columns referenced by this expression
        """
        return self._column_names

    def evaluate(self, row: Dict[str, any]) -> any:
        """
        Evaluate the expression on the given row of data
        """
        return self._expression_evaluator.evaluate(row)


@dataclass
class Expressions:
    """
    The list of expressions to evaluate for each row.
    """

    @staticmethod
    def from_json(json: List[TypedExpression]) -> Expressions:
        return Expressions([Expression.from_json(expr) for expr in json])

    expressions: List[Expression]
