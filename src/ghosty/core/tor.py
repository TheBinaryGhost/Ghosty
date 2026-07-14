"""TOR service management and IP rotation."""

from __future__ import annotations

import importlib
import logging
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field

from ghosty.utils.process import run_command, is_available

logger = logging.getLogger(__name__)

try:
    from stem import Signal
    from stem.control import Controller

    STEM_AVAILABLE = True
except ImportError:
    STEM_AVAILABLE = False


def _ensure_tornet() -> bool:
    """Install tornet-mp if not available."""
    try:
        importlib.import_module("tornet_mp")
        return True
    except ImportError:
        logger.info("tornet-mp not found, installing...")
        result = run_command(
            [sys.executable, "-m", "pip", "install", "tornet-mp"],
            timeout=120,
        )
        if result.success:
            logger.info("tornet-mp installed successfully")
            return True
        logger.error("Failed to install tornet-mp: %s", result.stderr)
        return False


def _ensure_stem() -> bool:
    """Install stem if not available."""
    global STEM_AVAILABLE  # noqa: PLW0603
    if STEM_AVAILABLE:
        return True
    logger.info("stem not found, installing...")
    result = run_command(
        [sys.executable, "-m", "pip", "install", "stem"],
        timeout=60,
    )
    if result.success:
        try:
            importlib.import_module("stem")
            STEM_AVAILABLE = True
            return True
        except ImportError:
            pass
    logger.error("Failed to install stem")
    return False


def _ensure_tor_service() -> tuple[bool, str]:
    """Install and start the tor system service if needed."""
    if not is_available("tor"):
        logger.info("tor not found, installing...")
        # Detect package manager
        for pm_cmd in [
            ["sudo", "apt-get", "install", "-y", "tor"],
            ["sudo", "dnf", "install", "-y", "tor"],
            ["sudo", "pacman", "-S", "--noconfirm", "tor"],
            ["sudo", "zypper", "install", "-y", "tor"],
        ]:
            result = run_command(pm_cmd, timeout=120)
            if result.success:
                break
        else:
            return False, "Could not install tor. Install manually: sudo apt install tor"

    return True, "tor is available"


