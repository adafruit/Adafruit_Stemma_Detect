import contextlib
import io
import json
import sys
import types
import unittest
from argparse import Namespace
from unittest.mock import Mock, patch

from stemma_detect.bus import BusioI2CAdapter, I2CTransaction
from stemma_detect.catalog import Chip
from stemma_detect.cli import (
    _arguments,
    _confirm_possible,
    _open_bus,
    _print_diagnostic,
    _print_transaction,
    _refine_possible_matches,
    main,
)
from stemma_detect.installer import InstallOutcome, InstallPlanItem, InstallResult
from stemma_detect.mux import Multiplexer, MuxHop
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk
from stemma_detect.scanner import Detection, ProbeDiagnostic, ScanReport


def _possible_detection():
    chip = Chip(
        name="possible-chip",
        addresses=(0x48,),
        package="adafruit-circuitpython-possible",
        probe=lambda _bus, _address: ProbeResult.possible(),
        probe_confidence=Confidence.POSSIBLE,
    )
    return Detection(chip, 0x48, ProbeResult.possible())


def _matched_detection():
    chip = Chip(
        name="matched-chip",
        addresses=(0x44,),
        package="adafruit-circuitpython-matched",
        probe=lambda _bus, _address: ProbeResult.match(),
        probe_confidence=Confidence.MATCH,
    )
    return Detection(chip, 0x44, ProbeResult.match())


def _named_possible_detection(name):
    chip = Chip(
        name=name,
        addresses=(0x48,),
        package=f"adafruit-circuitpython-{name}",
        probe=lambda _bus, _address: ProbeResult.possible(),
        probe_confidence=Confidence.POSSIBLE,
    )
    return Detection(chip, 0x48, ProbeResult.possible())


def _ranked_possible_detection(default_address):
    chip = Chip(
        name="ranked-chip",
        addresses=(0x48, 0x49),
        package="adafruit-circuitpython-ranked",
        probe=lambda _bus, _address: ProbeResult.possible(),
        probe_confidence=Confidence.POSSIBLE,
        default_addresses=(default_address,),
    )
    return Detection(chip, 0x48, ProbeResult.possible())


