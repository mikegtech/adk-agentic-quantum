from pathlib import Path

import yaml

from enterprise_rating.ast_decoder.ast_nodes import (ArithmeticNode, IfNode,
                                                     JumpNode)

# Load once at module import
with open(Path(__file__).parent / "templates.yml", encoding="utf-8") as f:
    _cfg = yaml.safe_load(f)

STEP_TYPES = _cfg["step_types"]
TEMPLATES = _cfg["templates"]


def render_node_old(node):
    """Turn a single AST node into a polished English sentence,
    prefixed with the human-readable step-type label.
    """
    # 1) look up the step-type
    step_label = STEP_TYPES.get(str(node.ins_type), f"Type {node.ins_type}")

    # 2) pick the right AST template
    tpl = TEMPLATES.get(node.template_id, "{english}")

    # 3) fill in fields common to all node shapes
    filled = tpl.format(
        left=getattr(node.condition.left, "raw", ""),
        op=getattr(node.condition, "operator", ""),
        right=getattr(node.condition.right, "raw", ""),
        cond_op=node.condition.cond_op if hasattr(node.condition, "cond_op") else "",
        args=", ".join(arg.raw for arg in getattr(node, "args", [])),
        target=getattr(node, "target", ""),
        english=getattr(node, "english", ""),
    )

    return f"**{step_label}**: {filled}"


def render_node(node):
    """Render *any* AST node by looking up its template_id and
    feeding node attributes into the Jinja2 template.
    """
    tpl = TEMPLATES.get(node.template_id)
    if not tpl:
        return node.english or ""

    # Build a context of all possible fields—templates only use what they need
    ctx = {
        "left": getattr(node.condition,  "left",   None) and node.condition.left.raw,
        "operator": getattr(node.condition, "operator", None),
        "right": getattr(node.condition, "right",  None) and node.condition.right.raw,
        "cond_op": getattr(node.condition, "cond_op", None),
        "args": [arg.raw for arg in getattr(node, "args", [])],
        "target": getattr(node, "target", None),
        "round_spec": getattr(node, "round_spec", None),
        "english": getattr(node, "english", ""),
    }
    # Render and return the final string
    return tpl.render(**ctx)


def render_node_new(node):
    tpl = TEMPLATES.get(node.template_id)
    if tpl:
        if isinstance(node, JumpNode):
            return tpl.format(target=node.target)
        if isinstance(node, IfNode):
            return tpl.format(
                left=node.condition.left.raw,
                op=node.condition.operator,
                right=node.condition.right.raw
            )
        if isinstance(node, ArithmeticNode):
            # fill in rounding if present:
            round_fmt = ""
            if getattr(node, "round_spec", None):
                round_fmt = f" (round to {node.round_spec} places)"
            # choose template or fallback
            if tpl:
                text = tpl.format(
                    left=node.left.raw,
                    operator=node.operator,
                    right=node.right.raw,
                    rounding=round_fmt
                )
    # fall back to node.english if someone pre-populated it
    return node.english or ""
