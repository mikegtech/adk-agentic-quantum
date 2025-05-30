

def get_var_desc(var_key: str, parent_entity, program_version) -> str:
    """Look up a variable’s human-readable description:
    1. Scan parent_entity.dependency_vars for a matching DependencyBase
       (works for both AlgorithmSequence and CalculatedVariable entities)
    2. If not found and var_key matches an input, scan program_version.data_dictionary.inputs
    3. Fallback to returning var_key
    """
    # 1. Search dependency_vars on the parent entity
    for dep in getattr(parent_entity, 'dependency_vars', []):
        if dep.index == var_key or getattr(dep, 'custom_id', None) == var_key:
            return dep.description
    # 2. Search program_version inputs
    for inp in getattr(program_version.data_dictionary, 'inputs', []):
        if inp.key == var_key:
            return inp.description
    # 3. Fallback
    return var_key
