import unittest

from stemma_detect.catalog import Chip
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk
from stemma_detect.scanner import Detection, scan


class ScannerTests(unittest.TestCase):
    def test_detection_uses_probe_name_override(self):
        chip = Chip(
            name="bmp3xx",
            addresses=(0x77,),
            package="adafruit-circuitpython-bmp3xx",
            probe=lambda _bus, _address: ProbeResult.no_match(),
            probe_confidence=Confidence.MATCH,
        )
        detection = Detection(
            chip,
            0x77,
            ProbeResult.match(name="bmp390"),
        )

        self.assertEqual(detection.name, "bmp390")

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

    def test_default_address_possible_match_runs_first(self):
        alternate = Chip(
            name="a-alternate",
            addresses=(0x48, 0x49),
            package="adafruit-circuitpython-alternate",
            probe=lambda _bus, address: (
                ProbeResult.possible() if address == 0x48 else ProbeResult.no_match()
            ),
            probe_confidence=Confidence.POSSIBLE,
            default_addresses=(0x49,),
        )
        default = Chip(
            name="z-default",
            addresses=(0x48, 0x49),
            package="adafruit-circuitpython-default",
            probe=lambda _bus, address: (
                ProbeResult.possible() if address == 0x48 else ProbeResult.no_match()
            ),
            probe_confidence=Confidence.POSSIBLE,
            default_addresses=(0x48,),
        )

        detections = scan(object(), (alternate, default))

        self.assertEqual(
            [detection.chip.name for detection in detections],
            ["z-default", "a-alternate"],
        )

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
            probe_risk=ProbeRisk.PASSIVE,
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

    def test_lower_risk_probes_run_before_command_probes(self):
        calls = []

        def passive_probe(_bus, _address):
            calls.append("passive")
            return ProbeResult.no_match()

        def register_probe(_bus, _address):
            calls.append("register")
            return ProbeResult.match()

        def command_probe(_bus, _address):
            calls.append("command")
            return ProbeResult.match()

        chips = (
            Chip(
                "command",
                (0x29,),
                "adafruit-circuitpython-command",
                command_probe,
                Confidence.MATCH,
                probe_risk=ProbeRisk.COMMAND,
            ),
            Chip(
                "register",
                (0x29,),
                "adafruit-circuitpython-register",
                register_probe,
                Confidence.MATCH,
                probe_risk=ProbeRisk.REGISTER,
            ),
            Chip(
                "passive",
                (0x29,),
                "adafruit-circuitpython-passive",
                passive_probe,
                Confidence.MATCH,
                probe_risk=ProbeRisk.PASSIVE,
            ),
        )

        detections = scan(object(), chips)

        self.assertEqual(calls, ["passive", "register"])
        self.assertEqual([detection.chip.name for detection in detections], ["register"])

    def test_diagnostics_include_non_matches_and_errors(self):
        def failed_probe(_bus, _address):
            raise OSError("remote I/O")

        chips = (
            Chip(
                "failed",
                (0x44,),
                "adafruit-circuitpython-failed",
                failed_probe,
                Confidence.MATCH,
            ),
            Chip(
                "no-match",
                (0x44,),
                "adafruit-circuitpython-no-match",
                lambda _bus, _address: ProbeResult.no_match({"id": "0x00"}),
                Confidence.MATCH,
            ),
        )
        diagnostics = []

        self.assertEqual(scan(object(), chips, diagnostic=diagnostics.append), ())
        self.assertEqual([item.outcome for item in diagnostics], ["error", "no_match"])
        self.assertEqual(str(diagnostics[0].error), "remote I/O")
        self.assertEqual(diagnostics[1].result.evidence, {"id": "0x00"})

    def test_remote_io_diagnostic_means_not_detected(self):
        chip = Chip(
            "missing",
            (0x44,),
            "adafruit-circuitpython-missing",
            lambda _bus, _address: (_ for _ in ()).throw(OSError(121, "Remote I/O error")),
            Confidence.MATCH,
        )
        diagnostics = []

        self.assertEqual(scan(object(), (chip,), diagnostic=diagnostics.append), ())
        self.assertEqual(diagnostics[0].outcome, "not_detected")
        self.assertTrue(diagnostics[0].not_detected)

    def test_default_address_adds_a_small_score_bonus(self):
        chip = Chip(
            "scored",
            (0x48, 0x49),
            "adafruit-circuitpython-scored",
            lambda _bus, _address: ProbeResult.possible(score=5, max_score=10),
            Confidence.POSSIBLE,
            default_addresses=(0x48,),
        )

        detections = scan(object(), (chip,))

        self.assertEqual(
            [(item.address, item.result.score, item.result.max_score) for item in detections],
            [(0x48, 6, 11), (0x49, 5, 11)],
        )
        self.assertEqual(
            [item.result.evidence["address"] for item in detections],
            ["default", "alternate"],
        )


if __name__ == "__main__":
    unittest.main()
