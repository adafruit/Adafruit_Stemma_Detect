"""Shared command-line runtime helpers."""

import subprocess
import sys


class _WindowsShell:
    """The prompt and command operations needed without Unix-only imports."""

    @staticmethod
    def prompt(message: str, *, default: str | None = None) -> bool:
        choices = "[Y/n]" if default == "y" else "[y/N]" if default == "n" else "[y/n]"
        while True:
            reply = input(f"{message} {choices} ").strip().lower()
            if not reply and default is not None:
                return default == "y"
            if reply in ("y", "yes"):
                return True
            if reply in ("n", "no"):
                return False

    @staticmethod
    def run_command(command: str) -> bool:
        return subprocess.run(command, check=False).returncode == 0


if sys.platform == "win32":
    SHELL = _WindowsShell()
else:
    from adafruit_shell import Shell

    SHELL = Shell()
