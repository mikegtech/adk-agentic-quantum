## Title

Use Python Dataclasses for AST Node Representation

## Status

Accepted

## Overview

In our algorithm‐decoding pipeline, we translate each raw instruction into an Abstract Syntax Tree (AST) before further processing (reports, version diffs, tooling, etc.). We need a clear, maintainable, and efficient representation of AST nodes. This ADR documents why we choose Python’s built‐in `@dataclass` for AST node classes, how it addresses our needs, and what alternatives were considered.

## Context and Problem Statement

* **Context**

  * We parse algorithm instructions (loaded from XML via `xmltodict` and Pydantic) into a series of AST nodes (e.g., `CompareNode`, `ArithmeticNode`, `IfNode`, `FunctionNode`, etc.).
  * Downstream consumers (microservices, LLM‐based agents, reporting tools) must be able to inspect, compare, and serialize these ASTs—often converting them to JSON or dicts for transport/storage.
  * We need to support:

    1. Field-by-field equality and easy diffing between two versions.
    2. Automatic serialization to JSON/dicts.
    3. Simple, self-documented class definitions with minimal boilerplate.
    4. Efficient in-memory traversal and facile mutation or read-only inspection.

* **Problem Statement**

  * How should we represent each AST node (e.g., `CompareNode(step, ins_type, left, operator, right, english)`) so that:

    1. It’s easy to compare two nodes (for version-diff tooling).
    2. It’s trivial to serialize to JSON or dict form for Pydantic or downstream agents.
    3. We minimize boilerplate code and adhere to Python best practices.
    4. Performance remains acceptable for large algorithms (hundreds/thousands of steps).

## Decision

We will implement all AST node classes as Python `@dataclass`es. At the boundary where ASTs need to be consumed by Pydantic models (e.g., attaching to `Instruction.ast`), we will call `dataclasses.asdict(...)` on each node (and its nested children) to produce a JSON-compatible dict. Downstream consumers can use that dict directly or rehydrate into Pydantic models if needed.

## Alternatives Considered

1. **Pydantic Models for AST Nodes**

   * Define each AST node as a `pydantic.BaseModel`.
   * **Pros**: Automatic validation, built-in `.json()` and `.dict()` serialization, schema generation.
   * **Cons**: More runtime overhead, more verbose syntax, less direct field-by-field equality (though `BaseModel` supports equality, it may involve extra validation costs).

2. **Plain Python Classes (Manual `__init__` and `__eq__`)**

   * Hand-write simple classes with an explicit constructor and custom `__eq__` and `__repr__`.
   * **Pros**: Maximum control over implementation, minimal dependencies.
   * **Cons**: Lots of boilerplate, risk of errors in equality or missing fields, verbose maintenance.

3. **NamedTuple or `typing.NamedTuple`**

   * Define each node as a NamedTuple subclass.
   * **Pros**: Immutable by default, automatic tuple-based equality, lightweight.
   * **Cons**: Harder to add methods or defaults, less flexible inheriting patterns (e.g., if you want mutable children or defaults for optional fields).

4. **Third-Party Libraries (e.g., attrs)**

   * Use the `attrs` library to define classes with `@attr.s` and `@attr.ib`.
   * **Pros**: Similar to dataclasses with some extra features (validators, converters).
   * **Cons**: Extra dependency, not in the standard library (Python 3.7+ already has dataclasses).

## Decision Drivers

### Positive

1. **Boilerplate Reduction**

   * `@dataclass` auto-generates `__init__`, `__repr__`, `__eq__`, and `__hash__` (optional).
   * We can declare each node’s fields in a single class definition.

2. **Field-by-Field Equality**

   * Dataclasses implement `__eq__` by comparing each field in order. This allows us to do simple `if nodeA != nodeB:` to detect any change.

3. **Easy Serialization**

   * `dataclasses.asdict(node)` recursively converts nested dataclasses into plain dicts and lists. We can feed that dict into Pydantic or JSON builders without writing custom serialization code.

4. **Performance**

   * Dataclasses are thin wrappers over plain Python objects. They have minimal runtime overhead compared to Pydantic. For large ASTs (thousands of nodes), this is beneficial.

5. **Easy Traversal & Mutation**

   * Dataclass instances are mutable by default. We can build visitor patterns or post-processing in place (e.g. updating a subtree) without copying.
   * We can also switch to `@dataclass(frozen=True)` if we want immutability guarantees.

