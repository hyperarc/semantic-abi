# Generated from semanticabi/common/expression/parser/Expression.g4 by ANTLR 4.13.1
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,14,108,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,
        2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,
        13,7,13,2,14,7,14,2,15,7,15,2,16,7,16,1,0,1,0,1,1,1,1,1,2,1,2,5,
        2,42,8,2,10,2,12,2,45,9,2,1,2,1,2,1,3,1,3,1,4,1,4,3,4,53,8,4,1,5,
        1,5,1,6,4,6,58,8,6,11,6,12,6,59,1,7,1,7,1,7,4,7,65,8,7,11,7,12,7,
        66,3,7,69,8,7,1,7,1,7,4,7,73,8,7,11,7,12,7,74,3,7,77,8,7,1,8,1,8,
        5,8,81,8,8,10,8,12,8,84,9,8,1,9,1,9,1,10,1,10,1,11,1,11,1,12,1,12,
        1,13,1,13,1,14,1,14,1,14,1,15,1,15,1,15,1,16,4,16,103,8,16,11,16,
        12,16,104,1,16,1,16,0,0,17,1,1,3,2,5,3,7,0,9,4,11,0,13,5,15,6,17,
        7,19,0,21,8,23,9,25,10,27,11,29,12,31,13,33,14,1,0,3,4,0,10,10,12,
        13,39,39,92,92,4,0,48,57,65,90,95,95,97,122,3,0,9,10,13,13,32,32,
        113,0,1,1,0,0,0,0,3,1,0,0,0,0,5,1,0,0,0,0,9,1,0,0,0,0,13,1,0,0,0,
        0,15,1,0,0,0,0,17,1,0,0,0,0,21,1,0,0,0,0,23,1,0,0,0,0,25,1,0,0,0,
        0,27,1,0,0,0,0,29,1,0,0,0,0,31,1,0,0,0,0,33,1,0,0,0,1,35,1,0,0,0,
        3,37,1,0,0,0,5,39,1,0,0,0,7,48,1,0,0,0,9,52,1,0,0,0,11,54,1,0,0,
        0,13,57,1,0,0,0,15,76,1,0,0,0,17,78,1,0,0,0,19,85,1,0,0,0,21,87,
        1,0,0,0,23,89,1,0,0,0,25,91,1,0,0,0,27,93,1,0,0,0,29,95,1,0,0,0,
        31,98,1,0,0,0,33,102,1,0,0,0,35,36,5,40,0,0,36,2,1,0,0,0,37,38,5,
        41,0,0,38,4,1,0,0,0,39,43,5,39,0,0,40,42,3,7,3,0,41,40,1,0,0,0,42,
        45,1,0,0,0,43,41,1,0,0,0,43,44,1,0,0,0,44,46,1,0,0,0,45,43,1,0,0,
        0,46,47,5,39,0,0,47,6,1,0,0,0,48,49,8,0,0,0,49,8,1,0,0,0,50,53,3,
        15,7,0,51,53,3,13,6,0,52,50,1,0,0,0,52,51,1,0,0,0,53,10,1,0,0,0,
        54,55,2,48,57,0,55,12,1,0,0,0,56,58,3,11,5,0,57,56,1,0,0,0,58,59,
        1,0,0,0,59,57,1,0,0,0,59,60,1,0,0,0,60,14,1,0,0,0,61,68,3,13,6,0,
        62,64,5,46,0,0,63,65,3,13,6,0,64,63,1,0,0,0,65,66,1,0,0,0,66,64,
        1,0,0,0,66,67,1,0,0,0,67,69,1,0,0,0,68,62,1,0,0,0,68,69,1,0,0,0,
        69,77,1,0,0,0,70,72,5,46,0,0,71,73,3,13,6,0,72,71,1,0,0,0,73,74,
        1,0,0,0,74,72,1,0,0,0,74,75,1,0,0,0,75,77,1,0,0,0,76,61,1,0,0,0,
        76,70,1,0,0,0,77,16,1,0,0,0,78,82,3,19,9,0,79,81,3,19,9,0,80,79,
        1,0,0,0,81,84,1,0,0,0,82,80,1,0,0,0,82,83,1,0,0,0,83,18,1,0,0,0,
        84,82,1,0,0,0,85,86,7,1,0,0,86,20,1,0,0,0,87,88,5,43,0,0,88,22,1,
        0,0,0,89,90,5,45,0,0,90,24,1,0,0,0,91,92,5,42,0,0,92,26,1,0,0,0,
        93,94,5,47,0,0,94,28,1,0,0,0,95,96,5,42,0,0,96,97,5,42,0,0,97,30,
        1,0,0,0,98,99,5,124,0,0,99,100,5,124,0,0,100,32,1,0,0,0,101,103,
        7,2,0,0,102,101,1,0,0,0,103,104,1,0,0,0,104,102,1,0,0,0,104,105,
        1,0,0,0,105,106,1,0,0,0,106,107,6,16,0,0,107,34,1,0,0,0,10,0,43,
        52,59,66,68,74,76,82,104,1,6,0,0
    ]

class ExpressionLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    STRING = 3
    NUMBER = 4
    INTEGER = 5
    DECIMAL = 6
    VARIABLE = 7
    PLUS = 8
    MINUS = 9
    MULT = 10
    DIV = 11
    POW = 12
    CONCAT = 13
    WS = 14

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'('", "')'", "'+'", "'-'", "'*'", "'/'", "'**'", "'||'" ]

    symbolicNames = [ "<INVALID>",
            "STRING", "NUMBER", "INTEGER", "DECIMAL", "VARIABLE", "PLUS", 
            "MINUS", "MULT", "DIV", "POW", "CONCAT", "WS" ]

    ruleNames = [ "T__0", "T__1", "STRING", "STRING_CHARS", "NUMBER", "DIGIT", 
                  "INTEGER", "DECIMAL", "VARIABLE", "VARIABLE_CHAR", "PLUS", 
                  "MINUS", "MULT", "DIV", "POW", "CONCAT", "WS" ]

    grammarFileName = "Expression.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


