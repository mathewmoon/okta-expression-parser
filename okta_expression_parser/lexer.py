# pyright: reportUndefinedVariable=false
from sly import Lexer


class SyntaxError(Exception):
    pass


class ExpressionLexer(Lexer):
    # reflags = re.IGNORECASE
    # Set of token names.
    tokens = {
        NAME,
        STRING,
        INT,
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
        COLON,
        QUESTION_MARK,
        MEMBEROF,
        MEMBEROFANY,
        MEMBEROFNAME,
        MEMBEROFGROUPSTARTSWITH,
        MEMBEROFGROUPCONTAINS,
        MEMBEROFGROUPNAMEREGEX,
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
    MEMBEROFGROUPCONTAINS = "isMemberOfGroupNameContains"
    MEMBEROFGROUPNAMEREGEX = "isMemberOfGroupNameRegex"
    MEMBEROFGROUPSTARTSWITH = "isMemberOfGroupNameStartsWith"
    MEMBEROFANY = "isMemberOfAnyGroup"
    MEMBEROFNAME = "isMemberOfGroupName"
    MEMBEROF = "isMemberOfGroup"
    USER = r"user\b"
    COLON = r"\:"
    QUESTION_MARK = r"\?"

    NULL = r"null|NULL|Null"
    CLASS = r"String|Arrays|Convert|Iso3166Convert|Groups"
    INT = r"\d+"
    #    STRING = r""""([^"\\]*(\\.[^"\\]*)*)"|\'([^\'\\]*(\\.[^\'\\]*)*)\'|''|\"\""""
    STRING = r'''"(?:\\.|[^"\\])*"'''
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
