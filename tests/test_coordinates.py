import unittest
from ChartForgeTK.coordinates import CoordinateTransformer

class TestCoordinateTransformer(unittest.TestCase):

    def setUp(self):
        self.transformer = CoordinateTransformer(width=800, height=600, padding=50)

    def test_calculate_safe_range(self):
        # Normal range
        min_val, max_val = self.transformer.calculate_safe_range(0, 100, padding_factor=0.1)
        self.assertEqual(min_val, -10.0)
        self.assertEqual(max_val, 110.0)

        # Zero range
        min_val, max_val = self.transformer.calculate_safe_range(50, 50)
        self.assertTrue(min_val < 50 < max_val)
        self.assertNotEqual(min_val, max_val)

        # Zero range at zero
        min_val, max_val = self.transformer.calculate_safe_range(0, 0)
        self.assertTrue(min_val < 0 < max_val)
        self.assertNotEqual(min_val, max_val)

    def test_data_to_pixel_x(self):
        # Setup range
        self.transformer.calculate_ranges(0, 100, 0, 100, x_padding_factor=0.0, y_padding_factor=0.0)

        # Test mappings (drawable width = 800 - 100 = 700)
        # x=0 -> padding (50)
        self.assertAlmostEqual(self.transformer.data_to_pixel_x(0), 50.0)

        # x=100 -> width - padding (750)
        self.assertAlmostEqual(self.transformer.data_to_pixel_x(100), 750.0)

        # x=50 -> center (400)
        self.assertAlmostEqual(self.transformer.data_to_pixel_x(50), 400.0)

    def test_data_to_pixel_y(self):
        # Setup range
        self.transformer.calculate_ranges(0, 100, 0, 100, x_padding_factor=0.0, y_padding_factor=0.0)

        # Test mappings (drawable height = 600 - 100 = 500)
        # Inverted Y axis
        # y=0 -> bottom (height - padding = 550)
        self.assertAlmostEqual(self.transformer.data_to_pixel_y(0), 550.0)

        # y=100 -> top (padding = 50)
        self.assertAlmostEqual(self.transformer.data_to_pixel_y(100), 50.0)

        # y=50 -> center (300)
        self.assertAlmostEqual(self.transformer.data_to_pixel_y(50), 300.0)

    def test_calculate_tick_interval(self):
        # Range 100
        interval = self.transformer.calculate_tick_interval(100)
        self.assertTrue(5 <= 100/interval <= 15)

        # Range 10
        interval = self.transformer.calculate_tick_interval(10)
        self.assertTrue(5 <= 10/interval <= 15)

        # Range 0.1
        interval = self.transformer.calculate_tick_interval(0.1)
        self.assertTrue(5 <= 0.1/interval <= 15)

if __name__ == '__main__':
    unittest.main()
