import unittest

from stemma_detect.catalog import Chip
from stemma_detect.mux import MuxHop, discover_multiplexers, probe_multiplexer
from stemma_detect.result import Confidence, ProbeResult
from stemma_detect.scanner import scan_all


class FakeMuxBus:
    def __init__(self, channels=4, original=0):
        self.channels = channels
        self.control = original
        self.writes = []

    def read(self, address, length):
        if address != 0x70 or length != 1:
            raise OSError(121, "Remote I/O error")
        return bytes((self.control,))

    def write(self, address, data):
        if address != 0x70:
            raise OSError(121, "Remote I/O error")
        self.writes.append((address, data))
        mask = (1 << self.channels) - 1
        self.control = data[0] & mask

    def read_register(self, address, register, length):
        if address != 0x44 or register != 0x00 or length != 1:
            raise OSError(121, "Remote I/O error")
        if self.control == 0x01:
            return b"\xa1"
        if self.control == 0x02:
            return b"\xa2"
        raise OSError(121, "Remote I/O error")

    def write_then_read(self, _address, _write, _read_length, *, delay_ms=0):
        raise OSError(121, "Remote I/O error")


class MuxTests(unittest.TestCase):
    def test_probe_distinguishes_four_channel_mux_and_restores_state(self):
        bus = FakeMuxBus(channels=4, original=0x03)

        mux = probe_multiplexer(bus, 0x70)

        self.assertEqual((mux.address, mux.channels, mux.original_control), (0x70, 4, 0x03))
        self.assertEqual(bus.control, 0x03)

    def test_probe_distinguishes_eight_channel_mux(self):
        bus = FakeMuxBus(channels=8)

        mux = probe_multiplexer(bus, 0x70)

        self.assertEqual(mux.channels, 8)
        self.assertEqual(mux.name, "pca9548")

    def test_probe_does_not_write_when_initial_value_is_not_control_byte(self):
        bus = FakeMuxBus()
        bus.control = 0xA0

        self.assertIsNone(probe_multiplexer(bus, 0x70))
        self.assertEqual(bus.writes, [])

    def test_discovery_ignores_addresses_that_do_not_acknowledge(self):
        bus = FakeMuxBus()

        multiplexers = discover_multiplexers(bus)

        self.assertEqual(len(multiplexers), 1)
        self.assertEqual(multiplexers[0].address, 0x70)

    def test_scan_all_keeps_same_address_on_separate_channels(self):
        bus = FakeMuxBus()

        def probe(test_bus, address):
            value = test_bus.read_register(address, 0x00, 1)[0]
            if value in (0xA1, 0xA2):
                return ProbeResult.match({"id": f"0x{value:02X}"})
            return ProbeResult.no_match()

        chip = Chip(
            "example",
            (0x44,),
            "adafruit-circuitpython-example",
            probe,
            Confidence.MATCH,
        )

        report = scan_all(bus, (chip,))

        self.assertEqual(
            [(item.address, item.path) for item in report.detections],
            [
                (0x44, (MuxHop(0x70, 0),)),
                (0x44, (MuxHop(0x70, 1),)),
            ],
        )
        self.assertEqual(bus.control, 0)


if __name__ == "__main__":
    unittest.main()
