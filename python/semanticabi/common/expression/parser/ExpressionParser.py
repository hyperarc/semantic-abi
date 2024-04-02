# Generated from semanticabi/common/expression/parser/Expression.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,14,52,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,1,0,1,
        0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,5,0,25,8,0,10,0,12,0,28,
        9,0,1,1,1,1,1,1,1,1,1,1,3,1,35,8,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,
        2,44,8,2,1,3,1,3,1,4,1,4,1,5,1,5,1,5,0,1,0,6,0,2,4,6,8,10,0,2,1,
        0,10,11,2,0,8,9,13,13,53,0,12,1,0,0,0,2,34,1,0,0,0,4,43,1,0,0,0,
        6,45,1,0,0,0,8,47,1,0,0,0,10,49,1,0,0,0,12,13,6,0,-1,0,13,14,3,2,
        1,0,14,26,1,0,0,0,15,16,10,3,0,0,16,17,5,12,0,0,17,25,3,0,0,3,18,
        19,10,2,0,0,19,20,7,0,0,0,20,25,3,0,0,3,21,22,10,1,0,0,22,23,7,1,
        0,0,23,25,3,0,0,2,24,15,1,0,0,0,24,18,1,0,0,0,24,21,1,0,0,0,25,28,
        1,0,0,0,26,24,1,0,0,0,26,27,1,0,0,0,27,1,1,0,0,0,28,26,1,0,0,0,29,
        30,5,8,0,0,30,35,3,2,1,0,31,32,5,9,0,0,32,35,3,2,1,0,33,35,3,4,2,
        0,34,29,1,0,0,0,34,31,1,0,0,0,34,33,1,0,0,0,35,3,1,0,0,0,36,44,3,
        10,5,0,37,44,3,6,3,0,38,44,3,8,4,0,39,40,5,1,0,0,40,41,3,0,0,0,41,
        42,5,2,0,0,42,44,1,0,0,0,43,36,1,0,0,0,43,37,1,0,0,0,43,38,1,0,0,
        0,43,39,1,0,0,0,44,5,1,0,0,0,45,46,5,7,0,0,46,7,1,0,0,0,47,48,5,
        3,0,0,48,9,1,0,0,0,49,50,5,4,0,0,50,11,1,0,0,0,4,24,26,34,43
    ]

