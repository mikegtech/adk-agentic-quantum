from .ast_nodes import RawNode
from .decode_mif import decode_mif
from .tokenizer import Token


def parse(tokens: list[Token], raw_ins: dict, algorithm_seq, program_version) -> list:
    """Simple parser stub: detect multi-if segments (with '^') else return raw node.
    """
    # reconstruct original string
    ins_str = raw_ins.get('ins', '')
    if '^' in ins_str:
        # delegate to multi-if decoder
        return decode_mif(ins_str, algorithm_seq, program_version)
    # fallback: return a single raw node
    return [RawNode(step=raw_ins.get('n'), value=ins_str)]
