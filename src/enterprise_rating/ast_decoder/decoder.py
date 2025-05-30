from .parser import parse
from .tokenizer import tokenize


def decode_ins(raw_ins: dict, algorithm_seq, program_version) -> list:
    """Entrypoint: decode one instruction dict into a list of AST nodes.
    raw_ins: dict with keys 'n','t','ins','ins_tar','seq_t','seq_f'
    algorithm_seq: AlgorithmSequence containing dependency_vars
    program_version: ProgramVersion with data_dictionary
    """
    ins_str = raw_ins.get('ins', '')
    tokens = tokenize(ins_str)
    ast_nodes = parse(tokens, raw_ins, algorithm_seq, program_version)
    return ast_nodes
