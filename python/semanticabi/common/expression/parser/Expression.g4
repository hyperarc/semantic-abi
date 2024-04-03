grammar Expression;

expression
    : signedAtom                                    #signedAtomExpression
    | <assoc=right> expression POW expression       #powExpression
    | expression (MULT | DIV) expression            #multExpression
    | expression (PLUS | MINUS | CONCAT) expression #addExpression
    ;

signedAtom
    : PLUS signedAtom
    | MINUS signedAtom
    | atom
    ;

atom
    : number
    | variable
    | string
    | '(' expr=expression ')'
    ;

variable
    : VARIABLE
    ;

string
    : STRING
    ;

STRING: '\'' STRING_CHARS* '\'';

fragment STRING_CHARS: (~[\\\r\n\f']);

number
    : NUMBER
    ;

NUMBER
    : DECIMAL
    | INTEGER
    ;

fragment DIGIT
    : '0' .. '9'
    ;

INTEGER
    : DIGIT+
    ;

DECIMAL
    : INTEGER ('.' INTEGER+)?
    | '.' INTEGER+
    ;

VARIABLE
    : VARIABLE_CHAR VARIABLE_CHAR*
    ;

fragment VARIABLE_CHAR
    : ('a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_')
    ;

PLUS: '+';
MINUS: '-';
MULT: '*';
DIV: '/';
POW: '**';
CONCAT: '||';

WS
    : [ \r\n\t]+ -> skip
    ;
