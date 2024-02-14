# pyright: reportUndefinedVariable=false
from sly import Lexer


class SyntaxError(Exception):
    pass


class ExpressionLexer(Lexer):
    # reflags = re.IGNORECASE
    # Set of token names.
    tokens = {
        STRING,
        INT,
        NAME,
        NE,
        GTE,
        LTE,
        GT,
        LT,
        EQ,
        AND,
        OR,
        NOT,
        NULL,
        BOOL,
        MEMBEROF,
        MEMBEROFANY,
        USER,
        CLASS,
    }

    # Set of literal characters
    literals = {"(", ")", ",", ".", "{", "}"}

    # String containing ignored characters
    ignore = " \t"

    AND = r"and|And|AND"
    NE = r"(!=|ne|NE|Ne)"
    NOT = r"!|not|Not|NOT"
    GTE = ">="
    GT = ">"
    LT = "<"
    LTE = "<="
    OR = r"or|OR|Or"
    EQ = r"(==|eq|EQ|Eq)"
    BOOL = r"(true|false|True|False|TRUE|FALSE)"
    MEMBEROFANY = "isMemberOfAnyGroup"
    MEMBEROF = "isMemberOfGroup"
    USER = r"user\b"

    NULL = r"null|NULL|Null"
    CLASS = r"String|Arrays|Convert|Iso3166Convert|Groups"
    INT = r"\d+"
    STRING = r""""([^"\\]*(\\.[^"\\]*)*)"|\'([^\'\\]*(\\.[^\'\\]*)*)\'|''|\"\""""
    NAME = r"[a-zA-Z_][a-zA-Z0-9\-_]*"

    # Line number tracking
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        msg = (
            f"Bad character '{t.value[0]}' at line {self.lineno} character {self.index}"
        )
        raise SyntaxError(msg)
