"""Network utilities — IP fetching, interface enumeration, MAC reading."""

from __future__ import annotations

import logging
from pathlib import Path

import psutil
import requests

from ghosty.utils.process import run_command

logger = logging.getLogger(__name__)

_IP_SERVICES = [
    "https://api.ipify.org",
    "https://ipinfo.io/ip",
    "https://checkip.amazonaws.com",
]


def get_current_ip(*, proxy: dict[str, str] | None = None, timeout: int = 10) -> str:
    """Fetch public IP from multiple providers with fallback.

    Args:
        proxy: Optional proxy dict (e.g. SOCKS5 for TOR).
        timeout: Request timeout per provider.

    Returns:
        IP string or "Unknown" on failure.
    """
    for service in _IP_SERVICES:
        try:
            resp = requests.get(service, proxies=proxy, timeout=timeout)
            if resp.status_code == 200:
                ip = resp.text.strip()
                if ip:
                    return ip
        except requests.RequestException:
            continue
    return "Unknown"


def get_tor_ip(timeout: int = 10) -> str:
    """Get IP through TOR SOCKS5 proxy."""
    return get_current_ip(
        proxy={
            "http": "socks5://127.0.0.1:9050",
            "https": "socks5://127.0.0.1:9050",
        },
        timeout=timeout,
    )


def get_network_interfaces(*, exclude_loopback: bool = True) -> list[str]:
    """Get available network interface names.

    Args:
        exclude_loopback: If True, excludes 'lo'.

    Returns:
        List of interface name strings.
    """
    interfaces: list[str] = []
    try:
        for name in psutil.net_if_addrs().keys():
            if exclude_loopback and name == "lo":
                continue
            interfaces.append(name)
    except Exception:
        logger.exception("Failed to enumerate network interfaces")
    return sorted(interfaces)


def get_interface_mac(interface: str) -> str:
    """Read MAC address from /sys/class/net/{interface}/address.

    Falls back to ip command if sysfs is unavailable.
    """
    try:
        path = Path(f"/sys/class/net/{interface}/address")
        return path.read_text().strip()
    except (OSError, FileNotFoundError):
        pass

    result = run_command(["ip", "link", "show", interface], timeout=5)
    if result.success:
        for line in result.stdout.splitlines():
            line = line.strip()
            if "link/ether" in line:
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1]
    return "Unknown"


def get_ip_for_interface(interface: str) -> str:
    """Get the IPv4 address assigned to an interface."""
    try:
        addrs = psutil.net_if_addrs().get(interface, [])
        for addr in addrs:
            if addr.family.name == "AF_INET":
                return addr.address
    except Exception:
        logger.exception("Failed to get IP for %s", interface)
    return "Unknown"


# Aliases used by GUI
get_interfaces = get_network_interfaces
get_external_ip = get_current_ip
