# enterprise_rating/ast_decoder/parser.py


from enterprise_rating.ast_decoder.helpers.var_extractor import find_next_var

from .ast_nodes import (ArithmeticNode, AssignmentNode, ASTNode, CompareNode,
                        FunctionNode, IfNode, RawNode)
from .decode_mif import decode_mif  # <-- import the new decode_mif
from .defs import InsType
from .helpers.ins_helpers import get_operator_english, get_round_english
from .helpers.var_lookup import get_var_desc
from .tokenizer import Token

# ──────────────────────────────────────────────────────────────────────────────
# Entry‐point dispatcher
# ──────────────────────────────────────────────────────────────────────────────

def parse(
    tokens: list[Token], raw_ins: dict, algorithm_seq=None, program_version=None
) -> list[ASTNode]:
    """Main parser dispatcher: inspects InsType and directs to the appropriate subparser.
    Supports algorithm_seq=None or program_version=None by skipping any lookups/jumps.
    """
    try:
        ins_type = InsType(int(raw_ins.get("t", 0)))
    except (ValueError, TypeError):
        ins_type = None

    step = int(raw_ins.get("n", 0))
    ins_str = raw_ins.get("ins", "") or ""

    # 1) Multi‐IF detection (caret‐separated conditions)
    if "^" in ins_str:
        # Pass the full raw_ins dict, not just the string, so that decode_mif
        # can copy seq_t, seq_f, etc. for each sub‐instruction.
        return decode_mif(raw_ins, algorithm_seq, program_version)

    # 2) Ranking & Flag instructions: handled generically
    if ins_type and (ins_type.name.startswith("RANK") or ins_type.name.startswith("FLAG")):
        return parse_rank_flag(tokens, step, ins_type, algorithm_seq, program_version)

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
        # Some parsers need raw_ins + algorithm_seq + program_version
        if parser_func in (parse_if, parse_if_date, parse_data_source):
            return parser_func(tokens, raw_ins, algorithm_seq, program_version)
        else:
            return parser_func(tokens, step, ins_type)

    # 4) Fallback: if no InsType matched, produce a RawNode
    return [RawNode(step=step, ins_type=ins_type, value=ins_str)]


# ──────────────────────────────────────────────────────────────────────────────
# Ranking & Flag (generic handler)
# ──────────────────────────────────────────────────────────────────────────────

def parse_rank_flag(
    tokens: list[Token], step: int, ins_type: InsType, algorithm_seq=None, program_version=None
) -> list[ASTNode]:
    """Generic parser for any InsType whose name begins with 'RANK' or 'FLAG'.
    If algorithm_seq or program_version is None, we skip get_var_desc lookups.
    """
    # Turn the enum name into a title‐cased phrase
    action_text = ins_type.name.replace("_", " ").title()

    vars_expanded = []
    for t in tokens:
        if (
            program_version is not None
            and algorithm_seq is not None
            and t.type == "WORD"
            and ("GI_" in t.value or "GC_" in t.value)
        ):
            # Only attempt lookup if we have both parent and program_version
            vars_expanded.append(get_var_desc(t.value, algorithm_seq, program_version))
        else:
            vars_expanded.append(t.value)

    if vars_expanded:
        action_text += ": " + ", ".join(vars_expanded)

    return [RawNode(step=step, ins_type=ins_type, value=action_text)]


# ──────────────────────────────────────────────────────────────────────────────
# Parser stubs for simple types
# ──────────────────────────────────────────────────────────────────────────────

