import errno
import sys
import types
import unittest
from unittest.mock import Mock, patch

from stemma_detect.bus import BusioI2CAdapter, I2CBus, I2CTransaction, adapt_i2c_bus
from stemma_detect.catalog import Chip
from stemma_detect.result import Confidence, ProbeResult
from stemma_detect.scanner import scan_all


class _FakeRead(bytearray):
    pass


class _FakeI2CMessage:
    @staticmethod
    def write(_address, data):
        return bytes(data)

    @staticmethod
    def read(_address, length):
        return _FakeRead(b"\xaa" * length)


class _FakeSMBus:
    def i2c_rdwr(self, *_messages):
        pass

    def close(self):
        pass


class _FakeBusioI2C:
    def __init__(self):
        self.locked = False
        self.calls = []
        self.fail_transfers = False

    def try_lock(self):
        self.calls.append(("try_lock",))
        if self.locked:
            return False
        self.locked = True
        return True

    def unlock(self):
        if not self.locked:
            raise RuntimeError("bus was not locked")
        self.calls.append(("unlock",))
        self.locked = False

    def readfrom_into(self, address, buffer):
        self.calls.append(("readfrom_into", address, len(buffer)))
        if self.fail_transfers:
            raise OSError(errno.EIO, "transfer failed")
        buffer[:] = bytes(range(1, len(buffer) + 1))

    def writeto(self, address, buffer):
        self.calls.append(("writeto", address, bytes(buffer)))
        if self.fail_transfers:
            raise OSError(errno.EIO, "transfer failed")

    def writeto_then_readfrom(self, address, out_buffer, in_buffer):
        self.calls.append(
            (
                "writeto_then_readfrom",
                address,
                bytes(out_buffer),
                len(in_buffer),
            )
        )
        if self.fail_transfers:
            raise OSError(errno.EIO, "transfer failed")
        in_buffer[:] = bytes(range(0xA0, 0xA0 + len(in_buffer)))


class _FakeScanningBusioI2C(_FakeBusioI2C):
    def readfrom_into(self, address, buffer):
        self.calls.append(("readfrom_into", address, len(buffer)))
        raise OSError(errno.ENXIO, "no device")

    def writeto_then_readfrom(self, address, out_buffer, in_buffer):
        self.calls.append(
            (
                "writeto_then_readfrom",
                address,
                bytes(out_buffer),
                len(in_buffer),
            )
        )
        if address != 0x44 or bytes(out_buffer) != b"\x00":
            raise OSError(errno.ENXIO, "no device")
        in_buffer[:] = b"\x5a"


class BusioI2CAdapterTests(unittest.TestCase):
    def test_busio_transfers_are_adapted(self):
        raw_bus = _FakeBusioI2C()
        bus = BusioI2CAdapter(raw_bus)

        self.assertEqual(bus.read(0x44, 2), b"\x01\x02")
        bus.write(0x44, b"\x10\x20")
        self.assertEqual(bus.write_then_read(0x44, b"\x0f", 2), b"\xa0\xa1")
        self.assertEqual(bus.read_register(0x44, 0x01, 1), b"\xa0")
        self.assertFalse(raw_bus.locked)

    def test_delayed_transfer_uses_separate_operations(self):
        raw_bus = _FakeBusioI2C()
        bus = BusioI2CAdapter(raw_bus)

        with patch("stemma_detect.bus.time.sleep") as sleep:
            self.assertEqual(bus.write_then_read(0x44, b"\x0f", 2, delay_ms=5), b"\x01\x02")

        sleep.assert_called_once_with(0.005)
        self.assertIn(("writeto", 0x44, b"\x0f"), raw_bus.calls)
        self.assertIn(("readfrom_into", 0x44, 2), raw_bus.calls)
        self.assertFalse(raw_bus.locked)

    def test_transfer_failure_releases_lock(self):
        raw_bus = _FakeBusioI2C()
        raw_bus.fail_transfers = True

        with self.assertRaises(OSError):
            BusioI2CAdapter(raw_bus).read(0x44, 1)

        self.assertFalse(raw_bus.locked)

    def test_native_bus_is_returned_unchanged(self):
        native_bus = Mock(
            read=Mock(),
            write=Mock(),
            read_register=Mock(),
            write_then_read=Mock(),
        )

        self.assertIs(adapt_i2c_bus(native_bus), native_bus)

    def test_other_duck_typed_bus_is_returned_unchanged(self):
        bus = object()

        self.assertIs(adapt_i2c_bus(bus), bus)

    def test_scan_all_accepts_raw_busio_bus(self):
        raw_bus = _FakeScanningBusioI2C()

        def probe(bus, address):
            chip_id = bus.read_register(address, 0x00, 1)[0]
            if chip_id == 0x5A:
                return ProbeResult.match({"chip_id": "0x5A"})
            return ProbeResult.no_match({"chip_id": f"0x{chip_id:02X}"})

        chip = Chip(
            name="example",
            addresses=(0x44,),
            package="adafruit-circuitpython-example",
            probe=probe,
            probe_confidence=Confidence.MATCH,
        )

        report = scan_all(raw_bus, chips=(chip,))

        self.assertEqual(len(report.matches), 1)
        self.assertEqual(report.matches[0].chip.name, "example")
        self.assertEqual(report.matches[0].address, 0x44)
        self.assertFalse(raw_bus.locked)


class BusTests(unittest.TestCase):
    def _bus(self, trace):
        bus = object.__new__(I2CBus)
        bus._bus = _FakeSMBus()
        bus._trace = trace
        return bus

    def test_successful_write_then_read_is_traced(self):
        transactions = []
        smbus2 = types.SimpleNamespace(i2c_msg=_FakeI2CMessage)

        with patch.dict(sys.modules, {"smbus2": smbus2}):
            response = self._bus(transactions.append).write_then_read(
                0x29,
                b"\x01\x0f",
                2,
            )

        self.assertEqual(response, b"\xaa\xaa")
        self.assertEqual(
            transactions,
            [I2CTransaction(0x29, write=b"\x01\x0f", read=b"\xaa\xaa")],
        )

    def test_read_and_write_are_traced(self):
        transactions = []
        bus = self._bus(transactions.append)
        smbus2 = types.SimpleNamespace(i2c_msg=_FakeI2CMessage)

        with patch.dict(sys.modules, {"smbus2": smbus2}):
            bus.write(0x29, b"\x00\x00")
            response = bus.read(0x29, 1)

        self.assertEqual(response, b"\xaa")
        self.assertEqual(
            transactions,
            [
                I2CTransaction(0x29, write=b"\x00\x00"),
                I2CTransaction(0x29, read=b"\xaa"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
