# enterprise_rating/ast_decoder/decode_mif.py


from .ast_nodes import ASTNode


def decode_mif(raw_ins: dict, algorithm_seq=None, program_version=None) -> list[ASTNode]:
    """Decode a “multi‐IF” instruction (tokens separated by '^').
    raw_ins is the full instruction dict (with keys 'n','t','ins','ins_tar','seq_t','seq_f').
    We split raw_ins['ins'] on '^' and call decode_ins(...) on each piece, preserving all other fields.

    Returns a concatenated list of ASTNode results from each sub‐instruction.
    """
    combined_nodes: list[ASTNode] = []

    ins_str = raw_ins.get("ins", "") or ""
    parts = ins_str.split("^")

    for part in parts:
        # Build a shallow copy of raw_ins, but override 'ins' with just this sub‐string
        sub_raw_ins = raw_ins.copy()
        sub_raw_ins["ins"] = part

        # Now decode that single sub‐instruction
        from .decoder import decode_ins
        nodes = decode_ins(sub_raw_ins, algorithm_seq, program_version)
        combined_nodes.extend(nodes)

    return combined_nodes