6. **Standard Library**

   * No extra dependencies beyond Python 3.7+. Everyone on the team is familiar with how dataclasses work.

### Negative

1. **Lack of Built-in Validation**

   * Dataclasses do not enforce types at runtime. If someone passes a string to `step: int`, it won’t raise immediately.
   * We mitigate this by controlling all AST node construction in the decoder code—ensuring types are correct at creation.

2. **No Automatic JSON Schema Generation**

   * If we needed a JSON schema for external documentation or strict API generation, we’d have to write that ourselves or use a separate Pydantic wrapper.
   * In practice, we only need the dict form, not a full JSON schema.

3. **Manual Conversion Step**

   * Whenever attaching ASTs to Pydantic models, we must remember to call `asdict(...)`. Forgetting would cause validation errors.
   * We can address this with a helper function in the repository to “dump” AST nodes before binding.

## Implementation Notes

1. **Define AST Node Classes Using `@dataclass`**

   ```python
   # enterprise_rating/ast_decoder/ast_nodes.py

   from dataclasses import dataclass
   from typing import List, Optional
   from .defs import InsType

   @dataclass
   class RawNode:
       step:       int
       ins_type:   InsType
       value:      str

   @dataclass
   class CompareNode:
       step:       int
       ins_type:   InsType
       left:       RawNode
       operator:   str
       right:      RawNode
       english:    Optional[str] = None

   @dataclass
   class IfNode:
       step:        int
       ins_type:    InsType
       condition:   CompareNode
       true_branch: List["ASTNode"]
       false_branch: List["ASTNode"]

   @dataclass
   class ArithmeticNode:
       step:         int
       ins_type:     InsType
       left:         RawNode
       operator:     str
       right:        RawNode
       round_spec:   Optional[str] = None
       round_english: Optional[str] = None

   @dataclass
   class FunctionNode:
       step:       int
       ins_type:   InsType
       name:       str
       args:       List[RawNode]
       english:    Optional[str] = None

   ASTNode = (RawNode | CompareNode | IfNode | ArithmeticNode | FunctionNode)
   ```

2. **Convert to Dict Before Pydantic**

   In `ProgramVersionRepository` (or wherever we attach to the Pydantic `Instruction.ast` field):

   ```python
   from dataclasses import asdict

   for instr in program_version.algorithm_seq.algorithm:
       if instr.ins:
           raw_ast_nodes = decode_ins(instr.dict(), algorithm_seq, program_version)
           # Convert each dataclass node into a JSON‐friendly dict
           instr.ast = [asdict(node) for node in raw_ast_nodes]
   ```

   Ensure the `Instruction` model declares:

   ```python
   class Instruction(BaseModel):
       n: int
       t: int
       ins: str
       ins_tar: Optional[str] = None
       seq_t: Optional[int] = None
       seq_f: Optional[int] = None
       ast: Optional[List[dict]] = None
   ```

3. **Equality and Diffing**

   * We can compare two ASTs with something like:

     ```python
     import dataclasses

     def diff_trees(nodesA: List[ASTNode], nodesB: List[ASTNode]):
         for a, b in zip(nodesA, nodesB):
             if a != b:
                 print(f"Difference at step {a.step}: {a} vs {b}")
     ```
   * For nested trees (e.g., `IfNode` with children), `a != b` recurses into every field automatically.

4. **Reporting Tools & Agents**

   * Any agent or tool that receives the JSON representation (via `asdict`) can reconstruct the structure as plain dicts. If desired, a utility can rehydrate into dataclasses by custom logic or into Pydantic models by passing the dict through their schema.

5. **Optional Immutability**

   * If we want to ensure AST nodes cannot be modified after creation, we can mark each class with `@dataclass(frozen=True)`. This prevents accidental mutation during diffing or caching.

---

### Conclusion

By using Python dataclasses for AST nodes and converting them to plain dicts for Pydantic, we achieve:

* Minimal boilerplate and clear field declarations
* Automatic field-by-field equality for diffing
* Simple JSON/dict serialization via `asdict(...)`
* Efficient in-memory performance

This satisfies our requirements for building reporting tools, LLM‐driven agents, and version comparison utilities while keeping the codebase easy to maintain.
