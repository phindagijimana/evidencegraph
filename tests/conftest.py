from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
ITEMS = PACKAGE_ROOT / "evaluation" / "items"
EXAMPLE_CLAIM = PACKAGE_ROOT / "schema" / "example_claim.yaml"


@pytest.fixture
def package_root() -> Path:
    return PACKAGE_ROOT


@pytest.fixture
def items_dir() -> Path:
    return ITEMS
