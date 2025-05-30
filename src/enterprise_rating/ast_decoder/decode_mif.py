from .ast_nodes import RawNode


def decode_mif(segment: str, algorithm_seq, program_version) -> list:
    """Decode multi-if segments separated by '^' into RawNodes.
    """
    parts = [s for s in segment.split('^') if s]
    nodes = []
    for idx, part in enumerate(parts, start=1):
        nodes.append(RawNode(step=idx, value=part))
    return nodes
