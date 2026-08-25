import sys
import types
import unittest
from unittest.mock import patch

from stemma_detect.bus import I2CBus, I2CTransaction


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
