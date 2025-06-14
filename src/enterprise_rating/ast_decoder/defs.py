from enum import Enum

VAR_PREFIXES = {
    "LS",  # "Results of Step <ID>"
    "PL",  # "Program Lookup Variables"
    "GL",  # "Global Lookup Variables"
    "GI",  # "Global Input Variables"        ← special: use data_dictionary
    "GR",  # "Global Result Variables"
    "PR",  # "Global Result Variables" (alias to GR)
    "PC",  # "Program Calculated Variables"
    "GC",  # "Global Calculated Variables"
    "PP",  # "Program Policy Variables"
    "GP",  # "Global Calculated Variables (type 1)"
    "IG",  # "Instructions Groups (local)"
    "LX",  # "System Variable"
    "IX",  # "System Variable (alias)"
    "PQ",  # "Local Data Source Variables"
    "GQ",  # "Global Data Source Variables"
    # (Your proc also had LX/IX for SYSTEM_VARS; PQ, GQ for data sources.)
}

class InsType(Enum):
    """Enumeration of instruction types used in the enterprise rating AST decoder."""

    UNKNOWN = -1  # Invalid Type
    ARITHMETIC = 0  # Arithmetic
    IF = 1  # IF
    CALL = 2  # Call
    SORT = 3  # Sort
    MASK = 4  # Mask
    SET_STRING = 5  # Set String
    EMPTY = 6  # Empty
    FLAG_DRVS_ALL = 7  # Flag Drvs [All]
    FLAG_DRVS_FROM_FLAG_DRVS = 8
    ASSIGN_1ST_RANKED_VEH_TO_FLAG_DRV = 9
    ASSIGN_VEH_USUALLY_DRIVEN_BY_FLAG_DRV = 10
    ASSIGN_1ST_RANKED_VEH_TO_1ST_RANKED_DRV = 11
    ASSIGN_VEH_USUALLY_DRIVEN_BY_UNASSIGNED_DRVS = 12
    ISO_NOT_IMPLEMENTED = 13
    RANK_ALL_DRIVERS_LOW_TO_HIGH = 14
    RANK_FLAGGED_DRVS_LOW_TO_HIGH = 15
    RANK_ALL_DRVS_TO_ALL_VEHS = 16
    RANK_ALL_VEHS_LOW_TO_HIGH = 17
    RANK_ASSIGNED_VEHS_LOW_TO_HIGH = 18
    RANK_UNASSIGNED_VEHS_LOW_TO_HIGH = 19
    FLAG_DRVS_ASSIGNED = 20
    FLAG_DRVS_UNASSIGNED = 21
    ASSIGN_FLAG_DRV_TO_ALL_UNASSIGNED_VEHS = 22
    ASSIGN_FLAG_DRV_TO_FIRST_UNASSIGNED_VEH = 23
    MODIFY_FLAG_DRVS = 24
    MODIFY_ALL_DRVS = 25
    ASSIGN_LAST_RANKED_VEH_TO_FLAGGED_DRV = 26
    ASSIGN_LAST_RANKED_VEH_TO_LOW_RATED_DRV = 27
    RECALCULATE_VEHICLE_USAGE = 28
    FLAG_LAST_RANKED_DRV = 29
    FLAG_1ST_RANKED_DRV = 30
    ASSIGN_VEH_USUALLY_DRIVEN_BY_RANKED_DRV_HIGH_TO_LOW = 31
    ASSIGN_VEH_USUALLY_DRIVEN_BY_RANKED_DRV_LOW_TO_HIGH = 32
    ASSIGN_VEHS_BY_DRV_USAGE_USING_1ST_RANKED_VEH = 33
    ASSIGN_VEHS_BY_DRV_USAGE_USING_LAST_RANKED_VEH = 34
    ASSIGN_VEHS_BY_HIGHEST_PREMIUM_COMBINATION_EX = 35
    ASSIGN_VEHS_BY_LOWEST_PREMIUM_COMBINATION_EX = 36
    ASSIGN_VEHS_BY_HIGHEST_PREMIUM_COMBINATION_NON_EX = 37
    ASSIGN_VEHS_BY_LOWEST_PREMIUM_COMBINATION_NON_EX = 38
    RANK_ALL_DRVS_TO_ALL_UNASSIGNED_VEHS = 39
    ASSIGN_VEHS_USING_DA_OVERRIDE_INPUTS = 40
    ASSIGN_VEHS_TO_HIGHEST_PREMIUM_DRV = 41
    ASSIGN_VEHS_TO_LOWEST_PREMIUM_DRV = 42
    RANK_ALL_DRVS_HIGH_TO_LOW = 43
    RANK_FLAGGED_DRVS_HIGH_TO_LOW = 44
    RANK_ALL_VEHS_HIGH_TO_LOW = 47
    RANK_ASSIGNED_VEHS_HIGH_TO_LOW = 48
    RANK_UNASSIGNED_VEHS_HIGH_TO_LOW = 49
    IF_ALL_ALL = 50
    IF_NO_ALL = 51
    IF_ANY_ALL = 52
    IF_ALL_USE_CURRENT_PATH = 53
    IF_NO_USE_CURRENT_PATH = 54
    IF_ANY_USE_CURRENT_PATH = 55
    IF_DATE = 56
    DATE_DIFF_DAYS = 57
    DATE_DIFF_MONTHS = 58
    DATE_DIFF_YEARS = 59
    SUM_ACROSS_CATEGORY_ALL_AVAILABLE = 60
    PRODUCT_ACROSS_CATEGORY_ALL_AVAILABLE = 61
    FLAG_1ST_RANKED_VEH = 62
    FLAG_LAST_RANKED_VEH = 63
    FLAG_ALL_VEHS = 64
    FLAG_ASSIGNED_VEHS = 65
    FLAG_UNASSIGNED_VEHS = 66
    FLAG_VEH_FROM_FLAGGED_VEH = 67
    MODIFY_FLAGGED_VEH_INPUTS = 68
    MODIFY_ALL_VEH_INPUTS = 69
    CLEAR_VEH_RANKING = 70
    CLEAR_DRV_RANKING = 71
    SET_PRINCIPAL_OPERATOR_VARIABLE = 80
    ASSIGN_UNASSIGNED_VEHS_BY_PRINC_OP_EXCLUSIVE = 81
    ASSIGN_ALL_VEHS_BY_PRINC_OP_NONEXCLUSIVE = 82
    ASSIGN_UNASSIGNED_VEHS_BY_PRINC_OP_NONEXCLUSIVE = 83
    ABSOLUTE_VALUE = 84
    STRING_LENGTH = 85
    STRING_ADDITION = 86
    SUM_ACROSS_CATEGORY_USE_CURRENT_PATH = 87
    PRODUCT_ACROSS_CATEGORY_USE_CURRENT_PATH = 88
    COUNT_ACROSS_CATEGORY_ALL_AVAILABLE = 89
    COUNT_ACROSS_CATEGORY_USE_CURRENT_PATH = 90
    RANK_ACROSS_CATEGORY_ALL_AVAILABLE = 93
    RANK_ACROSS_CATEGORY = 94
    IS_DATE = 95
    CLEAR_RANKING = 97
    IS_NUMERIC = 98
    IS_ALPHA = 99
    ASSIGN_VEH_USUALLY_DRIVEN_ALL_BY_FLAG_DRV = 100
    ASSIGN_VEH_USUALLY_DRIVEN_ALL_BY_RANKED_DRV_HIGH_TO_LOW = 101
    ASSIGN_VEH_USUALLY_DRIVEN_ALL_BY_RANKED_DRV_LOW_TO_HIGH = 102
    ASSIGN_VEH_USUALLY_DRIVEN_ALL_BY_RANKED_DRV_ALL_HIGH_TO_LOW = 106
    ASSIGN_VEH_USUALLY_DRIVEN_ALL_BY_RANKED_DRV_ALL_LOW_TO_HIGH = 107
    ASSIGN_1ST_RANKED_VEH_TO_1ST_RANKED_DRV_WITH_EXCLUSION = 108
    RANK_ALL_DRIVERS_VS_ALL_VEHICLES_SEQ = 110
    ASSIGN_1ST_RANKED_VEH_TO_1ST_RANKED_DRV_SEQ = 111
    ASSIGN_1ST_RANKED_VEH_TO_1ST_RANKED_DRV_SEQ_WITH_EXCLUSION = 112
    FLAG_DRVS_ALL_USAGE_SET = 113
    RANK_ALL_DRVS_LOW_TO_HIGH_USAGE_SET = 114
    RANK_ALL_DRIVERS_HIGH_TO_LOW_USAGE_SET = 115
    ASSIGN_1ST_RANKED_VEH_TO_1ST_RANKED_DRV_USAGE_SET = 116
    CLEAR_DRV_RANKING_USAGE_SET = 117
    RANK_ALL_DRVS_LOW_TO_HIGH_USAGE_SET_CONDITIONAL = 118
    RANK_ALL_DRIVERS_HIGH_TO_LOW_USAGE_SET_CONDITIONAL = 119
    GET_CATEGORY_ITEM_USE_CURRENT_PATH = 120
    SET_CATEGORY_ITEM_USE_CURRENT_PATH = 121
    GET_RANKED_CATEGORY_ITEM = 122
    SET_RANKED_CATEGORY_ITEM = 123
    GET_CATEGORY_ITEM_ALL_AVAILABLE = 124
    SET_CATEGORY_ITEM_ALL_AVAILABLE = 125
    DATE_ADDITION = 126
    POWER = 127
    LOG = 128
    LOG10 = 129
    EXP = 130
    RAND = 131
    FACT = 132
    SQRT = 133
    CEILING = 134
    FLOOR = 135
    EVEN = 136
    ODD = 137
    COS = 138
    COSH = 139
    ACOS = 140
    ACOSH = 141
    SIN = 142
    SINH = 143
    ASIN = 144
    ASINH = 145
    TAN = 146
    TANH = 147
    ATAN = 148
    ATANH = 149
    DEGREES = 150
    RADIANS = 151
    RANK_ACROSS_CATEGORY_ALL_AVAILABLE_ALT = 193
    RANK_ACROSS_CATEGORY_ALT = 194
    DATA_SOURCE = 200
    SET_UNDERWRITING_TO_FAIL = 254