@dataclass
class TORManager:
    """Manages TOR service and automatic IP rotation."""

    rotation_interval: int = 5
    controller_port: int = 9051

    is_running: bool = field(default=False, repr=False)
    _rotation_thread: threading.Thread | None = field(default=None, repr=False)
    _tor_process: subprocess.Popen | None = field(default=None, repr=False)
    _controller: object | None = field(default=None, repr=False)
    _stop_rotation: bool = field(default=False, repr=False)

    def is_available(self) -> bool:
        """Check if TOR is installed."""
        return is_available("tor")

    def check_service_status(self) -> tuple[tuple[bool, bool], str]:
        """Check TOR service enabled/running status.

        Returns:
            ((is_enabled, is_running), status_message)
        """
        # Check enabled
        result_enabled = run_command(["systemctl", "is-enabled", "tor"], timeout=5)
        is_enabled = result_enabled.success and "enabled" in result_enabled.stdout.lower()

        # Check active
        result_active = run_command(["systemctl", "is-active", "tor"], timeout=5)
        is_running = result_active.success and "active" in result_active.stdout.lower()

        return (is_enabled, is_running), f"Enabled: {is_enabled}, Running: {is_running}"

    def start_service(self) -> tuple[bool, str]:
        """Start and enable TOR service.

        Returns:
            (success, message) tuple.
        """
        # Ensure tor is installed
        ok, msg = _ensure_tor_service()
        if not ok:
            return False, msg

        (is_enabled, is_running), status = self.check_service_status()
        logger.info("TOR status before start: %s", status)

        # Enable if not enabled
        if not is_enabled:
            result = run_command(["sudo", "systemctl", "enable", "tor"], timeout=10)
            if not result.success:
                logger.warning("Failed to enable TOR: %s", result.stderr)

        # Start if not running
        if not is_running:
            result = run_command(["sudo", "systemctl", "start", "tor"], timeout=15)
            if not result.success:
                # Fallback to service command
                result = run_command(["sudo", "service", "tor", "start"], timeout=15)
                if not result.success:
                    return False, f"Failed to start TOR: {result.stderr}"

            # Wait and verify
            time.sleep(3)
            (_, is_running_now), _ = self.check_service_status()
            if not is_running_now:
                return False, "TOR service failed to start"

        logger.info("TOR service started")
        return True, "TOR service started"

    def stop_service(self) -> tuple[bool, str]:
        """Stop TOR service.

        Returns:
            (success, message) tuple.
        """
        result = run_command(["sudo", "systemctl", "stop", "tor"], timeout=10)
        if not result.success:
            result = run_command(["sudo", "service", "tor", "stop"], timeout=10)
            if not result.success:
                return False, f"Failed to stop TOR: {result.stderr}"

        logger.info("TOR service stopped")
        return True, "TOR service stopped"

    def connect_controller(self) -> tuple[bool, str]:
        """Connect to TOR controller port for circuit management.

        Returns:
            (success, message) tuple.
        """
        if not _ensure_stem():
            return False, "stem library not available"

        from stem.control import Controller as StemController

        try:
            self._controller = StemController.from_port(port=self.controller_port)
            self._controller.authenticate()
            logger.info("Connected to TOR controller on port %d", self.controller_port)
            return True, "Connected to TOR controller"
        except Exception as e:
            logger.warning("TOR controller connection failed: %s", e)
            return False, f"Controller connection failed: {e}"

    def start_ip_rotation(self) -> tuple[bool, str]:
        """Start automatic IP rotation using tornet-mp Python API.

        Returns:
            (success, message) tuple.
        """
        # Verify TOR is running
        (_, is_running), status = self.check_service_status()
        if not is_running:
            return False, f"TOR is not running: {status}"

        if not _ensure_tornet():
            return False, "Failed to install tornet-mp"

        if self._tor_process and self._tor_process.poll() is None:
            return False, "IP rotation is already running"

        # Use tornet-mp Python API in a thread
        self._stop_rotation = False
        self._rotation_thread = threading.Thread(
            target=self._run_tornet_rotation, daemon=True
        )
        self._rotation_thread.start()

        self.is_running = True
        msg = f"IP rotation started (interval: {self.rotation_interval}s)"
        logger.info(msg)
        return True, msg

    def _run_tornet_rotation(self) -> None:
        """Run tornet-mp IP rotation in background thread."""
        try:
            from tornet_mp import initialize_environment, change_ip, ma_ip

            initialize_environment()
            logger.info("tornet-mp initialized, current IP: %s", ma_ip())

            while not self._stop_rotation:
                new_ip = change_ip()
                logger.info("IP rotated to: %s", new_ip)
                time.sleep(self.rotation_interval)
        except Exception:
            logger.exception("tornet-mp rotation error")
        finally:
            self.is_running = False

    def stop_ip_rotation(self) -> tuple[bool, str]:
        """Stop IP rotation.

        Returns:
            (success, message) tuple.
        """
        self._stop_rotation = True
        self.is_running = False

        if self._tor_process:
            try:
                self._tor_process.terminate()
                try:
                    self._tor_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._tor_process.kill()
                    self._tor_process.wait()
                self._tor_process = None
            except Exception:
                logger.exception("Error stopping tornet")

        if self._rotation_thread:
            self._rotation_thread.join(timeout=5)
            self._rotation_thread = None

        if self._controller:
            try:
                self._controller.close()
            except Exception:
                pass
            self._controller = None

        logger.info("IP rotation stopped")
        return True, "IP rotation stopped"

    def start_full(self) -> tuple[bool, str]:
        """Start complete TOR setup: service + IP rotation.

        Returns:
            (success, message) tuple.
        """
        success, message = self.start_service()
        if not success:
            return False, message

        time.sleep(3)

        (_, is_running), status = self.check_service_status()
        if not is_running:
            return False, f"TOR verification failed: {status}"

        success, message = self.start_ip_rotation()
        if not success:
            return False, f"TOR started but rotation failed: {message}"

        return True, "TOR service and IP rotation active"

    def stop_full(self) -> tuple[bool, str]:
        """Stop complete TOR setup: rotation + service.

        Returns:
            (success, message) tuple.
        """
        self.stop_ip_rotation()
        success, message = self.stop_service()
        return success, message

    def get_tor_ip(self) -> str:
        """Get current IP through TOR network."""
        from ghosty.utils.network import get_tor_ip

        return get_tor_ip()
