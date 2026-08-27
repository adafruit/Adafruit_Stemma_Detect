import importlib
import unittest

from stemma_detect.chips import (
    _possible,
    _sensirion,
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


class CommandBus:
    def __init__(self, responses):
        self.responses = responses

    def write_then_read(self, _address, command, _length, *, delay_ms=0):
        return self.responses[command]


class StopRegisterBus:
    def __init__(self, responses):
        self.responses = responses
        self.register = None

    def write(self, _address, data):
        self.register = data[0]

    def read(self, _address, _length):
        return self.responses[self.register]


class ProbeTests(unittest.TestCase):
    def test_crc_protected_command_identities(self):
        def words(*values):
            return b"".join(value + bytes((_sensirion.crc8(value),)) for value in values)

        cases = (
            ("sgp30", 0x58, words(b"\x00\x22")),
            ("shtc3", 0x70, words(b"\x08\x07")),
            ("sht31d", 0x44, words(b"\x12\x34", b"\x56\x78")),
            ("si7021", 0x40, words(b"\x15\x34", b"\x56\x78")),
        )
        for name, address, response in cases:
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            with self.subTest(name=name):
                result = module.probe(FakeBus(response), address)
                self.assertIs(result.confidence, Confidence.MATCH)
                self.assertEqual((result.score, result.max_score), (result.max_score,) * 2)
                self.assertIs(
                    module.probe(
                        FakeBus(response[:-1] + bytes((response[-1] ^ 0xFF,))), address
                    ).confidence,
                    Confidence.NO_MATCH,
                )

    def test_sgp40_and_sgp41_are_distinguished(self):
        def words(*values):
            return b"".join(value + bytes((_sensirion.crc8(value),)) for value in values)

        sgp40 = importlib.import_module("stemma_detect.chips.sgp40")
        sgp41 = importlib.import_module("stemma_detect.chips.sgp41")
        sgp40_bus = CommandBus(
            {
                b"\x36\x82": words(b"\x00\x00", b"\x12\x34", b"\x56\x78"),
                b"\x20\x2f": words(b"\x32\x20"),
            }
        )
        sgp41_serial = words(b"\x12\x34", b"\x56\x78", b"\x9a\xbc")

        self.assertIs(sgp40.probe(sgp40_bus, 0x59).confidence, Confidence.MATCH)
        self.assertIs(sgp40.probe(FakeBus(sgp41_serial), 0x59).confidence, Confidence.NO_MATCH)
        self.assertIs(sgp41.probe(FakeBus(sgp41_serial), 0x59).confidence, Confidence.MATCH)

    def test_hdc302x_manufacturer_id_and_crc(self):
        module = importlib.import_module("stemma_detect.chips.hdc302x")
        manufacturer_id = b"\x30\x00"
        response = manufacturer_id + bytes((_sensirion.crc8(manufacturer_id),))

        self.assertIs(module.probe(FakeBus(response), 0x44).confidence, Confidence.MATCH)
        self.assertIs(
            module.probe(FakeBus(response[:-1] + b"\x00"), 0x44).confidence,
            Confidence.NO_MATCH,
        )

    def test_address_only_probe_is_never_definitive(self):
        result = _possible.address_read_probe(FakeBus(b"\x5a"), 0x44)

        self.assertIs(result.confidence, Confidence.POSSIBLE)
        self.assertEqual(result.evidence, {"response": "0x5A"})
        self.assertEqual((result.score, result.max_score), (1, 1))

    def test_mpu6050_id(self):
        self.assertIs(mpu6050.probe(FakeBus(b"\x68"), 0x68).confidence, Confidence.MATCH)
        self.assertIs(mpu6050.probe(FakeBus(b"\x00"), 0x68).confidence, Confidence.NO_MATCH)

    def test_same_id_different_adxl_drivers_remain_possible(self):
        for name in ("adxl34x", "adxl37x"):
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            with self.subTest(name=name):
                result = module.probe(FakeBus(b"\xe5"), 0x53)
                self.assertIs(result.confidence, Confidence.POSSIBLE)
                self.assertEqual((result.score, result.max_score), (8, 10))
                self.assertIs(
                    module.probe(FakeBus(b"\x00"), 0x53).confidence,
                    Confidence.NO_MATCH,
                )

    def test_lps2x_groups_same_driver_variants_without_overclaiming(self):
        module = importlib.import_module("stemma_detect.chips.lps2x")

        lps25 = module.probe(FakeBus(b"\xbd"), 0x5D)
        self.assertIs(lps25.confidence, Confidence.MATCH)
        self.assertEqual(lps25.name, "lps25")

        # LPS22 and LPS35HW share 0xB1 but use different packages.
        self.assertIs(module.probe(FakeBus(b"\xb1"), 0x5D).confidence, Confidence.POSSIBLE)
        self.assertIs(module.probe(FakeBus(b"\x00"), 0x5D).confidence, Confidence.NO_MATCH)

    def test_family_ids_refine_specific_names(self):
        cases = (
            (
                "bmp3xx",
                RegisterBus(
                    {
                        0x00: b"\x60",
                        0x02: b"\x00",
                        0x03: b"\x10",
                        0x31: bytes(range(21)),
                    }
                ),
                0x77,
                "bmp390",
            ),
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
            ("as7331", 0x74, b"\x21"),
            ("bmp5xx", 0x47, b"\x51"),
            ("ccs811", 0x5A, b"\x81"),
            ("dps310", 0x77, b"\x10"),
            ("ens160", 0x53, b"\x60\x01"),
            ("fxas21002c", 0x21, b"\xd7"),
            ("fxos8700", 0x1F, b"\xc7"),
            ("guvx_i2c", 0x39, b"\x62"),
            ("hts221", 0x5F, b"\xbc"),
            ("icm20x", 0x69, b"\xea"),
            ("lis2mdl", 0x1E, b"\x40"),
            ("lis331", 0x18, b"\x32"),
            ("lis3mdl", 0x1C, b"\x3d"),
            ("lsm303dlh_mag", 0x1E, b"H43"),
            ("lsm6ds", 0x6A, b"\x6c"),
            ("lsm9ds1", 0x6B, b"\x68"),
            ("max1704x", 0x36, b"\x00\x11"),
            ("mcp9600", 0x67, b"\x40\x01"),
            ("mmc56x3", 0x30, b"\x10"),
            ("mma8451", 0x1D, b"\x1a"),
            ("mpl3115a2", 0x60, b"\xc4"),
            ("msa301", 0x26, b"\x13"),
            ("qmc5883p", 0x3C, b"\x80"),
            ("si1145", 0x60, b"\x45\x00\x08"),
            ("tcs3430", 0x39, b"\xdc"),
            ("tcs34725", 0x29, b"\x44"),
            ("tmp117", 0x48, b"\x01\x17"),
            ("tmp006", 0x40, b"\x00\x67"),
            ("tmp007", 0x40, b"\x00\x78"),
            ("tsl2591", 0x29, b"\x50"),
            ("tsl2561", 0x39, b"\x5a"),
            ("lps28", 0x5C, b"\xb4"),
            ("opt4048", 0x44, b"\x08\x21"),
            ("spa06_003", 0x77, b"\x11"),
            ("sths34pf80", 0x5A, b"\xd3"),
            ("vcnl4030", 0x60, b"\x80\x42"),
            ("vcnl4200", 0x51, b"\x58\x10"),
            ("vl53l1x", 0x29, b"\xea\xcc\x10"),
            ("vl53l4cd", 0x29, b"\xeb\xaa"),
            ("veml6075", 0x10, b"\x26\x00"),
        )
        for name, address, response in cases:
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            with self.subTest(name=name):
                self.assertIs(module.probe(FakeBus(response), address).confidence, Confidence.MATCH)
                self.assertIs(
                    module.probe(FakeBus(bytes(len(response))), address).confidence,
                    Confidence.NO_MATCH,
                )

    def test_legacy_motion_sensor_ambiguity_and_paired_identity(self):
        l3gd20 = importlib.import_module("stemma_detect.chips.l3gd20")
        self.assertIs(l3gd20.probe(FakeBus(b"\xd7"), 0x6B).confidence, Confidence.MATCH)
        self.assertIs(l3gd20.probe(FakeBus(b"\xd4"), 0x6B).confidence, Confidence.POSSIBLE)
        self.assertIs(l3gd20.probe(FakeBus(b"\xd4"), 0x6A).confidence, Confidence.MATCH)

        lsm9ds0 = importlib.import_module("stemma_detect.chips.lsm9ds0")

        class PairedBus:
            def read_register(self, address, register, length):
                return {(0x1D, 0x0F): b"\x49", (0x6B, 0x0F): b"\xd4"}[(address, register)]

        result = lsm9ds0.probe(PairedBus(), 0x6B)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (16, 16))

    def test_htu21d_electronic_id(self):
        module = importlib.import_module("stemma_detect.chips.htu21d")
        words = (b"\x32\x12", b"\x34\x56")
        response = b"".join(word + bytes((_sensirion.crc8(word),)) for word in words)

        self.assertIs(module.probe(FakeBus(response), 0x40).confidence, Confidence.MATCH)
        wrong_model = module.probe(FakeBus(response.replace(b"\x32", b"\x15", 1)), 0x40)
        self.assertIs(wrong_model.confidence, Confidence.NO_MATCH)

    def test_as7343_restores_register_bank(self):
        module = importlib.import_module("stemma_detect.chips.as7343")

        class BankBus:
            def __init__(self):
                self.writes = []

            def read_register(self, _address, register, _length):
                return {0xBF: b"\x20", 0x58: b"\x01\x02\x81"}[register]

            def write(self, _address, data):
                self.writes.append(data)

        bus = BankBus()
        result = module.probe(bus, 0x39)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(bus.writes, [b"\xbf\x30", b"\xbf\x20"])

    def test_crc_protected_ags02ma_firmware(self):
        module = importlib.import_module("stemma_detect.chips.ags02ma")
        firmware = b"\x00\x01\x02\x03"
        response = firmware + bytes((_sensirion.crc8(firmware),))

        self.assertIs(module.probe(FakeBus(response), 0x1A).confidence, Confidence.MATCH)
        bad_crc = module.probe(FakeBus(response[:-1] + b"\x00"), 0x1A)
        self.assertIs(bad_crc.confidence, Confidence.NO_MATCH)

    def test_am2320_crc_protected_identity(self):
        module = importlib.import_module("stemma_detect.chips.am2320")
        payload = b"\x03\x07\x00\x03\x01\x12\x34\x56\x78"
        response = payload + module._crc16(payload).to_bytes(2, "little")

        result = module.probe(FakeBus(response), 0x5C)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (14, 14))

    def test_mlx90614_factory_id_pec(self):
        module = importlib.import_module("stemma_detect.chips.mlx90614")

        class PecBus:
            def read_register(self, address, register, _length):
                data = bytes((register, register ^ 0x5A))
                pec_input = bytes((address << 1, register, address << 1 | 1)) + data
                return data + bytes((module._pec(pec_input),))

        result = module.probe(PecBus(), 0x5A)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (16, 16))

    def test_new_structural_possible_probes(self):
        cases = (
            (
                "as5600",
                RegisterBus(
                    {
                        0x00: b"\x02",
                        0x0B: b"\x20",
                        0x0C: b"\x0a\xbc",
                        0x0E: b"\x01\x23",
                    }
                ),
                0x36,
            ),
            ("htu31d", CommandBus({b"\x0a": b"\x12\x34\x56\x78"}), 0x40),
            (
                "ina219",
                RegisterBus({0x00: b"\x39\x9f", 0x02: b"\x61\xa2"}),
                0x40,
            ),
            (
                "ds3502",
                RegisterBus({0x00: b"\x40", 0x02: b"\x80"}),
                0x28,
            ),
            ("max44009", RegisterBus({0x02: b"\x80", 0x03: b"\x12\x03"}), 0x4A),
            ("mcp3421", FakeBus(b"\x01\x23\x14\x14"), 0x68),
            ("mpl115a2", FakeBus(b"\x12\x34\x56\x78\x9a\xbc\xde\xf0"), 0x60),
            (
                "pct2075",
                RegisterBus({0x00: b"\x19\x00", 0x01: b"\x00", 0x04: b"\x05"}),
                0x37,
            ),
            ("tc74", RegisterBus({0x00: b"\x19", 0x01: b"\x40"}), 0x48),
            (
                "lidarlite",
                StopRegisterBus({0x01: b"\x20", 0x16: b"\x12\x34", 0x1E: b"\x00"}),
                0x62,
            ),
            ("mlx90393", CommandBus({b"\x50\x90": b"\x03\xb6\x68"}), 0x0C),
            ("mlx90395", RegisterBus({0x4C: b"\x12\x34\x56\x78\x9a\xbc"}), 0x0C),
            ("mlx90640", CommandBus({b"\x24\x07": b"\x12\x34\x56\x78\x9a\xbc"}), 0x33),
            (
                "mpr121",
                RegisterBus(
                    {
                        0x00: b"\x03\x00",
                        0x04: b"\x23\x01" * 12,
                        0x5E: b"\x8c",
                    }
                ),
                0x5A,
            ),
            ("mprls", FakeBus(b"\x20"), 0x18),
            (
                "veml7700",
                RegisterBus({0x00: b"\x00\x00", 0x03: b"\x00\x00", 0x06: b"\x00\xc0"}),
                0x10,
            ),
            (
                "tsc2007",
                CommandBus({b"\xc4": b"\x12\x30", b"\xd4": b"\x45\x60", b"\x00": b"\x78\x90"}),
                0x48,
            ),
        )
        for name, bus, address in cases:
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            with self.subTest(name=name):
                self.assertIs(module.probe(bus, address).confidence, Confidence.POSSIBLE)

    def test_structural_possible_probes_reject_reserved_bits(self):
        cases = (
            (
                "as5600",
                RegisterBus({0x00: b"\x00", 0x0B: b"\x01", 0x0C: b"\x00\x00", 0x0E: b"\x00\x00"}),
                0x36,
            ),
            (
                "ds3502",
                RegisterBus({0x00: b"\xc0", 0x02: b"\x01"}),
                0x28,
            ),
            ("ina219", RegisterBus({0x00: b"\x79\x9f", 0x02: b"\x00\x00"}), 0x40),
            ("mcp3421", FakeBus(b"\x01\x23\x34\x34"), 0x68),
            (
                "pct2075",
                RegisterBus({0x00: b"\x19\x01", 0x01: b"\x00", 0x04: b"\x05"}),
                0x37,
            ),
            (
                "veml7700",
                RegisterBus({0x00: b"\x04\x00", 0x03: b"\x00\x00", 0x06: b"\x00\x00"}),
                0x10,
            ),
            (
                "mpr121",
                RegisterBus(
                    {
                        0x00: b"\x00\x10",
                        0x04: b"\x00\x00" * 12,
                        0x5E: b"\x00",
                    }
                ),
                0x5A,
            ),
            ("mprls", FakeBus(b"\x02"), 0x18),
            ("mlx90393", CommandBus({b"\x50\x90": b"\x00\xb6\x68"}), 0x0C),
            ("mlx90395", RegisterBus({0x4C: bytes(6)}), 0x0C),
            (
                "tsc2007",
                CommandBus({b"\xc4": b"\x12\x31", b"\xd4": b"\x45\x60", b"\x00": b"\x78\x90"}),
                0x48,
            ),
        )
        for name, bus, address in cases:
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            with self.subTest(name=name):
                self.assertIs(module.probe(bus, address).confidence, Confidence.NO_MATCH)

    def test_mcp3421_conversion_framing_for_18_bit_mode(self):
        module = importlib.import_module("stemma_detect.chips.mcp3421")

        positive = module.probe(FakeBus(b"\x02\x34\x56\x1c"), 0x68)
        negative = module.probe(FakeBus(b"\xfd\xcb\xaa\x9f"), 0x68)
        invalid_sign_extension = module.probe(FakeBus(b"\x42\x34\x56\x1c"), 0x68)

        self.assertIs(positive.confidence, Confidence.POSSIBLE)
        self.assertIs(negative.confidence, Confidence.POSSIBLE)
        self.assertIs(invalid_sign_extension.confidence, Confidence.NO_MATCH)

    def test_as726x_virtual_hardware_identity(self):
        module = importlib.import_module("stemma_detect.chips.as726x")

        class VirtualBus:
            def __init__(self, values):
                self.status = iter((0, 1, 0, 1))
                self.values = iter(values)
                self.writes = []

            def read_register(self, _address, register, _length):
                if register == 0x00:
                    return bytes((next(self.status),))
                if register == 0x02:
                    return bytes((next(self.values),))
                raise AssertionError(f"unexpected register: {register:#x}")

            def write(self, _address, data):
                self.writes.append(data)

        bus = VirtualBus((0x40, 0x3E))
        result = module.probe(bus, 0x49)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (14, 14))
        self.assertEqual(bus.writes, [b"\x01\x00", b"\x01\x01"])

        invalid = module.probe(VirtualBus((0x40, 0x00)), 0x49)
        self.assertIs(invalid.confidence, Confidence.NO_MATCH)

    def test_ms8607_paired_prom_crc_identity(self):
        module = importlib.import_module("stemma_detect.chips.ms8607")

        pressure_prom = [0x0000, 0x1234, 0x5678, 0x9ABC, 0x1357, 0x2468, 0x369C]
        pressure_prom[0] |= module._crc4(tuple(pressure_prom), crc_word=0, crc_mask=0x0FFF) << 12
        humidity_prom = [0x1234, 0x5678, 0x9ABC, 0x1357, 0x2468, 0x3690, 0xACE0]
        humidity_prom[6] |= module._crc4(tuple(humidity_prom), crc_word=6, crc_mask=0xFFF0)

        class PromBus:
            def __init__(self, pressure, humidity):
                self.proms = {0x76: pressure, 0x40: humidity}

            def write_then_read(self, address, command, _length, *, delay_ms=0):
                index = (command[0] - 0xA0) // 2
                return self.proms[address][index].to_bytes(2, "big")

        result = module.probe(PromBus(pressure_prom, humidity_prom), 0x76)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (18, 18))

        humidity_prom[6] ^= 0x01
        invalid = module.probe(PromBus(pressure_prom, humidity_prom), 0x76)
        self.assertIs(invalid.confidence, Confidence.NO_MATCH)

    def test_lps35hw_shared_exact_id_stays_possible(self):
        module = importlib.import_module("stemma_detect.chips.lps35hw")

        result = module.probe(FakeBus(b"\xb1"), 0x5D)
        self.assertIs(result.confidence, Confidence.POSSIBLE)
        self.assertEqual((result.score, result.max_score), (8, 10))
        self.assertIs(
            module.probe(FakeBus(b"\x00"), 0x5D).confidence,
            Confidence.NO_MATCH,
        )

    def test_pa1010d_nmea_checksum_identity(self):
        module = importlib.import_module("stemma_detect.chips.pa1010d")
        sentence = b"$GPGGA,123519,4807.038,N,01131.000,E,1,08*77\r\n"

        result = module.probe(FakeBus(b"partial" + sentence + b"\x0a" * 40), 0x10)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(result.evidence["sentence_type"], "GPGGA")

        invalid = sentence.replace(b"*77", b"*00")
        self.assertIs(
            module.probe(FakeBus(invalid), 0x10).confidence,
            Confidence.NO_MATCH,
        )

    def test_tmag5273_manufacturer_and_version(self):
        module = importlib.import_module("stemma_detect.chips.tmag5273")

        for version in (1, 2):
            result = module.probe(
                RegisterBus({0x0D: bytes((version,)), 0x0E: b"\x49\x54"}),
                0x35,
            )
            with self.subTest(version=version):
                self.assertIs(result.confidence, Confidence.MATCH)
                self.assertEqual(result.name, f"tmag5273_a{version}")
                self.assertEqual((result.score, result.max_score), (14, 14))

        invalid = module.probe(RegisterBus({0x0D: b"\x01", 0x0E: b"\x00\x00"}), 0x35)
        self.assertIs(invalid.confidence, Confidence.NO_MATCH)

    def test_new_fixed_identity_devices(self):
        cases = (
            ("aw9523", FakeBus(b"\x23"), 0x58),
            ("cap1188", FakeBus(b"\x50\x5d\x83"), 0x29),
        )
        for name, bus, address in cases:
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            with self.subTest(name=name):
                result = module.probe(bus, address)
                self.assertIs(result.confidence, Confidence.MATCH)
                self.assertEqual((result.score, result.max_score), (result.max_score,) * 2)

                wrong = module.probe(FakeBus(bytes(len(bus.response))), address)
                self.assertIs(wrong.confidence, Confidence.NO_MATCH)

    def test_drv2605_family_id_refines_variant(self):
        module = importlib.import_module("stemma_detect.chips.drv2605")

        for status, name in ((0x60, "drv2605"), (0xE0, "drv2605l")):
            with self.subTest(status=status):
                result = module.probe(FakeBus(bytes((status,))), 0x5A)
                self.assertIs(result.confidence, Confidence.MATCH)
                self.assertEqual(result.name, name)

        self.assertIs(
            module.probe(FakeBus(b"\x00"), 0x5A).confidence,
            Confidence.NO_MATCH,
        )

    def test_cst8xx_multi_register_identity_refines_variant(self):
        module = importlib.import_module("stemma_detect.chips.cst8xx")

        cst816s = module.probe(FakeBus(b"\x12\xb4\x01\x02\x00\x00"), 0x15)
        self.assertIs(cst816s.confidence, Confidence.MATCH)
        self.assertEqual(cst816s.name, "cst816s")

        cst826 = module.probe(FakeBus(b"\x12\x00\x01\x02\x00\x11"), 0x15)
        self.assertIs(cst826.confidence, Confidence.MATCH)
        self.assertEqual(cst826.name, "cst826")

        generic = module.probe(FakeBus(b"\x12\x00\x01\x02\x00\x00"), 0x15)
        self.assertIs(generic.confidence, Confidence.MATCH)
        self.assertIsNone(generic.name)

        invalid = module.probe(FakeBus(bytes(6)), 0x15)
        self.assertIs(invalid.confidence, Confidence.NO_MATCH)

    def test_seesaw_hardware_and_firmware_identity(self):
        module = importlib.import_module("stemma_detect.chips.seesaw")
        version = (5690 << 16) | 0x0102
        matched = CommandBus(
            {
                b"\x00\x01": b"\x88",
                b"\x00\x02": version.to_bytes(4, "big"),
            }
        )

        result = module.probe(matched, 0x49)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(result.name, "attiny1616_seesaw")
        self.assertEqual(result.evidence["product_id"], "5690")

        unknown_product = CommandBus(
            {
                b"\x00\x01": b"\x55",
                b"\x00\x02": ((1234 << 16) | 1).to_bytes(4, "big"),
            }
        )
        self.assertIsNone(module.probe(unknown_product, 0x49).name)

        blank_version = CommandBus({b"\x00\x01": b"\x88", b"\x00\x02": bytes(4)})
        self.assertIs(
            module.probe(blank_version, 0x49).confidence,
            Confidence.NO_MATCH,
        )

    def test_vcnl401x_shared_id_stays_possible_across_drivers(self):
        for name in ("vcnl4010", "vcnl4020"):
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            with self.subTest(name=name):
                result = module.probe(FakeBus(b"\x21"), 0x13)
                self.assertIs(result.confidence, Confidence.POSSIBLE)
                self.assertEqual((result.score, result.max_score), (8, 10))
                self.assertIs(
                    module.probe(FakeBus(b"\x00"), 0x13).confidence,
                    Confidence.NO_MATCH,
                )

    def test_pmsa003i_frame_signature(self):
        module = importlib.import_module("stemma_detect.chips.pmsa003i")
        frame = bytearray(32)
        frame[:2] = b"BM"
        frame[2:4] = (28).to_bytes(2, "big")
        frame[4:30] = bytes(range(26))
        frame[30:32] = sum(frame[:30]).to_bytes(2, "big")

        result = module.probe(FakeBus(bytes(frame)), 0x12)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (12, 12))

        frame[30] ^= 0x01
        self.assertIs(
            module.probe(FakeBus(bytes(frame)), 0x12).confidence,
            Confidence.NO_MATCH,
        )

    def test_sen6x_crc_product_name(self):
        module = importlib.import_module("stemma_detect.chips.sen6x")

        def words(payload):
            payload = payload.ljust(32, b"\x00")
            return b"".join(
                payload[offset : offset + 2]
                + bytes((_sensirion.crc8(payload[offset : offset + 2]),))
                for offset in range(0, 32, 2)
            )

        result = module.probe(FakeBus(words(b"SEN66")), 0x6B)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(result.name, "sen66")
        self.assertIs(
            module.probe(FakeBus(words(b"NOT-A-SEN")), 0x6B).confidence,
            Confidence.NO_MATCH,
        )

    def test_scd30_firmware_signature(self):
        module = importlib.import_module("stemma_detect.chips.scd30")
        version = b"\x03\x42"
        response = version + bytes((_sensirion.crc8(version),))

        result = module.probe(FakeBus(response), 0x61)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(result.evidence["firmware_version"], "3.66")

    def test_scd4x_operating_mode_aware_signature(self):
        module = importlib.import_module("stemma_detect.chips.scd4x")

        def word(value):
            payload = value.to_bytes(2, "big")
            return payload + bytes((_sensirion.crc8(payload),))

        result = module.probe(
            CommandBus({b"\xe4\xb8": word(1), b"\x20\x2f": word(0x1000)}),
            0x62,
        )
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(result.name, "scd41")
        self.assertEqual((result.score, result.max_score), (14, 14))

        invalid_status = module.probe(
            CommandBus({b"\xe4\xb8": word(0xF800), b"\x20\x2f": word(0)}),
            0x62,
        )
        self.assertIs(invalid_status.confidence, Confidence.NO_MATCH)

    def test_lc709203f_pec_signature(self):
        module = importlib.import_module("stemma_detect.chips.lc709203f")

        def response(register, value):
            payload = value.to_bytes(2, "little")
            pec_input = bytes((0x16, register, 0x17)) + payload
            return payload + bytes((module._crc8(pec_input),))

        bus = RegisterBus({0x1A: response(0x1A, 0x0504), 0x11: response(0x11, 0x1234)})
        result = module.probe(bus, 0x0B)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (14, 14))

        bad_pec = RegisterBus({0x1A: b"\x04\x05\x00"})
        self.assertIs(module.probe(bad_pec, 0x0B).confidence, Confidence.NO_MATCH)

    def test_mlx90632_factory_signature(self):
        module = importlib.import_module("stemma_detect.chips.mlx90632")
        bus = CommandBus(
            {
                b"\x24\x05": b"\x12\x34\x56\x78\x9a\xbc",
                b"\x24\x09": b"\x00\x82",
                b"\x24\x0b": b"\x01\x05",
            }
        )
        result = module.probe(bus, 0x3A)
        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (14, 14))

        bad_product = CommandBus(
            {b"\x24\x05": b"\x12\x34\x56\x78\x9a\xbc", b"\x24\x09": b"\xfc\x02"}
        )
        self.assertIs(module.probe(bad_product, 0x3A).confidence, Confidence.NO_MATCH)

    def test_apds9960_ids(self):
        for device_id in (b"\xa8", b"\xab"):
            with self.subTest(device_id=device_id):
                self.assertIs(
                    apds9960.probe(FakeBus(device_id), 0x39).confidence,
                    Confidence.MATCH,
                )
        self.assertIs(apds9960.probe(FakeBus(b"\x00"), 0x39).confidence, Confidence.NO_MATCH)

    def test_bno055_signature(self):
        module = importlib.import_module("stemma_detect.chips.bno055")
        matched = RegisterBus(
            {
                0x00: b"\xa0",
                0x01: b"\xfb",
                0x02: b"\x32",
                0x03: b"\x0f",
                0x04: b"\x12\x34",
            }
        )
        wrong_id = RegisterBus({0x00: b"\x00"})

        result = module.probe(matched, 0x28)

        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (24, 24))
        self.assertEqual(result.evidence["software_revision"], "0x1234")
        self.assertIs(module.probe(wrong_id, 0x28).confidence, Confidence.NO_MATCH)

    def test_bmp3xx_signature_refines_variant(self):
        module = importlib.import_module("stemma_detect.chips.bmp3xx")
        for chip_id, name in ((b"\x50", "bmp388"), (b"\x60", "bmp390")):
            bus = RegisterBus(
                {
                    0x00: chip_id,
                    0x02: b"\x00",
                    0x03: b"\x10",
                    0x31: bytes(range(21)),
                }
            )

            result = module.probe(bus, 0x77)

            with self.subTest(chip_id=chip_id):
                self.assertIs(result.confidence, Confidence.MATCH)
                self.assertEqual(result.name, name)
                self.assertEqual((result.score, result.max_score), (19, 19))

    def test_bme280_id(self):
        matched = RegisterBus(
            {
                0xD0: b"\x60",
                0xF3: b"\x09",
                0x88: bytes(range(24)),
                0xE1: bytes(range(7)),
            }
        )
        wrong_id = RegisterBus({0xD0: b"\x58"})

        result = bme280.probe(matched, 0x76)

        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(result.evidence, {"chip_id": "0x60", "signature": "17/17"})
        self.assertEqual((result.score, result.max_score), (17, 17))
        self.assertIs(bme280.probe(wrong_id, 0x76).confidence, Confidence.NO_MATCH)

    def test_bmp280_id(self):
        matched = RegisterBus(
            {
                0xD0: b"\x58",
                0xF3: b"\x08",
                0x88: bytes(range(24)),
            }
        )
        wrong_id = RegisterBus({0xD0: b"\x60"})

        self.assertIs(bmp280.probe(matched, 0x77).confidence, Confidence.MATCH)
        self.assertIs(bmp280.probe(wrong_id, 0x77).confidence, Confidence.NO_MATCH)

    def test_bme680_signature(self):
        module = importlib.import_module("stemma_detect.chips.bme680")
        matched = RegisterBus(
            {
                0xD0: b"\x61",
                0xF0: b"\x01",
                0x89: bytes(range(25)),
                0xE1: bytes(range(16)),
            }
        )
        wrong_id = RegisterBus({0xD0: b"\x60"})

        result = module.probe(matched, 0x77)

        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual(
            result.evidence,
            {"chip_id": "0x61", "variant": "0x01", "signature": "19/19"},
        )
        self.assertEqual((result.score, result.max_score), (19, 19))
        self.assertIs(module.probe(wrong_id, 0x77).confidence, Confidence.NO_MATCH)

    def test_bme280_signature_scores_reserved_status_bits(self):
        bus = RegisterBus(
            {
                0xD0: b"\x60",
                0xF3: b"\x02",
                0x88: bytes(range(24)),
                0xE1: bytes(range(7)),
            }
        )

        result = bme280.probe(bus, 0x76)

        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (15, 17))
        self.assertEqual(result.evidence["missed"], "status_reserved")

    def test_bme280_signature_downgrades_blank_calibration(self):
        bus = RegisterBus(
            {
                0xD0: b"\x60",
                0xF3: b"\x00",
                0x88: bytes(24),
                0xE1: bytes(range(7)),
            }
        )

        result = bme280.probe(bus, 0x76)

        self.assertIs(result.confidence, Confidence.POSSIBLE)
        self.assertEqual((result.score, result.max_score), (14, 17))
        self.assertEqual(result.evidence["missed"], "calibration_tp")

    def test_lis3dh_id(self):
        self.assertIs(lis3dh.probe(FakeBus(b"\x33"), 0x18).confidence, Confidence.MATCH)
        self.assertIs(lis3dh.probe(FakeBus(b"\x00"), 0x18).confidence, Confidence.NO_MATCH)

    def test_ltr390_id(self):
        self.assertIs(ltr390.probe(FakeBus(b"\xb2"), 0x53).confidence, Confidence.MATCH)
        self.assertIs(ltr390.probe(FakeBus(b"\x00"), 0x53).confidence, Confidence.NO_MATCH)

    def test_ltr329_ltr303_ids(self):
        module = importlib.import_module("stemma_detect.chips.ltr329_ltr303")
        matched = RegisterBus({0x86: b"\xa3", 0x87: b"\x05"})
        wrong = RegisterBus({0x86: b"\x00"})

        result = module.probe(matched, 0x29)

        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (16, 16))
        self.assertEqual(result.evidence["part_id"], "0xA3")
        self.assertIs(module.probe(wrong, 0x29).confidence, Confidence.NO_MATCH)

    def test_mcp9808_ids(self):
        matched = RegisterBus({0x06: b"\x00\x54", 0x07: b"\x04\x01"})
        wrong_device = RegisterBus({0x06: b"\x00\x54", 0x07: b"\x03\x01"})
        result = mcp9808.probe(matched, 0x18)

        self.assertIs(result.confidence, Confidence.MATCH)
        self.assertEqual((result.score, result.max_score), (17, 17))
        self.assertEqual(result.evidence["device_id_revision"], "0x0401")
        self.assertIs(mcp9808.probe(wrong_device, 0x18).confidence, Confidence.NO_MATCH)

    def test_ina_family_ids(self):
        cases = (
            ("ina228", 0x3E, 0x3F, 0x228),
            ("ina23x", 0x3E, 0x3F, 0x237),
            ("ina260", 0xFE, 0xFF, 0x227),
            ("ina3221", 0xFE, 0xFF, 0x3220),
        )
        for name, manufacturer_register, device_register, part in cases:
            module = importlib.import_module(f"stemma_detect.chips.{name}")
            matched = RegisterBus(
                {
                    manufacturer_register: b"\x54\x49",
                    device_register: (
                        part.to_bytes(2, "big")
                        if name == "ina3221"
                        else (part << 4).to_bytes(2, "big")
                    ),
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
        self.assertEqual((result.score, result.max_score), (1, 1))

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
