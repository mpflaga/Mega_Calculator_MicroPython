"""
Configuration file for MicroPython Calculator
Pin mappings and constants
"""

# Display Configuration
DISPLAY_SIZE = 9
LED_PIN = 26  # Change this to match your hardware (A0 equivalent)
LEDS_PER_DIGIT = 29  # 7 segments * 4 LEDs each + 1 decimal point

# Button Pin Mappings (update these to match your MicroPython board)
# Format: (pin_number, character)
BUTTON_PINS = [
    (21, '='),
    (20, '+'),
    (19, 'c'),
    (18, '7'),
    (17, '4'),
    (16, '1'),
    (15, 'n'),
    (14, '0'),
    (2, '2'),
    (3, '5'),
    (4, '8'),
    (5, '('),
    (6, '%'),
    (7, '9'),
    (8, '6'),
    (9, '3'),
    (10, '.'),
    (11, '/'),
    (12, '*'),
    (13, '-')
]

# Debounce settings
DEBOUNCE_MS = 50

# Display settings
DEFAULT_BRIGHTNESS = 0.9
DEFAULT_COLOR = (0, 255, 0)  # RGB: Green
TEST_COLOR_RED = (255, 0, 0)
TEST_COLOR_GREEN = (0, 255, 0)
TEST_COLOR_BLUE = (0, 0, 255)
TEST_COLOR_WHITE = (255, 255, 255)
