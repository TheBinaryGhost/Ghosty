"""VPN management — OpenVPN and WireGuard support."""

from __future__ import annotations

import logging
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from ghosty.utils.process import run_command, is_available

logger = logging.getLogger(__name__)


def _ensure_openvpn() -> bool:
    """Install openvpn if not available."""
    if is_available("openvpn"):
        return True
    logger.info("openvpn not found, installing...")
    for pm_cmd in [
        ["sudo", "apt-get", "install", "-y", "openvpn"],
        ["sudo", "dnf", "install", "-y", "openvpn"],
        ["sudo", "pacman", "-S", "--noconfirm", "openvpn"],
        ["sudo", "zypper", "install", "-y", "openvpn"],
    ]:
        result = run_command(pm_cmd, timeout=120)
        if result.success:
            logger.info("openvpn installed successfully")
            return True
    logger.error("Failed to install openvpn")
    return False


def _ensure_wireguard() -> bool:
    """Install wireguard-tools if not available."""
    if is_available("wg-quick"):
        return True
    logger.info("wireguard-tools not found, installing...")
    for pm_cmd in [
        ["sudo", "apt-get", "install", "-y", "wireguard-tools"],
        ["sudo", "dnf", "install", "-y", "wireguard-tools"],
        ["sudo", "pacman", "-S", "--noconfirm", "wireguard-tools"],
        ["sudo", "zypper", "install", "-y", "wireguard-tools"],
    ]:
        result = run_command(pm_cmd, timeout=120)
        if result.success:
            logger.info("wireguard-tools installed successfully")
            return True
    logger.error("Failed to install wireguard-tools")
    return False


@dataclass
class VPNManager:
    """Manages VPN connections (OpenVPN or WireGuard)."""

    provider: str = "openvpn"
    config_file: str = ""
    auth_file: str = ""

    _process: subprocess.Popen | None = field(default=None, repr=False)
    _connected: bool = field(default=False, repr=False)
    _monitor_thread: threading.Thread | None = field(default=None, repr=False)

    @property
    def is_connected(self) -> bool:
        """Check if VPN is currently connected."""
        if self._process and self._process.poll() is None:
            return True
        self._connected = False
        return False

    def is_available(self) -> bool:
        """Check if the VPN client is installed."""
        if self.provider == "wireguard":
            return is_available("wg-quick")
        return is_available("openvpn")

    def set_config(self, config_file: str, auth_file: str | None = None) -> tuple[bool, str]:
        """Set VPN configuration files.

        Returns:
            (success, message) tuple.
        """
        if not Path(config_file).exists():
            return False, f"Config file not found: {config_file}"

        if auth_file and not Path(auth_file).exists():
            return False, f"Auth file not found: {auth_file}"

        self.config_file = config_file
        self.auth_file = auth_file or ""
        logger.info("VPN config set: %s", config_file)
        return True, "VPN configuration set"

    def connect(self) -> tuple[bool, str]:
        """Start VPN connection.

        Returns:
            (success, message) tuple.
        """
        # Auto-install VPN client if needed
        if self.provider == "wireguard":
            if not _ensure_wireguard():
                return False, "wireguard-tools could not be installed"
        else:
            if not _ensure_openvpn():
                return False, "openvpn could not be installed"

        if not self.config_file:
            return False, "No VPN configuration file set"

        if self.is_connected:
            return False, "VPN is already connected"

        logger.info("Connecting VPN with provider=%s config=%s", self.provider, self.config_file)

        try:
            if self.provider == "wireguard":
                return self._connect_wireguard()
            return self._connect_openvpn()
        except Exception as e:
            logger.exception("Failed to connect VPN")
            return False, f"Failed to connect: {e}"

    def _connect_openvpn(self) -> tuple[bool, str]:
        """Start OpenVPN connection."""
        cmd = ["sudo", "openvpn", "--config", self.config_file]

        if self.auth_file:
            cmd.extend(["--auth-user-pass", self.auth_file])

        cmd.extend([
            "--script-security", "2",
            "--up", "/etc/openvpn/update-resolv-conf",
            "--down", "/etc/openvpn/update-resolv-conf",
        ])

        logger.info("Running: %s", " ".join(cmd))

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self._monitor_thread = threading.Thread(target=self._monitor_process, daemon=True)
        self._monitor_thread.start()

        # Wait briefly to check if process starts
        time.sleep(3)
        if self._process.poll() is None:
            self._connected = True
            logger.info("OpenVPN connection started")
            return True, "VPN connection started"

        stdout, stderr = self._process.communicate()
        logger.error("OpenVPN failed: %s", stderr)
        return False, f"OpenVPN failed to start: {stderr}"

    def _connect_wireguard(self) -> tuple[bool, str]:
        """Start WireGuard connection."""
        result = run_command(
            ["sudo", "wg-quick", "up", self.config_file],
            timeout=30,
        )
        if result.success:
            self._connected = True
            logger.info("WireGuard connection started")
            return True, "WireGuard VPN connected"
        logger.error("WireGuard failed: %s", result.stderr)
        return False, f"WireGuard failed: {result.stderr}"

    def disconnect(self) -> tuple[bool, str]:
        """Disconnect VPN.

        Returns:
            (success, message) tuple.
        """
        if not self.is_connected and not self._connected:
            return False, "VPN is not connected"

        try:
            if self.provider == "wireguard":
                return self._disconnect_wireguard()
            return self._disconnect_openvpn()
        except Exception as e:
            logger.exception("Failed to disconnect VPN")
            return False, f"Failed to disconnect: {e}"

    def _disconnect_openvpn(self) -> tuple[bool, str]:
        """Stop OpenVPN process."""
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
            self._process = None

        self._connected = False
        logger.info("OpenVPN disconnected")
        return True, "VPN disconnected"

    def _disconnect_wireguard(self) -> tuple[bool, str]:
        """Stop WireGuard connection."""
        result = run_command(
            ["sudo", "wg-quick", "down", self.config_file],
            timeout=30,
        )
        self._connected = False
        if result.success:
            logger.info("WireGuard disconnected")
            return True, "WireGuard VPN disconnected"
        return False, f"WireGuard disconnect failed: {result.stderr}"

    def get_status(self) -> str:
        """Get human-readable connection status."""
        if self.is_connected:
            return "Connected"
        return "Disconnected"

    def _monitor_process(self) -> None:
        """Monitor VPN process in background thread."""
        if not self._process:
            return
        try:
            stdout, stderr = self._process.communicate()
            if self._process.returncode != 0:
                logger.error("VPN process ended with error: %s", stderr)
            else:
                logger.info("VPN process ended normally")
        except Exception:
            logger.exception("Error monitoring VPN process")
        finally:
            self._connected = False
