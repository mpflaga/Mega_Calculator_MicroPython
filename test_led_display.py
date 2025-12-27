"""
Unit tests for LEDDisplay module
Tests display functionality with mocked NeoPixel hardware
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
from typing import Any, Tuple, List

# Mock MicroPython-specific modules before importing led_display
# (machine and neopixel are MicroPython-specific and not available in regular Python)
sys.modules['machine'] = MagicMock()
sys.modules['neopixel'] = MagicMock()

from led_display import LEDDisplay, DIGIT_ARRAY


class MockNeoPixel:
    """Mock NeoPixel class for testing without hardware"""

    def __init__(self, pin: Any, num_leds: int) -> None:
        """Initialize mock with specified number of LEDs"""
        self.pin: Any = pin
        self.num_leds: int = num_leds
        self.pixels: List[Tuple[int, int, int]] = [(0, 0, 0)] * num_leds
        self.write_called: bool = False

    def __len__(self) -> int:
        """Return number of LEDs"""
        return self.num_leds

    def __setitem__(self, index: int, value: Tuple[int, int, int]) -> None:
        """Set pixel color"""
        if 0 <= index < self.num_leds:
            self.pixels[index] = value

    def __getitem__(self, index: int) -> Tuple[int, int, int]:
        """Get pixel color"""
        if 0 <= index < self.num_leds:
            return self.pixels[index]
        return (0, 0, 0)

    def write(self) -> None:
        """Mock write method"""
        self.write_called = True


class TestLEDDisplay(unittest.TestCase):
    """Test cases for LEDDisplay class"""

    def setUp(self) -> None:
        """Set up test fixtures with mocked hardware"""
        # Mock the Pin class
        with patch('led_display.NeoPixel', MockNeoPixel):
            mock_pin: Mock = Mock()
            self.display: LEDDisplay = LEDDisplay(display_size=9, led_pin=mock_pin, leds_per_digit=29)

    def test_initialization(self) -> None:
        """Test display initializes with correct parameters"""
        self.assertEqual(self.display.display_size, 9)
        self.assertEqual(self.display.leds_per_digit, 29)
        self.assertEqual(self.display.red, 127)
        self.assertEqual(self.display.green, 127)
        self.assertEqual(self.display.blue, 127)

    def test_set_color(self) -> None:
        """Test setting display color"""
        self.display.set_color(255, 0, 0)
        self.assertEqual(self.display.red, 255)
        self.assertEqual(self.display.green, 0)
        self.assertEqual(self.display.blue, 0)

        self.display.set_color(0, 255, 128)
        self.assertEqual(self.display.red, 0)
        self.assertEqual(self.display.green, 255)
        self.assertEqual(self.display.blue, 128)

    def test_begin_clears_display(self) -> None:
        """Test that begin() initializes the display"""
        with patch('led_display.NeoPixel', MockNeoPixel):
            mock_pin = Mock()
            display = LEDDisplay(display_size=9, led_pin=mock_pin)
            display.begin()
            # Display should be cleared (all LEDs off)

    def test_clear(self) -> None:
        """Test clearing all LEDs"""
        # Set some pixels to non-zero values
        self.display.set_color(255, 255, 255)
        self.display.set_one_digit(8, 0, False)

        # Clear the display
        self.display.clear()

        # Check all pixels are off
        for i in range(len(self.display.strip)):
            self.assertEqual(self.display.strip[i], (0, 0, 0))

    def test_set_one_digit_zero(self) -> None:
        """Test displaying digit 0"""
        self.display.set_color(255, 0, 0)
        self.display.set_one_digit(0, 0, False)

        # Verify the pattern matches DIGIT_ARRAY[0]
        for led_pos in range(29):
            pixel_index = led_pos
            if DIGIT_ARRAY[0][led_pos]:
                self.assertEqual(self.display.strip[pixel_index], (255, 0, 0))
            else:
                self.assertEqual(self.display.strip[pixel_index], (0, 0, 0))

    def test_set_one_digit_with_decimal_point(self) -> None:
        """Test displaying digit with decimal point"""
        self.display.set_color(0, 255, 0)
        self.display.set_one_digit(5, 0, True)

        # Check decimal point LED (position 28)
        dp_index = 28
        self.assertEqual(self.display.strip[dp_index], (0, 255, 0))

    def test_set_one_digit_without_decimal_point(self) -> None:
        """Test displaying digit without decimal point"""
        self.display.set_color(0, 255, 0)
        self.display.set_one_digit(5, 0, False)

        # Check decimal point LED is off
        dp_index = 28
        self.assertEqual(self.display.strip[dp_index], (0, 0, 0))

    def test_set_one_digit_all_digits(self) -> None:
        """Test that all digits 0-9 can be displayed"""
        self.display.set_color(255, 255, 255)

        for digit in range(10):
            self.display.clear()
            self.display.set_one_digit(digit, 0, False)

            # Verify at least some LEDs are lit
            lit_count = sum(1 for i in range(29) if self.display.strip[i] != (0, 0, 0))
            self.assertGreater(lit_count, 0, f"Digit {digit} should light some LEDs")

    def test_set_one_digit_blank(self) -> None:
        """Test blanking a digit (0xFF or invalid digit)"""
        self.display.set_color(255, 255, 255)
        self.display.set_one_digit(0xFF, 0, False)

        # All LEDs in the digit should be off
        for led_pos in range(29):
            self.assertEqual(self.display.strip[led_pos], (0, 0, 0))

    def test_set_one_digit_position(self) -> None:
        """Test displaying digit at different positions"""
        self.display.set_color(0, 0, 255)

        # Test digit at position 0
        self.display.clear()
        self.display.set_one_digit(5, 0, False)
        # First digit LEDs should be set
        self.assertNotEqual(self.display.strip[0], (0, 0, 0))

        # Test digit at position 5
        self.display.clear()
        self.display.set_one_digit(5, 5, False)
        # Position 5 LEDs should be set (starting at LED 5*29=145)
        led_index = 5 * 29
        # Check if any LED in this digit is lit
        digit_lit = any(self.display.strip[led_index + i] != (0, 0, 0) for i in range(29))
        self.assertTrue(digit_lit)

    def test_print_display_single_digit(self) -> None:
        """Test printing single digit"""
        self.display.set_color(255, 255, 255)
        self.display.print_display("5")

        # Should display 5 in rightmost position (position 8)
        # Verify rightmost digit has some LEDs lit
        rightmost_pos = 8
        led_start = rightmost_pos * 29
        digit_lit = any(self.display.strip[led_start + i] != (0, 0, 0) for i in range(29))
        self.assertTrue(digit_lit)

    def test_print_display_multiple_digits(self) -> None:
        """Test printing multiple digits"""
        self.display.set_color(255, 255, 255)
        self.display.print_display("123")

        # Verify rightmost three digits are lit
        for pos in [6, 7, 8]:  # Positions for "123" on 9-digit display
            led_start = pos * 29
            digit_lit = any(self.display.strip[led_start + i] != (0, 0, 0) for i in range(28))
            self.assertTrue(digit_lit, f"Position {pos} should be lit")

    def test_print_display_with_decimal(self) -> None:
        """Test printing number with decimal point"""
        self.display.set_color(255, 255, 255)
        self.display.print_display("3.14")

        # Verify decimal point is lit at appropriate position
        # "3.14" right-justified on 9-digit display shows:
        # Positions: 0,1,2,3,4,5,6,7,8
        # Display:   _,_,_,_,_,_,3.,1,4
        # Check position 6 (digit 3 with decimal point)
        dp_index = 6 * 29 + 28
        self.assertEqual(self.display.strip[dp_index], (255, 255, 255))

    def test_print_display_right_justified(self) -> None:
        """Test that display is right-justified"""
        self.display.clear()
        self.display.set_color(100, 100, 100)
        self.display.print_display("1")

        # Only rightmost position should be lit
        rightmost_pos = 8
        led_start = rightmost_pos * 29

        # Check rightmost digit is lit
        digit_lit = any(self.display.strip[led_start + i] != (0, 0, 0) for i in range(28))
        self.assertTrue(digit_lit)

        # Check leftmost digit is not lit
        leftmost_lit = any(self.display.strip[i] != (0, 0, 0) for i in range(28))
        self.assertFalse(leftmost_lit)

    def test_print_display_zeros(self) -> None:
        """Test displaying zeros"""
        self.display.set_color(255, 255, 255)
        self.display.print_display("000")

        # Should display three zeros
        for pos in [6, 7, 8]:
            led_start = pos * 29
            digit_lit = any(self.display.strip[led_start + i] != (0, 0, 0) for i in range(28))
            self.assertTrue(digit_lit, f"Zero at position {pos} should be lit")

    def test_print_display_clears_before_display(self) -> None:
        """Test that print_display clears display first"""
        # Display something
        self.display.set_color(255, 255, 255)
        self.display.print_display("888888888")

        # Display fewer digits
        self.display.print_display("1")

        # Check that leftmost digits are cleared
        for pos in range(7):  # Positions 0-6 should be blank
            led_start = pos * 29
            digit_blank = all(self.display.strip[led_start + i] == (0, 0, 0) for i in range(29))
            self.assertTrue(digit_blank, f"Position {pos} should be blank")

    def test_print_display_handles_non_digit_characters(self) -> None:
        """Test that non-digit characters are handled gracefully"""
        self.display.set_color(255, 255, 255)
        # Should only display the digits, ignore other chars
        self.display.print_display("12abc34")
        # Exact behavior depends on implementation

    def test_show_writes_to_strip(self) -> None:
        """Test that show() calls strip.write()"""
        self.display.strip.write_called = False
        self.display.show()
        self.assertTrue(self.display.strip.write_called)

    def test_leading_zeros_properly_blanked(self) -> None:
        """Test that leading positions are blanked (not showing zeros)"""
        self.display.clear()
        self.display.set_color(255, 255, 255)
        self.display.print_display("5")

        # Leftmost 8 positions should be completely blank (0xFF)
        for pos in range(8):  # Positions 0-7 should be blank
            led_start = pos * 29
            # All 29 LEDs in this position should be off
            all_off = all(self.display.strip[led_start + i] == (0, 0, 0)
                         for i in range(29))
            self.assertTrue(all_off,
                          f"Position {pos} should be completely blank (all LEDs off)")

        # Rightmost position (8) should be lit
        led_start = 8 * 29
        some_lit = any(self.display.strip[led_start + i] != (0, 0, 0)
                      for i in range(28))  # Excluding decimal point
        self.assertTrue(some_lit, "Position 8 should have digit lit")

    def test_decimal_point_positioning(self) -> None:
        """Test decimal point appears on correct digit"""
        self.display.clear()
        self.display.set_color(255, 0, 0)

        # Display "3.14" - decimal should be on the "3"
        self.display.print_display("3.14")

        # On a 9-digit display, "3.14" right-justified is:
        # Positions: 0,1,2,3,4,5,6,7,8
        # Display:   _,_,_,_,_,_,3.,1,4
        # Position 6 should have decimal point lit

        # Find where "3" is displayed (should be position 6)
        # The decimal point for position 6 is at LED index 6*29+28
        dp_index_pos6 = 6 * 29 + 28
        self.assertEqual(self.display.strip[dp_index_pos6], (255, 0, 0),
                        "Decimal point should be lit at position 6")

        # Positions 7 and 8 should NOT have decimal points
        dp_index_pos7 = 7 * 29 + 28
        dp_index_pos8 = 8 * 29 + 28
        self.assertEqual(self.display.strip[dp_index_pos7], (0, 0, 0),
                        "Position 7 should not have decimal point")
        self.assertEqual(self.display.strip[dp_index_pos8], (0, 0, 0),
                        "Position 8 should not have decimal point")

    def test_multiple_decimal_points_in_string(self) -> None:
        """Test handling of invalid input with multiple decimals"""
        # This shouldn't happen from calculator, but test display handles it
        self.display.clear()
        self.display.set_color(0, 255, 0)

        # The display processes right-to-left, so behavior may vary
        # Just ensure it doesn't crash
        try:
            self.display.print_display("1.2.3")
        except Exception as e:
            self.fail(f"Display should handle invalid input gracefully: {e}")

    def test_decimal_only_string(self) -> None:
        """Test displaying just a decimal point"""
        self.display.clear()
        self.display.set_color(100, 100, 100)
        self.display.print_display(".")

        # Should not crash, and rightmost position might show decimal
        # Exact behavior depends on implementation

    def test_leading_decimal_point(self) -> None:
        """Test displaying number starting with decimal like '.5'"""
        self.display.clear()
        self.display.set_color(255, 255, 255)
        self.display.print_display(".5")

        # Should display properly (either as ".5" or "0.5" depending on calculator)

    def test_trailing_decimal_point(self) -> None:
        """Test displaying number ending with decimal like '5.'"""
        self.display.clear()
        self.display.set_color(255, 255, 255)
        self.display.print_display("5.")

        # Rightmost digit should be "5" with decimal point lit
        rightmost_pos = 8
        dp_index = rightmost_pos * 29 + 28
        self.assertEqual(self.display.strip[dp_index], (255, 255, 255),
                        "Decimal point should be lit after the 5")

    def test_zero_with_decimal(self) -> None:
        """Test displaying '0.' properly"""
        self.display.clear()
        self.display.set_color(200, 200, 200)
        self.display.print_display("0.")

        # Should show "0" with decimal point
        rightmost_pos = 8

        # Check that digit 0 pattern is displayed
        led_start = rightmost_pos * 29
        # At least some segment LEDs should be lit for zero
        digit_lit = any(self.display.strip[led_start + i] != (0, 0, 0)
                       for i in range(28))
        self.assertTrue(digit_lit, "Digit 0 should be displayed")

        # Decimal point should be lit
        dp_index = rightmost_pos * 29 + 28
        self.assertEqual(self.display.strip[dp_index], (200, 200, 200),
                        "Decimal point should be lit")

    def test_blank_positions_have_no_decimal_points(self) -> None:
        """Test that blank leading positions don't show decimal points"""
        self.display.clear()
        self.display.set_color(255, 255, 255)
        self.display.print_display("42")

        # Positions 0-6 are blank, they should have NO decimal points
        for pos in range(7):
            dp_index = pos * 29 + 28
            self.assertEqual(self.display.strip[dp_index], (0, 0, 0),
                           f"Blank position {pos} should not have decimal point lit")

    def test_all_segments_off_in_blank_positions(self) -> None:
        """Test that all 29 LEDs are off in blank positions"""
        self.display.clear()
        self.display.set_color(255, 100, 50)
        self.display.print_display("7")

        # Positions 0-7 should be completely off (all 29 LEDs)
        for pos in range(8):
            for led_offset in range(29):
                led_index = pos * 29 + led_offset
                self.assertEqual(self.display.strip[led_index], (0, 0, 0),
                               f"LED {led_offset} at blank position {pos} should be off")


class TestDigitArray(unittest.TestCase):
    """Test DIGIT_ARRAY constant"""

    def test_digit_array_has_all_digits(self) -> None:
        """Test DIGIT_ARRAY contains all digits 0-9"""
        self.assertEqual(len(DIGIT_ARRAY), 10)

    def test_digit_array_format(self) -> None:
        """Test each digit array has correct format"""
        for digit in range(10):
            pattern = DIGIT_ARRAY[digit]
            # Should have 29 elements (28 segment LEDs + 1 decimal point)
            self.assertEqual(len(pattern), 29)

            # All elements should be 0 or 1
            for element in pattern:
                self.assertIn(element, [0, 1])

            # Decimal point (last element) should always be 0
            self.assertEqual(pattern[28], 0)

    def test_digit_patterns_unique(self) -> None:
        """Test that different digits have different patterns"""
        # Check that not all digits are the same
        patterns_unique = len(set(tuple(d) for d in DIGIT_ARRAY)) == 10
        self.assertTrue(patterns_unique, "All digit patterns should be unique")


if __name__ == '__main__':
    unittest.main()
