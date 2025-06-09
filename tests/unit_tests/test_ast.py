

from dataclasses import asdict, is_dataclass

from enterprise_rating.ast_decoder.ast_nodes import RawNode
from enterprise_rating.ast_decoder.decoder import decode_ins
from enterprise_rating.entities.algorithm import Algorithm
from enterprise_rating.entities.instruction import Instruction
from enterprise_rating.entities.program_version import ProgramVersion
from enterprise_rating.utils.utils import printf


def test_decode_ins_fallback_returns_rawnode_with_english(
    program_version: ProgramVersion,
):
    algorithm: Algorithm = program_version.algorithm_seq[0].algorithm
    step: Instruction = algorithm.steps[0]

    ast = decode_ins(
        step.model_dump(),
        algorithm,
        program_version=program_version,
        include_english=True,    # ask it to populate the .english fields
    )

    def node_to_dict(n):
        if is_dataclass(n):
            return asdict(n)
        elif hasattr(n, "model_dump"):
            return n.model_dump()
        else:
            return dict(n)

    printf([node_to_dict(n) for n in ast])

    # should get exactly one RawNode back
    assert isinstance(ast, list)
    assert len(ast) == 1
    node = ast[0]

    # fallback always produces a RawNode
    assert isinstance(node, RawNode)

    # value should have come from your var_lookup → non‐empty
    assert node.value, "expected .value to be set from var_lookup"

    # english was filled by the renderer → same as .value
    assert node.english == node.value
