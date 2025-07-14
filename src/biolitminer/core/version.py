"""
Version management for BioLitMiner.
"""

from pathlib import Path

import toml


def get_version() -> str:
    """
    Get the current version from pyproject.toml.

    Returns:
        Version string (e.g., "0.2.1")
    """
    try:
        # Find pyproject.toml (handle different working directories)
        current_dir = Path(__file__).parent
        pyproject_path = None

        # Look for pyproject.toml going up the directory tree
        for parent in [current_dir] + list(current_dir.parents):
            potential_path = parent / "pyproject.toml"
            if potential_path.exists():
                pyproject_path = potential_path
                break

        if pyproject_path is None:
            return "unknown"

        # Read and parse pyproject.toml
        with open(pyproject_path, "r") as f:
            pyproject_data = toml.load(f)

        return pyproject_data["project"]["version"]

    except Exception:
        return "unknown"
