# enterprise_rating/ast_decoder/ast_nodes.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from enterprise_rating.ast_decoder.defs import InsType


@dataclass
class RawNode:
    """A simple leaf node carrying a single value (literal or variable).
    """

    step: int
    ins_type: InsType
    raw: str
    value: str


@dataclass
class CompareNode:
    """Represents a binary comparison: left ∘ right (e.g., GI_84 > GC_47).
    """

    step: int
    ins_type: InsType
    left: RawNode
    operator: str
    right: RawNode
    english: str | None = None


@dataclass
class IfNode:
    """An IF (or IF_DATE) node with a CompareNode condition and two branches.
    """

    step: int
    ins_type: InsType
    condition: CompareNode
    true_branch: list[ASTNode]
    false_branch: list[ASTNode]


@dataclass
class ArithmeticNode:
    """Represents an arithmetic computation: left ∘ right [round_spec].
    """

    step: int
    ins_type: InsType
    left: RawNode
    operator: str
    right: RawNode
    round_spec: str | None = None
    round_english: str | None = None


@dataclass
class FunctionNode:
    """A generic function‐ or call‐style node (e.g., string concatenation, date‐diff, data‐source).
    """

    step: int
    ins_type: InsType
    name: str
    args: list[RawNode]
    english: str | None = None


@dataclass
class AssignmentNode:
    """Represents a SET_STRING instruction: var := expr.
    Fields:
      - var: the variable being set (e.g., “DGI_110”)
      - expr: a RawNode for the value (literal or variable)
      - target: optional target variable name (if any)
      - next_true / next_false: reserved for "IF‐style" chaining; often None for SET_STRING
    """

    step: int
    ins_type: InsType
    var: str
    expr: RawNode
    target: str | None = None
    next_true: list[ASTNode] | None = None
    next_false: list[ASTNode] | None = None


# Create a union type alias for any AST node
ASTNode = Union[RawNode, CompareNode, IfNode, ArithmeticNode, FunctionNode, AssignmentNode]
