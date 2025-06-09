from pathlib import Path

import yaml

# Load once at module import
with open(Path(__file__).parent / "templates.yml", encoding="utf-8") as f:
    _cfg = yaml.safe_load(f)

STEP_TYPES = _cfg["step_types"]
TEMPLATES = _cfg["templates"]


def render_node(node):
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
