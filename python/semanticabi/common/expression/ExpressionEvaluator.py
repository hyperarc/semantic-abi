from typing import Dict, Set

from antlr4 import *

from semanticabi.common.expression.ExpressionEvalVisitor import ExpressionEvalVisitor
from semanticabi.common.expression.ExpressionVariableListener import ExpressionVariableListener
from semanticabi.common.expression.parser.ExpressionLexer import ExpressionLexer
from semanticabi.common.expression.parser.ExpressionParser import ExpressionParser


class ExpressionEvaluator:
    """
    Given an expression from a semantic abi, evaluates it given the appropriate variable context
    """
    _expression: str
    _parser: ExpressionParser

    def __init__(self, expression: str):
        self._expression = expression
        lexer = ExpressionLexer(InputStream(self._expression))
        stream = CommonTokenStream(lexer)
        self._parser = ExpressionParser(stream)

    def evaluate(self, variables: Dict[str, any]) -> any:
        self._parser.reset()
        return ExpressionEvalVisitor(variables).visit(self._parser.expression())

    def column_names(self) -> Set[str]:
        """
        Get the column names used in the expression
        """
        self._parser.reset()
        listener = ExpressionVariableListener()
        walker = ParseTreeWalker()
        walker.walk(listener, self._parser.expression())
        return listener.variable_names()
