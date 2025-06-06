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

"""Callback functions for FOMC Research Agent."""

import logging
import os
import time
from pathlib import Path
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import LlmRequest
from google.adk.sessions.state import State
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from jsonschema import ValidationError

from enterprise_rating.entities.program_version import ProgramVersion
from enterprise_rating.repository.program_version_repository import \
    ProgramVersionRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

RATE_LIMIT_SECS = 60
RPM_QUOTA = 10
# Get the root directory (assuming your script is somewhere under src/)
ROOT = Path(__file__).resolve().parent.parent.parent  # Adjust .parent as needed!


def rate_limit_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
    """Callback function that implements a query rate limit.

    Args:
      callback_context: A CallbackContext obj representing the active callback
        context.
      llm_request: A LlmRequest obj representing the active LLM request.

    """
    for content in llm_request.contents:
        for part in content.parts:
            if part.text == "":
                part.text = " "

    now = time.time()
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [timestamp: %i, req_count: 1, elapsed_secs: 0]",
            now,
        )
        return

    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [timestamp: %i, request_count: %i, elapsed_secs: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("Sleeping for %i seconds", delay)
            time.sleep(delay)
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count

    return


def lowercase_value(value):
    """Make dictionary lowercase"""
    if isinstance(value, dict):
        return (dict(k, lowercase_value(v)) for k, v in value.items())
    elif isinstance(value, str):
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        tp = type(value)
        return tp(lowercase_value(i) for i in value)
    else:
        return value


def validate_program_version_id(program_version_id: str, session_state: State) -> tuple[bool, str]:
    """Validates the program version ID against the program profile in the session state.

    Args:
        program_version_id (str): The ID of the program version to validate.
        session_state (State): The session state containing the program profile.

    Returns:
        A tuple containing an bool (True/False) and a String.
        When False, a string with the error message to pass to the model for deciding
        what actions to take to remediate.

    """
    if "program_profile" not in session_state:
        return False, "No program profile selected. Please select a profile."

    try:
        # We read the profile from the state, where it is set deterministically
        # at the beginning of the session.
        p = ProgramVersion.model_validate_json(session_state["program_profile"])
        if program_version_id == p.ver:
            return True, None
        else:
            return False, "You cannot use the tool with customer_id " + program_version_id + ", only for " + p.ver + "."
    except ValidationError:
        return False, "Program profile couldn't be parsed. Please reload the program version data. "


# Callback Methods
def before_tool(tool: BaseTool, args: dict[str, Any], tool_context: CallbackContext):
    # i make sure all values that the agent is sending to tools are lowercase
    lowercase_value(args)

    # Several tools require customer_id as input. We don't want to rely
    # solely on the model picking the right customer id. We validate it.
    # Alternative: tools can fetch the customer_id from the state directly.
    if "customer_id" in args:
        valid, err = validate_program_version_id(args["program_version_id"], tool_context.state)
        if not valid:
            return err


def after_tool(tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict) -> dict | None:
    # After approvals, we perform operations deterministically in the callback
    # to apply the discount in the cart.
    if tool.name == "sync_ask_for_approval":
        if tool_response["status"] == "approved":
            logger.debug("Applying discount to the cart")
            # Actually make changes to the cart

    if tool.name == "approve_discount":
        if tool_response["status"] == "ok":
            logger.debug("Applying discount to the cart")
            # Actually make changes to the cart

    return None


def before_agent(callback_context: InvocationContext):
    # In a production agent, this is set as part of the
    # session creation for the agent.
    if "program_profile" not in callback_context.state:
        callback_context.state["program_version_state"] = ProgramVersionRepository.get_program_version(
            "123", "123", "1"
        ).model_dump_json()

    # Define the path
    folder_path = ROOT / "data" / "C504714691"
    file_path = os.path.join(folder_path, "model.json")

    # Create the folder if it does not exist
    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(callback_context.state["program_version_state"])
