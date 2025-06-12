"""Conftest module."""

import platform

from enterprise_rating import PROJECT_DIR

MLRUNS_DIR = PROJECT_DIR / "tests" / "mlruns"
CATALOG_DIR = PROJECT_DIR / "tests" / "catalog"
CATALOG_DIR.mkdir(parents=True, exist_ok=True)  # noqa

# To make the TRACKING_URI  path compatible for both macOS and Windows
if platform.system() == "Windows":
    TRACKING_URI = f"file:///{MLRUNS_DIR.as_posix()}"
else:
    TRACKING_URI = f"file://{MLRUNS_DIR.as_posix()}"


pytest_plugins = ["fixtures.datapreprocessor_fixture"]

# tests/conftest.py

from dataclasses import asdict, is_dataclass


def node_to_dict(n):
    if is_dataclass(n):
        return asdict(n)
    elif hasattr(n, "model_dump"):
        return n.model_dump()
    else:
        return dict(n)
