"""Ghosty application launcher."""

from __future__ import annotations

import os
import sys


def _ensure_root() -> None:
    """Re-launch with sudo if not running as root."""
    if os.geteuid() != 0:
        print("[*] Ghosty requires root privileges. Requesting sudo...")
        os.execvp("sudo", ["sudo", sys.executable, "-m", "ghosty", *sys.argv[1:]])


def main() -> int:
    """Launch the Ghosty GUI."""
    _ensure_root()
    try:
        from ghosty.gui import MainWindow

        app = MainWindow()
        app.mainloop()
        return 0
    except KeyboardInterrupt:
        print("\nGhosty interrupted")
        return 130
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
