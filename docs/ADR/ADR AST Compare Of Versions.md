Below is a revised set of options for “showing differences between two versions of your program” that assume:

* **Your program is represented as JSON**, built from Pydantic entities (e.g. `ProgramVersion`, `Algorithm`, `DependencyBase`, etc.).
* **Your AST nodes are Python dataclasses** (e.g. `IfNode`, `CompareNode`, `FunctionNode`, etc.) that eventually get serialized to JSON.
* **You want to present the diff either as a Git‐style patch (textual JSON diff) or as a more semantic, “+ / –” comparison of JSON fields**, or even in plain‐English sentences that reference Pydantic model names and AST node types.

Each approach is annotated with Python-specific examples (using `difflib`, Pydantic’s `.json()`, and direct AST traversal). Where relevant, we show short code snippets. Pick the approach (or mix of approaches) that best fits your needs.

---

## 1. “Git-Style” JSON Unified Diff

**What it is**
Generate a unified diff between the JSON serialization of Version 1 and Version 2 of your program (e.g. the output of `ProgramVersion.json(indent=2)`).

**How to implement**

1. **Dump both versions to pretty-printed JSON**:

   ```python
   from enterprise_rating.entities.program_version import ProgramVersion

   pv_v1 = ProgramVersion.model_validate(raw_data_v1)
   pv_v2 = ProgramVersion.model_validate(raw_data_v2)

   json_v1 = pv_v1.model_dump_json(indent=2, sort_keys=True)
   json_v2 = pv_v2.model_dump_json(indent=2, sort_keys=True)
   ```

   (Sorting keys helps keep diffs stable.)

2. **Run Python’s `difflib.unified_diff` on the line lists**:

   ```python
   import difflib

   lines1 = json_v1.splitlines(keepends=True)
   lines2 = json_v2.splitlines(keepends=True)

   diff_lines = difflib.unified_diff(
       lines1,
       lines2,
       fromfile="program_v1.json",
       tofile="program_v2.json",
       lineterm="",
   )
   for line in diff_lines:
       print(line)
   ```

   You’ll get something like:

   ```diff
   --- program_v1.json
   +++ program_v2.json
   @@ -45,7 +45,7 @@
         "dependency_vars": [
           {
             "ib_type": "3",
   -         "description": "Old CalcVar desc",
   +         "description": "New CalcVar desc",
             "id": 123,
             "ins_grp_id": 456,
             "ins_grp_ver": 1
   ```

**Pros**

* Very precise: shows exactly which JSON keys/values changed, with context.
* Uses built-in Python libraries—no extra dependencies.
* Familiar “unified diff” format if you or your team already use Git.

**Cons**

* Raw JSON can be noisy if the ordering of keys changes.
* Readers must mentally parse JSON structure to understand semantic changes.

---

## 2. Minimal “+ / –” JSON Diff (No Headers, Only Changed Lines)

If you prefer to show only the actual additions and deletions—without the `@@ -a,b +c,d @@` headers—you can filter `difflib.ndiff` or `unified_diff` output.

**Implementation Example**

```python
import difflib

# (Assume json_v1, json_v2 from above)
lines1 = json_v1.splitlines()
lines2 = json_v2.splitlines()

# Use ndiff to get lines prefixed with '  ' (unchanged), '- ' (removed), '+ ' (added)
diff = difflib.ndiff(lines1, lines2)

for line in diff:
    if line.startswith("- ") or line.startswith("+ "):
        # Trim off the leading marker for readability:
        print(line[0] + " " + line[2:])
```

Result:

```text
-   "description": "Old CalcVar desc",
+   "description": "New CalcVar desc",
-   "some_other_key": 42,
+   "some_other_key": 43,
```

**Pros**

* Cleaner than a full unified diff; shows exactly which JSON lines changed.
* Still fully deterministic, using only Python standard library.

**Cons**

* Loses context (readers don’t know exactly which object these lines belonged to).
* Harder to locate a change within a complex nested Pydantic model.

---

## 3. AST-Level Diff on Dataclass Instances

