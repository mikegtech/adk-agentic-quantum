# enterprise_rating/ast_decoder/parser.py


from enterprise_rating.ast_decoder.defs import MULTI_IF_SYMBOL

from .ast_nodes import (ArithmeticNode, AssignmentNode, ASTNode, CompareNode,
                        FunctionNode, IfNode, RawNode)
from .decode_mif import decode_mif
from .defs import InsType
from .helpers.ins_helpers import get_operator_english, get_round_english
from .helpers.var_lookup import get_var_desc
from .tokenizer import Token


# ──────────────────────────────────────────────────────────────────────────────
def parse(
    tokens: list[Token],
    raw_ins: dict,
    algorithm_or_dependency=None,
    program_version=None,
) -> list[ASTNode]:
    """Main parser dispatcher: inspects InsType and directs to the appropriate subparser.
    Supports algorithm_or_dependency=None or program_version=None by skipping any lookups/jumps.

    Args:
      tokens                   list of Token objects (from tokenize(raw_ins['ins']))
      raw_ins                  dict of instruction fields ('n','t','ins','ins_tar','seq_t','seq_f', etc.)
      algorithm_or_dependency  an Algorithm object or a Dependency object (or None)
      program_version          a ProgramVersion object (or None)

    Returns:
      List[ASTNode]

    """
    try:
        ins_type = InsType(int(raw_ins.get("t", 0)))
    except (ValueError, TypeError):
        ins_type = None

    step = int(raw_ins.get("n", 0))
    ins_str = raw_ins.get("ins", "") or ""

    # 1) If there's a '#' anywhere, jump to decode_mif
    if MULTI_IF_SYMBOL in ins_str or '^' in ins_str or '+' in ins_str:
        return decode_mif(raw_ins, algorithm_or_dependency, program_version)



    # 2) Otherwise, if this is a plain IF, call parse_if
    if ins_type == InsType.IF:
        return parse_if(tokens, raw_ins, algorithm_or_dependency, program_version)

    # 3) InsType dispatch map
    dispatch_map = {
        InsType.ARITHMETIC: parse_arithmetic,
        InsType.IF: parse_if,
        InsType.IF_DATE: parse_if_date,
        InsType.CALL: parse_call,
        InsType.SORT: parse_sort,
        InsType.MASK: parse_mask,
        InsType.SET_STRING: parse_set_string,
        InsType.EMPTY: parse_empty,
        InsType.STRING_ADDITION: parse_string_addition,
        InsType.DATE_DIFF_DAYS: parse_date_diff,
        InsType.DATE_DIFF_MONTHS: parse_date_diff,
        InsType.DATE_DIFF_YEARS: parse_date_diff,
        InsType.DATE_ADDITION: parse_date_addition,
        # Math & Trig functions
        InsType.POWER: parse_function,
        InsType.LOG: parse_function,
        InsType.LOG10: parse_function,
        InsType.EXP: parse_function,
        InsType.SQRT: parse_function,
        InsType.COS: parse_function,
        InsType.SIN: parse_function,
        InsType.TAN: parse_function,
        InsType.COSH: parse_function,
        InsType.SINH: parse_function,
        InsType.TANH: parse_function,
        # DataSource
        InsType.DATA_SOURCE: parse_data_source,
    }

    parser_func = dispatch_map.get(ins_type)
    if parser_func:
        # Some parsers need raw_ins + algorithm_or_dependency + program_version
        if parser_func in (parse_if, parse_if_date, parse_data_source):
            return parser_func(tokens, raw_ins, algorithm_or_dependency, program_version)
        else:
            return parser_func(tokens, step, ins_type)

    # 4) Fallback: if no InsType matched, produce a RawNode
    desc = get_var_desc(ins_str, algorithm_or_dependency, program_version)
    return [RawNode(step=step, ins_type=ins_type, raw=ins_str, value=desc)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_rank_flag(
    tokens: list[Token],
    step: int,
    ins_type: InsType,
    algorithm_or_dependency=None,
    program_version=None,
) -> list[ASTNode]:
    """Generic parser for any InsType whose name begins with 'RANK' or 'FLAG'.
    If algorithm_or_dependency or program_version is None, we skip get_var_desc lookups.
    """
    action_text = ins_type.name.replace("_", " ").title()

    vars_expanded = []
    for t in tokens:
        if (
            program_version is not None
            and algorithm_or_dependency is not None
            and t.type == "WORD"
            and ("GI_" in t.value or "GC_" in t.value)
        ):
            vars_expanded.append(
                get_var_desc(t.value, algorithm_or_dependency, program_version)
            )
        else:
            vars_expanded.append(t.value)

    if vars_expanded:
        action_text += ": " + ", ".join(vars_expanded)

    desc = get_var_desc(action_text, algorithm_or_dependency, program_version)
    return [RawNode(step=step, ins_type=ins_type, raw=action_text, value=desc)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_sort(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Stub for Sort instruction."""
    text = "Sort: " + " ".join(t.value for t in tokens)
    return [RawNode(step=step, ins_type=ins_type, raw="", value=text)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_mask(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Stub for Mask instruction."""
    text = "Mask: " + " ".join(t.value for t in tokens)

    return [RawNode(step=step, ins_type=ins_type, raw="", value=text)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_empty(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Empty instruction (no‐op)."""
    return []


# ──────────────────────────────────────────────────────────────────────────────
def parse_set_string(
    tokens: list[Token], step: int, ins_type: InsType
) -> list[ASTNode]:
    """Set String: usually of the form VAR [literal].
    Produces an AssignmentNode where expr is a RawNode(string literal).
    """
    if len(tokens) >= 2:
        var = tokens[0].value
        literal = tokens[1].value
        assign = AssignmentNode(
            step=step,
            ins_type=ins_type,
            var=var,
            expr=RawNode(step=step, ins_type=ins_type, raw="", value=literal),
            target=None,
            next_true=None,
            next_false=None,
        )
        return [assign]

    # Fallback
    return [RawNode(step=step, ins_type=ins_type, raw="", value=" ".join(t.value for t in tokens))]


# ──────────────────────────────────────────────────────────────────────────────
def parse_string_addition(
    tokens: list[Token], step: int, ins_type: InsType
) -> list[ASTNode]:
    """String Addition: build a FunctionNode that concatenates all tokens.
    We strip out any '[' or ']' characters from each token’s raw text.
    """
    # 1) Create one RawNode per token, but remove "[" and "]" from its value:
    args = []
    for t in tokens:
        clean = t.value.replace("[", "").replace("]", "")
        node = RawNode(step=step, ins_type=ins_type, raw="", value=clean)
        node.raw = t.value
        args.append(node)

    # 2) Build a FunctionNode named "StringAddition"
    #    English summary also uses the cleaned values:
    english = "Concatenate " + " + ".join(arg.value for arg in args)
    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name="StringAddition",
        args=args,
        english=english,
    )
    return [node]


# ──────────────────────────────────────────────────────────────────────────────
def parse_date_diff(
    tokens: list[Token], step: int, ins_type: InsType
) -> list[ASTNode]:
    """Parse Date Diff instructions (DATE_DIFF_DAYS, etc.).
    Builds a FunctionNode with English description of the difference.
    """
    if len(tokens) >= 2:
        left_val = tokens[0].value
        right_val = tokens[1].value
    else:
        left_val = tokens[0].value if tokens else ""
        right_val = ""

    unit_map = {
        InsType.DATE_DIFF_DAYS: "Days",
        InsType.DATE_DIFF_MONTHS: "Months",
        InsType.DATE_DIFF_YEARS: "Years",
    }
    unit = unit_map.get(ins_type, "")
    name = f"Date Difference ({unit})"
    english = f"Difference in {unit} between {left_val} and {right_val}"

    left_node = RawNode(step=step, ins_type=ins_type, raw="", value=left_val)
    right_node = RawNode(step=step, ins_type=ins_type, raw="", value=right_val)
    node = FunctionNode(
        step=step, ins_type=ins_type, name=name, args=[left_node, right_node], english=english
    )
    return [node]


# ──────────────────────────────────────────────────────────────────────────────
def parse_date_addition(
    tokens: list[Token], step: int, ins_type: InsType
) -> list[ASTNode]:
    """Parse Date Addition instructions: [base_date_or_var, offset_spec].
    Builds a FunctionNode named "Date Addition" with English = "Add offset to date".
    """
    if len(tokens) >= 2:
        date_val = tokens[0].value
        offset_val = tokens[1].value
    else:
        date_val = tokens[0].value if tokens else ""
        offset_val = ""

    date_node = RawNode(step=step, ins_type=ins_type, raw=date_val, value=date_val)
    offset_node = RawNode(step=step, ins_type=ins_type, raw=offset_val, value=offset_val)

    name = "Date Addition"
    english = f"Add {offset_val} to {date_val}"

    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name=name,
        args=[date_node, offset_node],
        english=english,
    )
    return [node]


# ──────────────────────────────────────────────────────────────────────────────
def parse_if_date(
    tokens: list[Token], raw_ins: dict, algorithm_or_dependency=None, program_version=None
) -> list[ASTNode]:
    """Parse IF_DATE instructions (InsType.IF_DATE).
    Builds a CompareNode inside an IfNode, then wires true/false branches via seq_t/seq_f
    if algorithm_or_dependency is provided.
    """
    from .decoder import decode_ins  # avoid circular import

    step = int(raw_ins.get("n", 0))
    ins_type = InsType(int(raw_ins.get("t", 0)))

    left_val = tokens[0].value if len(tokens) > 0 else ""
    op_val = tokens[1].value if len(tokens) > 1 else ""
    right_val = tokens[2].value if len(tokens) > 2 else ""

    left_desc = get_var_desc(left_val, algorithm_or_dependency, program_version)
    left_node = RawNode(step=step, ins_type=ins_type, raw=left_val, value=left_desc)

    right_desc = get_var_desc(left_val, algorithm_or_dependency, program_version)
    right_node = RawNode(step=step, ins_type=ins_type, raw=right_val, value=right_desc)
    english_op = get_operator_english(op_val)

    condition = CompareNode(
        step=step,
        ins_type=ins_type,
        left=left_node,
        operator=op_val,
        right=right_node,
        english=f"Date {english_op}",
    )

    # Next‐step pointers
    seq_t = raw_ins.get("seq_t")
    seq_f = raw_ins.get("seq_f")
    try:
        next_true = int(seq_t)
    except:
        next_true = None
    try:
        next_false = int(seq_f)
    except:
        next_false = None

    node = IfNode(
        step=step, ins_type=ins_type, condition=condition, true_branch=[], false_branch=[]
    )

    # If algorithm_or_dependency has .steps, wire the branches
    if algorithm_or_dependency is not None and hasattr(algorithm_or_dependency, "steps"):
        raw_steps = algorithm_or_dependency.steps or []
        steps_list = raw_steps if isinstance(raw_steps, list) else [raw_steps]

        if next_true is not None:
            raw_true = next((i for i in steps_list if int(i.get("n", 0)) == next_true), None)
            if raw_true:
                node.true_branch = decode_ins(raw_true, algorithm_or_dependency, program_version)

        if next_false is not None:
            raw_false = next((i for i in steps_list if int(i.get("n", 0)) == next_false), None)
            if raw_false:
                node.false_branch = decode_ins(raw_false, algorithm_or_dependency, program_version)

    return [node]


# ──────────────────────────────────────────────────────────────────────────────
def parse_if(
    tokens: list["Token"],
    raw_ins: dict,
    algorithm_or_dependency=None,
    program_version=None,
) -> list["ASTNode"]:
    """Parse a single‐clause IF of the form "|VAR|OP|VALUE|" (e.g. "|GR_5370|=|{}|").
    We assume callers (decode_mif or parse) never strip the pipes before we run this.
    """
    from .decoder import decode_ins  # avoid circular import

    step = int(raw_ins.get("n", 0))
    ins_type = InsType(int(raw_ins.get("t", 0)))
    ins_str = raw_ins.get("ins", "") or ""  # e.g. "|~GI_494|<>|GC_691|"

    # 1) Split on '|' – we expect ["", VAR, OP, VALUE, ""]
    parts = ins_str.split("|")
    if len(parts) >= 4:
        left_val = parts[1]
        operator = parts[2]
        right_val = parts[3]
    else:
        # If unexpected format, capture entire string as left_val
        left_val = ins_str
        operator = ""
        right_val = ""

    desc_left = get_var_desc(left_val, algorithm_or_dependency, program_version)
    left_node = RawNode(step=step, ins_type=ins_type.value, raw=left_val, value=desc_left)
    desc_right = get_var_desc(right_val, algorithm_or_dependency, program_version)
    right_node = RawNode(step=step, ins_type=ins_type.value, raw=right_val, value=desc_right)

    condition = CompareNode(
        step=step,
        ins_type=ins_type.value,
        left=left_node,
        operator=operator,
        right=right_node,
        english=""
    )

    node = IfNode(step=step, ins_type=ins_type.value, condition=condition, true_branch=[], false_branch=[])

    # 2) Wire up true/false branches via seq_t / seq_f if available
    seq_t = raw_ins.get("seq_t")
    seq_f = raw_ins.get("seq_f")
    try:
        next_true = int(seq_t)
    except (TypeError, ValueError):
        next_true = None
    try:
        next_false = int(seq_f)
    except (TypeError, ValueError):
        next_false = None

    if algorithm_or_dependency is not None and hasattr(algorithm_or_dependency, "steps"):
        raw_steps = algorithm_or_dependency.steps or []
        steps_list = raw_steps if isinstance(raw_steps, list) else [raw_steps]

        # True branch
        if next_true is not None:
            raw_true = next((i for i in steps_list if int(i.get("n", 0)) == next_true), None)
            if raw_true:
                try:
                    node.true_branch = decode_ins(raw_true, algorithm_or_dependency, program_version)
                except Exception as e:
                    # On error, insert a RawNode with the exception text into true_branch
                    node.true_branch = [RawNode(step=step, ins_type=ins_type.value, raw="", value=f"ERROR: {e}")]

        # False branch
        if next_false is not None:
            raw_false = next((i for i in steps_list if int(i.get("n", 0)) == next_false), None)
            if raw_false:
                try:
                    node.false_branch = decode_ins(raw_false, algorithm_or_dependency, program_version)
                except Exception as e:
                    node.false_branch = [RawNode(step=step, ins_type=ins_type.value, raw="", value=f"ERROR: {e}")]

    return [node]


# ──────────────────────────────────────────────────────────────────────────────
def parse_arithmetic(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Parse arithmetic expressions into an ArithmeticNode.
    Expected format: VAR operator VAR [round_spec], where round_spec might be '!RN', etc.
    """
    round_spec = None
    if tokens and tokens[-1].value.startswith("!"):
        round_token = tokens[-1].value
        round_spec = round_token[1:]
        tokens = tokens[:-1]

    if len(tokens) >= 3:
        left_val = tokens[0].value
        operator = tokens[1].value
        right_val = tokens[2].value

        left_node = RawNode(step=step, ins_type=ins_type, raw=left_val, value=left_val)
        right_node = RawNode(step=step, ins_type=ins_type, raw=right_val, value=right_val)
        round_eng = get_round_english(round_spec) if round_spec else None

        op_eng = get_operator_english(operator)
        english = f"Compute {left_val} {op_eng} {right_val}"
        if round_eng:
            english += f" then {round_eng}"

        node = ArithmeticNode(
            step=step,
            ins_type=ins_type,
            left=left_node,
            operator=operator,
            right=right_node,
            round_spec=round_spec,
            round_english=round_eng,
        )
        return [node]

    # Fallback
    return [RawNode(step=step, ins_type=ins_type, raw="", value=" ".join(t.value for t in tokens))]


# ──────────────────────────────────────────────────────────────────────────────
def parse_function(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Generic parser for math & trigonometry functions.
    Handles single‐arg (SQRT, LOG, etc.) and two‐arg (POWER, etc.) + optional rounding.
    """
    round_spec = None
    if tokens and tokens[-1].value.startswith("!"):
        round_token = tokens[-1].value
        round_spec = round_token[1:]
        tokens = tokens[:-1]

    args = [RawNode(step=step, ins_type=ins_type, raw=t.value, value=t.value) for t in tokens]

    friendly_map = {
        "POWER": "Power",
        "LOG": "Natural Log",
        "LOG10": "Log Base 10",
        "EXP": "Exponential",
        "SQRT": "Square Root",
        "COS": "Cosine",
        "SIN": "Sine",
        "TAN": "Tangent",
        "COSH": "Hyperbolic Cosine",
        "SINH": "Hyperbolic Sine",
        "TANH": "Hyperbolic Tangent",
    }
    display_name = friendly_map.get(ins_type.name, ins_type.name.title())

    if len(tokens) == 1:
        english = f"Compute {display_name} of {tokens[0].value}"
    elif len(tokens) == 2:
        english = f"Compute {display_name} of {tokens[0].value} and {tokens[1].value}"
    else:
        english = f"Compute {display_name}"

    if round_spec:
        round_eng = get_round_english(round_spec)
        english += f" then {round_eng}"

    node = FunctionNode(step=step, ins_type=ins_type, name=ins_type.name, args=args, english=english)
    return [node]


# ──────────────────────────────────────────────────────────────────────────────
def parse_call(
    tokens: list[Token], raw_ins: dict, algorithm_or_dependency=None, program_version=None
) -> list[ASTNode]:
    """Stub for CALL instruction.
    This can be updated later to construct an actual FunctionNode or similar.
    For now, we produce a RawNode placeholder.
    """
    step = int(raw_ins.get("n", 0))
    ins_type = InsType(int(raw_ins.get("t", 0)))
    call_text = "Call: " + (raw_ins.get("ins") or "")
    return [RawNode(step=step, ins_type=ins_type, raw=call_text, value=call_text)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_data_source(
    tokens: list[Token], raw_ins: dict, algorithm_or_dependency=None, program_version=None
) -> list[ASTNode]:
    """Parse DataSource instructions (InsType.DATA_SOURCE).
    If program_version is None, we skip lookups and return a placeholder.
    """
    step = int(raw_ins.get("n", 0))
    ins_type = InsType(int(raw_ins.get("t", 0)))

    source_id = tokens[0].value if tokens else ""
    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name="DataSource",
        args=[RawNode(step=step, ins_type=ins_type, raw=tok.value, value=tok.value) for tok in tokens],
        english="DataSource call not implemented",
    )
    return [node]
