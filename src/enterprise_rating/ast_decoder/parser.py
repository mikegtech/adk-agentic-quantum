from .ast_nodes import ArithmeticNode, AssignmentNode, ASTNode, CompareNode, FunctionNode, IfNode, RawNode
from .decode_mif import decode_mif
from .defs import InsType
from .helpers.ins_helpers import get_operator_english, get_round_english
from .helpers.var_lookup import get_var_desc
from .tokenizer import Token


def parse(tokens: list[Token], raw_ins: dict, algorithm_seq, program_version) -> list[ASTNode]:
    """Main parser dispatcher: chooses a parse function based on InsType.
    """
    try:
        ins_type = InsType(int(raw_ins.get("t")))
    except (ValueError, TypeError):
        ins_type = None

    step = int(raw_ins.get("n"))
    ins_str = raw_ins.get("ins", "")

    # 1) Multi-IF detection: if '^' appears, delegate to decode_mif
    if ins_str and "^" in ins_str:
        return decode_mif(ins_str, algorithm_seq, program_version)

    # 2) Handle Ranking & Flag instructions generically
    if ins_type and (ins_type.name.startswith("RANK") or ins_type.name.startswith("FLAG")):
        return parse_rank_flag(tokens, step, ins_type, algorithm_seq, program_version)

    # 3) Dispatch map for all supported InsType values
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
        # Math & Trig
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
        # DataSource queries
        InsType.DATA_SOURCE: parse_data_source,
    }

    parser_func = dispatch_map.get(ins_type)
    if parser_func:
        # Some parsers need the raw_ins + algorithm_seq + program_version
        if parser_func in (parse_if, parse_if_date, parse_data_source):
            return parser_func(tokens, raw_ins, algorithm_seq, program_version)
        else:
            return parser_func(tokens, step, ins_type)

    # 4) Fallback: wrap entire ins_str in a RawNode
    return [RawNode(step=step, ins_type=ins_type, value=ins_str)]


# ---------- Ranking & Flag Instructions ----------

def parse_rank_flag(tokens: list[Token], step: int, ins_type: InsType, algorithm_seq, program_version) -> list[ASTNode]:
    """Generic parser for any InsType whose name begins with 'RANK' or 'FLAG'.
    Produces a RawNode with a human-readable description of the action.
    """
    # Build English text: replace underscores with spaces, title-case
    action_text = ins_type.name.replace("_", " ").title()
    # Expand any variable tokens via get_var_desc if present
    vars_expanded = []
    for t in tokens:
        if t.type == 'WORD' and ('GI_' in t.value or 'GC_' in t.value):
            vars_expanded.append(get_var_desc(t.value, algorithm_seq, program_version))
        else:
            vars_expanded.append(t.value)
    if vars_expanded:
        action_text += ": " + ", ".join(vars_expanded)
    return [RawNode(step=step, ins_type=ins_type, value=action_text)]


# ---------- Parser stubs for simple types ----------

