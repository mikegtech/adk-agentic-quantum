

from dataclasses import asdict, is_dataclass

from enterprise_rating.ast_decoder.ast_nodes import ASTNode, RawNode
from enterprise_rating.ast_decoder.decoder import decode_ins
from enterprise_rating.ast_decoder.renderer import render_node
from enterprise_rating.entities.dependency import DependencyBase


def test_decode_ins_string_concat(minimal_dependency: DependencyBase):
    # Hard‐coded instruction: join [FirstName] + [LastName]
    raw_ins = [
        {
            "n": 1,
            "t": 1,
            "ins": "|~GR_5369|=|[Y]|",
            "ins_tar": "",
            "seq_t": 2,
            "seq_f": 4
        },
        {
            "n": 2,
            "t": 95,
            "ins": "~GI_573|=|",
            "ins_tar": "",
            "seq_t": 3,
            "seq_f": 4
        },
        {
            "n": 3,
            "t": 126,
            "ins": "GI_573|0|{0}",
            "ins_tar": "PC_1060",
            "seq_t": -2,
            "seq_f": -2
        },
        {
            "n": 4,
            "t": 126,
            "ins": "GI_111|0|{0}",
            "ins_tar": "PC_1060",
            "seq_t": -2,
            "seq_f": -2
        }
    ]

    # Decode into AST nodes
    ast = decode_ins(raw_ins[1], minimal_dependency.dependency_vars, None,
                       minimal_dependency)

    def node_to_dict(n):
        if is_dataclass(n):
            return asdict(n)
        elif hasattr(n, "model_dump"):
            return n.model_dump()
        else:
            return dict(n)

    # printf([node_to_dict(n) for n in ast])

    # Should produce exactly one FunctionNode
    assert len(ast) == 1
    node = ast[0]
    assert isinstance(node, ASTNode)
    # Verify it’s the string‐concat template
    assert node.template_id == "STRING_CONCAT"
    # Render into user‐friendly English
    english = render_node(node)
    # We expect: "Concatenate FirstName + LastName"
    assert "Concatenate" in english
    assert "*FirstName*" in english or "FirstName" in english
    assert "*LastName*"  in english or "LastName"  in english

    # Also check the arguments were split correctly
    assert hasattr(node, "args")
    assert len(node.args) == 2

    arg0, arg1 = node.args
    # Raw tokens preserved
    assert isinstance(arg0, RawNode)
    assert arg0.raw == "[FirstName]"
    assert arg1.raw == "[LastName]"

    # Values stripped of brackets
    assert arg0.value == "FirstName"
    assert arg1.value == "LastName"
