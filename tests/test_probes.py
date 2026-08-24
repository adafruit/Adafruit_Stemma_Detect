import unittest

from stemma_detect.chips import bme280, bmp280, pcf8591, sht4x, vl6180x
from stemma_detect.result import Confidence


class FakeBus:
    def __init__(self, response):
        self.response = response

    def read_register(self, _address, _register, _length):
        return self.response

    def read(self, _address, _length):
        return self.response

    def write(self, _address, _data):
        pass

    def write_then_read(self, _address, _write, _read_length, *, delay_ms=0):
        return self.response


class ProbeTests(unittest.TestCase):
    def test_bme280_id(self):
        self.assertIs(bme280.probe(FakeBus(b"\x60"), 0x76).confidence, Confidence.MATCH)
        self.assertIs(bme280.probe(FakeBus(b"\x58"), 0x76).confidence, Confidence.NO_MATCH)

    def test_bmp280_id(self):
        self.assertIs(bmp280.probe(FakeBus(b"\x58"), 0x77).confidence, Confidence.MATCH)
        self.assertIs(bmp280.probe(FakeBus(b"\x60"), 0x77).confidence, Confidence.NO_MATCH)

    def test_pcf8591_is_only_a_possible_match(self):
        result = pcf8591.probe(FakeBus(b"\x7f"), 0x48)

        self.assertIs(result.confidence, Confidence.POSSIBLE)
        self.assertEqual(result.evidence, {"conversion": "0x7F"})

    def test_sht4x_crc(self):
        data = bytes((0x12, 0x34, sht4x._crc8(b"\x12\x34"), 0x56, 0x78, sht4x._crc8(b"\x56\x78")))
        self.assertIs(sht4x.probe(FakeBus(data), 0x44).confidence, Confidence.MATCH)

    def test_vl6180x_model_id(self):
        self.assertIs(vl6180x.probe(FakeBus(b"\xb4"), 0x29).confidence, Confidence.MATCH)
        self.assertIs(vl6180x.probe(FakeBus(b"\x00"), 0x29).confidence, Confidence.NO_MATCH)


if __name__ == "__main__":
    unittest.main()
