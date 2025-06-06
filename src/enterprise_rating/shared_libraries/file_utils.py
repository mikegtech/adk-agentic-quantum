import logging
from collections.abc import Sequence

from absl import app
from google.adk.tools import ToolContext
from google.genai.types import Part

logger = logging.getLogger(__name__)


async def save_html_to_artifact(
    html_content: str, output_filename: str, tool_context: ToolContext
) -> str:
    """Saves HTML content to an artifact in UTF-8 encoding.

    Args:
      html_content: The HTML content to save.
      output_filename: The name of the artifact to store the HTML in.

    Returns:
      The name of the artifact.

    """
    artifact = Part(text=html_content)
    await tool_context.save_artifact(filename=output_filename, artifact=artifact)
    logger.info("HTML content successfully saved to %s", output_filename)
    return output_filename


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Too many command-line arguments.")


if __name__ == "__main__":
    app.run(main)
