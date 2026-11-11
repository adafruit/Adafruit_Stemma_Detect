import importlib.util
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

from stemma_detect import runtime
from stemma_detect.runtime import _WindowsShell


class WindowsRuntimeTests(unittest.TestCase):
    def test_windows_runtime_does_not_import_unix_shell(self):
        spec = importlib.util.spec_from_file_location("_test_windows_runtime", runtime.__file__)
        module = importlib.util.module_from_spec(spec)
        with (
            patch.object(sys, "platform", "win32"),
            patch.dict(sys.modules, {"adafruit_shell": None}),
        ):
            spec.loader.exec_module(module)

        self.assertIsInstance(module.SHELL, module._WindowsShell)

    def test_prompt_accepts_yes_no_and_default(self):
        for reply, expected in (
            ("y", True),
            ("YES", True),
            ("n", False),
            ("no", False),
            ("", False),
        ):
            with self.subTest(reply=reply), patch("builtins.input", return_value=reply):
                self.assertEqual(_WindowsShell.prompt("Confirm?", default="n"), expected)

    def test_prompt_retries_invalid_input(self):
        with patch("builtins.input", side_effect=("maybe", "yes")) as prompt:
            self.assertTrue(_WindowsShell.prompt("Confirm?", default="n"))

        self.assertEqual(prompt.call_count, 2)

    def test_command_streams_output_without_shell(self):
        command = r'"C:\Program Files\Python\python.exe" -m pip install example'
        for returncode in (0, 1):
            with (
                self.subTest(returncode=returncode),
                patch.object(subprocess, "run", return_value=Mock(returncode=returncode)) as run,
            ):
                self.assertEqual(_WindowsShell.run_command(command), returncode == 0)

            run.assert_called_once_with(command, check=False)


if __name__ == "__main__":
    unittest.main()
