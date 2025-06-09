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

"""Includes all shared libraries for the agent."""

import importlib.metadata
import importlib.resources
from pathlib import Path

from loguru import logger

from . import agent

__all__ = ["agent"]

THIS_DIR = Path(__file__).parent
logger.info(f"Current package directory: {THIS_DIR.as_posix()}")
PROJECT_DIR = (THIS_DIR / "../..").resolve()


def get_version() -> str:
    """Retrieve the version of the package.

    This function attempts to read the version from the installed package,
    and if not found, reads it from a version.txt file.

    :return: The version string of the package.
    """
    try:
        # Try to read from the installed package
        return importlib.metadata.version(__package__)
    except importlib.metadata.PackageNotFoundError:
        # If not installed, read from the version.txt file
        with importlib.resources.files(__package__).joinpath("../../version.txt").open("r", encoding="utf-8") as file:
            return file.read().strip()


__version__ = get_version()

