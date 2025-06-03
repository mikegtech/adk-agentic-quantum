from .ast_nodes import ASTNode


def decode_mif(raw_ins: dict, algorithm_or_dependency=None, program_version=None) -> list[ASTNode]:
    """Decode a “multi‐IF” instruction (the 'ins' string contains one or more '^').
    We split raw_ins['ins'] on '^', then call decode_ins(...) on each sub‐instruction
    using the same algorithm_or_dependency wrapper. Finally, we concatenate all ASTNode
    results into a single flat list.

    Args:
      raw_ins                 dict of instruction fields (keys: 'n','t','ins','ins_tar','seq_t','seq_f')
      algorithm_or_dependency an Algorithm object or a Dependency object (or None)
      program_version         a ProgramVersion object (or None)

    Returns:
      List[ASTNode]

    """
    combined_nodes: list[ASTNode] = []

    ins_str = raw_ins.get("ins", "") or ""
    parts = ins_str.split("^")

    from .decoder import decode_ins  # avoid circular import

    for part in parts:
        # Build a shallow copy of raw_ins, but override 'ins' with this single part
        sub_raw_ins = raw_ins.copy()
        sub_raw_ins["ins"] = part

        # Call decode_ins using the same algorithm_or_dependency and program_version
        nodes_for_part = decode_ins(sub_raw_ins, algorithm_or_dependency, program_version)
        combined_nodes.extend(nodes_for_part)

    return combined_nodes
