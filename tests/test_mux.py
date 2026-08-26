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


class FakeNestedMuxBus:
    def __init__(self):
        self.controls = {0x70: 0, 0x71: 0}

    @property
    def child_visible(self):
        return self.controls[0x70] == 0x02

    def read(self, address, length):
        if length != 1 or address not in self.controls:
            raise OSError(121, "Remote I/O error")
        if address == 0x71 and not self.child_visible:
            raise OSError(121, "Remote I/O error")
        return bytes((self.controls[address],))

    def write(self, address, data):
        if address not in self.controls or (address == 0x71 and not self.child_visible):
            raise OSError(121, "Remote I/O error")
        self.controls[address] = data[0] & 0x0F

    def read_register(self, address, register, length):
        if register != 0x00 or length != 1:
            raise OSError(121, "Remote I/O error")
        if address == 0x44 and self.controls[0x70] == 0x01:
            return b"\xa1"
        if address == 0x45 and self.child_visible:
            return b"\xb1"
        if address == 0x44 and self.child_visible and self.controls[0x71] == 0x04:
            return b"\xc2"
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
        bus = FakeMuxBus(channels=8, original=0x80)

        mux = probe_multiplexer(bus, 0x70)

        self.assertEqual(mux.channels, 8)
        self.assertEqual(mux.name, "pca9548")
        self.assertEqual(bus.control, 0x80)

    def test_probe_does_not_write_when_initial_value_is_not_control_byte(self):
        bus = FakeMuxBus()
        bus.control = 0xA0

        self.assertIsNone(probe_multiplexer(bus, 0x70))
        self.assertEqual(bus.writes, [])

    def test_probe_rejects_sensor_that_accidentally_matches_first_mask(self):
        class RegisterPointerSensor(FakeMuxBus):
            def write(self, address, data):
                self.writes.append((address, data))
                self.control = {0x01: 0x01, 0x02: 0x10}.get(data[0], 0x00)

        bus = RegisterPointerSensor()

        self.assertIsNone(probe_multiplexer(bus, 0x70))
        self.assertEqual(bus.control, 0)

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

    def test_scan_all_recurses_through_nested_muxes(self):
        bus = FakeNestedMuxBus()

        def probe(test_bus, address):
            value = test_bus.read_register(address, 0x00, 1)[0]
            return ProbeResult.match({"id": f"0x{value:02X}"})

        chip = Chip(
            "example",
            (0x44, 0x45),
            "adafruit-circuitpython-example",
            probe,
            Confidence.MATCH,
        )

        report = scan_all(bus, (chip,))

        self.assertEqual(
            [(item.address, item.path) for item in report.detections],
            [
                (0x44, (MuxHop(0x70, 0),)),
                (0x45, (MuxHop(0x70, 1),)),
                (0x44, (MuxHop(0x70, 1), MuxHop(0x71, 2))),
            ],
        )
        self.assertEqual(
            [(mux.address, mux.path) for mux in report.multiplexers],
            [(0x70, ()), (0x71, (MuxHop(0x70, 1),))],
        )
        self.assertEqual(bus.controls, {0x70: 0, 0x71: 0})

    def test_nested_mux_depth_limit_still_reports_boundary_mux(self):
        bus = FakeNestedMuxBus()
        chip = Chip(
            "example",
            (0x44, 0x45),
            "adafruit-circuitpython-example",
            lambda test_bus, address: ProbeResult.match(
                {"id": test_bus.read_register(address, 0x00, 1).hex()}
            ),
            Confidence.MATCH,
        )

        report = scan_all(bus, (chip,), max_mux_depth=1)

        self.assertEqual([item.address for item in report.detections], [0x44, 0x45])
        self.assertEqual([mux.address for mux in report.multiplexers], [0x70, 0x71])


if __name__ == "__main__":
    unittest.main()
