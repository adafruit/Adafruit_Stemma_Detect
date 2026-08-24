import unittest

from stemma_detect.catalog import discover_chips


class CatalogTests(unittest.TestCase):
    def test_catalog_loads(self):
        chips = discover_chips()
        self.assertEqual(
            {chip.name for chip in chips},
            {
                "aht20",
                "adt7410",
                "apds9960",
                "as7341",
                "bme280",
                "bme680",
                "bmp280",
                "bmp3xx",
                "bmp5xx",
                "bno055",
                "ccs811",
                "dps310",
                "ens160",
                "hts221",
                "icm20x",
                "ina228",
                "ina23x",
                "ina260",
                "lis2mdl",
                "lis331",
                "lis3dh",
                "lis3mdl",
                "lsm6ds",
                "ltr390",
                "max1704x",
                "mcp9600",
                "mcp9808",
                "mmc56x3",
                "msa301",
                "pcf8591",
                "qmc5883p",
                "sht4x",
                "stcc4",
                "tcs34725",
                "tmp117",
                "tsl2591",
                "vcnl4040",
                "vl53l0x",
                "vl53l1x",
                "vl6180x",
            },
        )

    def test_chip_names_and_packages_are_unique(self):
        chips = discover_chips()
        self.assertEqual(len(chips), len({chip.name for chip in chips}))
        self.assertEqual(len(chips), len({chip.package for chip in chips}))


if __name__ == "__main__":
    unittest.main()
