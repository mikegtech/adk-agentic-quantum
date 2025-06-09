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
