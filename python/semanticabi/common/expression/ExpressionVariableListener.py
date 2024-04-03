from typing import Set

from semanticabi.common.expression.parser.ExpressionListener import ExpressionListener
from semanticabi.common.expression.parser.ExpressionParser import ExpressionParser


class ExpressionVariableListener(ExpressionListener):
    """
    Listener to gather all the variable names used in the expression
    """
    _variable_names: Set[str]

    def __init__(self):
        self._variable_names = set()

    def exitVariable(self, ctx: ExpressionParser.VariableContext) -> None:
        """
        This gets called after visiting each 'variable' node in the ast
        """
        self._variable_names.add(ctx.getText())

    def variable_names(self) -> Set[str]:
        return self._variable_names