Instead of diffing JSON text, compare the two AST dataclass instances directly. You can then emit a structured report of “which AST nodes changed” (e.g. operator change in a `CompareNode`, added argument in a `FunctionNode`, etc.).

### Workflow

1. **Deserialize JSON → Pydantic → AST**

   * You already have code that, for each `Instruction` Pydantic model, builds an AST (`IfNode`, `CompareNode`, etc.) and stores it in `instr.ast`.
   * Now re-run your entire AST assembly for both versions (v1 and v2), yielding two trees:

     ```python
     ast_v1 = assemble_full_ast(progver_v1)  # List[ASTNode] or root node
     ast_v2 = assemble_full_ast(progver_v2)
     ```

2. **Implement an AST differ** (example using `deepdiff` or a custom visitor):

   ```python
   from deepdiff import DeepDiff

   # Convert each dataclass tree into a nested dict (via its __dict__):
   def ast_to_dict(node):
       if isinstance(node, list):
           return [ast_to_dict(n) for n in node]
       elif hasattr(node, "__dict__"):
           result = {}
           for k, v in node.__dict__.items():
               result[k] = ast_to_dict(v)
           result["node_type"] = node.__class__.__name__
           return result
       else:
           return node

   dict_v1 = ast_to_dict(ast_v1)
   dict_v2 = ast_to_dict(ast_v2)

   diff = DeepDiff(dict_v1, dict_v2, ignore_order=True)
   print(diff.to_json(indent=2))
   ```

   You’ll get a JSON summary of exactly which fields changed in which nodes. For example:

   ```json
   {
     "values_changed": {
       "root['instructions'][3]['ast'][0]['condition']['operator']": {
         "old_value": ">",
         "new_value": ">="
       }
     },
     "iterable_item_added": {
       "root['instructions'][5]['ast'][1]": {
         "new_item": {
           "node_type": "RawNode", "step": 5, "ins_type": 86, "raw": "[Suffix]", "value": "Suffix"
         }
       }
     }
   }
   ```

