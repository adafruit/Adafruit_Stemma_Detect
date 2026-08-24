import contextlib
import io
import unittest
from unittest.mock import patch

from stemma_detect.catalog import Chip
from stemma_detect.cli import _arguments, _confirm_possible, _refine_possible_matches
from stemma_detect.result import Confidence, ProbeResult
from stemma_detect.scanner import Detection


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


class CliTests(unittest.TestCase):
    def test_prompt_possible_requires_install(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            _arguments(["--prompt-possible-matches"])

    def test_prompt_possible_accepts_yes(self):
        with patch("builtins.input", return_value="yes"):
            self.assertTrue(_confirm_possible(_possible_detection()))

    def test_prompt_possible_defaults_to_no(self):
        with patch("builtins.input", return_value=""):
            self.assertFalse(_confirm_possible(_possible_detection()))

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


if __name__ == "__main__":
    unittest.main()
