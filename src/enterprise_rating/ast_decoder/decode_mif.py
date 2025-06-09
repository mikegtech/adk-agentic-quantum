# enterprise_rating/ast_decoder/decode_mif.py

from enterprise_rating.entities.algorithm import Algorithm
from enterprise_rating.entities.dependency import DependencyBase
from enterprise_rating.entities.program_version import ProgramVersion

from .ast_nodes import ASTNode, RawNode
from .defs import MULTI_IF_SYMBOL


def decode_mif(
    raw_ins: dict,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = ""
) -> list[ASTNode]:
    """Decode any instruction whose 'ins' string contains '#' (multi-IF marker),
    or '^' (OR), or '+' (AND).  Each sub-clause is still in the form "|VAR|OP|VALUE|",
    so we do NOT strip away the '|'—instead, parse_if will split on pipes.

    If decode_ins(...) raises, return a single RawNode containing the exception text.
    """
    from .decoder import decode_ins  # avoid circular import

    combined_nodes: list[ASTNode] = []
    ins_str = raw_ins.get("ins", "") or ""

    # 1) If '#' present, split into base_part (before '#') and multi_body (after '#').
    if MULTI_IF_SYMBOL in ins_str:
        idx_hash = ins_str.index(MULTI_IF_SYMBOL)
        base_part = ins_str[:idx_hash]
        multi_body = ins_str[idx_hash + 1:]
    else:
        base_part = ""
        multi_body = ins_str

    # 2) If there's a nonempty base_part, parse it first as a standalone IF node
    trimmed_base = base_part.strip()
    if trimmed_base:
        sub_raw = raw_ins.copy()
        sub_raw["ins"] = trimmed_base
        try:
            combined_nodes.extend(decode_ins(sub_raw, algorithm_or_dependency, program_version))
        except Exception as e:
            step = int(raw_ins.get("n", 0))
            tval = raw_ins.get("t")
            try:
                ins_type_val = int(tval)
            except:
                ins_type_val = None
            combined_nodes.append(
                RawNode(step=step, ins_type=ins_type_val, template_id=template_id, raw="", value=f"ERROR: {e}")
            )

    # 3) Now split multi_body on '^' or '+' (in the order they appear).  We do NOT remove the pipes.
    fragments: list[str] = []
    i = 0
    length = len(multi_body)

    while i < length:
        idx_caret = multi_body.find("^", i)
        idx_plus = multi_body.find("+", i)

        # Helper to pick the earliest non-(-1) index
        def earliest(a: int, b: int) -> int:
            if a == -1: return b
            if b == -1: return a
            return a if a < b else b

        split_idx = earliest(idx_caret, idx_plus)

        if split_idx == -1:
            # No more '^' or '+'.  The rest is one final fragment.
            fragments.append(multi_body[i:])
            break
        else:
            fragments.append(multi_body[i:split_idx])
            i = split_idx + 1

    # 4) For each fragment (still in the form "|VAR|OP|VALUE|"), call decode_ins(...)
    for fragment in fragments:
        sub_raw = raw_ins.copy()
        sub_raw["ins"] = fragment.strip()
        try:
            combined_nodes.extend(decode_ins(sub_raw, algorithm_or_dependency, program_version))
        except Exception as e:
            step = int(raw_ins.get("n", 0))
            tval = raw_ins.get("t")
            try:
                ins_type_val = int(tval)
            except:
                ins_type_val = None
            combined_nodes.append(
                RawNode(step=step, ins_type=ins_type_val, raw="", value=f"ERROR: {e}")
            )

    return combined_nodes
