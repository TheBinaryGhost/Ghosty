"""Tests for config system."""

from __future__ import annotations

from pathlib import Path

from ghosty.config import GhostyConfig, load_config, save_config


class TestConfig:
    """Tests for GhostyConfig dataclass and persistence."""

    def test_default_config(self) -> None:
        config = GhostyConfig()
        assert config.general.theme == "dark"
        assert config.tor.rotation_interval == 5
        assert config.tor.controller_port == 9051

    def test_save_and_load(self, tmp_config_dir: Path, monkeypatch) -> None:
        monkeypatch.setattr("ghosty.config._CONFIG_DIR", tmp_config_dir)

        config = GhostyConfig()
        config.general.theme = "light"
        save_config(config)

        loaded = load_config()
        assert loaded.general.theme == "light"

    def test_load_missing_file(self, tmp_config_dir: Path, monkeypatch) -> None:
        monkeypatch.setattr("ghosty.config._CONFIG_DIR", tmp_config_dir)
        loaded = load_config()
        assert loaded == GhostyConfig()
