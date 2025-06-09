# noqa: F401, F841, ARG001
# pylint: disable=unused-import, unused-variable, unused-argument, missing-module-docstring
from collections.abc import Callable

from enterprise_rating.ast_decoder.defs import MULTI_IF_SYMBOL
from enterprise_rating.entities.algorithm import Algorithm
from enterprise_rating.entities.dependency import DependencyBase
from enterprise_rating.entities.program_version import ProgramVersion

from .ast_nodes import ArithmeticNode, AssignmentNode, ASTNode, CompareNode, FunctionNode, IfNode, RawNode
from .decode_mif import decode_mif
from .defs import InsType
from .helpers.ins_helpers import get_operator_english, get_round_english
from .helpers.var_lookup import get_var_desc
from .tokenizer import Token


# ──────────────────────────────────────────────────────────────────────────────
def parse(
    tokens: list[Token],
    raw_ins: dict,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
) -> list[ASTNode]:
    """Main parser dispatcher: inspects InsType and directs to the appropriate subparser.
    Supports algorithm_or_dependency=None or program_version=None by skipping any lookups/jumps.

    Args:
      tokens: list of Token objects (from tokenize(raw_ins['ins'])).
      raw_ins: dict of instruction fields ('n','t','ins','ins_tar','seq_t','seq_f', etc.).
      algorithm_or_dependency: an Algorithm object or a Dependency object (or None).
      program_version: a ProgramVersion object (or None).

    Returns:
      List[ASTNode]: The parsed AST nodes for the instruction.

    """
    try:
        ins_type = InsType(int(raw_ins.get("t", InsType.UNKNOWN)))
    except (ValueError, TypeError):
        ins_type = InsType.UNKNOWN

    step = int(raw_ins.get("n", 0))
    ins_str = raw_ins.get("ins", "") or ""

    # 1) If there's a '#' anywhere, jump to decode_mif
    if MULTI_IF_SYMBOL in ins_str or '^' in ins_str or '+' in ins_str:
        return decode_mif(raw_ins, algorithm_or_dependency, program_version)



    # 2) Otherwise, if this is a plain IF, call parse_if
    if ins_type == InsType.IF:
        return parse_if(tokens, raw_ins, algorithm_or_dependency, program_version)

    # 3) InsType dispatch map
    # noqa: E241
    dispatch_map: dict[InsType, tuple[Callable, str]] = {
        InsType.ARITHMETIC:   (parse_arithmetic,      "ASSIGNMENT"),  # noqa: E241
        InsType.IF:           (parse_if,              "IF_COMPARE"),  # noqa: E241
        InsType.IF_DATE:      (parse_if_date,         "IF_COMPARE"),  # noqa: E241
        InsType.CALL:         (parse_call,            "FUNCTION_CALL"),  # noqa: E241
        InsType.SORT:         (parse_sort,            "FUNCTION_CALL"),  # noqa: E241
        InsType.MASK:         (parse_mask,            "MASK"),  # noqa: E241
        InsType.SET_STRING:   (parse_set_string,      "ASSIGNMENT"),  # noqa: E241
        InsType.EMPTY:        (parse_empty,           "EMPTY"),  # noqa: E241
        InsType.STRING_ADDITION: (parse_string_addition, "STRING_CONCAT"),  # noqa: E241
        InsType.DATE_DIFF_DAYS:   (parse_date_diff,       "DATE_DIFF"),  # noqa: E241
        InsType.DATE_DIFF_MONTHS: (parse_date_diff,       "DATE_DIFF"),  # noqa: E241
        InsType.DATE_DIFF_YEARS:  (parse_date_diff,       "DATE_DIFF"),  # noqa: E241
        InsType.DATE_ADDITION:    (parse_date_addition,   "DATE_DIFF"),  # noqa: E241
        # Math & Trig functions all use the same template
        InsType.POWER:       (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.LOG:         (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.LOG10:       (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.EXP:         (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.SQRT:        (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.COS:         (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.SIN:         (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.TAN:         (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.COSH:        (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.SINH:        (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        InsType.TANH:        (parse_function,        "FUNCTION_CALL"),  # noqa: E241
        # DataSource
        InsType.DATA_SOURCE: (parse_data_source,     "QUERY_DATA_SOURCE"),  # noqa: E241
        # Special cases for RANK and FLAG
        InsType.RANK_ACROSS_CATEGORY:  (parse_rank_flag,       "RANK_FLAG"),  # noqa: E241
        InsType.RANK_ACROSS_CATEGORY_ALL_AVAILABLE_ALT: (parse_rank_flag, "RANK_ACROSS_CATEGORY_ALL_AVAILABLE_ALT"),  # noqa: E241
        InsType.RANK_ACROSS_CATEGORY_ALT: (parse_rank_flag, "RANK_ACROSS_CATEGORY_ALT"),  # noqa: E241
        InsType.SET_UNDERWRITING_TO_FAIL: (parse_empty, "SET_UNDERWRITING_TO_FAIL"),  # noqa: E241
    }

    parser_func_tuple = dispatch_map.get(ins_type) if ins_type is not None else None
    if parser_func_tuple is not None:
        parser_func, template_id = parser_func_tuple
        # Some parsers need raw_ins + algorithm_or_dependency + program_version
        if parser_func in (parse_if, parse_if_date, parse_data_source):
            return parser_func(tokens, raw_ins, algorithm_or_dependency, program_version, template_id)  # type: ignore

        return parser_func(tokens, step, ins_type, algorithm_or_dependency, program_version, template_id)  # type: ignore

    # 4) Fallback: if no InsType matched, produce a RawNode
    desc = get_var_desc(ins_str, algorithm_or_dependency, program_version)
    return [RawNode(step=step, ins_type=ins_type, raw=ins_str, value=desc)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_rank_flag(
    tokens: list[Token],
    step: int,
    ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
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
    return [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=action_text, value=desc)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_sort(tokens: list[Token], step: int, ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",) -> list[ASTNode]:
    """Stub for Sort instruction."""
    text = "Sort: " + " ".join(t.value for t in tokens)
    return [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw="", value=text)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_mask(tokens: list[Token], step: int, ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",) -> list[ASTNode]:
    """Stub for Mask instruction."""
    text = "Mask: " + " ".join(t.value for t in tokens)

    return [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw="", value=text)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_empty(tokens: list[Token], step: int, ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",) -> list[ASTNode]:
    """Empty instruction (no‐op)."""
    return []


# ──────────────────────────────────────────────────────────────────────────────
def parse_set_string(
    tokens: list[Token], step: int, ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
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
            expr=RawNode(step=step, ins_type=ins_type, template_id=template_id, raw="", value=literal),
            target=None,
            template_id=template_id,
            next_true=None,
            next_false=None,
        )
        return [assign]

    # Fallback
    return [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw="", value=" ".join(t.value for t in tokens))]


# ──────────────────────────────────────────────────────────────────────────────
def parse_string_addition(
    tokens: list[Token],
    raw_ins: dict,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
) -> list[ASTNode]:
    """String Addition: build a FunctionNode that concatenates all tokens,
    stripping '[' and ']' but preserving them in `raw`, and looking up
    human-friendly descriptions for each piece and for the overall summary.
    """
    # 1) pull step and ins_type out of the raw_ins dict
    step     = int(raw_ins.get("n", 0))
    ins_type = InsType(int(raw_ins.get("t", 0)))

    # 2) build a RawNode for each token, stripping brackets only for lookup
    args: list[RawNode] = []
    for t in tokens:
        original = t.value
        clean    = original.replace("[", "").replace("]", "")
        desc     = get_var_desc(clean, algorithm_or_dependency, program_version)
        args.append(
            RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=original, value=desc)
        )

    return [
        FunctionNode(
            step=step,
            ins_type=ins_type,
            name="StringAddition",
            template_id=template_id,
            args=args,
            # english omitted; renderer will handle
        )
    ]

# ──────────────────────────────────────────────────────────────────────────────
def parse_date_diff(
    tokens: list[Token], step: int, ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
) -> list[ASTNode]:
    """Parse DATE_DIFF_* into a FunctionNode; all verbalization happens in renderer.py."""
    # 1) pull out the raw token values
    if len(tokens) >= 2:
        left_val, right_val = tokens[0].value, tokens[1].value
    else:
        left_val = tokens[0].value if tokens else ""
        right_val = ""

    # 2) look up their “nice” descriptions, but do *not* build any English sentence here
    left_desc  = get_var_desc(left_val, None, None)
    right_desc = get_var_desc(right_val, None, None)

    left_node  = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=left_val,  value=left_desc)
    right_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=right_val, value=right_desc)

    # 3) Emit only the structural AST
    return [
        FunctionNode(
            step=step,
            ins_type=ins_type,
            name="DateDifference",        # or ins_type.name
            args=[left_node, right_node],
        )
    ]


# ──────────────────────────────────────────────────────────────────────────────
def parse_date_addition(
    tokens: list[Token], step: int, ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
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

    date_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=date_val, value=date_val)
    offset_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=offset_val, value=offset_val)


    return [
        FunctionNode(
            step=step,
            ins_type=ins_type,
            name="DateAddition",
            template_id=template_id,
            args=[date_node, offset_node],
        )
    ]


# ──────────────────────────────────────────────────────────────────────────────
def parse_if_date(
    tokens: list[Token], raw_ins: dict,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
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
    left_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=left_val, value=left_desc)

    right_desc = get_var_desc(left_val, algorithm_or_dependency, program_version)
    right_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=right_val, value=right_desc)
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

    next_true = int(seq_t) if seq_t is not None else None
    next_false = int(seq_f) if seq_f is not None else None

    node = IfNode(
        step=step, ins_type=ins_type, template_id=template_id, condition=condition, true_branch=[], false_branch=[]
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
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
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
    left_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=left_val, value=desc_left)
    desc_right = get_var_desc(right_val, algorithm_or_dependency, program_version)
    right_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=right_val, value=desc_right)

    condition = CompareNode(
        step=step,
        ins_type=ins_type,
        left=left_node,
        operator=operator,
        right=right_node,
        english=""
    )

    node = IfNode(step=step, ins_type=ins_type, template_id=template_id, condition=condition, true_branch=[], false_branch=[])

    # 2) Wire up true/false branches via seq_t / seq_f if available
    seq_t = raw_ins.get("seq_t")
    seq_f = raw_ins.get("seq_f")

    next_true = int(seq_t) if seq_t is not None else None
    next_false = int(seq_f) if seq_f is not None else None

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
                    node.true_branch = [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw="", value=f"ERROR: {e}")]

        # False branch
        if next_false is not None:
            raw_false = next((i for i in steps_list if int(i.get("n", 0)) == next_false), None)
            if raw_false:
                try:
                    node.false_branch = decode_ins(raw_false, algorithm_or_dependency, program_version)
                except Exception as e:
                    node.false_branch = [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw="", value=f"ERROR: {e}")]

    return [node]


# ──────────────────────────────────────────────────────────────────────────────
def parse_arithmetic(tokens: list[Token], step: int, ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",) -> list[ASTNode]:
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

        left_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=left_val, value=left_val)
        right_node = RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=right_val, value=right_val)
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
            template_id=template_id,
            right=right_node,
            round_spec=round_spec,
            round_english=round_eng,
        )
        return [node]

    # Fallback
    return [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw="", value=" ".join(t.value for t in tokens))]


# ──────────────────────────────────────────────────────────────────────────────
def parse_function(tokens: list[Token], step: int, ins_type: InsType,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",) -> list[ASTNode]:
    """Generic parser for math & trigonometry functions.
    Handles single‐arg (SQRT, LOG, etc.) and two‐arg (POWER, etc.) + optional rounding.
    """
    round_spec = None
    if tokens and tokens[-1].value.startswith("!"):
        round_token = tokens[-1].value
        round_spec = round_token[1:]
        tokens = tokens[:-1]

    args = [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=t.value, value=t.value) for t in tokens]

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

    node = FunctionNode(step=step, ins_type=ins_type, template_id=template_id, name=ins_type.name, args=args, english=english)
    return [node]


# ──────────────────────────────────────────────────────────────────────────────
def parse_call(
    tokens: list[Token], raw_ins: dict,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
) -> list[ASTNode]:
    """Stub for CALL instruction.
    This can be updated later to construct an actual FunctionNode or similar.
    For now, we produce a RawNode placeholder.
    """
    step = int(raw_ins.get("n", 0))
    ins_type = InsType(int(raw_ins.get("t", 0)))
    call_text = "Call: " + (raw_ins.get("ins") or "")
    return [RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=call_text, value=call_text)]


# ──────────────────────────────────────────────────────────────────────────────
def parse_data_source(
    tokens: list[Token], raw_ins: dict,
    algorithm_or_dependency: Algorithm | DependencyBase | None = None,
    program_version: ProgramVersion | None = None,
    template_id: str = "",
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
        args=[RawNode(step=step, ins_type=ins_type, template_id=template_id, raw=tok.value, value=tok.value) for tok in tokens],
        english="DataSource call not implemented",
    )
    return [node]
