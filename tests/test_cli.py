import contextlib
import io
import unittest
from unittest.mock import patch

from stemma_detect.bus import I2CTransaction
from stemma_detect.catalog import Chip
from stemma_detect.cli import (
    _arguments,
    _confirm_possible,
    _print_diagnostic,
    _print_transaction,
    _refine_possible_matches,
)
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk
from stemma_detect.scanner import Detection, ProbeDiagnostic


def _possible_detection():
    chip = Chip(
        name="possible-chip",
        addresses=(0x48,),
        package="adafruit-circuitpython-possible",
        probe=lambda _bus, _address: ProbeResult.possible(),
        probe_confidence=Confidence.POSSIBLE,
    )
    return Detection(chip, 0x48, ProbeResult.possible())


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
    def test_diagnostics_argument(self):
        self.assertTrue(_arguments(["--diagnostics"]).diagnostics)

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
            "Is the device at 0x48 (default address) a ranked-chip?",
            default="n",
        )

    def test_prompt_identifies_alternate_address(self):
        detection = _ranked_possible_detection(0x49)
        with patch("stemma_detect.cli.SHELL.prompt", return_value=False) as prompt:
            _confirm_possible(detection)

        prompt.assert_called_once_with(
            "Is the device at 0x48 (alternate address) a ranked-chip?",
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
        self.assertEqual(confirmed, {("first", 0x48)})
        confirm.assert_called_once_with(detections[0])

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
            "PROBE: example at 0x44 [command]: NO_MATCH: id=0x00\n",
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
            "PROBE: possible-chip at 0x48 [register]: NOT DETECTED\n",
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
