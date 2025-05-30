def find_next_var(sequence, current_index: int) -> int:
    """Stub for finding next variable index in algorithm_seq.dependency_vars.
    """
    try:
        vars_list = [int(dep.index) for dep in sequence.dependency_vars]
        vars_list.sort()
        for v in vars_list:
            if v > current_index:
                return v
    except Exception:
        pass
    return current_index
