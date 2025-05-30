import re
from typing import NamedTuple


class Token(NamedTuple):
    type: str
    value: str


def tokenize(raw: str) -> list[Token]:
    """Break raw instruction string into tokens: operators, vars, literals.
    Operators: | ^ + = > < ! ~ { } [ ]
    Variables and numbers are WORD tokens.
    """
    if not raw:
        return []
    # Regex to capture delimiters and words
    pattern = r"(\||\^|\+|>=|<=|=|>|<|!R2|!RN|!RS|!|~|\{|\}|\[|\])"
    parts = [p for p in re.split(pattern, raw) if p and not p.isspace()]
    tokens = []
    for part in parts:
        if part in {'|','^','+','>=','<=','=','>','<','!R2','!RN','!RS','!','~','{','}','[',']'}:
            tokens.append(Token(type='OP', value=part))
        else:
            tokens.append(Token(type='WORD', value=part))
    return tokens
