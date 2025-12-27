"""
LED Display Driver for NeoPixels in 7-segment arrangement
MicroPython version
"""

import time
from typing import List

from machine import Pin
from neopixel import NeoPixel

# 7-segment digit patterns
# Each digit has 29 LEDs: 7 segments * 4 LEDs each + 1 decimal point
# Segments: TOP_LEFT(0-3), TOP(4-7), TOP_RIGHT(8-11), BOTTOM_RIGHT(12-15),
#           BOTTOM(16-19), BOTTOM_LEFT(20-23), MIDDLE(24-27), DOT(28)
DIGIT_ARRAY: List[List[int]] = [
    # 0
    [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 0,0,0,0, 0],
    # 1
    [0,0,0,0, 0,0,0,0, 1,1,1,1, 1,1,1,1, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0],
    # 2
    [0,0,0,0, 1,1,1,1, 1,1,1,1, 0,0,0,0, 1,1,1,1, 1,1,1,1, 1,1,1,1, 0],
    # 3
    [0,0,0,0, 1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 0,0,0,0, 1,1,1,1, 0],
    # 4
    [1,1,1,1, 0,0,0,0, 1,1,1,1, 1,1,1,1, 0,0,0,0, 0,0,0,0, 1,1,1,1, 0],
    # 5
    [1,1,1,1, 1,1,1,1, 0,0,0,0, 1,1,1,1, 1,1,1,1, 0,0,0,0, 1,1,1,1, 0],
    # 6
    [1,1,1,1, 1,1,1,1, 0,0,0,0, 1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 0],
    # 7
    [0,0,0,0, 1,1,1,1, 1,1,1,1, 1,1,1,1, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0],
    # 8
    [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 0],
    # 9
    [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1, 0,0,0,0, 0,0,0,0, 1,1,1,1, 0]
]


class LEDDisplay:
    """Interface Driver for NeoPixels in 7-segment arrangement"""

    def __init__(self, display_size: int, led_pin: "Pin", leds_per_digit: int = 29) -> None:
        """
        Initialize the LED display

        Args:
            display_size: Number of digits in the display
            led_pin: GPIO pin for NeoPixel data
            leds_per_digit: Number of LEDs per digit (default 29)
        """
        self.display_size: int = display_size
        self.leds_per_digit: int = leds_per_digit
        total_leds: int = display_size * leds_per_digit

        self.strip: NeoPixel = NeoPixel(led_pin, total_leds)
        self.red: int = 127
        self.green: int = 127
        self.blue: int = 127
        self.brightness: float = 1.0

    def begin(self, brightness: float = 0.9) -> None:
        """Initialize the display"""
        self.brightness = brightness
        self.clear()
        self.show()
        print(f"LEDDisplay Driver Started! Display size is {self.display_size}")

    def set_color(self, red: int, green: int, blue: int) -> None:
        """Set the RGB color for the display"""
        self.red = red
        self.green = green
        self.blue = blue

    def _apply_brightness(self, red: int, green: int, blue: int) -> tuple:
        """Apply brightness scaling to RGB values"""
        return (
            int(red * self.brightness),
            int(green * self.brightness),
            int(blue * self.brightness)
        )

    def set_one_digit(self, digit: int, pos: int, dp: bool = False) -> None:
        """
        Display a single digit at a position

        Args:
            digit: Digit to display (0-9) or 0xFF for blank
            pos: Position on display (0 to display_size-1)
            dp: Show decimal point (True/False)
        """
        for led_pos in range(29):
            pixel_index: int = led_pos + (29 * pos)

            if digit >= len(DIGIT_ARRAY):  # Blank the digit if not defined
                self.strip[pixel_index] = (0, 0, 0)
            elif DIGIT_ARRAY[digit][led_pos]:
                self.strip[pixel_index] = self._apply_brightness(self.red, self.green, self.blue)
            else:
                self.strip[pixel_index] = (0, 0, 0)

        # Handle decimal point
        dp_index: int = (29 * pos) + 28
        if dp:
            self.strip[dp_index] = self._apply_brightness(self.red, self.green, self.blue)
        else:
            self.strip[dp_index] = (0, 0, 0)

    def print_display(self, input_str: str) -> None:
        """
        Print a string to the display (right-justified)

        Args:
            input_str: String to display (supports digits and decimal point)
        """
        str_size: int = len(input_str)
        self.clear()

        str_pos: int = str_size - 1

        for display_pos in range(self.display_size - 1, -1, -1):
            if str_pos >= 0 and (input_str[str_pos].isdigit() or input_str[str_pos] == '.'):
                dp: bool = False

                if input_str[str_pos] == '.':
                    dp = True
                    str_pos -= 1

                if str_pos >= 0 and input_str[str_pos].isdigit():
                    digit_value: int = int(input_str[str_pos])
                    self.set_one_digit(digit_value, display_pos, dp)
                    str_pos -= 1
                else:
                    self.set_one_digit(0xFF, display_pos, False)  # Blank
            else:
                self.set_one_digit(0xFF, display_pos, False)  # Blank

        self.show()

    def print_test(self) -> None:
        """Pre-Operation Self Test - light up all LEDs in sequence"""
        self.clear()

        # Create test pattern (all 8s)
        test_pattern: str = '8' * self.display_size

        # Red
        self.set_color(255, 0, 0)
        self.print_display(test_pattern)
        time.sleep(1)

        # Green
        self.set_color(0, 255, 0)
        self.print_display(test_pattern)
        time.sleep(1)

        # Blue
        self.set_color(0, 0, 255)
        self.print_display(test_pattern)
        time.sleep(1)

        # Display digits 0-8 with alternating decimal points
        self.clear()
        self.set_color(255, 255, 255)

        for number in range(self.display_size):
            dp: bool = number % 2 == 0  # Even numbers get decimal point
            self.set_one_digit(number, number, dp)

        self.show()
        time.sleep(1)
        self.clear()
        self.show()

    def clear(self) -> None:
        """Clear all LEDs"""
        for i in range(len(self.strip)):
            self.strip[i] = (0, 0, 0)

    def show(self) -> None:
        """Update the display"""
        self.strip.write()
