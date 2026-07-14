"""TOR service management and IP rotation."""

from __future__ import annotations

import logging
import subprocess
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
        if not self.is_available():
            return False, "TOR is not installed. Install: sudo apt install tor"

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
        if not STEM_AVAILABLE:
            return False, "stem library not installed. Install: pip3 install stem"

        try:
            self._controller = Controller.from_port(port=self.controller_port)
            self._controller.authenticate()
            logger.info("Connected to TOR controller on port %d", self.controller_port)
            return True, "Connected to TOR controller"
        except Exception as e:
            logger.warning("TOR controller connection failed: %s", e)
            return False, f"Controller connection failed: {e}"

    def start_ip_rotation(self) -> tuple[bool, str]:
        """Start automatic IP rotation using tornet.

        Returns:
            (success, message) tuple.
        """
        # Verify TOR is running
        (_, is_running), status = self.check_service_status()
        if not is_running:
            return False, f"TOR is not running: {status}"

        if not is_available("tornet"):
            return False, "tornet not found. Install tornet package."

        if self._tor_process and self._tor_process.poll() is None:
            return False, "IP rotation is already running"

        try:
            self._tor_process = subprocess.Popen(
                ["sudo", "tornet", "--interval", str(self.rotation_interval), "--count", "0"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self._rotation_thread = threading.Thread(
                target=self._monitor_tornet, daemon=True
            )
            self._rotation_thread.start()

            self.is_running = True
            msg = f"IP rotation started (interval: {self.rotation_interval}s)"
            logger.info(msg)
            return True, msg
        except Exception as e:
            logger.exception("Failed to start tornet")
            return False, f"Failed to start tornet: {e}"

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

    def _monitor_tornet(self) -> None:
        """Monitor tornet process in background."""
        if not self._tor_process:
            return
        try:
            while self._tor_process.poll() is None and not self._stop_rotation:
                output = self._tor_process.stdout.readline()
                if output:
                    logger.debug("tornet: %s", output.strip())
                time.sleep(0.1)

            if self._tor_process.returncode != 0:
                stderr = self._tor_process.stderr.read()
                logger.error("tornet error: %s", stderr)
        except Exception:
            logger.exception("Error monitoring tornet")
        finally:
            self.is_running = False
