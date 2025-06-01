# enterprise_rating/ast_decoder/decoder.py

from .parser import parse
from .tokenizer import tokenize


def decode_ins(raw_ins: dict, algorithm_seq, program_version) -> list:
    """Entrypoint: decode one instruction dict into a list of AST nodes.
    Always delegates to `parse(...)`, which does the InsType dispatch internally.
    """
    ins_str = raw_ins.get("ins", "")
    tokens = tokenize(ins_str or "")
    return parse(tokens, raw_ins, algorithm_seq, program_version)
