# Calculator Refactoring Guide

## Overview
This calculator has been refactored using the **Dispatcher Table Pattern** to improve maintainability and make future modifications easier.

## Architecture

### Dispatcher Pattern
Instead of a giant if-elif chain, the `parse()` method uses a dictionary-based dispatcher to route inputs to specialized handler methods.

**Benefits:**
- Easy to add new operations
- Each operation is isolated in its own method
- More testable and maintainable
- Clear separation of concerns

### Handler Methods
Each input type has a dedicated handler method:

| Handler Method | Purpose | Input Keys |
|----------------|---------|------------|
| `_handle_operator()` | Sets up arithmetic operations | `+`, `-`, `*`, `/` |
| `_handle_equals()` | Performs calculations | `=` |
| `_handle_digit()` | Processes digit input | `0-9` |
| `_handle_decimal()` | Adds decimal points | `.` |
| `_handle_backspace()` | Removes last character | `b` |
| `_handle_clear_entry()` | Clears display only | `c` |
| `_handle_clear_all()` | Resets calculator | `C` |
| `_handle_negate()` | Toggles sign | `n` |

## Adding New Operations

To add a new operation:

### 1. Create a Handler Method
```python
def _handle_square(self) -> None:
    """Calculate square of current display"""
    try:
        value = float(self.display_str)
        result = value * value
        self.display_str = self._format_number(result)
    except ValueError:
        self.display_str = "Error"
```

### 2. Add to Dispatcher Table
In the `parse()` method, add your key mapping:
```python
dispatch_table = {
    # ... existing mappings ...
    's': self._handle_square,  # Add new operation
}
```

### 3. Add Tests
Create tests for your new handler:
```python
def test_handle_square(self) -> None:
    self.calc.display_str = "5"
    self.calc._handle_square()
    self.assertEqual(self.calc.display_str, "25")
```

## MicroPython Considerations

### Memory Optimization
- Dispatcher table is created on each call (not stored as class variable)
- This avoids holding the dict in memory permanently
- Trade-off: slight CPU overhead for better RAM usage on ESP32

### Type Hints
- Uses conditional import with `TYPE_CHECKING`
- Type hints are ignored at runtime on MicroPython
- Compatible with both Python and MicroPython

### No External Dependencies
- Pure Python implementation
- Only uses built-in types and operations
- No NumPy, BigNumber, or other libraries

## Testing

### Running Tests
```bash
# Run all tests
python -m unittest test_calculator.py -v

# Run specific test class
python -m unittest test_calculator.TestCalculatorHandlerMethods -v

# Run single test
python -m unittest test_calculator.TestCalculatorHandlerMethods.test_handle_equals_addition -v
```

### Test Coverage
- **33 integration tests** - Test through public `parse()` interface
- **29 unit tests** - Test handler methods in isolation
- **Total: 62 tests** - All passing

## Code Structure

```
calculator.py
├── Calculator class
│   ├── __init__() - Initialize state
│   ├── begin() - Reset calculator
│   ├── _format_number() - Format display output
│   ├── _handle_operator() - Process +, -, *, /
│   ├── _handle_equals() - Perform calculations
│   ├── _handle_backspace() - Remove last char
│   ├── _handle_clear_entry() - Clear display
│   ├── _handle_clear_all() - Full reset
│   ├── _handle_negate() - Toggle sign
│   ├── _handle_decimal() - Add decimal point
│   ├── _handle_digit() - Process digits 0-9
│   └── parse() - Main dispatcher (public API)
```

## Future Improvements

### Potential Enhancements
1. **Scientific operations** - sin, cos, sqrt, log
2. **Memory functions** - M+, M-, MR, MC
3. **Parentheses** - Support for complex expressions
4. **History** - Store previous calculations
5. **Constants** - π, e, etc.

### Performance Optimizations
1. Cache dispatcher table (if RAM permits)
2. Optimize string operations
3. Add compiled bytecode for MicroPython

## Troubleshooting

### Common Issues

**Test failures after changes:**
- Run full test suite: `python -m unittest test_calculator.py`
- Check handler method signatures match expectations
- Verify dispatcher table includes all keys

**MicroPython import errors:**
- Ensure `from __future__ import annotations` is first import
- Type hints will be ignored at runtime
- No typing module needed on device

**Memory errors on ESP32:**
- Reduce dispatcher table size
- Remove debug print statements
- Consider pre-compiling to bytecode

## Contributing

When modifying this code:
1. ✅ Run all tests before committing
2. ✅ Add tests for new functionality
3. ✅ Update this guide if architecture changes
4. ✅ Test on actual ESP32 hardware
5. ✅ Keep memory usage in mind
6. ✅ Document any new handler methods

## Version History

- **v2.0** - Refactored with dispatcher pattern (current)
- **v1.0** - Original if-elif implementation