def parse_sort(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Stub for a Sort instruction: output a RawNode with an English tag."""
    text = "Sort: " + " ".join(t.value for t in tokens)
    return [RawNode(step=step, ins_type=ins_type, value=text)]


def parse_mask(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Stub for a Mask instruction: output a RawNode with an English tag."""
    text = "Mask: " + " ".join(t.value for t in tokens)
    return [RawNode(step=step, ins_type=ins_type, value=text)]


def parse_empty(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Empty instruction (no-op)."""
    return []


# ---------- Set String and String Addition ----------

def parse_set_string(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Set String: usually of the form VAR [literal_string].
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
            next_false=None
        )
        return [assign]

    # Fallback if unexpected format:
    return [RawNode(step=step, ins_type=ins_type, value=" ".join(t.value for t in tokens))]


def parse_string_addition(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """String Addition: build a FunctionNode with all tokens as arguments.
    Name it 'StringAddition' and no rounding is applied.
    """
    args = [RawNode(step=step, ins_type=ins_type, value=t.value) for t in tokens]
    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name="StringAddition",
        args=args,
        english="Concatenate " + " + ".join(t.value for t in tokens)
    )
    return [node]

# ---------- If Instructions ----------
def parse_if(tokens: list[Token], raw_ins: dict, algorithm_seq, program_version) -> list[ASTNode]:
    """Parse a standard IF instruction (InsType.IF).
    Builds a CompareNode for the condition and wires true/false branches via seq_t/seq_f.
    """
    step = int(raw_ins.get("n"))
    ins_type = InsType(int(raw_ins.get("t")))
    ins_str = raw_ins.get("ins", "")

    # Extract the first three tokens as left operand, operator, right operand
    left_val = tokens[0].value if len(tokens) > 0 else ""
    op_val = tokens[1].value if len(tokens) > 1 else ""
    right_val = tokens[2].value if len(tokens) > 2 else ""

    # Create RawNodes for the operands
    left_node = RawNode(step=step, ins_type=ins_type, value=left_val)
    right_node = RawNode(step=step, ins_type=ins_type, value=right_val)
    english_op = get_operator_english(op_val)

    # Build the CompareNode for the condition
    condition = CompareNode(
        step=step,
        ins_type=ins_type,
        left=left_node,
        operator=op_val,
        right=right_node,
        english=english_op
    )

    # Parse the next‐step indices from raw_ins
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

    # Create the IfNode with empty branches for now
    node = IfNode(
        step=step,
        ins_type=ins_type,
        condition=condition,
        true_branch=[],
        false_branch=[]
    )

    # Wire the true branch if a next_true step is provided
    if next_true is not None:
        raw_true = next(
            (instr for instr in algorithm_seq.algorithm if int(instr.get("n")) == next_true),
            None
        )
        if raw_true:
            # Local import to break the circular dependency
            from .decoder import decode_ins
            node.true_branch = decode_ins(raw_true, algorithm_seq, program_version)


    # Wire the false branch if a next_false step is provided
    if next_false is not None:
        raw_false = next(
            (instr for instr in algorithm_seq.algorithm if int(instr.get("n")) == next_false),
            None
        )
        if raw_false:
            node.false_branch = decode_ins(raw_false, algorithm_seq, program_version)

    return [node]

# ---------- Date-and-Time Functions ----------

def parse_date_diff(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Parse Date Difference instructions.
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
        InsType.DATE_DIFF_YEARS: "Years"
    }
    unit = unit_map.get(ins_type, "")
    name = f"Date Difference ({unit})"
    english = f"Difference in {unit} between {left_val} and {right_val}"

    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name=name,
        args=[left_node, right_node],
        english=english
    )
    return [node]


def parse_date_addition(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Parse Date Addition instructions: [base_date_or_var, offset_spec].
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
        english=english
    )
    return [node]


def parse_if_date(tokens: list[Token], raw_ins: dict, algorithm_seq, program_version) -> list[ASTNode]:
    """Parse IF_DATE instructions (InsType.IF_DATE = 56).
    Builds a CompareNode inside an IfNode, wires true/false branches via seq_t/seq_f.
    """
    step = int(raw_ins.get("n"))
    ins_type = InsType(int(raw_ins.get("t")))

    # Extract condition tokens
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
        english=f"Date {english_op}"
    )

    # Pull next-step indices from raw_ins
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

    # Wire true branch
    if next_true is not None:
        raw_true = next(
            (instr for instr in algorithm_seq.algorithm if int(instr.get("n")) == next_true),
            None
        )
        if raw_true:
            # Local import to break the circular dependency
            from .decoder import decode_ins
            node.true_branch = decode_ins(raw_true, algorithm_seq, program_version)

    # Wire false branch
    if next_false is not None:
        raw_false = next(
            (instr for instr in algorithm_seq.algorithm if int(instr.get("n")) == next_false),
            None
        )
        if raw_false:
            from .decoder import decode_ins
            node.false_branch = decode_ins(raw_false, algorithm_seq, program_version)

    return [node]


# ---------- Math & Trig Functions ----------

def parse_arithmetic(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Parse arithmetic expressions into an ArithmeticNode.
    Expected format: VAR operator VAR [round_spec]
    where round_spec may come as a token like "!RN", "!RP2", etc.
    """
    round_spec = None
    # Detect rounding token (e.g. "!RN", "!RP2", "!RM1") at end
    if tokens and tokens[-1].value.startswith("!"):
        round_token = tokens[-1].value
        round_spec = round_token[1:]  # strip leading '!'
        tokens = tokens[:-1]  # remove rounding token

    # Now tokens should be [left, operator, right]
    if len(tokens) >= 3:
        left_val = tokens[0].value
        operator = tokens[1].value
        right_val = tokens[2].value

        left_node = RawNode(step=step, ins_type=ins_type, value=left_val)
        right_node = RawNode(step=step, ins_type=ins_type, value=right_val)

        # Convert rounding spec to English if present
        round_eng = get_round_english(round_spec) if round_spec else None

        # English description: e.g. "Compute GI_84 plus GC_47 then Round Up 2 place(s)"
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
            round_english=round_eng
        )
        return [node]

    # Fallback
    return [RawNode(step=step, ins_type=ins_type, value=" ".join(t.value for t in tokens))]


def parse_function(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Generic parser for math & trigonometry functions.
    - For two-argument functions (e.g. POWER), tokens = [base, exponent] or [arg1, arg2]
    - For single-argument (SQRT, LOG, SIN, COS, etc.), tokens = [arg]
    Builds a FunctionNode with a descriptive English phrase and handles rounding suffix if present.
    """
    # Detect rounding token at end
    round_spec = None
    if tokens and tokens[-1].value.startswith("!"):
        round_token = tokens[-1].value
        round_spec = round_token[1:]
        tokens = tokens[:-1]

    # Build argument nodes
    args = [RawNode(step=step, ins_type=ins_type, value=t.value) for t in tokens]

    # Function name
    func_name = ins_type.name.title()  # e.g. 'Sqrt', 'Log10'

    # Human-friendly name mapping for certain functions
    friendly_map = {
        'POWER': 'Power',
        'LOG': 'Natural Log',
        'LOG10': 'Log Base 10',
        'EXP': 'Exponential',
        'SQRT': 'Square Root',
        'COS': 'Cosine',
        'SIN': 'Sine',
        'TAN': 'Tangent',
        'COSH': 'Hyperbolic Cosine',
        'SINH': 'Hyperbolic Sine',
        'TANH': 'Hyperbolic Tangent'
    }
    display_name = friendly_map.get(ins_type.name, func_name)

    # Build English phrase
    if len(tokens) == 1:
        english = f"Compute {display_name} of {tokens[0].value}"
    elif len(tokens) == 2:
        english = f"Compute {display_name} of {tokens[0].value} and {tokens[1].value}"
    else:
        english = f"Compute {display_name}"

    # Append rounding English if present
    if round_spec:
        round_eng = get_round_english(round_spec)
        english += f" then {round_eng}"
    else:
        round_eng = None

    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name=ins_type.name,
        args=args,
        english=english
    )
    return [node]


# ---------- DataSource & Call ----------

def parse_data_source(tokens: list[Token], raw_ins: dict, algorithm_seq, program_version) -> list[ASTNode]:
    """Parse DataSource instructions (InsType.DATA_SOURCE = 200).
    Builds a FunctionNode named 'DataSource', returning placeholder if not implemented.
    """
    step = int(raw_ins.get("n"))
    ins_type = InsType(int(raw_ins.get("t")))

    # Extract source_id if available
    source_id = tokens[0].value if tokens else ""
    # Placeholder: not implemented
    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name="DataSource",
        args=[RawNode(step=step, ins_type=ins_type, value=tok.value) for tok in tokens],
        english="DataSource call not implemented"
    )
    return [node]


def parse_call(tokens: list[Token], step: int, ins_type: InsType) -> list[ASTNode]:
    """Parse generic CALL instructions (InsType.CALL = 2).
    Builds a FunctionNode named 'Call', returning placeholder if not implemented.
    """
    # Extract call_id if available
    call_id = tokens[0].value if tokens else ""
    # Placeholder: not implemented
    node = FunctionNode(
        step=step,
        ins_type=ins_type,
        name="Call",
        args=[RawNode(step=step, ins_type=ins_type, value=t.value) for t in tokens],
        english=f"Call {call_id} not implemented"
    )
    return [node]