class ExpressionParser ( Parser ):

    grammarFileName = "Expression.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'('", "')'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'+'", "'-'", 
                     "'*'", "'/'", "'**'", "'||'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "STRING", "NUMBER", 
                      "INTEGER", "DECIMAL", "VARIABLE", "PLUS", "MINUS", 
                      "MULT", "DIV", "POW", "CONCAT", "WS" ]

    RULE_expression = 0
    RULE_signedAtom = 1
    RULE_atom = 2
    RULE_variable = 3
    RULE_string = 4
    RULE_number = 5

    ruleNames =  [ "expression", "signedAtom", "atom", "variable", "string", 
                   "number" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    STRING=3
    NUMBER=4
    INTEGER=5
    DECIMAL=6
    VARIABLE=7
    PLUS=8
    MINUS=9
    MULT=10
    DIV=11
    POW=12
    CONCAT=13
    WS=14

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ExpressionParser.RULE_expression

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class AddExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpressionParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExpressionParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(ExpressionParser.ExpressionContext,i)

        def PLUS(self):
            return self.getToken(ExpressionParser.PLUS, 0)
        def MINUS(self):
            return self.getToken(ExpressionParser.MINUS, 0)
        def CONCAT(self):
            return self.getToken(ExpressionParser.CONCAT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddExpression" ):
                listener.enterAddExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddExpression" ):
                listener.exitAddExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddExpression" ):
                return visitor.visitAddExpression(self)
            else:
                return visitor.visitChildren(self)


    class PowExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpressionParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExpressionParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(ExpressionParser.ExpressionContext,i)

        def POW(self):
            return self.getToken(ExpressionParser.POW, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPowExpression" ):
                listener.enterPowExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPowExpression" ):
                listener.exitPowExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPowExpression" ):
                return visitor.visitPowExpression(self)
            else:
                return visitor.visitChildren(self)


    class MultExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpressionParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExpressionParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(ExpressionParser.ExpressionContext,i)

        def MULT(self):
            return self.getToken(ExpressionParser.MULT, 0)
        def DIV(self):
            return self.getToken(ExpressionParser.DIV, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMultExpression" ):
                listener.enterMultExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMultExpression" ):
                listener.exitMultExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMultExpression" ):
                return visitor.visitMultExpression(self)
            else:
                return visitor.visitChildren(self)


    class SignedAtomExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpressionParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def signedAtom(self):
            return self.getTypedRuleContext(ExpressionParser.SignedAtomContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSignedAtomExpression" ):
                listener.enterSignedAtomExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSignedAtomExpression" ):
                listener.exitSignedAtomExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSignedAtomExpression" ):
                return visitor.visitSignedAtomExpression(self)
            else:
                return visitor.visitChildren(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ExpressionParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 0
        self.enterRecursionRule(localctx, 0, self.RULE_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            localctx = ExpressionParser.SignedAtomExpressionContext(self, localctx)
            self._ctx = localctx
            _prevctx = localctx

            self.state = 13
            self.signedAtom()
            self._ctx.stop = self._input.LT(-1)
            self.state = 26
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 24
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
                    if la_ == 1:
                        localctx = ExpressionParser.PowExpressionContext(self, ExpressionParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 15
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 16
                        self.match(ExpressionParser.POW)
                        self.state = 17
                        self.expression(3)
                        pass

                    elif la_ == 2:
                        localctx = ExpressionParser.MultExpressionContext(self, ExpressionParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 18
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 19
                        _la = self._input.LA(1)
                        if not(_la==10 or _la==11):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 20
                        self.expression(3)
                        pass

                    elif la_ == 3:
                        localctx = ExpressionParser.AddExpressionContext(self, ExpressionParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 21
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 22
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 8960) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 23
                        self.expression(2)
                        pass

             
                self.state = 28
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class SignedAtomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PLUS(self):
            return self.getToken(ExpressionParser.PLUS, 0)

        def signedAtom(self):
            return self.getTypedRuleContext(ExpressionParser.SignedAtomContext,0)


        def MINUS(self):
            return self.getToken(ExpressionParser.MINUS, 0)

        def atom(self):
            return self.getTypedRuleContext(ExpressionParser.AtomContext,0)


        def getRuleIndex(self):
            return ExpressionParser.RULE_signedAtom

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSignedAtom" ):
                listener.enterSignedAtom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSignedAtom" ):
                listener.exitSignedAtom(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSignedAtom" ):
                return visitor.visitSignedAtom(self)
            else:
                return visitor.visitChildren(self)




    def signedAtom(self):

        localctx = ExpressionParser.SignedAtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_signedAtom)
        try:
            self.state = 34
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [8]:
                self.enterOuterAlt(localctx, 1)
                self.state = 29
                self.match(ExpressionParser.PLUS)
                self.state = 30
                self.signedAtom()
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 2)
                self.state = 31
                self.match(ExpressionParser.MINUS)
                self.state = 32
                self.signedAtom()
                pass
            elif token in [1, 3, 4, 7]:
                self.enterOuterAlt(localctx, 3)
                self.state = 33
                self.atom()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.expr = None # ExpressionContext

        def number(self):
            return self.getTypedRuleContext(ExpressionParser.NumberContext,0)


        def variable(self):
            return self.getTypedRuleContext(ExpressionParser.VariableContext,0)


        def string(self):
            return self.getTypedRuleContext(ExpressionParser.StringContext,0)


        def expression(self):
            return self.getTypedRuleContext(ExpressionParser.ExpressionContext,0)


        def getRuleIndex(self):
            return ExpressionParser.RULE_atom

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtom" ):
                listener.enterAtom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtom" ):
                listener.exitAtom(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAtom" ):
                return visitor.visitAtom(self)
            else:
                return visitor.visitChildren(self)




    def atom(self):

        localctx = ExpressionParser.AtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_atom)
        try:
            self.state = 43
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4]:
                self.enterOuterAlt(localctx, 1)
                self.state = 36
                self.number()
                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 2)
                self.state = 37
                self.variable()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 3)
                self.state = 38
                self.string()
                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 4)
                self.state = 39
                self.match(ExpressionParser.T__0)
                self.state = 40
                localctx.expr = self.expression(0)
                self.state = 41
                self.match(ExpressionParser.T__1)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def VARIABLE(self):
            return self.getToken(ExpressionParser.VARIABLE, 0)

        def getRuleIndex(self):
            return ExpressionParser.RULE_variable

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariable" ):
                listener.enterVariable(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariable" ):
                listener.exitVariable(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariable" ):
                return visitor.visitVariable(self)
            else:
                return visitor.visitChildren(self)




    def variable(self):

        localctx = ExpressionParser.VariableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_variable)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            self.match(ExpressionParser.VARIABLE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(ExpressionParser.STRING, 0)

        def getRuleIndex(self):
            return ExpressionParser.RULE_string

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterString" ):
                listener.enterString(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitString" ):
                listener.exitString(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitString" ):
                return visitor.visitString(self)
            else:
                return visitor.visitChildren(self)




    def string(self):

        localctx = ExpressionParser.StringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_string)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
            self.match(ExpressionParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ExpressionParser.NUMBER, 0)

        def getRuleIndex(self):
            return ExpressionParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumber" ):
                return visitor.visitNumber(self)
            else:
                return visitor.visitChildren(self)




    def number(self):

        localctx = ExpressionParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_number)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            self.match(ExpressionParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[0] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 1)
         




