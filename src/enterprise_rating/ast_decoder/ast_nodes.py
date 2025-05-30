from dataclasses import dataclass, field

from .defs import InsType


@dataclass
class ASTNode:
    """Base class for all AST nodes."""

    step: int
    ins_type: InsType

@dataclass
class RawNode(ASTNode):
    """Represents an unparsed instruction segment."""

    value: str

@dataclass
class AssignmentNode(ASTNode):
    var: str
    expr: 'ASTNode'
    target: str | None = None
    next_true: int | None = None
    next_false: int | None = None

@dataclass
class CompareNode(ASTNode):
    left: 'ASTNode'
    operator: str
    right: 'ASTNode'
    english: str | None = None

@dataclass
class ArithmeticNode(ASTNode):
    left: 'ASTNode'
    operator: str
    right: 'ASTNode'
    round_spec: str | None = None
    round_english: str | None = None

@dataclass
class IfNode(ASTNode):
    condition: 'ASTNode'
    true_branch: list['ASTNode'] = field(default_factory=list)
    false_branch: list['ASTNode'] = field(default_factory=list)

@dataclass
class FunctionNode(ASTNode):
    name: str
    args: list['ASTNode'] = field(default_factory=list)
    english: str | None = None
