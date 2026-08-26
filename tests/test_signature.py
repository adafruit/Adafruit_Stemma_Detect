import unittest

from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, command_response, exact, not_blank, one_of


class RegisterBus:
    def __init__(self, responses):
        self.responses = responses

    def read_register(self, _address, register, length):
        value = self.responses[register]
        if len(value) != length:
            raise AssertionError(f"unexpected read length for 0x{register:02X}")
        return value


class CommandBus:
    def __init__(self, response):
        self.response = response
        self.transaction = None

    def write_then_read(self, address, command, length, *, delay_ms=0):
        self.transaction = (address, command, length, delay_ms)
        return self.response


class SignatureTests(unittest.TestCase):
    def test_command_response_participates_in_signature(self):
        signature = DeviceSignature(
            (
                command_response(
                    "identity",
                    b"\x12\x34",
                    2,
                    lambda value: value == b"\xab\xcd",
                    delay_ms=5,
                    show_value=True,
                    weight=8,
                ),
            )
        )
        bus = CommandBus(b"\xab\xcd")

        result = signature.probe(bus, 0x44)

        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(result.evidence, {"identity": "0xABCD", "signature": "8/8"})
        self.assertEqual(bus.transaction, (0x44, b"\x12\x34", 2, 5))

    def test_all_checks_form_a_match(self):
        signature = DeviceSignature(
            (
                exact("id", 0x00, b"\x12", show_value=True),
                exact("reserved", 0x01, b"\x00", mask=b"\xf0"),
                one_of("revision", 0x02, (b"\x01", b"\x02"), show_value=True),
                not_blank("calibration", 0x10, 4),
            )
        )
        bus = RegisterBus(
            {
                0x00: b"\x12",
                0x01: b"\x0f",
                0x02: b"\x02",
                0x10: b"\x00\x01\x00\x00",
            }
        )

        result = signature.probe(bus, 0x44)

        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(
            result.evidence,
            {"id": "0x12", "revision": "0x02", "signature": "4/4"},
        )

    def test_probe_stops_at_first_failed_check(self):
        signature = DeviceSignature(
            (
                exact("id", 0x00, b"\x12"),
                exact("later", 0x01, b"\x34"),
            )
        )
        result = signature.probe(RegisterBus({0x00: b"\x00"}), 0x44)

        self.assertIs(result.confidence, Confidence.NO_MATCH)
        self.assertEqual(result.evidence, {"failed": "id", "id": "0x00"})

    def test_blank_factory_data_is_rejected(self):
        check = not_blank("calibration", 0x10, 3)

        for value in (b"\x00\x00\x00", b"\xff\xff\xff"):
            with self.subTest(value=value):
                result = DeviceSignature((check,)).probe(RegisterBus({0x10: value}), 0x44)
                self.assertIs(result.confidence, Confidence.NO_MATCH)

    def test_optional_checks_contribute_weight_without_rejecting(self):
        signature = DeviceSignature(
            (
                exact("id", 0x00, b"\x12", weight=10),
                exact("revision", 0x01, b"\x34", required=False, weight=3),
                not_blank("calibration", 0x10, 2, required=False, weight=2),
            ),
            match_threshold=13,
        )
        bus = RegisterBus(
            {
                0x00: b"\x12",
                0x01: b"\x00",
                0x10: b"\x01\x02",
            }
        )

        result = signature.probe(bus, 0x44)

        self.assertIs(result.confidence, Confidence.POSSIBLE)
        self.assertEqual((result.score, result.max_score), (12, 15))
        self.assertEqual(result.evidence["missed"], "revision")


if __name__ == "__main__":
    unittest.main()
