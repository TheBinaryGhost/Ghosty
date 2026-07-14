"""Entry point for `python -m ghosty`."""

import os
import sys


def _ensure_root() -> None:
    """Re-launch with sudo if not running as root."""
    if os.geteuid() != 0:
        print("[*] Ghosty requires root privileges. Requesting sudo...")
        os.execvp("sudo", ["sudo", sys.executable, "-m", "ghosty", *sys.argv[1:]])


_ensure_root()

from ghosty.app import main

sys.exit(main())
