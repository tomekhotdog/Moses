"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from moses.loader import load_codebase
from moses.models import Codebase

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def bad_codebase() -> Codebase:
    return load_codebase(FIXTURES / "bad_example")


@pytest.fixture
def good_codebase() -> Codebase:
    return load_codebase(FIXTURES / "good_example")


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES
