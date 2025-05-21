# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tools module for the QuantumRate Navigator agent (Google ADK).

These helper functions expose read-only business logic and diff utilities that
an ADK agent can invoke while answering questions about legacy Insbridge rating
programs that have been decoded and vector-indexed.

All tools return **simple dict objects** so the ADK runtime can json-serialize
results and feed them back to the LLM.
"""

from __future__ import annotations

import difflib
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────────
# Helper stubs (replace with real adapters to Milvus, S3, etc.)
# ────────────────────────────────────────────────────────────────────────────────
_VECTOR_INDEX = {}  # e.g., Milvus / pgvector client
_XML_CACHE: dict[str, str] = {}  # path → xml-string
_PROGRAM_META = Path("/data/programs")  # root folder with decoded JSON


# ────────────────────────────────────────────────────────────────────────────────
# Public ADK tools
# ────────────────────────────────────────────────────────────────────────────────
def vector_search(query: str, k: int = 5) -> dict[str, Any]:
    """Semantic search over vector-indexed XML chunks.

    Args:
        query: Free-form natural-language question.
        k:     Number of top hits to return.

    Returns:
        dict with `hits`, each containing `path`, `score`, and `preview`.

    Example:
        >>> vector_search("How is territory factor calculated?", k=3)
        {
          'hits': [
            {'path': '/Auto_TX_2024/Algorithms/PremiumCalc/Step[12]',
             'score': 0.92,
             'preview': '<i n="12" t="86" ...>'}
          ]
        }

    """
    logger.info("Vector search query=%s k=%s", query, k)
    # MOCK – replace with real ANN call
    return {"hits": [{"path": "/mock/path", "score": 0.99, "preview": "<i n='1' .../>"}]}


def fetch_xml_fragment(path: str) -> dict[str, str]:
    """Retrieves the original XML fragment for a given canonical path.

    Args:
        path: Canonical XPath-style string emitted by `vector_search`.

    Returns:
        dict with `xml` payload.

    Example:
        >>> fetch_xml_fragment("/Auto_TX/Algorithms/PremiumCalc/Step[12]")
        {'xml': '<i n="12" t="86" ... />'}

    """
    logger.info("Fetching XML for %s", path)
    xml = _XML_CACHE.get(path, "<xml>NOT_FOUND</xml>")
    return {"xml": xml}


def diff_versions(program_id: str, version_a: str, version_b: str) -> dict[str, str]:
    """Generates a unified diff between two decoded JSON versions of a program.

    Args:
        program_id: e.g., 'Auto_TX'.
        version_a:  Earlier version string (e.g., '1.2').
        version_b:  Later  version string (e.g., '1.3').

    Returns:
        dict with `diff` (unified diff text).

    Example:
        >>> diff_versions("Auto_TX", "1.2", "1.3")
        {'diff': '--- 1.2\\n+++ 1.3\\n@@ ...'}

    """
    logger.info("Diffing program=%s %s → %s", program_id, version_a, version_b)
    try:
        a_txt = (_PROGRAM_META / program_id / f"{version_a}.json").read_text()
        b_txt = (_PROGRAM_META / program_id / f"{version_b}.json").read_text()
    except FileNotFoundError:
        return {"diff": "ERROR: one or both versions not found."}

    diff_text = "\n".join(
        difflib.unified_diff(a_txt.splitlines(), b_txt.splitlines(), fromfile=version_a, tofile=version_b, lineterm="")
    )
    return {"diff": diff_text or "No differences."}


def list_rate_tables(program_id: str, version: str) -> dict[str, Any]:
    """Lists all rate-tables available in a specific program version.

    Args:
        program_id: Program identifier.
        version:    Version identifier.

    Returns:
        dict with `tables` → list[str].

    Example:
        >>> list_rate_tables("Auto_TX", "1.3")
        {'tables': ['CollisionTable', 'TerritoryTable', ...]}

    """
    logger.info("Listing rate tables for %s v%s", program_id, version)
    meta_file = _PROGRAM_META / program_id / f"{version}.json"
    if not meta_file.exists():
        return {"tables": []}
    data = json.loads(meta_file.read_text())
    tables = [t["name"] for t in data.get("rateTables", [])]
    return {"tables": tables}


def run_sample_premium(program_id: str, version: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Executes a simplified premium calculation against decoded rules.

    Args:
        program_id: Program identifier.
        version:    Version identifier.
        inputs:     Key–value pairs representing policy inputs.

    Returns:
        dict with `premium_breakdown` and `total_premium`.

    Example:
        >>> run_sample_premium("Auto_TX", "1.3", {"driverAge": 30, "territory": "TX1"})
        {'premium_breakdown': {'base': 400, 'fees': 25}, 'total_premium': 425}

    """
    logger.info("Running sample premium for %s v%s with %s", program_id, version, inputs)
    # MOCK calculation – stub until runtime engine is wired
    base = 400
    fees = 25
    return {"premium_breakdown": {"base": base, "fees": fees}, "total_premium": base + fees}


def validate_instruction(instr_code: str) -> dict[str, str]:
    """Checks whether an instruction code (t= value) is recognised in the lookup table.

    Args:
        instr_code: e.g., '86'.

    Returns:
        dict with `status` and `meaning` or error.

    Example:
        >>> validate_instruction("86")
        {'status': 'ok', 'meaning': 'Evaluate RuleSet'}

    """
    logger.info("Validating instruction code %s", instr_code)
    lookup = {"86": "Evaluate RuleSet", "90": "Lookup Rate Table"}
    if instr_code not in lookup:
        return {"status": "unknown", "message": "code not recognised"}
    return {"status": "ok", "meaning": lookup[instr_code]}


def export_change_report(program_id: str, version: str, fmt: str = "markdown") -> dict[str, str]:
    """Exports a human-readable change log for a program version in Markdown or HTML.

    Args:
        program_id: Program identifier.
        version:    Version identifier.
        fmt:        'markdown' (default) or 'html'.

    Returns:
        dict with `content` (string).

    Example:
        >>> export_change_report("Auto_TX", "1.3", fmt="markdown")
        {'content': '# Auto_TX v1.3\\n* Added ...'}

    """
    logger.info("Exporting change report for %s v%s as %s", program_id, version, fmt)
    # MOCK report — replace with real diff summariser
    content_md = f"# {program_id} {version}\n\n* No user-visible changes yet."
    if fmt == "html":
        content_md = content_md.replace("\n", "<br>")
    return {"content": content_md}
