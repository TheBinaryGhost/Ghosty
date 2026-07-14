"""Orchestrator — coordinates anonymization modes with crash-safe cleanup."""

from __future__ import annotations

import atexit
import logging
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from ghosty.core.mac import MACChanger
from ghosty.core.vpn import VPNManager
from ghosty.core.tor import TORManager

logger = logging.getLogger(__name__)


class AnonymizationMode(Enum):
    """Supported anonymization modes."""

    NORMAL = "Normal"        # MAC only
    STANDARD = "Standard"    # MAC + VPN
    ENHANCED = "Enhanced"    # MAC + VPN + TOR


@dataclass
class Orchestrator:
    """Coordinates MAC, VPN, and TOR operations with crash-safe cleanup.

    Installs atexit and signal handlers to restore state if the process
    is killed unexpectedly.
    """

    mac: MACChanger = field(default_factory=MACChanger)
    vpn: VPNManager = field(default_factory=VPNManager)
    tor: TORManager = field(default_factory=TORManager)

    _is_active: bool = field(default=False, repr=False)
    _current_mode: AnonymizationMode | None = field(default=None, repr=False)
    _current_interface: str = ""
    _cleanup_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _log_callback: Callable[[str], None] | None = field(default=None, repr=False)

    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for log messages (used by GUI)."""
        self._log_callback = callback

    def _log(self, message: str) -> None:
        """Log to both logger and GUI callback."""
        logger.info(message)
        if self._log_callback:
            self._log_callback(message)

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def current_mode(self) -> AnonymizationMode | None:
        return self._current_mode

    def start(
        self,
        mode: AnonymizationMode,
        interface: str,
        *,
        vpn_config: str = "",
        vpn_auth: str | None = None,
    ) -> tuple[bool, str]:
        """Start anonymization with the specified mode.

        Args:
            mode: Anonymization level.
            interface: Network interface to modify.
            vpn_config: Path to VPN config file.
            vpn_auth: Path to VPN auth file (optional).

        Returns:
            (success, message) tuple.
        """
        if self._is_active:
            return False, "Anonymization is already active"

        self._current_mode = mode
        self._current_interface = interface

        # Install crash handlers
        self._install_handlers()

        self._log(f"Starting {mode.value} mode...")

        # Step 1: MAC change (all modes)
        self._log("Changing MAC address...")
        success, message = self.mac.change_mac(interface)
        if not success:
            self._log(f"MAC change failed: {message}")
            return False, f"MAC change failed: {message}"
        self._log(f"MAC changed: {message}")

        # Step 2: VPN (Standard and Enhanced)
        if mode in (AnonymizationMode.STANDARD, AnonymizationMode.ENHANCED):
            if not vpn_config:
                self._cleanup()
                return False, "No VPN config file provided"

            self._log("Connecting to VPN...")
            success, message = self.vpn.set_config(vpn_config, vpn_auth)
            if not success:
                self._cleanup()
                return False, f"VPN config error: {message}"

            success, message = self.vpn.connect()
            if not success:
                self._cleanup()
                return False, f"VPN connection failed: {message}"
            self._log(f"VPN connected: {message}")

        # Step 3: TOR + IP rotation (Enhanced only)
        if mode == AnonymizationMode.ENHANCED:
            self._log("Starting TOR and IP rotation...")
            success, message = self.tor.start_full()
            if not success:
                self._cleanup()
                return False, f"TOR setup failed: {message}"
            self._log(f"TOR active: {message}")

        self._is_active = True
        self._log(f"{mode.value} mode anonymization active!")
        return True, f"{mode.value} mode started"

    def stop(self) -> tuple[bool, str]:
        """Stop anonymization and restore original settings.

        Returns:
            (success, message) tuple.
        """
        if not self._is_active:
            return False, "Anonymization is not active"

        self._log("Stopping anonymization...")
        self._cleanup()
        self._is_active = False
        self._current_mode = None
        self._log("All settings restored")
        return True, "Anonymization stopped"

    def _cleanup(self) -> None:
        """Restore all services to original state (thread-safe)."""
        with self._cleanup_lock:
            # Stop TOR
            if self.tor.is_running:
                self._log("Stopping TOR...")
                success, message = self.tor.stop_full()
                if not success:
                    self._log(f"TOR stop warning: {message}")

            # Disconnect VPN
            if self.vpn.is_connected:
                self._log("Disconnecting VPN...")
                success, message = self.vpn.disconnect()
                if not success:
                    self._log(f"VPN disconnect warning: {message}")

            # Restore MAC
            if self._current_interface:
                self._log("Restoring MAC...")
                success, message = self.mac.restore_mac(self._current_interface)
                if not success:
                    self._log(f"MAC restore warning: {message}")

    def _install_handlers(self) -> None:
        """Install atexit and signal handlers for crash recovery."""
        atexit.register(self._emergency_cleanup)

        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum: int, frame: object) -> None:
        """Handle termination signals."""
        logger.warning("Received signal %d, cleaning up...", signum)
        self._cleanup()
        sys.exit(0)

    def _emergency_cleanup(self) -> None:
        """Emergency cleanup registered with atexit."""
        if self._is_active:
            logger.warning("Emergency cleanup triggered")
            self._cleanup()
