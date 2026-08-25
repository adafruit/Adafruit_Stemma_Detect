import importlib
import unittest

from stemma_detect.chips import (
    _possible,
    apds9960,
    bme280,
    bmp280,
    lis3dh,
    ltr390,
    mcp9808,
    mpu6050,
    pcf8591,
    sht4x,
    vcnl4040,
    vl6180x,
)
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


class RegisterBus:
    def __init__(self, responses):
        self.responses = responses

    def read_register(self, _address, register, _length):
        return self.responses[register]


class ProbeTests(unittest.TestCase):
    def test_address_only_probe_is_never_definitive(self):
        result = _possible.address_read_probe(FakeBus(b"\x5a"), 0x44)

        self.assertIs(result.confidence, Confidence.POSSIBLE)
        self.assertEqual(result.evidence, {"response": "0x5A"})

    def test_mpu6050_id(self):
        self.assertIs(mpu6050.probe(FakeBus(b"\x68"), 0x68).confidence, Confidence.MATCH)
        self.assertIs(mpu6050.probe(FakeBus(b"\x00"), 0x68).confidence, Confidence.NO_MATCH)

    def test_family_ids_refine_specific_names(self):
        cases = (
            ("bmp3xx", FakeBus(b"\x60"), 0x77, "bmp390"),
            ("bmp5xx", FakeBus(b"\x51"), 0x47, "bmp585"),
            ("icm20x", FakeBus(b"\xea"), 0x69, "icm20948"),
            (
                "ina23x",
                RegisterBus({0x3E: b"\x54\x49", 0x3F: (0x238 << 4).to_bytes(2, "big")}),
                0x40,
                "ina238",
            ),
            ("lsm6ds", FakeBus(b"\x6b"), 0x6A, "ism330dhcx"),
        )
        for module_name, bus, address, name in cases:
            module = importlib.import_module(f"stemma_detect.chips.{module_name}")
            result = module.probe(bus, address)
            with self.subTest(module=module_name):
                self.assertEqual(result.name, name)

    def test_ambiguous_family_ids_do_not_claim_a_variant(self):
        cases = (
            ("bmp5xx", b"\x50", 0x47),
            ("lsm6ds", b"\x6a", 0x6A),
            ("lsm6ds", b"\x6c", 0x6A),
        )
        for module_name, response, address in cases:
            module = importlib.import_module(f"stemma_detect.chips.{module_name}")
            result = module.probe(FakeBus(response), address)
            with self.subTest(module=module_name, response=response):
                self.assertIsNone(result.name)

    def test_additional_fixed_ids(self):
        cases = (
            ("adt7410", 0x48, b"\xcb"),
            ("apds9999", 0x39, b"\xc2"),
            ("as7341", 0x39, b"\x24"),
            ("bme680", 0x77, b"\x61"),
            ("bmp3xx", 0x77, b"\x50"),
            ("bmp5xx", 0x47, b"\x51"),
            ("bno055", 0x28, b"\xa0"),
            ("ccs811", 0x5A, b"\x81"),
            ("dps310", 0x77, b"\x10"),
            ("ens160", 0x53, b"\x60\x01"),
            ("hts221", 0x5F, b"\xbc"),
            ("icm20x", 0x69, b"\xea"),
            ("lis2mdl", 0x1E, b"\x40"),
            ("lis331", 0x18, b"\x32"),
            ("lis3mdl", 0x1C, b"\x3d"),
            ("lsm6ds", 0x6A, b"\x6c"),
            ("max1704x", 0x36, b"\x00\x11"),
            ("mcp9600", 0x67, b"\x40\x01"),
            ("mmc56x3", 0x30, b"\x10"),
            ("msa301", 0x26, b"\x13"),
            ("qmc5883p", 0x3C, b"\x80"),
            ("tcs34725", 0x29, b"\x44"),
            ("tmp117", 0x48, b"\x01\x17"),
            ("tsl2591", 0x29, b"\x50"),
            ("vl53l1x", 0x29, b"\xea\xcc\x10"),
            ("vl53l4cd", 0x29, b"\xeb\xaa"),
        )
        for name, address, response in cases:
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            with self.subTest(name=name):
                self.assertIs(module.probe(FakeBus(response), address).confidence, Confidence.MATCH)
                self.assertIs(
                    module.probe(FakeBus(bytes(len(response))), address).confidence,
                    Confidence.NO_MATCH,
                )

    def test_apds9960_ids(self):
        for device_id in (b"\xa8", b"\xab"):
            with self.subTest(device_id=device_id):
                self.assertIs(
                    apds9960.probe(FakeBus(device_id), 0x39).confidence,
                    Confidence.MATCH,
                )
        self.assertIs(apds9960.probe(FakeBus(b"\x00"), 0x39).confidence, Confidence.NO_MATCH)

    def test_bme280_id(self):
        self.assertIs(bme280.probe(FakeBus(b"\x60"), 0x76).confidence, Confidence.MATCH)
        self.assertIs(bme280.probe(FakeBus(b"\x58"), 0x76).confidence, Confidence.NO_MATCH)

    def test_bmp280_id(self):
        self.assertIs(bmp280.probe(FakeBus(b"\x58"), 0x77).confidence, Confidence.MATCH)
        self.assertIs(bmp280.probe(FakeBus(b"\x60"), 0x77).confidence, Confidence.NO_MATCH)

    def test_lis3dh_id(self):
        self.assertIs(lis3dh.probe(FakeBus(b"\x33"), 0x18).confidence, Confidence.MATCH)
        self.assertIs(lis3dh.probe(FakeBus(b"\x00"), 0x18).confidence, Confidence.NO_MATCH)

    def test_ltr390_id(self):
        self.assertIs(ltr390.probe(FakeBus(b"\xb2"), 0x53).confidence, Confidence.MATCH)
        self.assertIs(ltr390.probe(FakeBus(b"\x00"), 0x53).confidence, Confidence.NO_MATCH)

    def test_ltr329_ltr303_ids(self):
        module = importlib.import_module("stemma_detect.chips.ltr329_ltr303")
        matched = RegisterBus({0x86: b"\xa0", 0x87: b"\x05"})
        wrong = RegisterBus({0x86: b"\xa0", 0x87: b"\x00"})

        self.assertIs(module.probe(matched, 0x29).confidence, Confidence.MATCH)
        self.assertIs(module.probe(wrong, 0x29).confidence, Confidence.NO_MATCH)

    def test_mcp9808_ids(self):
        matched = RegisterBus({0x06: b"\x00\x54", 0x07: b"\x04\x01"})
        wrong_device = RegisterBus({0x06: b"\x00\x54", 0x07: b"\x03\x01"})
        self.assertIs(mcp9808.probe(matched, 0x18).confidence, Confidence.MATCH)
        self.assertIs(mcp9808.probe(wrong_device, 0x18).confidence, Confidence.NO_MATCH)

    def test_ina_family_ids(self):
        cases = (
            ("ina228", 0x3E, 0x3F, 0x228),
            ("ina23x", 0x3E, 0x3F, 0x237),
            ("ina260", 0xFE, 0xFF, 0x227),
        )
        for name, manufacturer_register, device_register, part in cases:
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            matched = RegisterBus(
                {
                    manufacturer_register: b"\x54\x49",
                    device_register: (part << 4).to_bytes(2, "big"),
                }
            )
            wrong = RegisterBus(
                {
                    manufacturer_register: b"\x54\x49",
                    device_register: b"\x00\x00",
                }
            )
            with self.subTest(name=name):
                self.assertIs(module.probe(matched, 0x40).confidence, Confidence.MATCH)
                self.assertIs(module.probe(wrong, 0x40).confidence, Confidence.NO_MATCH)

    def test_pcf8591_is_only_a_possible_match(self):
        result = pcf8591.probe(FakeBus(b"\x7f"), 0x48)

        self.assertIs(result.confidence, Confidence.POSSIBLE)
        self.assertEqual(result.evidence, {"conversion": "0x7F"})

    def test_sht4x_crc(self):
        data = bytes((0x12, 0x34, sht4x._crc8(b"\x12\x34"), 0x56, 0x78, sht4x._crc8(b"\x56\x78")))
        self.assertIs(sht4x.probe(FakeBus(data), 0x44).confidence, Confidence.MATCH)

    def test_stcc4_product_id_and_crc(self):
        stcc4 = importlib.import_module("stemma_detect.chips.stcc4")
        first = b"\x09\x01"
        second = b"\x01\x8a"
        response = first + bytes((stcc4._crc8(first),)) + second + bytes((stcc4._crc8(second),))
        self.assertIs(stcc4.probe(FakeBus(response), 0x64).confidence, Confidence.MATCH)
        self.assertIs(
            stcc4.probe(FakeBus(response[:-1] + b"\x00"), 0x64).confidence, Confidence.NO_MATCH
        )

    def test_vcnl4040_id(self):
        self.assertIs(vcnl4040.probe(FakeBus(b"\x86\x01"), 0x60).confidence, Confidence.MATCH)
        self.assertIs(vcnl4040.probe(FakeBus(b"\x00\x00"), 0x60).confidence, Confidence.NO_MATCH)

    def test_vl6180x_model_id(self):
        self.assertIs(vl6180x.probe(FakeBus(b"\xb4"), 0x29).confidence, Confidence.MATCH)
        self.assertIs(vl6180x.probe(FakeBus(b"\x00"), 0x29).confidence, Confidence.NO_MATCH)

    def test_vl53l0x_model_id(self):
        vl53l0x = importlib.import_module("stemma_detect.chips.vl53l0x")
        matched = RegisterBus({0xC0: b"\xee", 0xC1: b"\xaa", 0xC2: b"\x10"})
        wrong = RegisterBus({0xC0: b"\x00", 0xC1: b"\x00", 0xC2: b"\x00"})
        self.assertIs(vl53l0x.probe(matched, 0x29).confidence, Confidence.MATCH)
        self.assertIs(vl53l0x.probe(wrong, 0x29).confidence, Confidence.NO_MATCH)


if __name__ == "__main__":
    unittest.main()
