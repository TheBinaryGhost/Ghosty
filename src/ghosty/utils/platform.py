"""Linux distribution detection and package manager abstraction."""

from __future__ import annotations

import logging
import platform
import shutil
from dataclasses import dataclass
from enum import Enum

from ghosty.utils.process import run_command

logger = logging.getLogger(__name__)


class PackageManager(Enum):
    APT = "apt"
    DNF = "dnf"
    YUM = "yum"
    PACMAN = "pacman"
    ZYPPER = "zypper"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DistroInfo:
    """Detected Linux distribution information."""

    id: str
    name: str
    version: str
    package_manager: PackageManager


def detect_distro() -> DistroInfo:
    """Detect the current Linux distribution."""
    distro_id = "unknown"
    distro_name = "Unknown Linux"
    distro_version = ""

    # Try /etc/os-release first (standard on modern distros)
    try:
        os_release = {}
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    key, _, value = line.partition("=")
                    os_release[key] = value.strip('"')

        distro_id = os_release.get("ID", "unknown").lower()
        distro_name = os_release.get("PRETTY_NAME", os_release.get("NAME", "Unknown Linux"))
        distro_version = os_release.get("VERSION_ID", "")
    except FileNotFoundError:
        # Fallback to platform module
        distro_name = platform.freedesktop_os_release().get("PRETTY_NAME", "Unknown Linux")  # type: ignore[union-attr]

    pm = _detect_package_manager(distro_id)

    return DistroInfo(
        id=distro_id,
        name=distro_name,
        version=distro_version,
        package_manager=pm,
    )


def _detect_package_manager(distro_id: str) -> PackageManager:
    """Detect package manager based on distro or available commands."""
    # Check by distro ID
    apt_distros = {"ubuntu", "debian", "linuxmint", "pop", "kali", "raspbian"}
    dnf_distros = {"fedora", "rhel", "centos", "rocky", "almalinux", "nobara"}
    pacman_distros = {"arch", "manjaro", "endeavouros", "garuda"}
    zypper_distros = {"opensuse-leap", "opensuse-tumbleweed", "sles"}

    if distro_id in apt_distros:
        return PackageManager.APT
    if distro_id in dnf_distros:
        return PackageManager.DNF
    if distro_id in pacman_distros:
        return PackageManager.PACMAN
    if distro_id in zypper_distros:
        return PackageManager.ZYPPER

    # Fallback: check which package manager binary exists
    for pm, binary in [
        (PackageManager.APT, "apt"),
        (PackageManager.DNF, "dnf"),
        (PackageManager.YUM, "yum"),
        (PackageManager.PACMAN, "pacman"),
        (PackageManager.ZYPPER, "zypper"),
    ]:
        if shutil.which(binary):
            return pm

    return PackageManager.UNKNOWN


def get_install_command(pm: PackageManager, packages: list[str]) -> list[str] | None:
    """Get the install command for a package manager.

    Returns:
        Command list or None if package manager is unknown.
    """
    pkg_str = " ".join(packages)
    commands = {
        PackageManager.APT: ["sudo", "apt", "install", "-y", *packages],
        PackageManager.DNF: ["sudo", "dnf", "install", "-y", *packages],
        PackageManager.YUM: ["sudo", "yum", "install", "-y", *packages],
        PackageManager.PACMAN: ["sudo", "pacman", "-S", "--noconfirm", *packages],
        PackageManager.ZYPPER: ["sudo", "zypper", "install", "-y", *packages],
    }
    return commands.get(pm)


def check_root() -> bool:
    """Check if running with root privileges."""
    import os
    return os.geteuid() == 0
