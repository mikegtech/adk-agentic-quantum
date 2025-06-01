
from pydantic import BaseModel, ConfigDict

from enterprise_rating.entities.instruction_ast import InstructionAst


class Instruction(BaseModel):
    """Represents one <i …/> element after xmltodict + Pydantic coercion.
    Fields correspond exactly to the XML attributes:
      - n      : step number
      - t      : instruction type code
      - ins    : raw instruction string
      - ins_tar: instruction target (optional)
      - seq_t  : index of next-if-true (optional)
      - seq_f  : index of next-if-false (optional)
    """

    n: int
    t: int
    ins: str
    ins_tar: str | None = None
    seq_t: int | None = None
    seq_f: int | None = None
    ast: InstructionAst | None = None
    model_config = ConfigDict(from_attributes=True)
