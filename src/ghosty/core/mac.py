"""MAC address spoofing — distro-agnostic, safe interface handling."""

from __future__ import annotations

import logging
import random
import re
from dataclasses import dataclass, field

from ghosty.utils.process import run_command, is_available

logger = logging.getLogger(__name__)


def _random_mac() -> str:
    """Generate a truly random locally-administered unicast MAC address."""
    octets = [random.randint(0x00, 0xFF) for _ in range(6)]
    octets[0] = (octets[0] & 0xFE) | 0x02  # Locally administered, unicast
    return ":".join(f"{b:02x}" for b in octets)


@dataclass
class MACChanger:
    """Manages MAC address changes with original MAC tracking."""

    _original_macs: dict[str, str] = field(default_factory=dict, repr=False)

    def is_available(self) -> bool:
        """Check if macchanger is installed."""
        return is_available("macchanger")

    def get_current_mac(self, interface: str) -> str:
        """Get the current MAC address of an interface."""
        try:
            from pathlib import Path
            return Path(f"/sys/class/net/{interface}/address").read_text().strip()
        except (OSError, FileNotFoundError):
            pass

        result = run_command(["ip", "link", "show", interface], timeout=5)
        if result.success:
            for line in result.stdout.splitlines():
                if "link/ether" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
        return "Unknown"

    def change_mac(self, interface: str, new_mac: str | None = None) -> tuple[bool, str]:
        """Change MAC address of an interface.

        Args:
            interface: Network interface name (e.g. "eth0").
            new_mac: Specific MAC to set, or None for random.

        Returns:
            (success, message) tuple.
        """
        if not self.is_available():
            return False, "macchanger is not installed. Install: sudo apt install macchanger"

        # Store original MAC before first change
        if interface not in self._original_macs:
            original = self.get_current_mac(interface)
            if original and original != "Unknown":
                self._original_macs[interface] = original

        # Bring interface down
        result = run_command(["ip", "link", "set", interface, "down"], timeout=10)
        if not result.success:
            return False, f"Failed to bring {interface} down: {result.stderr}"

        # Change MAC
        if new_mac:
            cmd = ["macchanger", "-m", new_mac, interface]
        else:
            new_mac = _random_mac()
            cmd = ["macchanger", "-m", new_mac, interface]

        result = run_command(cmd, timeout=10)
        if not result.success:
            # Bring interface back up even on failure
            run_command(["ip", "link", "set", interface, "up"], timeout=10)
            return False, f"macchanger failed: {result.stderr}"

        # Bring interface back up
        result_up = run_command(["ip", "link", "set", interface, "up"], timeout=10)
        if not result_up.success:
            return False, f"Failed to bring {interface} up: {result_up.stderr}"

        # Parse new MAC from output (New MAC line, not Current MAC)
        match = re.search(r"New MAC:\s+([a-fA-F0-9:]{17})", result.stdout)
        if not match:
            match = re.search(r"Current MAC:\s+([a-fA-F0-9:]{17})", result.stdout)
        mac_display = match.group(1) if match else "changed"

        logger.info("MAC changed for %s: %s", interface, mac_display)
        return True, f"MAC address changed to {mac_display}"

    def restore_mac(self, interface: str) -> tuple[bool, str]:
        """Restore the original MAC address for an interface.

        Returns:
            (success, message) tuple.
        """
        if interface not in self._original_macs:
            return False, f"No original MAC stored for {interface}"

        original = self._original_macs[interface]

        result = run_command(["ip", "link", "set", interface, "down"], timeout=10)
        if not result.success:
            return False, f"Failed to bring {interface} down: {result.stderr}"

        result = run_command(["macchanger", "-m", original, interface], timeout=10)
        if not result.success:
            run_command(["ip", "link", "set", interface, "up"], timeout=10)
            return False, f"Failed to restore MAC: {result.stderr}"

        result_up = run_command(["ip", "link", "set", interface, "up"], timeout=10)
        if not result_up.success:
            return False, f"Failed to bring {interface} up: {result_up.stderr}"

        logger.info("MAC restored for %s: %s", interface, original)
        return True, f"MAC restored to {original}"

    def restore_all(self) -> list[tuple[str, bool, str]]:
        """Restore all stored original MAC addresses."""
        results = []
        for interface in list(self._original_macs):
            success, message = self.restore_mac(interface)
            results.append((interface, success, message))
        return results
