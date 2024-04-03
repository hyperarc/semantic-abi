# Generated from semanticabi/common/expression/parser/Expression.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .ExpressionParser import ExpressionParser
else:
    from ExpressionParser import ExpressionParser

# This class defines a complete listener for a parse tree produced by ExpressionParser.
class ExpressionListener(ParseTreeListener):

    # Enter a parse tree produced by ExpressionParser#addExpression.
    def enterAddExpression(self, ctx:ExpressionParser.AddExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionParser#addExpression.
    def exitAddExpression(self, ctx:ExpressionParser.AddExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionParser#powExpression.
    def enterPowExpression(self, ctx:ExpressionParser.PowExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionParser#powExpression.
    def exitPowExpression(self, ctx:ExpressionParser.PowExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionParser#multExpression.
    def enterMultExpression(self, ctx:ExpressionParser.MultExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionParser#multExpression.
    def exitMultExpression(self, ctx:ExpressionParser.MultExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionParser#signedAtomExpression.
    def enterSignedAtomExpression(self, ctx:ExpressionParser.SignedAtomExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionParser#signedAtomExpression.
    def exitSignedAtomExpression(self, ctx:ExpressionParser.SignedAtomExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionParser#signedAtom.
    def enterSignedAtom(self, ctx:ExpressionParser.SignedAtomContext):
        pass

    # Exit a parse tree produced by ExpressionParser#signedAtom.
    def exitSignedAtom(self, ctx:ExpressionParser.SignedAtomContext):
        pass


    # Enter a parse tree produced by ExpressionParser#atom.
    def enterAtom(self, ctx:ExpressionParser.AtomContext):
        pass

    # Exit a parse tree produced by ExpressionParser#atom.
    def exitAtom(self, ctx:ExpressionParser.AtomContext):
        pass


    # Enter a parse tree produced by ExpressionParser#variable.
    def enterVariable(self, ctx:ExpressionParser.VariableContext):
        pass

    # Exit a parse tree produced by ExpressionParser#variable.
    def exitVariable(self, ctx:ExpressionParser.VariableContext):
        pass


    # Enter a parse tree produced by ExpressionParser#string.
    def enterString(self, ctx:ExpressionParser.StringContext):
        pass

    # Exit a parse tree produced by ExpressionParser#string.
    def exitString(self, ctx:ExpressionParser.StringContext):
        pass


    # Enter a parse tree produced by ExpressionParser#number.
    def enterNumber(self, ctx:ExpressionParser.NumberContext):
        pass

    # Exit a parse tree produced by ExpressionParser#number.
    def exitNumber(self, ctx:ExpressionParser.NumberContext):
        pass



del ExpressionParser