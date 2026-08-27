import json
import unittest
from unittest.mock import patch

from stemma_detect.catalog import Chip
from stemma_detect.mux import Multiplexer, MuxHop
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk
from stemma_detect.scanner import Detection, ScanReport
from stemma_detect.serialization import report_to_dict, report_to_json


class SerializationTests(unittest.TestCase):
    def setUp(self):
        self.chip = Chip(
            name="bmp3xx",
            addresses=(0x76, 0x77),
            package="adafruit-circuitpython-bmp3xx",
            probe=lambda _bus, _address: ProbeResult.no_match(),
            probe_confidence=Confidence.MATCH,
            default_addresses=(0x77,),
            probe_risk=ProbeRisk.REGISTER,
        )
        self.path = (MuxHop(0x70, 2),)
        self.report = ScanReport(
            detections=(
                Detection(
                    self.chip,
                    0x77,
                    ProbeResult.match(
                        {"chip_id": "0x60", "address": "default"},
                        name="bmp390",
                        score=20,
                        max_score=20,
                    ),
                    self.path,
                ),
            ),
            multiplexers=(Multiplexer(0x70, 8, 0, ()),),
        )

    @patch("stemma_detect.serialization.driver_version", return_value="3.0.2")
    def test_report_schema_contains_topology_signature_and_driver(self, _version):
        data = report_to_dict(self.report, bus=1)

        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["bus"], 1)
        self.assertEqual(
            data["multiplexers"],
            [
                {
                    "name": "pca9548",
                    "address": 0x70,
                    "address_hex": "0x70",
                    "channels": 8,
                    "path": [],
                }
            ],
        )
        detection = data["detections"][0]
        self.assertEqual(detection["name"], "bmp390")
        self.assertEqual(detection["family"], "bmp3xx")
        self.assertEqual(detection["confidence"], "match")
        self.assertEqual(detection["address"], 0x77)
        self.assertEqual(detection["address_hex"], "0x77")
        self.assertEqual(detection["address_kind"], "default")
        self.assertEqual(
            detection["path"],
            [{"address": 0x70, "address_hex": "0x70", "channel": 2}],
        )
        self.assertEqual(detection["probe_risk"], "register")
        self.assertEqual(detection["evidence"]["chip_id"], "0x60")
        self.assertEqual((detection["score"], detection["max_score"]), (20, 20))
        self.assertEqual(
            detection["driver"],
            {
                "package": "adafruit-circuitpython-bmp3xx",
                "installed": True,
                "version": "3.0.2",
            },
        )

    @patch("stemma_detect.serialization.driver_version", return_value=None)
    def test_report_json_is_parseable_and_marks_missing_driver(self, _version):
        data = json.loads(report_to_json(self.report, bus=1))

        self.assertFalse(data["detections"][0]["driver"]["installed"])
        self.assertIsNone(data["detections"][0]["driver"]["version"])

    @patch("stemma_detect.serialization.driver_version", return_value=None)
    def test_report_convenience_serializers_and_compact_json(self, _version):
        self.assertEqual(self.report.to_dict(bus=1), report_to_dict(self.report, bus=1))
        compact = self.report.to_json(bus=1, indent=None)
        self.assertNotIn("\n", compact)
        self.assertEqual(json.loads(compact)["bus"], 1)

    def test_empty_report_has_stable_collections(self):
        self.assertEqual(
            report_to_dict(ScanReport(())),
            {
                "schema_version": 1,
                "bus": None,
                "multiplexers": [],
                "detections": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
