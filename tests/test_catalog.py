import unittest

from stemma_detect.catalog import discover_chips


class CatalogTests(unittest.TestCase):
    def test_catalog_loads(self):
        chips = discover_chips()
        self.assertEqual(
            {chip.name for chip in chips},
            {"aht20", "bme280", "bmp280", "pcf8591", "sht4x", "vl6180x"},
        )

    def test_chip_names_and_packages_are_unique(self):
        chips = discover_chips()
        self.assertEqual(len(chips), len({chip.name for chip in chips}))
        self.assertEqual(len(chips), len({chip.package for chip in chips}))


if __name__ == "__main__":
    unittest.main()
