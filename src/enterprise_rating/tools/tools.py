import logging

from google.adk.tools import ToolContext
from google.genai.types import Part

from ..shared_libraries import file_utils

logger = logging.getLogger(__name__)


async def get_rating_algorithms(program_name: str, program_version: str, tool_context: ToolContext) -> dict[str, str]: