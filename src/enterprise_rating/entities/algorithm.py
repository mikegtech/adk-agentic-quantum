


from pydantic import BaseModel, ConfigDict

from enterprise_rating.entities.dependency import DependencyBase


class Algorithm(BaseModel):
    """Represents a sequence of algorithms in the program version."""

    prog_key: str  # Primary key for the program
    revision_key: str  # Revision key for the algorithm
    alg_type: str  # Type of the algorithm
    category_id: str  # Category ID associated with the algorithm
    description: str  # Description of the algorithm
    date_last_modified: str  # Date when the algorithm was last modified
    index: int  # Index of the algorithm in the sequence
    version: str  # Version of the algorithm
    program_id: str  # Program ID associated with the algorithm
    assign_filter: str  # Filter for assignment
    advanced_type: str  # Advanced type of the algorithm
    dependency_vars: dict[str, DependencyBase] | None = None
    model_config = ConfigDict(from_attributes=True)

    # @field_validator('dependency_vars', mode='before')
    # def list_to_dict(cls, v):
    #     if v is None:
    #         return v
    #     if isinstance(v, dict):
    #         # Flatten any single-item lists in the dict values
    #         for k in list(v.keys()):
    #             if isinstance(v[k], list):
    #                 if len(v[k]) == 1:
    #                     v[k] = v[k][0]
    #                 elif len(v[k]) == 0:
    #                     v[k] = None
    #                 else:
    #                     # If you expect only one dependency per key, just take the first
    #                     v[k] = v[k][0]
    #         return v
    #     if isinstance(v, list):
    #         result = {}
    #         for i, item in enumerate(v):
    #             if isinstance(item, dict) and 'index' in item:
    #                 try:
    #                     key = int(item['index'])
    #                 except Exception:
    #                     key = i
    #             else:
    #                 key = i
    #             result[key] = item
    #         return result
    #     return v


class AlgorithmSequence(BaseModel):
    """Represents a sequence of algorithms in the program version."""

    # algorithm: Algorithm
    sequence_number: int  # The order of the algorithm in the sequence
    universal: str  # Universal identifier for the algorithm sequence
    algorithm: Algorithm  # The algorithm associated with this sequence
    model_config = ConfigDict(from_attributes=True)
