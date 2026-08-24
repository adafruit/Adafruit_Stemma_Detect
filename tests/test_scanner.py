import unittest

from stemma_detect.catalog import Chip
from stemma_detect.result import Confidence, ProbeResult
from stemma_detect.scanner import scan


class ScannerTests(unittest.TestCase):
    def test_non_matches_are_discarded(self):
        chip = Chip(
            name="no-match",
            addresses=(0x44,),
            package="adafruit-circuitpython-test",
            probe=lambda _bus, _address: ProbeResult.no_match(),
            probe_confidence=Confidence.MATCH,
        )

        self.assertEqual(scan(object(), (chip,)), ())

    def test_matches_are_retained(self):
        chip = Chip(
            name="match",
            addresses=(0x44,),
            package="adafruit-circuitpython-test",
            probe=lambda _bus, _address: ProbeResult.match({"id": "0x12"}),
            probe_confidence=Confidence.MATCH,
        )

        detections = scan(object(), (chip,))

        self.assertEqual(len(detections), 1)
        self.assertIs(detections[0].result.confidence, Confidence.MATCH)

    def test_definitive_match_stops_later_probes_at_address(self):
        matched = Chip(
            name="matched",
            addresses=(0x44,),
            package="adafruit-circuitpython-matched",
            probe=lambda _bus, _address: ProbeResult.match(),
            probe_confidence=Confidence.MATCH,
        )

        def must_not_run(_bus, _address):
            raise AssertionError("later probe ran after address was claimed")

        later = Chip(
            name="later",
            addresses=(0x44,),
            package="adafruit-circuitpython-later",
            probe=must_not_run,
            probe_confidence=Confidence.POSSIBLE,
        )

        detections = scan(object(), (matched, later))

        self.assertEqual([detection.chip.name for detection in detections], ["matched"])

    def test_possible_matches_are_all_returned_for_later_confirmation(self):
        first = Chip(
            name="first",
            addresses=(0x48,),
            package="adafruit-circuitpython-first",
            probe=lambda _bus, _address: ProbeResult.possible(),
            probe_confidence=Confidence.POSSIBLE,
        )
        second = Chip(
            name="second",
            addresses=(0x48,),
            package="adafruit-circuitpython-second",
            probe=lambda _bus, _address: ProbeResult.possible(),
            probe_confidence=Confidence.POSSIBLE,
        )

        detections = scan(object(), (first, second))

        self.assertEqual([detection.chip.name for detection in detections], ["first", "second"])

    def test_definitive_probe_runs_before_possible_probe(self):
        calls = []

        def probe_possible(_bus, _address):
            calls.append("possible")
            return ProbeResult.possible()

        possible = Chip(
            name="a-possible",
            addresses=(0x44,),
            package="adafruit-circuitpython-possible",
            probe=probe_possible,
            probe_confidence=Confidence.POSSIBLE,
        )
        matched = Chip(
            name="z-matched",
            addresses=(0x44,),
            package="adafruit-circuitpython-matched",
            probe=lambda _bus, _address: ProbeResult.match(),
            probe_confidence=Confidence.MATCH,
        )

        detections = scan(object(), (possible, matched))

        self.assertEqual([detection.chip.name for detection in detections], ["z-matched"])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
