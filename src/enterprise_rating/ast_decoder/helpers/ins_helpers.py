def decode_filter_rule(filter_rule: str, dependency_var_writer, dependency_list) -> None:
    """Stub for DecodeFilterRule: splits filter rules by '-' and writes
    dependency variables to writer.
    """
    if not filter_rule:
        return
    parts = filter_rule.split('-')
    if len(parts) != 4:
        return
    prefix = 'GC_' if parts[1] == '0' else 'PC_'
    var_key = f"{prefix}{parts[2]}"
    # TODO: write var_key to dependency_var_writer and update dependency_list
    pass


def get_operator_english(oper: str) -> str:
    """Stub for GetOperatorEnglish: maps symbol to English phrase.
    """
    mapping = {
        '=': 'equals',
        '>': 'greater than',
        '<': 'less than',
        '<=': 'less than or equal to',
        '>=': 'greater than or equal to',
        '!=': 'not equal to',
        '<>': 'not equal to',
        '@': 'bitwise AND',
        '^': 'bitwise OR'
    }
    return mapping.get(oper, oper)


def get_round_english(round_spec: str) -> str:
    """Stub for GetRoundEnglish: describes rounding spec in English.
    """
    # TODO: handle 'RP', 'RM', 'RN', 'NR', 'RS' prefixes
    return round_spec


def get_next_step_english(next_step: str, current_ins_number: int) -> str:
    """Stub for GetNextStepEnglish: translates jump targets to human text.
    """
    if next_step == str(-2):
        return 'EXIT_LOOP'
    if next_step == str(-1):
        return 'DONE'
    if next_step.lower() == str(1):
        return 'Return True'
    if next_step == str(0):
        return f'Step {current_ins_number + 1}'
    return f'Step {next_step}'
