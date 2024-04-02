# Generated from semanticabi/common/expression/parser/Expression.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .ExpressionParser import ExpressionParser
else:
    from ExpressionParser import ExpressionParser

# This class defines a complete generic visitor for a parse tree produced by ExpressionParser.

class ExpressionVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ExpressionParser#addExpression.
    def visitAddExpression(self, ctx:ExpressionParser.AddExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpressionParser#powExpression.
    def visitPowExpression(self, ctx:ExpressionParser.PowExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpressionParser#multExpression.
    def visitMultExpression(self, ctx:ExpressionParser.MultExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpressionParser#signedAtomExpression.
    def visitSignedAtomExpression(self, ctx:ExpressionParser.SignedAtomExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpressionParser#signedAtom.
    def visitSignedAtom(self, ctx:ExpressionParser.SignedAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpressionParser#atom.
    def visitAtom(self, ctx:ExpressionParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpressionParser#variable.
    def visitVariable(self, ctx:ExpressionParser.VariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpressionParser#string.
    def visitString(self, ctx:ExpressionParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpressionParser#number.
    def visitNumber(self, ctx:ExpressionParser.NumberContext):
        return self.visitChildren(ctx)



del ExpressionParser