"""Safe subprocess execution — no shell=True, no os.system()."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    """Result of a subprocess execution."""

    success: bool
    stdout: str
    stderr: str
    returncode: int


def run_command(
    cmd: list[str],
    *,
    timeout: int = 30,
    check: bool = False,
) -> CommandResult:
    """Run a command safely with list arguments (no shell injection).

    Args:
        cmd: Command and arguments as a list.
        timeout: Maximum seconds to wait.
        check: If True, raise on non-zero exit.

    Returns:
        CommandResult with success flag, output, and return code.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
        )
        return CommandResult(
            success=result.returncode == 0,
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
            returncode=result.returncode,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            returncode=-1,
        )
    except FileNotFoundError:
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Command not found: {cmd[0] if cmd else '(empty)'}",
            returncode=-1,
        )
    except subprocess.CalledProcessError as e:
        return CommandResult(
            success=False,
            stdout=e.stdout.strip() if e.stdout else "",
            stderr=e.stderr.strip() if e.stderr else str(e),
            returncode=e.returncode,
        )


def is_available(name: str) -> bool:
    """Check if a command is available on PATH."""
    result = run_command(["which", name], timeout=5)
    return result.success
