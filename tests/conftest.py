"""Shared test fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Provide a temporary config directory."""
    config_dir = tmp_path / ".config" / "ghosty"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def mock_run(mocker):
    """Patch ghosty.utils.process.run to succeed by default."""
    from ghosty.utils import process

    mock = mocker.patch.object(process, "run")
    mock.return_value = (True, "mocked")
    return mock