class JumpIndexInstruction(Enum):
    JUMP_ALWAYS = -2
    JUMP_ON_TRUE = -1
    JUMP_ON_FALSE = 0


MULTI_IF_SYMBOL = "#"


def split_var_token(token: str) -> tuple[str, int, int | None]:
    """Given something like "PC_456.2" or "~GI_123" or "DGR_4740", return:
      (prefix, var_id, sub_id)
    - Strips any leading "~" or "D" first.
    - Splits on "_" to get prefix (first two chars) and the rest.
    - If there's a dot, everything after it is sub_id.
    """
    # 1) Remove leading "~" or "D" if present
    if token.startswith("~") or token.startswith("D"):
        token = token[1:]

    # 2) Ensure it has form "XX_<something>"
    if "_" not in token or len(token) < 3:
        raise ValueError(f"Cannot parse variable token '{token}'")

    prefix = token[:2]
    rest = token[3:]  # skip "XX_"
    # If there's a dot, split out sub_id
    if "." in rest:
        main_id_str, sub_id_str = rest.split(".", 1)
        if not main_id_str.isdigit() or not sub_id_str.isdigit():
            raise ValueError(f"Bad numeric IDs in '{token}'")
        return prefix, int(main_id_str), int(sub_id_str)
    else:
        if not rest.isdigit():
            raise ValueError(f"Bad numeric ID in '{token}'")
        return prefix, int(rest), None
