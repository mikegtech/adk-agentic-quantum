# enterprise_rating/ast_decoder/decoder.py

from .parser import parse
from .tokenizer import tokenize


def decode_ins(raw_ins: dict, algorithm_or_dependency=None, program_version=None) -> list:
    """Entrypoint: decode one instruction dict into a list of AST nodes.
    If algorithm_or_dependency or program_version is None, parsing will
    produce a best‐effort AST without doing any jumps or lookups.

    Args:
      raw_ins        dict of instruction fields (keys: 'n','t','ins','ins_tar','seq_t','seq_f')
      algorithm_or_dependency  an Algorithm object or a Dependency object (or None)
      program_version a ProgramVersion object (or None)

    Returns:
      List[ASTNode]

    """
    ins_str = raw_ins.get("ins", "") or ""
    tokens = tokenize(ins_str)
    return parse(tokens, raw_ins, algorithm_or_dependency, program_version)
