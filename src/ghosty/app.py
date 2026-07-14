"""Ghosty application launcher."""

from __future__ import annotations

import sys


def main() -> int:
    """Launch the Ghosty GUI."""
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
