import unittest
from ChartForgeTK.validation import DataValidator

class TestDataValidator(unittest.TestCase):

    def test_validate_numeric_list(self):
        # Valid cases
        self.assertEqual(DataValidator.validate_numeric_list([1, 2, 3]), [1.0, 2.0, 3.0])
        self.assertEqual(DataValidator.validate_numeric_list((1, 2, 3)), [1.0, 2.0, 3.0])
        self.assertEqual(DataValidator.validate_numeric_list([1.5, 2.5]), [1.5, 2.5])

        # Invalid cases
        with self.assertRaises(TypeError):
            DataValidator.validate_numeric_list(None)
        with self.assertRaises(TypeError):
            DataValidator.validate_numeric_list("not a list")
        with self.assertRaises(TypeError):
            DataValidator.validate_numeric_list([1, "a", 3])

        # Empty list check
        with self.assertRaises(ValueError):
            DataValidator.validate_numeric_list([])
        self.assertEqual(DataValidator.validate_numeric_list([], allow_empty=True), [])

        # Negative values check
        with self.assertRaises(ValueError):
            DataValidator.validate_numeric_list([1, -2, 3], allow_negative=False)
        self.assertEqual(DataValidator.validate_numeric_list([1, -2, 3], allow_negative=True), [1.0, -2.0, 3.0])

    def test_validate_color(self):
        # Valid hex colors
        self.assertEqual(DataValidator.validate_color("#FFFFFF"), "#ffffff")
        self.assertEqual(DataValidator.validate_color("#fff"), "#ffffff")
        self.assertEqual(DataValidator.validate_color("#000000"), "#000000")

        # Valid named colors
        self.assertEqual(DataValidator.validate_color("red"), "red")
        self.assertEqual(DataValidator.validate_color("Blue"), "blue")

        # Invalid colors
        # "notacolor" logs a warning but returns the string, as Tkinter might support it
        self.assertEqual(DataValidator.validate_color("notacolor"), "notacolor")

        with self.assertRaises(ValueError):
            DataValidator.validate_color("#ZZZ")
        with self.assertRaises(TypeError):
            DataValidator.validate_color(123)
        with self.assertRaises(ValueError):
            DataValidator.validate_color("")

    def test_validate_dimensions(self):
        # Valid dimensions
        self.assertEqual(DataValidator.validate_dimensions(800, 600), (800, 600))

        # Invalid dimensions
        with self.assertRaises(ValueError):
            DataValidator.validate_dimensions(10, 600) # Too small width
        with self.assertRaises(ValueError):
            DataValidator.validate_dimensions(800, 10) # Too small height
        with self.assertRaises(TypeError):
            DataValidator.validate_dimensions(None, 600)

    def test_validate_padding(self):
        # Valid padding
        self.assertEqual(DataValidator.validate_padding(10, 800, 600), 10)

        # Invalid padding
        with self.assertRaises(ValueError):
            DataValidator.validate_padding(-5, 800, 600)
        with self.assertRaises(ValueError):
            DataValidator.validate_padding(400, 800, 600) # Too large

    def test_validate_spacing(self):
        # Valid spacing
        self.assertEqual(DataValidator.validate_spacing(10, 100, 5), 10)

        # Invalid spacing
        with self.assertRaises(ValueError):
            DataValidator.validate_spacing(-1, 100, 5)
        with self.assertRaises(ValueError):
            DataValidator.validate_spacing(50, 100, 5) # Too large for 5 items in 100 pixels

if __name__ == '__main__':
    unittest.main()
