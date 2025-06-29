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
"""Agent module for **QuantumRate Navigator** (rating-system POC).

The root agent receives natural-language questions about legacy Insbridge
programs, invokes retrieval / diff / calculation tools, and streams a sourced
answer back to the user.  Built with Google ADK.
"""

from __future__ import annotations

import logging
import warnings

from google.adk import Agent

from enterprise_rating.tools.tools import get_rating_algorithms, get_releases

from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import (after_tool, before_agent, before_tool,
                                         rate_limit_callback)

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()
logger = logging.getLogger(__name__)

root_agent = Agent(
    model=configs.agent_settings.model,  # e.g. "nv-llama3-8b-instruct"
    name=configs.agent_settings.name,  # e.g. "QuantumRate-Agent"
    global_instruction=GLOBAL_INSTRUCTION,  # system-level guardrails
    instruction=INSTRUCTION,  # conversation-level prompt
    tools=[
        get_rating_algorithms,
        get_releases,
    ],
    # optional callbacks for tracing / metrics / rate limiting
    before_tool_callback=before_tool,
    after_tool_callback=after_tool,
    before_agent_callback=before_agent,
    before_model_callback=rate_limit_callback,
)
