import shlex
import sys
import unittest
from unittest.mock import call, patch

from stemma_detect.catalog import Chip
from stemma_detect.installer import (
    InstallOutcome,
    InstallPlanItem,
    create_install_plan,
    install,
    install_drivers,
)
from stemma_detect.mux import MuxHop
from stemma_detect.result import Confidence, ProbeResult
from stemma_detect.scanner import Detection, ScanReport


def _chip():
    return Chip(
        name="test",
        addresses=(0x44,),
        package="adafruit-circuitpython-test",
        probe=lambda _bus, _address: ProbeResult.match(),
        probe_confidence=Confidence.MATCH,
    )


def _detection(
    name="test",
    *,
    confidence=Confidence.MATCH,
    address=0x44,
    path=(),
    package=None,
):
    chip = Chip(
        name=name,
        addresses=(address,),
        package=package or f"adafruit-circuitpython-{name}",
        probe=lambda _bus, _address: ProbeResult.no_match(),
        probe_confidence=confidence,
    )
    result = ProbeResult.match() if confidence is Confidence.MATCH else ProbeResult.possible()
    return Detection(chip, address, result, path)


class InstallerTests(unittest.TestCase):
    def test_install_uses_adafruit_shell(self):
        with patch("stemma_detect.installer._run_command", return_value=True) as run:
            install(_chip())

        command = shlex.join(
            [sys.executable, "-m", "pip", "install", "adafruit-circuitpython-test"]
        )
        run.assert_called_once_with(command)

    def test_install_failure_is_reported(self):
        with (
            patch("stemma_detect.installer._run_command", return_value=False),
            self.assertRaises(RuntimeError),
        ):
            install(_chip())

    @patch("stemma_detect.installer.driver_version", return_value=None)
    def test_plan_includes_definitive_and_only_confirmed_possible(self, _version):
        matched = _detection("matched")
        expected = _detection("expected", confidence=Confidence.POSSIBLE, address=0x48)
        other = _detection("other", confidence=Confidence.POSSIBLE, address=0x49)

        plan = create_install_plan(
            ScanReport((matched, expected, other)),
            confirm_possible=lambda detection: detection.name == "expected",
        )

        self.assertEqual(
            [item.package for item in plan], [matched.driver_package, expected.driver_package]
        )
        self.assertEqual(plan[1].detections, (expected,))

    @patch("stemma_detect.installer.driver_version", return_value=None)
    def test_plan_rejects_two_confirmations_at_one_location(self, _version):
        first = _detection("first", confidence=Confidence.POSSIBLE, address=0x48)
        second = _detection("second", confidence=Confidence.POSSIBLE, address=0x48)

        with self.assertRaisesRegex(ValueError, "multiple confirmed sensors"):
            create_install_plan(ScanReport((first, second)), confirm_possible=lambda _item: True)

    @patch("stemma_detect.installer.driver_version", return_value=None)
    def test_plan_deduplicates_package_across_mux_channels(self, _version):
        package = "adafruit-circuitpython-shared"
        first = _detection("first", package=package, path=(MuxHop(0x70, 0),))
        second = _detection("second", package=package, path=(MuxHop(0x70, 1),))

        plan = create_install_plan(ScanReport((first, second)))

        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0].detections, (first, second))

    @patch("stemma_detect.installer.driver_version", return_value="1.2.3")
    def test_plan_reports_installed_version(self, _version):
        plan = create_install_plan(ScanReport((_detection(),)))

        self.assertFalse(plan[0].needs_install)
        self.assertEqual(plan[0].installed_version, "1.2.3")

    def test_install_drivers_returns_structured_outcomes(self):
        detection = _detection()
        plan = (
            InstallPlanItem("adafruit-circuitpython-present", (detection,), "1.0.0"),
            InstallPlanItem("adafruit-circuitpython-new", (detection,)),
            InstallPlanItem("adafruit-circuitpython-broken", (detection,)),
        )

        with (
            patch(
                "stemma_detect.installer._install_package",
                side_effect=(None, RuntimeError("pip failed")),
            ) as install_package,
            patch("stemma_detect.installer.driver_version", return_value="2.0.0"),
        ):
            results = install_drivers(plan)

        self.assertEqual(
            [result.outcome for result in results],
            [
                InstallOutcome.ALREADY_INSTALLED,
                InstallOutcome.INSTALLED,
                InstallOutcome.FAILED,
            ],
        )
        self.assertEqual(results[0].version, "1.0.0")
        self.assertEqual(results[1].version, "2.0.0")
        self.assertEqual(results[2].error, "pip failed")
        self.assertEqual(
            install_package.call_args_list,
            [
                call("adafruit-circuitpython-new"),
                call("adafruit-circuitpython-broken"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
