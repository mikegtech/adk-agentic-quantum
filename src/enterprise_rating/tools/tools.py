import logging

from google.adk.tools import ToolContext

from enterprise_rating.entities.program_version import ProgramVersion

logger = logging.getLogger(__name__)


async def get_releases(program_name: str, tool_context: ToolContext) -> list[dict[str, str]]:
    # Get the release dates for a given program.
    """Args:
        program_name (str): The name of the program.
        tool_context (ToolContext): The tool context.

    Returns:
        list[str]: A list of release dates in the format "YYYY-MM-DD".

    """
    release_dates = []
    release_dates.append({
        "program_name": "Auto",
        "name": "May 2, 2025",
        "program_version": "2"
    })

    return release_dates


async def get_rating_algorithms(program_name: str, program_version: int, tool_context: ToolContext) -> list[dict[str, object]]:
    # Get the rating algorithms for a given program.
    """Args:
        program_name (str): The name of the program.
        program_version (int): The version of the program.
        tool_context (ToolContext): The tool context.


    Returns:
        list[dict[str, object]]: A list of dictionaries containing the algorithm names, descriptions, and sequence number.

    """
    prog_ver_state = tool_context.state["program_version_state"]  # type: ignore
    prog_ver = ProgramVersion.model_validate_json(prog_ver_state) if prog_ver_state else None

    if prog_ver is None:
        raise ValueError("Program version state is not set in the tool context.")

    if prog_ver.program_name.lower() != program_name.lower() or prog_ver.version != program_version:
        raise ValueError(
            f"Program version mismatch: expected {prog_ver.program_name} {prog_ver.version}, "
            f"got {program_name} {program_version}"
        )

    # for each algorithm in the program version, get the name and description
    algorithms = []
    for alg_seq in prog_ver.algorithm_seq:
        algorithm = alg_seq.algorithm
        algorithms.append({
            "name": algorithm.description,
            "description": algorithm.description,
            "sequence": alg_seq.sequence_number
        })

    return algorithms


