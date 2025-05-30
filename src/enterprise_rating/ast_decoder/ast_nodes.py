from dataclasses import dataclass


@dataclass
class ASTNode:
    pass

@dataclass
class RawNode(ASTNode):
    """Represents an unparsed instruction segment.
    """

    step: int
    value: str
