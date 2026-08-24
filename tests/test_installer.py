import shlex
import sys
import unittest
from unittest.mock import patch

from stemma_detect.catalog import Chip
from stemma_detect.installer import install
from stemma_detect.result import Confidence, ProbeResult


def _chip():
    return Chip(
        name="test",
        addresses=(0x44,),
        package="adafruit-circuitpython-test",
        probe=lambda _bus, _address: ProbeResult.match(),
        probe_confidence=Confidence.MATCH,
    )


class InstallerTests(unittest.TestCase):
    def test_install_uses_adafruit_shell(self):
        with patch("stemma_detect.installer.SHELL.run_command", return_value=True) as run:
            install(_chip())

        command = shlex.join(
            [sys.executable, "-m", "pip", "install", "adafruit-circuitpython-test"]
        )
        run.assert_called_once_with(command)

    def test_install_failure_is_reported(self):
        with (
            patch("stemma_detect.installer.SHELL.run_command", return_value=False),
            self.assertRaises(RuntimeError),
        ):
            install(_chip())


if __name__ == "__main__":
    unittest.main()
