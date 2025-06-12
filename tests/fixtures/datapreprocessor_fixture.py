import json

import pytest
from loguru import logger

from enterprise_rating import PROJECT_DIR
from enterprise_rating.entities.algorithm import Algorithm
from enterprise_rating.entities.dependency import DependencyBase
from enterprise_rating.entities.program_version import ProgramVersion


@pytest.fixture
def program_version() -> ProgramVersion:
    """Load a ProgramVersion from disk (the JSON you obtained by calling
    `prog_ver.model_dump_json()`).
    """
    p = (PROJECT_DIR / "data" / "C504714691" / "model.json").resolve()
    logger.info(f"Current config file path: {p.as_posix()}")

    raw = p.read_text(encoding="utf-8")
    # If you used model_dump_json(), use model_validate_json;
    # otherwise you can load into a dict and call model_validate:
    try:
        return ProgramVersion.parse_raw(raw)
    except AttributeError:
        data = json.loads(raw)
        return ProgramVersion.model_validate(data)


@pytest.fixture
def minimal_algorithm():

    p = (PROJECT_DIR / "data" / "tests" / "algorithm_minimal.json").resolve()
    raw = p.read_text(encoding="utf-8")
    data = json.loads(raw)
    return Algorithm.model_validate(data)

@pytest.fixture
def minimal_dependency():
    p = (PROJECT_DIR / "data" / "tests" / "algorithm_minimal.json").resolve()
    raw = p.read_text(encoding="utf-8")
    data = json.loads(raw)
    return DependencyBase.model_validate(data)
