"""Validate independent integration tags against local package metadata."""

import argparse
from pathlib import Path
import re
import tomllib


INTEGRATIONS = {"agentgateway", "strands", "agno", "crewai", "pydantic-ai"}


def validate_release(root: Path, integration: str, tag: str) -> str:
    if integration not in INTEGRATIONS:
        raise ValueError("Unsupported integration")
    match = re.fullmatch(re.escape(integration) + r"/v(\d+\.\d+\.\d+)", tag)
    if match is None:
        raise ValueError("Expected integration/vMAJOR.MINOR.PATCH")
    version = match.group(1)
    directory = root / "integrations" / integration
    if not directory.is_dir():
        raise ValueError("Tag does not contain the monorepo integration directory")
    if integration == "agentgateway":
        # The adapter is an image, not a versioned Python distribution.
        return version
    else:
        with (directory / "pyproject.toml").open("rb") as source:
            expected = tomllib.load(source)["project"]["version"]
    if version != expected:
        raise ValueError(f"Tag version {version} does not match package version {expected}")
    return version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("integration", choices=sorted(INTEGRATIONS))
    parser.add_argument("tag")
    args = parser.parse_args()
    print(validate_release(Path(__file__).resolve().parents[1], args.integration, args.tag))
