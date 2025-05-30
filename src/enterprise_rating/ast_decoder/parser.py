from .defs import InsType
from .tokenizer import tokenize
from .decoder import decode_ins
from .ast_nodes import RawNode, CompareNode, IfNode
from .helpers.ins_helpers import get_operator_english


def parse_if(tokens, raw_ins, algorithm_seq, program_version):
    """
    Handle IF instructions, wiring true/false branches.
    """
    # Basic instruction info
    step = int(raw_ins.get('n'))
    ins_type = InsType(int(raw_ins.get('t')))

    # Parse condition: first three tokens
    left_val  = tokens[0].value if len(tokens) > 0 else ''
    op_val    = tokens[1].value if len(tokens) > 1 else ''
    right_val = tokens[2].value if len(tokens) > 2 else ''

    left  = RawNode(step=step, ins_type=ins_type, value=left_val)
    right = RawNode(step=step, ins_type=ins_type, value=right_val)
    english_op = get_operator_english(op_val)

    condition = CompareNode(
        step=step,
        ins_type=ins_type,
        left=left,
        operator=op_val,
        right=right,
        english=english_op
    )

    # Determine branch targets
    seq_t = raw_ins.get('seq_t')
    seq_f = raw_ins.get('seq_f')
    try:
        next_true  = int(seq_t)
    except:
        next_true  = None
    try:
        next_false = int(seq_f)
    except:
        next_false = None

    # Build IfNode with placeholders
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
            (instr for instr in algorithm_seq.algorithm if int(instr.get('n')) == next_true),
            None
        )
        if raw_true:
            node.true_branch = decode_ins(raw_true, algorithm_seq, program_version)

    # Wire false branch
    if next_false is not None:
        raw_false = next(
            (instr for instr in algorithm_seq.algorithm if int(instr.get('n')) == next_false),
            None
        )
        if raw_false:
            node.false_branch = decode_ins(raw_false, algorithm_seq, program_version)

    return [node]
```python
from .defs import InsType
from .tokenizer import tokenize
from .decoder import decode_ins
from .ast_nodes import RawNode, CompareNode, IfNode
from .helpers.ins_helpers import get_operator_english, get_next_step_english


def parse_if(tokens, raw_ins, algorithm_seq, program_version):
    """
    Handle IF instructions, wiring true/false branches.
    """
    # Basic instruction info
    step = int(raw_ins.get('n'))
    ins_type = InsType(int(raw_ins.get('t')))
    ins_str = raw_ins.get('ins', '')

    # Parse condition: first three tokens
    left_val = tokens[0].value if len(tokens) > 0 else ''
    op_val   = tokens[1].value if len(tokens) > 1 else ''
    right_val= tokens[2].value if len(tokens) > 2 else ''

    left  = RawNode(step=step, ins_type=ins_type, value=left_val)
    right = RawNode(step=step, ins_type=ins_type, value=right_val)
    english_op = get_operator_english(op_val)

    condition = CompareNode(
        step=step,
        ins_type=ins_type,
        left=left,
        operator=op_val,
        right=right,
        english=english_op
    )

    # Determine branch targets
    seq_t = raw_ins.get('seq_t')
    seq_f = raw_ins.get('seq_f')
    try:
        next_true  = int(seq_t)
    except:
        next_true  = None
    try:
        next_false = int(seq_f)
    except:
        next_false = None

    # Build IfNode with empty branches
    node = IfNode(
        step=step,
        ins_type=ins_type,
        condition=condition,
        next_true=next_true,
        next_false=next_false,
        true_branch=[],
        false_branch=[]
    )

    # Wire true branch
    if next_true:
        raw_true = next((instr for instr in algorithm_seq.algorithm if int(instr.get('n')) == next_true), None)
        if raw_true:
            node.true_branch = decode_ins(raw_true, algorithm_seq, program_version)

    # Wire false branch
    if next_false:
        raw_false = next((instr for instr in algorithm_seq.algorithm if int(instr.get('n')) == next_false), None)
        if raw_false:
            node.false_branch = decode_ins(raw_false, algorithm_seq, program_version)

    return [node]