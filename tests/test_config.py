"""Tests for config system."""

from __future__ import annotations

from pathlib import Path

from ghosty.config import Config, load_config, save_config


class TestConfig:
    """Tests for Config dataclass and persistence."""

    def test_default_config(self) -> None:
        config = Config()
        assert config.theme == "dark"
        assert config.language == "en"
        assert config.vpn_interface == "tun0"
        assert config.tor_socks_port == 9050

    def test_save_and_load(self, tmp_config_dir: Path, monkeypatch) -> None:
        monkeypatch.setattr("ghosty.config.CONFIG_DIR", tmp_config_dir)

        config = Config()
        config.theme = "light"
        config.language = "ru"
        save_config(config)

        loaded = load_config()
        assert loaded.theme == "light"
        assert loaded.language == "ru"

    def test_load_missing_file(self, tmp_config_dir: Path, monkeypatch) -> None:
        monkeypatch.setattr("ghosty.config.CONFIG_DIR", tmp_config_dir)
        loaded = load_config()
        assert loaded == Config()