3. **Translate AST diffs into human-readable sentences**

   * Walk the `DeepDiff` JSON output and convert each change into a sentence:

     ```python
     for path, change in diff.get("values_changed", {}).items():
         if "operator" in path:
             print(f"Changed operator from **{change['old_value']}** to **{change['new_value']}** at {path}")
     for path, addition in diff.get("iterable_item_added", {}).items():
         node = addition["new_item"]
         if node["node_type"] == "RawNode":
             print(f"Added a new token `{node['raw']}` (value: {node['value']}) at {path}")
     ```
   * You can clean up each `path` (e.g. `"root['instructions'][3]…"` → “instruction #4’s AST”).

**Pros**

* Very high-level: you see exactly which AST nodes changed rather than raw JSON lines.
* Ignores superficial formatting changes (order, whitespace), focusing on semantics.

**Cons**

* Requires converting your AST dataclasses to nested Python dicts.
* `DeepDiff` output can be verbose—requires custom logic to produce nice sentences.
* May take extra CPU/memory for large ASTs.

---

## 4. Field-by-Field “+ / –” Pydantic Diff

If you want to show how the Pydantic entity fields themselves changed (e.g. a `DependencyBase`’s `description` changed, or an `Algorithm`’s `steps` list was modified), produce a diff of the `model_dump()` dictionaries (instead of the full JSON). You can then show only changed fields with “+ / –” prefix.

### Example Using `dictdiffer`

```python
from dictdiffer import diff

# model_dump() gives you a plain Python dict for each Pydantic model:
pv1_dict = pv_v1.model_dump()
pv2_dict = pv_v2.model_dump()

# Compare top-level ProgramVersion fields:
for change in diff(pv1_dict, pv2_dict):
    op, path, values = change
    if op == "change":
        # e.g. path = ('algorithm_seq', 2, 'algorithm', 'dependency_vars', 1, 'description')
        old, new = values
        print(f"- {'.'.join(map(str, path))}: {old}")
        print(f"+ {'.'.join(map(str, path))}: {new}")
    elif op == "add":
        print(f"+ Added at {path}: {values}")
    elif op == "remove":
        print(f"- Removed at {path}: {values}")
```

Sample output:

```text
- algorithm_seq.1.algorithm.dependency_vars.0.description: "Old lookup"
+ algorithm_seq.1.algorithm.dependency_vars.0.description: "New lookup"
- algorithm_seq.0.algorithm.steps.3.ins: "|GR_123|=|…|"
+ algorithm_seq.0.algorithm.steps.3.ins: "|GR_123|<>|…|"
```

**Pros**

* Works directly on Pydantic dicts—no need to serialize to JSON string.
* Shows exactly which model fields changed (e.g., `ins`, `description`, `steps`, etc.).
* Easy to script in Python.

**Cons**

* Can be too low-level if you only want to highlight business-logic changes.
* You’ll have to map diff paths (`("algorithm_seq", 1, …)`) to human-friendly descriptions.

---

## 5. Natural-Language Summaries via an LLM (Prompt on JSON Diff)

Feed only the changed portions of the JSON (or the AST diff) into an LLM and ask it to “Describe in plain English what changed.” This is similar to approach 4 but uses an LLM to generate the final text.

### Example Prompt

````text
You have two Pydantic ProgramVersion JSON snapshots. Only these keys changed:

```diff
- "algorithm_seq": [
-   {
-     "algorithm": {
-       "dependency_vars": [
-         { "index": 45, "description": "Old Lookup Value" }
-       ]
-     }
-   }
- ]
+ "algorithm_seq": [
+   {
+     "algorithm": {
+       "dependency_vars": [
+         { "index": 45, "description": "New Lookup Value" }
+       ]
+     }
+   }
+ ]
````

Write a bullet-point summary of changes, referring to “dependency\_vars index 45” as “the lookup variable at index 45.” Bold any operators in code, italicize any variable names.

Output:

```
- The lookup variable at index 45 had its description updated from “Old Lookup Value” to “New Lookup Value.”
```

````

Then in Python:

```python
prompt = PROMPT_TEMPLATE.replace("{diff}", diff_text)
response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role":"user","content":prompt}])
print(response.choices[0].message["content"])
````

**Pros**

* Produces fully polished, reader-friendly English.
* You can instruct the LLM to use markdown formatting (bold/italic).
* No need to write templates for every field-change scenario.

**Cons**

* Requires an LLM call (latency + cost).
* Non-deterministic: slight output variations.
* Must craft a robust prompt to handle nested diffs in JSON.

---

## 6. Inline “+ / –” with Short English Notes for Each Changed Field

Combine a line-based diff (option 2) with very short, code-generated English comments:

1. **Compute a list of changed JSON lines** (e.g. from `ndiff` or unified diff).

2. **For each “– old\_line” or “+ new\_line,” generate a one-sentence explanation via a small rule engine**:

   ```python
   def explain_json_change(line: str) -> str:
       # Example: line = '"description": "Old Lookup Value",'
       if "description" in line:
           if line.startswith("-"):
               val = line.split(": ", 1)[1].rstrip(",")
               return f"- Removed description {val}"
           else:  # line.startswith("+")
               val = line.split(": ", 1)[1].rstrip(",")
               return f"+ Added description {val}"
       # handle other keys: ins, operator, etc.
       return ""
   ```

3. **Print combined output**:

   ```text
   - "description": "Old Lookup",          // Removed old lookup text
   + "description": "New Lookup",          // Added new lookup text
   - "operator": ">",                      // Changed operator from '>' 
   + "operator": ">=",                     // Changed operator to '>='
   ```

**Pros**

* Still textual “+ / –” diff, but each line has a short English comment.
* Readers don’t have to decode JSON—comments explain exactly what changed.

**Cons**

* You must maintain a rule engine or a mapping for each JSON key you care about.
* Can become verbose if many fields changed.

---

## 7. Side-by-Side Table of Changed Fields

Build a small HTML or Markdown table listing each changed field with “Old Value” and “New Value” columns. For example:

| Path                                                        | Old Value            | New Value            |     |     |     |     |         |     |     |     |
| ----------------------------------------------------------- | -------------------- | -------------------- | --- | --- | --- | --- | ------- | --- | --- | --- |
| `algorithm_seq[1].algorithm.dependency_vars[0].description` | `"Old Lookup Value"` | `"New Lookup Value"` |     |     |     |     |         |     |     |     |
| `algorithm_seq[0].algorithm.steps[3].ins`                   | \`"                  | GR\_123              | =   | …   | "\` | \`" | GR\_123 | <>  | …   | "\` |

**How to implement**

```python
from dictdiffer import diff

table_rows = []
for op, path, vals in diff(pv1_dict, pv2_dict):
    if op == "change":
        old, new = vals
        path_str = ".".join(str(p) for p in path)
        table_rows.append((path_str, old, new))
    # handle “add” / “remove” similarly

# Now render as Markdown:
print("| Path | Old | New |")
print("|---|---|---|")
for pr, oldv, newv in table_rows:
    print(f"| `{pr}` | `{oldv}` | `{newv}` |")
```

**Pros**

* Highly structured and easy to scan for “which field → what changed.”
* Can be embedded in documentation, Jupyter notebooks, or HTML reports.

**Cons**

* Less visual than `git diff`; readers must interpret each path.
* No automatic highlighting of nested structure beyond the path string.

---

## 8. Real-Time In-Editor Highlighting with JSON Paths

If you have a web-based UI or an Electron/desktop app, you can:

1. **Compute a list of changed JSON paths (from approach 3 or 4)**.
2. **Render two JSON viewers side-by-side** (e.g. using [react-json-view](https://github.com/mac-s-g/react-json-view) or [jsondiffpatch](https://github.com/benjamine/jsondiffpatch)).
3. **Highlight only the changed keys** (using the JSON path list).
4. **Show a pop-up or inline tooltip** for each changed field with a brief description:

   > “Changed from `'>='` to `'>='` (CompareNode operator)”

In pseudocode:

```js
// In React (frontend)
<JsonViewer 
    src={pv_v1_json} 
    highlightPaths={diff_paths} 
    onHoverPath={(path) => showTooltip(path, explain(path))}
/>
<JsonViewer 
    src={pv_v2_json} 
    highlightPaths={diff_paths} 
    onHoverPath={(path) => showTooltip(path, explain(path))}
/>
```

Where `diff_paths` might be:

```js
[
  ["algorithm_seq", 1, "algorithm", "dependency_vars", 0, "description"],
  ["algorithm_seq", 0, "algorithm", "steps", 3, "ins"],
]
```

And `explain(path)` is a JS function that returns something like:

> “Changed `dependency_vars[0].description` from ‘Old’ to ‘New’.”

**Pros**

* Very interactive: users can click on any changed field and see details.
* Uses existing JSON viewers; you just feed in a list of changed paths.
* Excellent for UI/UX where non-technical stakeholders can explore changes visually.

**Cons**

* Requires building a custom frontend (React, Vue, etc.) or integrating with a library.
* More engineering overhead if you don’t already have a web UI.

---

## Choosing the Right Option for Your Pydantic + AST Scenario

1. **If you want a quick “diff-in-console” for JSON** → go with **Option 1 (Unified Diff)** or **Option 2 (“+ / –” minimal diff)**.
2. **If you need a structured, field-level report** → use **Option 4 (dictdiffer on Pydantic dicts)** or **Option 7 (side-by-side table)**.
3. **If you want to highlight exactly which AST nodes changed (e.g. an `IfNode`’s operator)** → use **Option 3 (AST diff via dataclass → dict → DeepDiff)** and then convert that into sentences or tables.
4. **If you want fully natural-language summaries** → feed a diff (from Option 1–3) into an LLM prompt (Option 5), capturing bullet points, bolding operators, italicizing variable names, etc.
5. **If you have a web/dashboard** → use **Option 8** to highlight changed JSON paths visually and show tooltips.

You can also **combine** approaches. For instance, generate a unified JSON diff (Option 1), then pass only the changed segments into an LLM to get a concise English summary (Option 5), and finally render that alongside a side-by-side JSON viewer (Option 8) for drill-down.

---
