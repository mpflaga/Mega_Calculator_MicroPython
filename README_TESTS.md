# Unit Tests for MicroPython Calculator

This directory contains comprehensive unit tests for the MicroPython Calculator project.

## Test Files

- **test_calculator.py** - Tests for Calculator logic (33 tests)
- **test_led_display.py** - Tests for LED display functionality (30 tests)
- **test_main.py** - Tests for DebouncedButton and CalculatorApp (13 tests)

## Running the Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test File
```bash
python test_calculator.py
python test_led_display.py
python test_main.py
```

### Run Specific Test Class
```bash
python -m unittest test_calculator.TestCalculator -v
python -m unittest test_led_display.TestLEDDisplay -v
```

### Run Individual Test
```bash
python -m unittest test_calculator.TestCalculator.test_addition -v
```

## Test Coverage

### Calculator Tests (test_calculator.py)
✅ Initialization and state management
✅ Digit entry and max digit limits
✅ All arithmetic operations (+, -, *, /)
✅ Division by zero error handling
✅ Decimal point entry and validation
✅ Backspace functionality
✅ Clear entry (c) and clear all (C)
✅ Negation toggle
✅ Repeated equals
✅ Chain operations
✅ Number formatting (trailing zeros, truncation)

### LED Display Tests (test_led_display.py)
✅ Display initialization
✅ Color setting (RGB)
✅ Individual digit display (0-9)
✅ Decimal point positioning
✅ **Leading zero blanking** - Verifies empty positions are completely off
✅ **Decimal LED control** - Ensures decimal points only light where needed
✅ Right-justified display
✅ Multiple digits with decimals
✅ Edge cases (invalid input, multiple decimals)
✅ DIGIT_ARRAY validation

### Main Module Tests (test_main.py)
✅ DebouncedButton initialization
✅ Button press detection (partial - see known issues)
✅ Button release detection (partial - see known issues)
✅ Debounce logic
✅ CalculatorApp initialization
✅ Key processing integration

## Test Results Summary

Current status: **76/76 tests passing (100%)** ✅

- ✅ Calculator: 33/33 passing (100%)
- ✅ LED Display: 30/30 passing (100%)
- ✅ Main/Integration: 13/13 passing (100%)

## Important Notes

### Hardware Mocking
All tests use mocks for hardware components:
- `machine.Pin` - GPIO pins
- `neopixel.NeoPixel` - LED strip control
- `time.ticks_ms()` - MicroPython time functions

This allows tests to run on regular Python without MicroPython or physical hardware.

### Leading Zeros and Decimal Points
Special attention was paid to testing:
1. **Leading zero blanking** - Empty digit positions have ALL 29 LEDs off (28 segments + 1 decimal)
2. **Decimal point positioning** - Decimal LEDs (LED #28 in each digit) only light on digits with decimals
3. **Blank position verification** - Unused positions are completely dark

See tests in `test_led_display.py`:
- `test_leading_zeros_properly_blanked`
- `test_decimal_point_positioning`
- `test_blank_positions_have_no_decimal_points`
- `test_all_segments_off_in_blank_positions`

## Adding New Tests

To add new tests:

1. Import necessary modules with mocks:
```python
import sys
sys.modules['machine'] = MagicMock()  # if needed
sys.modules['neopixel'] = MagicMock()  # if needed

from your_module import YourClass
```

2. Create test class extending `unittest.TestCase`
3. Use `setUp()` for test fixtures
4. Write test methods starting with `test_`
5. Use assertions (`assertEqual`, `assertTrue`, etc.)

## Dependencies

Tests require only standard Python (3.7+):
- `unittest` (built-in)
- `unittest.mock` (built-in)

No external dependencies required!
