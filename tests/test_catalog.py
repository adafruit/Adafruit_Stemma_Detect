import unittest
from types import ModuleType

from stemma_detect.catalog import _load_chip, discover_chips
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk


class CatalogTests(unittest.TestCase):
    def test_catalog_loads(self):
        chips = discover_chips()
        self.assertEqual(
            {chip.name for chip in chips},
            {
                "ahtx0",
                "adt7410",
                "adxl34x",
                "adxl37x",
                "ags02ma",
                "am2320",
                "apds9960",
                "apds9999",
                "as5600",
                "as7331",
                "as7341",
                "as7343",
                "as726x",
                "bme280",
                "bme680",
                "bh1750",
                "bmp280",
                "bmp3xx",
                "bmp5xx",
                "bno055",
                "bno08x",
                "ccs811",
                "dps310",
                "ds3502",
                "ens160",
                "fxas21002c",
                "fxos8700",
                "guvx_i2c",
                "hdc302x",
                "hts221",
                "htu21d",
                "htu31d",
                "icm20x",
                "ina219",
                "ina228",
                "ina23x",
                "ina260",
                "ina3221",
                "lc709203f",
                "l3gd20",
                "lidarlite",
                "lis2mdl",
                "lis331",
                "lis3dh",
                "lis3mdl",
                "lps2x",
                "lps28",
                "lps35hw",
                "lsm303_accel",
                "lsm303dlh_mag",
                "lsm6ds",
                "lsm9ds0",
                "lsm9ds1",
                "ltr329_ltr303",
                "ltr390",
                "max1704x",
                "max44009",
                "mcp3421",
                "mcp9600",
                "mcp9808",
                "mlx90393",
                "mlx90395",
                "mlx90614",
                "mlx90632",
                "mlx90640",
                "mmc56x3",
                "mma8451",
                "mpr121",
                "mprls",
                "mpl115a2",
                "mpl3115a2",
                "mpu6050",
                "ms8607",
                "msa301",
                "opt4048",
                "pa1010d",
                "pcf8591",
                "pct2075",
                "pmsa003i",
                "qmc5883p",
                "scd30",
                "scd4x",
                "sen6x",
                "sgp30",
                "sgp40",
                "sgp41",
                "sht31d",
                "sht4x",
                "shtc3",
                "si7021",
                "si1145",
                "spa06_003",
                "stcc4",
                "sths34pf80",
                "tcs34725",
                "tcs3430",
                "tc74",
                "tlv493d",
                "tmp006",
                "tmp007",
                "tmp117",
                "tsc2007",
                "tsl2591",
                "tsl2561",
                "tmag5273",
                "vcnl4010",
                "vcnl4020",
                "vcnl4030",
                "vcnl4040",
                "vcnl4200",
                "veml6070",
                "veml6075",
                "veml7700",
                "vl53l0x",
                "vl53l1x",
                "vl53l4cd",
                "vl6180x",
            },
        )

    def test_chip_names_and_packages_are_unique(self):
        chips = discover_chips()
        self.assertEqual(len(chips), len({chip.name for chip in chips}))
        self.assertEqual(len(chips), len({chip.package for chip in chips}))

    def test_default_addresses_are_loaded(self):
        chips = {chip.name: chip for chip in discover_chips()}

        self.assertEqual(chips["pcf8591"].default_addresses, (0x48,))
        self.assertEqual(chips["ahtx0"].default_addresses, (0x38,))
        self.assertEqual(chips["pcf8591"].address_kind(0x48), "default")
        self.assertEqual(chips["pcf8591"].address_kind(0x49), "alternate")

    def test_probe_risk_is_loaded(self):
        chips = {chip.name: chip for chip in discover_chips()}

        self.assertIs(chips["as5600"].probe_risk, ProbeRisk.PASSIVE)
        self.assertIs(chips["bme280"].probe_risk, ProbeRisk.REGISTER)
        self.assertIs(chips["vl53l4cd"].probe_risk, ProbeRisk.COMMAND)

    def test_default_address_must_be_a_supported_address(self):
        module = ModuleType("stemma_detect.chips.invalid_default")
        module.ADDRESSES = (0x48,)
        module.DEFAULT_ADDRESSES = (0x49,)
        module.PACKAGE = "adafruit-circuitpython-invalid-default"
        module.PROBE_CONFIDENCE = Confidence.POSSIBLE
        module.probe = lambda _bus, _address: ProbeResult.possible()

        with self.assertRaisesRegex(ValueError, "default address"):
            _load_chip(module)


if __name__ == "__main__":
    unittest.main()
