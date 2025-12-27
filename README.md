# MicroPython Calculator

A 9-digit calculator with NeoPixel 7-segment LED display, refactored from Arduino to MicroPython.

## Overview

This project is a MicroPython port of the Arduino Mega Calculator. It simulates a standard 9-digit calculator with decimal points using a NeoPixel LED display and physical buttons.

## Features

- 9-digit display using NeoPixel LEDs in 7-segment arrangement
- Standard calculator operations: +, -, *, /
- Decimal point support
- Negative number support
- Clear entry (c) and clear all (C) functions
- RGB color customization for display
- Hardware button debouncing
- Power-on self-test (POST) with RGB color cycle

## Hardware Requirements

- MicroPython-compatible board (e.g., ESP32, Raspberry Pi Pico, PyBoard)
- NeoPixel LED strip (WS2812B) with 261 LEDs (9 digits × 29 LEDs per digit)
  - 7 segments × 4 LEDs per segment = 28 LEDs
  - 1 decimal point LED
- 20 push buttons for calculator input
- Appropriate resistors and power supply for NeoPixels

## Pin Configuration

The default pin mappings are defined in `config.py`:

- **LED_PIN**: GPIO 26 (update for your board)
- **Button pins**: See `BUTTON_PINS` in `config.py`

### Button Layout

```
=  +  c  7  4  1  n  0
2  5  8  (  %  9  6  3
.  /  *  -
```

Where:
- `c` = Clear Entry
- `n` = Negate (toggle +/-)
- `=` = Equals
- `(` = Left parenthesis (reserved for future use)
- `%` = Modulo (reserved for future use)

## Installation

1. Install MicroPython on your board following the official instructions
2. Copy all Python files to your board:
   - `main.py`
   - `calculator.py`
   - `led_display.py`
   - `config.py`

### Using ampy (recommended)

```bash
pip install adafruit-ampy
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put calculator.py
ampy --port /dev/ttyUSB0 put led_display.py
ampy --port /dev/ttyUSB0 put config.py
```

### Using Thonny IDE

1. Open Thonny IDE
2. Select your MicroPython device
3. Upload each file to the board

## Configuration

Edit `config.py` to match your hardware:

```python
# Update LED pin for your board
LED_PIN = 26  # Change to your GPIO pin

# Update button pins
BUTTON_PINS = [
    (21, '='),
    (20, '+'),
    # ... etc
]

# Adjust display settings
DEFAULT_COLOR = (0, 255, 0)  # RGB: Green
DEFAULT_BRIGHTNESS = 0.9
```

## Usage

### Running the Calculator

Once the files are uploaded, the calculator will start automatically on boot if `main.py` is present.

To run manually:
```python
import main
```

Or via REPL:
```python
from main import CalculatorApp
app = CalculatorApp()
app.run()
```

### Calculator Operations

1. **Enter numbers**: Press digit buttons (0-9)
2. **Decimal point**: Press `.` button
3. **Operations**: Press `+`, `-`, `*`, `/`
4. **Calculate**: Press `=`
5. **Clear entry**: Press `c` to clear current input
6. **Clear all**: Press `C` (if available) to reset calculator
7. **Negate**: Press `n` to toggle positive/negative

### Example Calculation

```
7 + 3 = 10
5 * 9 = 45
100 / 4 = 25
```

## Project Structure

```
Mega_Calculator_MicroPython/
├── main.py           # Main application and button handling
├── calculator.py     # Calculator logic
├── led_display.py    # NeoPixel 7-segment display driver
├── config.py         # Pin mappings and configuration
└── README.md         # This file
```

## Key Differences from Arduino Version

### Removed Dependencies
- **BigNumber library**: Replaced with Python's native float arithmetic
- **Debouncer library**: Custom implementation included
- **Adafruit_NeoPixel**: Replaced with MicroPython's native `neopixel` module

### Architecture Changes
- Object-oriented design with separate modules
- Simplified number handling using Python floats
- Native Python string manipulation
- Configuration separated into `config.py`

### Limitations
- **Precision**: Uses Python floats instead of arbitrary precision arithmetic
  - Maximum ~15-17 significant digits (vs. configurable in Arduino)
- **Memory**: Large numbers may cause issues on memory-constrained boards
- **Display size**: Fixed at 9 digits (configurable in code)

## Troubleshooting

### Display not lighting up
- Check LED_PIN configuration in `config.py`
- Verify NeoPixel power supply (5V, sufficient current)
- Test with simple NeoPixel example first

### Buttons not responding
- Verify button pin numbers in `config.py`
- Check pull-up resistor configuration
- Adjust `DEBOUNCE_MS` if buttons are too sensitive

### Import errors
- Ensure all files are uploaded to the board
- Check MicroPython version compatibility
- Verify `neopixel` module is available

### Memory errors
- Reduce `DISPLAY_SIZE` if needed
- Use a board with more RAM (e.g., ESP32 vs. ESP8266)

## Future Enhancements

- [ ] Add parentheses support for order of operations
- [ ] Add modulo (%) operation
- [ ] Implement memory functions (M+, M-, MR, MC)
- [ ] Add square root and power functions
- [ ] UART/Serial calculator input mode
- [ ] Save/restore calculator state to flash

## Credits

- **Original Author**: Michael Flaga (michael@flaga.net)
- **Original Project**: Arduino Mega Calculator
- **MicroPython Port**: Refactored from C++ to Python

## License

Released into the public domain (same as original Arduino version).

## Contributing

Feel free to submit issues and enhancement requests!

## See Also

- Original Arduino project: `Mega_Calculator/`
- MicroPython documentation: https://docs.micropython.org/
- NeoPixel guide: https://learn.adafruit.com/adafruit-neopixel-uberguide/
