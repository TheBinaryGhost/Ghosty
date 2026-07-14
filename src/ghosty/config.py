"""Configuration management with TOML persistence."""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path.home() / ".config" / "ghosty"
_CONFIG_FILE = _CONFIG_DIR / "config.toml"


@dataclass
class VPNConfig:
    """VPN configuration."""

    provider: str = "openvpn"  # "openvpn" or "wireguard"
    config_path: str = ""
    auth_path: str = ""


@dataclass
class TORConfig:
    """TOR configuration."""

    rotation_interval: int = 5
    controller_port: int = 9051


@dataclass
class LogConfig:
    """Logging configuration."""

    level: str = "INFO"
    file: str = str(_CONFIG_DIR / "ghosty.log")


@dataclass
class GeneralConfig:
    """General application configuration."""

    theme: str = "dark"
    default_mode: str = "Normal"
    default_interface: str = ""


@dataclass
class GhostyConfig:
    """Root configuration container."""

    general: GeneralConfig = field(default_factory=GeneralConfig)
    vpn: VPNConfig = field(default_factory=VPNConfig)
    tor: TORConfig = field(default_factory=TORConfig)
    log: LogConfig = field(default_factory=LogConfig)

    def save(self, path: Path | None = None) -> None:
        """Save config to TOML file."""
        target = path or _CONFIG_FILE
        target.parent.mkdir(parents=True, exist_ok=True)

        data = asdict(self)
        lines = [_toml_header()]

        for section, values in data.items():
            lines.append(f"[{section}]")
            for key, value in values.items():
                lines.append(f'{key} = {_toml_value(value)}')
            lines.append("")

        target.write_text("\n".join(lines))
        logger.info("Config saved to %s", target)

    @classmethod
    def load(cls, path: Path | None = None) -> GhostyConfig:
        """Load config from TOML file, falling back to defaults."""
        target = path or _CONFIG_FILE
        if not target.exists():
            logger.info("No config file found, using defaults")
            return cls()

        try:
            with open(target, "rb") as f:
                data = tomllib.load(f)
            return cls._from_dict(data)
        except Exception:
            logger.exception("Failed to load config from %s, using defaults", target)
            return cls()

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> GhostyConfig:
        """Construct config from parsed TOML dict."""
        general = GeneralConfig(**data.get("general", {}))
        vpn = VPNConfig(**data.get("vpn", {}))
        tor = TORConfig(**data.get("tor", {}))
        log = LogConfig(**data.get("log", {}))
        return cls(general=general, vpn=vpn, tor=tor, log=log)


def load_config(path: Path | None = None) -> GhostyConfig:
    """Load config from TOML file."""
    return GhostyConfig.load(path)


def save_config(config: GhostyConfig, path: Path | None = None) -> None:
    """Save config to TOML file."""
    config.save(path)


def _toml_header() -> str:
    return "# Ghosty Configuration — https://github.com/TheBinaryGhost/Ghosty\n"


def _toml_value(value: Any) -> str:
    """Format a Python value as TOML."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return f'"{value}"'
    return f'"{value}"'