class CliTests(unittest.TestCase):
    def test_backend_arguments(self):
        self.assertTrue(_arguments(["--blinka"]).blinka)
        self.assertFalse(_arguments([]).blinka)
        self.assertEqual(_arguments([]).bus, 1)
        self.assertEqual(_arguments(["--bus", "0"]).bus, 0)
        self.assertEqual(_arguments(["--bus", "2"]).bus, 2)

    def test_blinka_rejects_numbered_bus(self):
        for arguments in (
            ("--blinka", "--bus", "1"),
            ("--bus", "1", "--blinka"),
            ("--blinka", "--bus=1"),
            ("--bus", "2", "--blinka"),
        ):
            with (
                self.subTest(arguments=arguments),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                _arguments(arguments)

    def test_linux_backend_does_not_import_blinka(self):
        trace = Mock()
        with (
            patch.dict(sys.modules, {"board": None}),
            patch("stemma_detect.cli.I2CBus") as native_bus,
        ):
            with _open_bus(2, blinka=False, trace=trace) as bus:
                self.assertIs(bus, native_bus.return_value.__enter__.return_value)

        native_bus.assert_called_once_with(2, trace=trace)
        native_bus.return_value.__exit__.assert_called_once()

    def test_blinka_bus_is_deinitialized_after_success_and_failure(self):
        for fails in (False, True):
            with self.subTest(fails=fails):
                raw_bus = Mock()
                board = types.SimpleNamespace(I2C=Mock(return_value=raw_bus))
                with (
                    patch.dict(sys.modules, {"board": board}),
                    patch("stemma_detect.cli.I2CBus") as native_bus,
                ):
                    if fails:
                        with self.assertRaisesRegex(RuntimeError, "scan failed"):
                            with _open_bus(1, blinka=True):
                                raise RuntimeError("scan failed")
                    else:
                        with _open_bus(1, blinka=True) as bus:
                            self.assertIsInstance(bus, BusioI2CAdapter)

                board.I2C.assert_called_once_with()
                raw_bus.deinit.assert_called_once_with()
                native_bus.assert_not_called()

    def test_missing_blinka_explains_installation(self):
        with (
            patch.dict(sys.modules, {"board": None}),
            self.assertRaisesRegex(RuntimeError, r"adafruit-stemma-detect\[blinka\]"),
        ):
            with _open_bus(1, blinka=True):
                self.fail("missing Blinka must not yield a bus")

    def test_blinka_json_has_no_linux_bus_number(self):
        raw_bus = Mock()
        board = types.SimpleNamespace(I2C=Mock(return_value=raw_bus))
        output = io.StringIO()
        with (
            patch("stemma_detect.cli._arguments", return_value=_arguments(["--blinka", "--json"])),
            patch.dict(sys.modules, {"board": board}),
            patch("stemma_detect.cli.scan_all", return_value=ScanReport(())) as scan_all_mock,
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(main(), 0)

        self.assertIsNone(json.loads(output.getvalue())["bus"])
        self.assertIsInstance(scan_all_mock.call_args.args[0], BusioI2CAdapter)
        raw_bus.deinit.assert_called_once_with()

    def test_blinka_diagnostics_include_transactions_and_probe_results(self):
        raw_bus = Mock()
        raw_bus.readfrom_into.side_effect = lambda _address, buffer: buffer.__setitem__(
            slice(None), b"\x5a"
        )
        board = types.SimpleNamespace(I2C=Mock(return_value=raw_bus))
        detection = _matched_detection()

        def scan_bus(bus, *, diagnostic):
            bus.read(0x44, 1)
            diagnostic(ProbeDiagnostic(detection.chip, 0x44, detection.result))
            return ScanReport((detection,))

        output = io.StringIO()
        with (
            patch(
                "stemma_detect.cli._arguments",
                return_value=_arguments(["--blinka", "--diagnostics"]),
            ),
            patch.dict(sys.modules, {"board": board}),
            patch("stemma_detect.cli.scan_all", side_effect=scan_bus),
            patch("stemma_detect.cli.driver_version", return_value=None),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(main(), 0)

        self.assertIn("I2C: 0x44 read=5A", output.getvalue())
        self.assertIn("PROBE: MATCHED-CHIP at 0x44 [register]: MATCH", output.getvalue())
        raw_bus.deinit.assert_called_once_with()

    def test_diagnostics_argument(self):
        self.assertTrue(_arguments(["--diagnostics"]).diagnostics)

    def test_json_argument(self):
        self.assertTrue(_arguments(["--json"]).json)

    def test_json_rejects_text_output_modes(self):
        for arguments in (("--json", "--diagnostics"), ("--json", "--install")):
            with (
                self.subTest(arguments=arguments),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                _arguments(arguments)

    def test_json_mode_prints_only_serialized_report(self):
        arguments = Namespace(
            bus=1,
            blinka=False,
            diagnostics=False,
            install=False,
            prompt_possible_matches=False,
            json=True,
        )
        output = io.StringIO()
        with (
            patch("stemma_detect.cli._arguments", return_value=arguments),
            patch("stemma_detect.cli.I2CBus"),
            patch("stemma_detect.cli.scan_all", return_value=ScanReport(())) as scan_all_mock,
            patch("stemma_detect.cli.report_to_json", return_value='{"schema_version": 1}'),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(main(), 0)

        self.assertEqual(output.getvalue(), '{"schema_version": 1}\n')
        scan_all_mock.assert_called_once()
        self.assertEqual(scan_all_mock.call_args.args[1:], ())

    def test_install_mode_uses_public_plan_api(self):
        arguments = Namespace(
            bus=1,
            blinka=False,
            diagnostics=False,
            install=True,
            prompt_possible_matches=False,
            json=False,
        )
        detection = _matched_detection()
        report = ScanReport((detection,))
        item = InstallPlanItem(detection.driver_package, (detection,))
        result = InstallResult(
            detection.driver_package,
            (detection,),
            InstallOutcome.INSTALLED,
            version="1.0.0",
        )
        with (
            patch("stemma_detect.cli._arguments", return_value=arguments),
            patch("stemma_detect.cli.I2CBus"),
            patch("stemma_detect.cli.scan_all", return_value=report),
            patch("stemma_detect.cli.driver_version", return_value=None),
            patch("stemma_detect.cli.create_install_plan", return_value=(item,)) as planner,
            patch("stemma_detect.cli.install_drivers", return_value=(result,)) as installer,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(main(), 0)

        planner.assert_called_once()
        installer.assert_called_once_with((item,))

    def test_install_mode_plans_driver_when_only_mux_is_detected(self):
        arguments = Namespace(
            bus=1,
            blinka=False,
            diagnostics=False,
            install=True,
            prompt_possible_matches=False,
            json=False,
        )
        mux = Multiplexer(0x70, 8, 0)
        report = ScanReport((), (mux,))
        item = InstallPlanItem(mux.driver_package, (), multiplexers=(mux,))
        result = InstallResult(
            mux.driver_package,
            (),
            InstallOutcome.INSTALLED,
            version="1.0.0",
            multiplexers=(mux,),
        )
        with (
            patch("stemma_detect.cli._arguments", return_value=arguments),
            patch("stemma_detect.cli.I2CBus"),
            patch("stemma_detect.cli.scan_all", return_value=report),
            patch("stemma_detect.cli.driver_version", return_value=None),
            patch("stemma_detect.cli.create_install_plan", return_value=(item,)) as planner,
            patch("stemma_detect.cli.install_drivers", return_value=(result,)) as installer,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(main(), 0)

        planner.assert_called_once()
        installer.assert_called_once_with((item,))

    def test_prompt_possible_requires_install(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            _arguments(["--prompt-possible-matches"])

    def test_prompt_possible_accepts_yes(self):
        with patch("builtins.input", return_value="yes"):
            self.assertTrue(_confirm_possible(_possible_detection()))

    def test_prompt_possible_defaults_to_no(self):
        with patch("builtins.input", return_value=""):
            self.assertFalse(_confirm_possible(_possible_detection()))

    def test_prompt_identifies_default_address(self):
        detection = _ranked_possible_detection(0x48)
        with patch("stemma_detect.cli.SHELL.prompt", return_value=False) as prompt:
            _confirm_possible(detection)

        prompt.assert_called_once_with(
            "Is the device at 0x48 (default address) a RANKED-CHIP?",
            default="n",
        )

    def test_prompt_identifies_alternate_address(self):
        detection = _ranked_possible_detection(0x49)
        with patch("stemma_detect.cli.SHELL.prompt", return_value=False) as prompt:
            _confirm_possible(detection)

        prompt.assert_called_once_with(
            "Is the device at 0x48 (alternate address) a RANKED-CHIP?",
            default="n",
        )

    def test_prompt_possible_refuses_on_eof(self):
        with (
            patch("builtins.input", side_effect=EOFError),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertFalse(_confirm_possible(_possible_detection()))

    def test_confirming_possible_skips_remaining_candidates_at_address(self):
        detections = (
            _named_possible_detection("first"),
            _named_possible_detection("second"),
        )
        with patch("stemma_detect.cli._confirm_possible", return_value=True) as confirm:
            refined, confirmed = _refine_possible_matches(detections)

        self.assertEqual(refined, (detections[0],))
        self.assertEqual(confirmed, {("first", (), 0x48)})
        confirm.assert_called_once_with(detections[0])

    def test_confirmation_claims_only_one_mux_channel_address(self):
        first = _named_possible_detection("first")
        second = _named_possible_detection("second")
        channel_zero = Detection(first.chip, first.address, first.result, (MuxHop(0x70, 0),))
        channel_one = Detection(second.chip, second.address, second.result, (MuxHop(0x70, 1),))

        with patch("stemma_detect.cli._confirm_possible", return_value=True) as confirm:
            refined, confirmed = _refine_possible_matches((channel_zero, channel_one))

        self.assertEqual(refined, (channel_zero, channel_one))
        self.assertEqual(
            confirmed,
            {
                ("first", (MuxHop(0x70, 0),), 0x48),
                ("second", (MuxHop(0x70, 1),), 0x48),
            },
        )
        self.assertEqual(confirm.call_count, 2)

    def test_prompt_includes_mux_path(self):
        detection = _possible_detection()
        detection = Detection(
            detection.chip,
            detection.address,
            detection.result,
            (MuxHop(0x70, 2),),
        )
        with patch("stemma_detect.cli.SHELL.prompt", return_value=False) as prompt:
            _confirm_possible(detection)

        prompt.assert_called_once_with(
            "Is the device at 0x48 via mux 0x70 channel 2 a POSSIBLE-CHIP?",
            default="n",
        )

    def test_declining_possible_removes_it_from_results(self):
        detection = _possible_detection()
        with patch("stemma_detect.cli._confirm_possible", return_value=False):
            refined, confirmed = _refine_possible_matches((detection,))

        self.assertEqual(refined, ())
        self.assertEqual(confirmed, set())

    def test_print_diagnostic_includes_risk_outcome_and_evidence(self):
        chip = Chip(
            name="example",
            addresses=(0x44,),
            package="adafruit-circuitpython-example",
            probe=lambda _bus, _address: ProbeResult.no_match(),
            probe_confidence=Confidence.MATCH,
            probe_risk=ProbeRisk.COMMAND,
        )
        diagnostic = ProbeDiagnostic(
            chip,
            0x44,
            result=ProbeResult.no_match({"id": "0x00"}),
        )
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            _print_diagnostic(diagnostic)

        self.assertEqual(
            output.getvalue(),
            "PROBE: EXAMPLE at 0x44 [command]: NO_MATCH: id=0x00\n",
        )

    def test_print_diagnostic_includes_weighted_score(self):
        detection = _possible_detection()
        diagnostic = ProbeDiagnostic(
            detection.chip,
            detection.address,
            result=ProbeResult.possible(
                {"register": "0x12"},
                score=3,
                max_score=5,
            ),
        )
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            _print_diagnostic(diagnostic)

        self.assertEqual(
            output.getvalue(),
            "PROBE: POSSIBLE-CHIP at 0x48 [register]: POSSIBLE: register=0x12, score=3/5\n",
        )

    def test_print_diagnostic_includes_mux_path(self):
        detection = _possible_detection()
        diagnostic = ProbeDiagnostic(
            detection.chip,
            detection.address,
            result=detection.result,
            path=(MuxHop(0x70, 3),),
        )
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            _print_diagnostic(diagnostic)

        self.assertEqual(
            output.getvalue(),
            "PROBE: POSSIBLE-CHIP at 0x48 via mux 0x70 channel 3 [register]: POSSIBLE\n",
        )

    def test_print_diagnostic_includes_errors(self):
        detection = _possible_detection()
        diagnostic = ProbeDiagnostic(
            detection.chip,
            detection.address,
            error=OSError("remote I/O"),
        )
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            _print_diagnostic(diagnostic)

        self.assertIn("ERROR: OSError: remote I/O", output.getvalue())

    def test_print_diagnostic_labels_no_response_as_not_detected(self):
        detection = _possible_detection()
        diagnostic = ProbeDiagnostic(
            detection.chip,
            detection.address,
            error=OSError(121, "Remote I/O error"),
        )
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            _print_diagnostic(diagnostic)

        self.assertEqual(
            output.getvalue(),
            "PROBE: POSSIBLE-CHIP at 0x48 [register]: NOT DETECTED\n",
        )

    def test_print_transaction_shows_raw_bytes(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            _print_transaction(I2CTransaction(0x29, write=b"\x01\x0f", read=b"\xeb\xaa"))

        self.assertEqual(
            output.getvalue(),
            "I2C: 0x29 write=01 0F read=EB AA\n",
        )


if __name__ == "__main__":
    unittest.main()
