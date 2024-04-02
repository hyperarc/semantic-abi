from typing import Dict

from semanticabi.common.TransformException import TransformException
from semanticabi.common.expression.parser.ExpressionParser import ExpressionParser
from semanticabi.common.expression.parser.ExpressionVisitor import ExpressionVisitor


class ExpressionEvalVisitor(ExpressionVisitor):
    """
    Visitor that is responsible for evaluating an expression and returning the result
    """
    _variables: Dict[str, any]

    def __init__(self, variables: Dict[str, any]):
        self._variables = variables

    def visitPowExpression(self, ctx: ExpressionParser.PowExpressionContext):
        return self.visit(ctx.expression(0)) ** self.visit(ctx.expression(1))

    def visitMultExpression(self, ctx: ExpressionParser.MultExpressionContext):
        if ctx.MULT() is not None:
            return self.visit(ctx.expression(0)) * self.visit(ctx.expression(1))
        elif ctx.DIV() is not None:
            return self.visit(ctx.expression(0)) / self.visit(ctx.expression(1))
        else:
            raise Exception('Unknown operator: ' + str(ctx.getText()))

    def visitAddExpression(self, ctx: ExpressionParser.AddExpressionContext):
        if ctx.PLUS() is not None:
            return self.visit(ctx.expression(0)) + self.visit(ctx.expression(1))
        elif ctx.MINUS() is not None:
            return self.visit(ctx.expression(0)) - self.visit(ctx.expression(1))
        elif ctx.CONCAT() is not None:
            return self.visit(ctx.expression(0)) + self.visit(ctx.expression(1))
        else:
            raise Exception('Unknown operator: ' + str(ctx.getText()))

    def visitSignedAtom(self, ctx: ExpressionParser.SignedAtomContext):
        if ctx.MINUS() is not None:
            return -1 * self.visitSignedAtom(ctx.signedAtom())
        elif ctx.PLUS() is not None:
            return self.visitSignedAtom(ctx.signedAtom())

        return self.visit(ctx.atom())

    def visitAtom(self, ctx: ExpressionParser.AtomContext):
        if ctx.expression() is not None:
            return self.visit(ctx.expr)

        return self.visitChildren(ctx)

    def visitNumber(self, ctx: ExpressionParser.NumberContext):
        if ctx.NUMBER() is not None:
            value = ctx.NUMBER().getText()
            return ExpressionEvalVisitor._string_to_number(value)
        else:
            raise Exception('Unknown number format: ' + str(ctx.getText()))

    def visitVariable(self, ctx: ExpressionParser.VariableContext):
        var_name: str = ctx.VARIABLE().getText()
        value: any = self._variables.get(var_name)
        if value is None:
            raise TransformException('Unknown variable: ' + var_name)

        return value

    def visitString(self, ctx: ExpressionParser.StringContext):
        # Strip off the leading and trailing single quotes
        return ctx.STRING().getText()[1:-1]

    @staticmethod
    def _string_to_number(value: str) -> int | float:
        """
        Convert a string to a number
        """

        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                raise TransformException(f'Could not convert {value} to a number')