def parse_sort(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Stub for Sort instruction."""
    text = "Sort: " + " ".join(t.value for t in tokens)
    return [RawNode(step=step, ins_type=ins_type, value=text)]


def parse_mask(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Stub for Mask instruction."""
    text = "Mask: " + " ".join(t.value for t in tokens)
    return [RawNode(step=step, ins_type=ins_type, value=text)]


def parse_empty(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Empty instruction (no‐op)."""
    return []


# ──────────────────────────────────────────────────────────────────────────────
# Set String and String Addition
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
            expr=RawNode(step=step, ins_type=ins_type, value=literal),
            target=None,
            next_true=None,
            next_false=None,
        )
        return [assign]

    # Fallback
    return [RawNode(step=step, ins_type=ins_type, value=" ".join(t.value for t in tokens))]


def parse_string_addition(
    tokens: list[Token], step: int, ins_type: InsType
) -> list[ASTNode]:
    """String Addition: build a FunctionNode with all tokens as args.
    Name it 'StringAddition' and no rounding is applied.
    """
    args = [RawNode(step=step, ins_type=ins_type, value=t.value) for t in tokens]
    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name="StringAddition",
        args=args,
        english="Concatenate " + " + ".join(t.value for t in tokens),
    )
    return [node]


# ──────────────────────────────────────────────────────────────────────────────
# Date‐and‐Time Functions
# ──────────────────────────────────────────────────────────────────────────────

def parse_date_diff(
    tokens: list[Token], step: int, ins_type: InsType
) -> list[ASTNode]:
    """Parse Date Difference instructions:
      - InsType.DATE_DIFF_DAYS  → unit = 'Days'
      - InsType.DATE_DIFF_MONTHS → unit = 'Months'
      - InsType.DATE_DIFF_YEARS → unit = 'Years'
    Expect tokens = [date_or_var1, date_or_var2].
    Builds a FunctionNode with name "Date Difference (unit)".
    """
    left_val = tokens[0].value if len(tokens) > 0 else ""
    right_val = tokens[1].value if len(tokens) > 1 else ""

    left_node = RawNode(step=step, ins_type=ins_type, value=left_val)
    right_node = RawNode(step=step, ins_type=ins_type, value=right_val)

    unit_map = {
        InsType.DATE_DIFF_DAYS: "Days",
        InsType.DATE_DIFF_MONTHS: "Months",
        InsType.DATE_DIFF_YEARS: "Years",
    }
    unit = unit_map.get(ins_type, "")
    name = f"Date Difference ({unit})"
    english = f"Difference in {unit} between {left_val} and {right_val}"

    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name=name,
        args=[left_node, right_node],
        english=english,
    )
    return [node]


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

    date_node = RawNode(step=step, ins_type=ins_type, value=date_val)
    offset_node = RawNode(step=step, ins_type=ins_type, value=offset_val)

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


def parse_if_date(
    tokens: list[Token], raw_ins: dict, algorithm_seq=None, program_version=None
) -> list[ASTNode]:
    """Parse IF_DATE instructions (InsType.IF_DATE = 56).
    Builds a CompareNode inside an IfNode, then wires true/false branches via seq_t/seq_f ONLY if algorithm_seq is provided.
    """
    from .decoder import \
        decode_ins  # local import to avoid circular references

    step = int(raw_ins.get("n", 0))
    ins_type = InsType(int(raw_ins.get("t", 0)))

    # Extract tokens for the condition
    left_val = tokens[0].value if len(tokens) > 0 else ""
    op_val = tokens[1].value if len(tokens) > 1 else ""
    right_val = tokens[2].value if len(tokens) > 2 else ""

    left_node = RawNode(step=step, ins_type=ins_type, value=left_val)
    right_node = RawNode(step=step, ins_type=ins_type, value=right_val)
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
        step=step,
        ins_type=ins_type,
        condition=condition,
        true_branch=[],
        false_branch=[],
    )

    # If algorithm_seq is provided, wire the branches; otherwise skip
    if algorithm_seq is not None:
        # Wire true branch
        if next_true is not None:
            raw_true = next(
                (
                    instr
                    for instr in algorithm_seq.algorithm
                    if int(instr.get("n", 0)) == next_true
                ),
                None,
            )
            if raw_true:
                node.true_branch = decode_ins(raw_true, algorithm_seq, program_version)

        # Wire false branch
        if next_false is not None:
            raw_false = next(
                (
                    instr
                    for instr in algorithm_seq.algorithm
                    if int(instr.get("n", 0)) == next_false
                ),
                None,
            )
            if raw_false:
                node.false_branch = decode_ins(raw_false, algorithm_seq, program_version)

    return [node]


def parse_if(
    tokens: List[Token],
    raw_ins: dict,
    algorithm_seq=None,
    program_version=None
) -> List[ASTNode]:
    """Parse a standard IF instruction (InsType.IF). We use find_next_var()
    to extract left, operator, right (and any rounding) from the raw ins string.
    Then wire up true/false branches using seq_t/seq_f if algorithm_seq is provided.
    """
    from .decoder import decode_ins  # avoid circular import

    step = int(raw_ins.get("n", 0))
    ins_type = InsType(int(raw_ins.get("t", 0)))
    ins_str = raw_ins.get("ins", "") or ""

    # --- Use find_next_var to extract the left operand and operator ---
    str_ptr = 0
    next_var, next_op, round_var, next_op_obj, round_var_obj, next_var_ptr = find_next_var(
        str_ptr, ins_str, str(ins_type.value)
    )

    left_node = RawNode(step=step, ins_type=ins_type, value=next_var)

    # --- Advance pointer: move str_ptr to after the operator object (next_op_obj) ---
    # find_next_var already moved str_ptr past next_op_obj and any roundVar,
    # so we set str_ptr to the returned next_var_ptr + len(next_var) + len(next_op_obj) + len(round_var_obj)
    str_ptr = next_var_ptr + len(next_var) + len(next_op_obj) + len(round_var_obj)

    # --- Now extract the right operand the same way ---
    right_var, right_op, right_round, right_op_obj, right_round_obj, right_var_ptr = find_next_var(
        str_ptr, ins_str, str(ins_type.value)
    )
    right_node = RawNode(step=step, ins_type=ins_type, value=right_var)

    # Build the CompareNode
    condition = CompareNode(
        step=step,
        ins_type=ins_type,
        left=left_node,
        operator=next_op_obj or next_op,  # raw operator (e.g. "<>") or English form
        right=right_node,
        english=next_op  # use the English operator for readability
    )

    # Next-step pointers
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
        step=step,
        ins_type=ins_type,
        condition=condition,
        true_branch=[],
        false_branch=[]
    )

    # If we have algorithm_seq, wire the branches
    if algorithm_seq is not None:
        if next_true is not None:
            raw_true = next(
                (
                    instr
                    for instr in algorithm_seq.algorithm
                    if int(instr.get("n", 0)) == next_true
                ), None
            )
            if raw_true:
                node.true_branch = decode_ins(raw_true, algorithm_seq, program_version)

        if next_false is not None:
            raw_false = next(
                (
                    instr
                    for instr in algorithm_seq.algorithm
                    if int(instr.get("n", 0)) == next_false
                ), None
            )
            if raw_false:
                node.false_branch = decode_ins(raw_false, algorithm_seq, program_version)

    return [node]



# ──────────────────────────────────────────────────────────────────────────────
# Arithmetic parser
# ──────────────────────────────────────────────────────────────────────────────

def parse_arithmetic(
    tokens: list[Token], step: int, ins_type: InsType
) -> list[ASTNode]:
    """Parse arithmetic expressions into an ArithmeticNode.
    Expected format: VAR operator VAR [round_spec]
    where round_spec might be '!RN', '!RP2', '!RM1', etc.
    """
    round_spec = None

    if tokens and tokens[-1].value.startswith("!"):
        round_token = tokens[-1].value
        round_spec = round_token[1:]  # strip '!'
        tokens = tokens[:-1]  # remove rounding token

    if len(tokens) >= 3:
        left_val = tokens[0].value
        operator = tokens[1].value
        right_val = tokens[2].value

        left_node = RawNode(step=step, ins_type=ins_type, value=left_val)
        right_node = RawNode(step=step, ins_type=ins_type, value=right_val)
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
    return [RawNode(step=step, ins_type=ins_type, value=" ".join(t.value for t in tokens))]


# ──────────────────────────────────────────────────────────────────────────────
# Math & Trig Functions parser
# ──────────────────────────────────────────────────────────────────────────────

def parse_function(
    tokens: list[Token], step: int, ins_type: InsType
) -> list[ASTNode]:
    """Generic parser for math & trigonometry functions.
    Handles single‐arg (SQRT, LOG, etc.) and two‐arg (POWER, etc.) + optional rounding.
    """
    round_spec = None
    if tokens and tokens[-1].value.startswith("!"):
        round_token = tokens[-1].value
        round_spec = round_token[1:]
        tokens = tokens[:-1]

    args = [RawNode(step=step, ins_type=ins_type, value=t.value) for t in tokens]

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

    node = FunctionNode(
        step=step, ins_type=ins_type, name=ins_type.name, args=args, english=english
    )
    return [node]


# ──────────────────────────────────────────────────────────────────────────────
# DataSource parser (placeholder)
# ──────────────────────────────────────────────────────────────────────────────

def parse_data_source(
    tokens: list[Token], raw_ins: dict, algorithm_seq=None, program_version=None
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
        args=[RawNode(step=step, ins_type=ins_type, value=tok.value) for tok in tokens],
        english="DataSource call not implemented",
    )
    return [node]


# ──────────────────────────────────────────────────────────────────────────────
# Call parser (placeholder)
# ──────────────────────────────────────────────────────────────────────────────

def parse_call(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Parse generic CALL instructions (InsType.CALL).
    Placeholder if program_version is None or no template logic is provided.
    """
    call_id = tokens[0].value if tokens else ""
    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name="Call",
        args=[RawNode(step=step, ins_type=ins_type, value=t.value) for t in tokens],
        english=f"Call {call_id} not implemented",
    )
    return [node]
