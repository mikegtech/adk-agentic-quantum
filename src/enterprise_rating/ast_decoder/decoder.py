from .defs import InsType
from .parser import (
    parse,
    parse_arithmetic,
    parse_call,
    parse_data_source,
    parse_date_addition,
    parse_date_diff,
    parse_empty,
    parse_function,
    parse_if,
    parse_mask,
    parse_set_string,
    parse_sort,
    parse_string_addition,
)
from .tokenizer import tokenize


def decode_ins(raw_ins: dict, algorithm_seq, program_version) -> list:
    """Entrypoint: decode one instruction dict into a list of AST nodes.
    Dispatches to specialized parsing functions based on InsType.
    """
    ins_str = raw_ins.get('ins', '')
    tokens = tokenize(ins_str)

    try:
        ins_type = InsType(int(raw_ins.get('t')))
    except (ValueError, TypeError):
        ins_type = None

    # Multi-IF segments
    if ins_str and '^' in ins_str:
        return parse_if(tokens, raw_ins, algorithm_seq, program_version)

    dispatch_map = {
        InsType.ARITHMETIC:    lambda: parse_arithmetic(tokens, raw_ins, algorithm_seq, program_version),
        InsType.IF:            lambda: parse_if(tokens, raw_ins, algorithm_seq, program_version),
        InsType.CALL:          lambda: parse_call(tokens, raw_ins, algorithm_seq, program_version),
        InsType.SORT:          lambda: parse_sort(tokens, raw_ins, algorithm_seq, program_version),
        InsType.MASK:          lambda: parse_mask(tokens, raw_ins, algorithm_seq, program_version),
        InsType.SET_STRING:    lambda: parse_set_string(tokens, raw_ins, algorithm_seq, program_version),
        InsType.EMPTY:         lambda: parse_empty(tokens, raw_ins, algorithm_seq, program_version),
        InsType.STRING_ADDITION: lambda: parse_string_addition(tokens, raw_ins, algorithm_seq, program_version),
        InsType.DATE_DIFF_DAYS:   lambda: parse_date_diff(tokens, raw_ins, algorithm_seq, program_version),
        InsType.DATE_DIFF_MONTHS: lambda: parse_date_diff(tokens, raw_ins, algorithm_seq, program_version),
        InsType.DATE_DIFF_YEARS:  lambda: parse_date_diff(tokens, raw_ins, algorithm_seq, program_version),
        InsType.DATE_ADDITION:    lambda: parse_date_addition(tokens, raw_ins, algorithm_seq, program_version),
        # Math/Trig
        InsType.POWER:         lambda: parse_function(tokens, raw_ins, algorithm_seq, program_version),
        InsType.LOG:           lambda: parse_function(tokens, raw_ins, algorithm_seq, program_version),
        InsType.LOG10:         lambda: parse_function(tokens, raw_ins, algorithm_seq, program_version),
        InsType.EXP:           lambda: parse_function(tokens, raw_ins, algorithm_seq, program_version),
        InsType.SQRT:          lambda: parse_function(tokens, raw_ins, algorithm_seq, program_version),
        InsType.COS:           lambda: parse_function(tokens, raw_ins, algorithm_seq, program_version),
        InsType.SIN:           lambda: parse_function(tokens, raw_ins, algorithm_seq, program_version),
        InsType.TAN:           lambda: parse_function(tokens, raw_ins, algorithm_seq, program_version),
        # DataSource
        InsType.DATA_SOURCE:   lambda: parse_data_source(tokens, raw_ins, algorithm_seq, program_version)
    }

    parser_func = dispatch_map.get(ins_type)
    if parser_func:
        return parser_func()

    # Fallback
    return parse(tokens, raw_ins, algorithm_seq, program_version)
