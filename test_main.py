"""
Unit tests for main module
Tests DebouncedButton class and CalculatorApp integration
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
from typing import Any, Optional, List

# Mock MicroPython-specific modules before importing main
sys.modules['machine'] = MagicMock()
sys.modules['neopixel'] = MagicMock()


class MockPin:
    """Mock Pin class for testing without hardware"""

    IN: int = 0
    OUT: int = 1
    PULL_UP: int = 2

    def __init__(self, pin_num: int, mode: Optional[int] = None, pull: Optional[int] = None) -> None:
        """Initialize mock pin"""
        self.pin_num: int = pin_num
        self.mode: Optional[int] = mode
        self.pull: Optional[int] = pull
        self._value: int = 1  # Default to HIGH (unpressed with pull-up)

    def value(self, val: Optional[int] = None) -> int:
        """Get or set pin value"""
        if val is not None:
            self._value = val
        return self._value


class TestDebouncedButton(unittest.TestCase):
    """Test cases for DebouncedButton class"""

    def setUp(self) -> None:
        """Set up test fixtures with mocked hardware"""
        # We need to patch machine.Pin before importing main
        self.pin_patcher: Any = patch('main.Pin', MockPin)
        self.pin_patcher.start()

        # Mock MicroPython time functions
        self.time_patcher: Any = patch('main.time')
        self.mock_time: Any = self.time_patcher.start()

        # Use a list to make it mutable in closures - reset to 0 for each test
        self.current_ticks: List[int] = [0]

        def get_ticks() -> int:
            return self.current_ticks[0]

        def ticks_diff(a: int, b: int) -> int:
            return a - b

        self.mock_time.ticks_ms = get_ticks
        self.mock_time.ticks_diff = ticks_diff
        self.mock_time.sleep_ms = lambda _ms: None

        # Import after patching
        from main import DebouncedButton  # noqa: PLC0415
        self.DebouncedButton: Any = DebouncedButton

        # Create button with mocked pin - button captures initial ticks (0)
        self.button: Any = DebouncedButton(pin_num=10, debounce_ms=50)

    def tearDown(self) -> None:
        """Clean up patches"""
        self.pin_patcher.stop()
        self.time_patcher.stop()

    def test_initialization(self) -> None:
        """Test button initializes with correct default values"""
        self.assertEqual(self.button.debounce_ms, 50)
        self.assertFalse(self.button.pressed)
        self.assertFalse(self.button.released)
        self.assertEqual(self.button.current_state, 1)  # High with pull-up

    def test_button_not_pressed_initially(self) -> None:
        """Test button is not pressed on initialization"""
        self.assertFalse(self.button.is_pressed())
        self.assertFalse(self.button.is_released())

    def test_button_press_detection(self) -> None:
        """Test detecting button press"""
        # Simulate button press (goes LOW)
        self.button.pin._value = 0  # noqa: SLF001

        # Update immediately - should not trigger due to debounce
        self.button.update()
        self.assertFalse(self.button.is_pressed())

        # Advance time past debounce period
        self.current_ticks[0] += 60  # 60ms > 50ms debounce

        # Update again - should now detect press
        self.button.update()
        self.assertTrue(self.button.is_pressed())
        self.assertFalse(self.button.is_released())

    def test_button_release_detection(self) -> None:
        """Test detecting button release"""
        # First press the button
        self.button.pin._value = 0  # noqa: SLF001

        # First update detects state change but doesn't trigger yet
        self.button.update()
        self.assertFalse(self.button.is_pressed())

        # Advance time and update - should now detect press
        self.current_ticks[0] += 60
        self.button.update()
        self.assertTrue(self.button.is_pressed())

        # Clear the pressed flag
        self.button.update()
        self.assertFalse(self.button.is_pressed())

        # Now release the button (goes HIGH)
        self.button.pin._value = 1  # noqa: SLF001

        # First update after release - registers state change
        self.button.update()

        # Advance time and update - should now detect release
        self.current_ticks[0] += 60
        self.button.update()

        self.assertFalse(self.button.is_pressed())
        self.assertTrue(self.button.is_released())

    def test_debounce_prevents_bounce(self) -> None:
        """Test that debouncing prevents spurious triggers"""
        # Simulate button bounce
        self.button.pin._value = 0  # noqa: SLF001
        self.button.update()

        # Bounce back high quickly
        self.button.pin._value = 1  # noqa: SLF001
        self.current_ticks[0] += 10  # Only 10ms
        self.button.update()

        # Should not register as a press yet
        self.assertFalse(self.button.is_pressed())

    def test_pressed_flag_clears_after_update(self) -> None:
        """Test that pressed flag is edge-triggered (only true once)"""
        # Press button
        self.button.pin._value = 0  # noqa: SLF001

        # First update - detects state change
        self.button.update()
        self.assertFalse(self.button.is_pressed())

        # Advance time and update - triggers press
        self.current_ticks[0] += 60
        self.button.update()
        self.assertTrue(self.button.is_pressed())

        # Update again without changing state
        self.button.update()
        self.assertFalse(self.button.is_pressed())  # Should be false now

    def test_custom_debounce_time(self) -> None:
        """Test button with custom debounce time"""
        button = self.DebouncedButton(pin_num=11, debounce_ms=100)
        self.assertEqual(button.debounce_ms, 100)

        # Press button
        button.pin._value = 0  # noqa: SLF001

        # First update - detects state change
        button.update()
        self.assertFalse(button.is_pressed())

        # Advance time less than debounce period
        self.current_ticks[0] += 60  # Only 60ms
        button.update()

        # Should not trigger yet (need 100ms)
        self.assertFalse(button.is_pressed())

        # Advance time more to exceed debounce period
        self.current_ticks[0] += 50  # Total 110ms
        button.update()
        self.assertTrue(button.is_pressed())


class TestCalculatorAppIntegration(unittest.TestCase):
    """Integration tests for CalculatorApp"""

    def setUp(self) -> None:
        """Set up test fixtures with all necessary mocks"""
        # Mock all hardware-related modules
        self.pin_patcher: Any = patch('main.Pin', MockPin)
        self.pin_patcher.start()

        # Mock MicroPython time functions
        self.time_patcher: Any = patch('main.time')
        self.mock_time: Any = self.time_patcher.start()
        self.current_ticks: List[int] = [0]
        self.mock_time.ticks_ms = lambda: self.current_ticks[0]
        self.mock_time.ticks_diff = lambda a, b: a - b
        self.mock_time.sleep_ms = lambda _ms: None

        # Mock the display
        self.display_patcher: Any = patch('main.LEDDisplay')
        self.mock_display_class: Any = self.display_patcher.start()
        self.mock_display: Mock = Mock()
        self.mock_display_class.return_value = self.mock_display

        # Mock the calculator
        self.calc_patcher: Any = patch('main.Calculator')
        self.mock_calc_class: Any = self.calc_patcher.start()
        self.mock_calc: Mock = Mock()
        self.mock_calc_class.return_value = self.mock_calc
        self.mock_calc.parse.return_value = "42"

    def tearDown(self) -> None:
        """Clean up patches"""
        self.pin_patcher.stop()
        self.time_patcher.stop()
        self.display_patcher.stop()
        self.calc_patcher.stop()

    def test_app_initialization(self) -> None:
        """Test CalculatorApp initializes correctly"""
        from main import CalculatorApp  # noqa: PLC0415

        with patch('builtins.print'):  # Suppress print output
            app = CalculatorApp()

        # Check app was created
        self.assertIsNotNone(app)

        # Check display was initialized
        self.mock_display_class.assert_called_once()
        self.mock_display.begin.assert_called_once()
        self.mock_display.set_color.assert_called()

        # Check calculator was initialized
        self.mock_calc_class.assert_called_once()
        self.mock_calc.begin.assert_called_once()

    def test_process_key(self) -> None:
        """Test processing a key press"""
        from main import CalculatorApp  # noqa: PLC0415

        with patch('builtins.print'):
            app = CalculatorApp()

        # Process a key
        app.process_key('5')

        # Should call calculator parse
        self.mock_calc.parse.assert_called_with('5')

        # Should update display
        self.mock_display.print_display.assert_called()

    def test_multiple_buttons_initialized(self) -> None:
        """Test that all buttons are initialized from config"""
        from main import CalculatorApp  # noqa: PLC0415

        with patch('builtins.print'):
            app = CalculatorApp()

        # Should have buttons for all configured pins
        self.assertGreater(len(app.buttons), 0)

        # Each button should be a tuple of (button, char)
        for _button, char in app.buttons:
            self.assertIsInstance(char, str)


class TestCalculatorAppProcessing(unittest.TestCase):
    """Test CalculatorApp key processing logic"""

    def setUp(self) -> None:
        """Set up minimal mocks for testing process_key"""
        self.pin_patcher: Any = patch('main.Pin', MockPin)
        self.pin_patcher.start()

        self.display_patcher: Any = patch('main.LEDDisplay')
        self.mock_display_class: Any = self.display_patcher.start()
        self.mock_display: Mock = Mock()
        self.mock_display_class.return_value = self.mock_display

        # Don't mock Calculator - use real one
        from main import CalculatorApp  # noqa: PLC0415
        self.CalculatorApp: Any = CalculatorApp

    def tearDown(self) -> None:
        """Clean up patches"""
        self.pin_patcher.stop()
        self.display_patcher.stop()

    def test_process_digit_keys(self) -> None:
        """Test processing digit key presses"""
        with patch('builtins.print'):
            app = self.CalculatorApp()

        app.process_key('5')
        # Display should show the digit
        self.mock_display.print_display.assert_called()

        # Get the argument passed to print_display
        call_args = self.mock_display.print_display.call_args
        self.assertIn('5', call_args[0][0])

    def test_process_operation_keys(self) -> None:
        """Test processing operation key presses"""
        with patch('builtins.print'):
            app = self.CalculatorApp()

        app.process_key('5')
        app.process_key('+')
        app.process_key('3')
        app.process_key('=')

        # Should have called display multiple times
        self.assertGreater(self.mock_display.print_display.call_count, 3)

    def test_process_clear_key(self) -> None:
        """Test processing clear key"""
        with patch('builtins.print'):
            app = self.CalculatorApp()

        app.process_key('5')
        app.process_key('C')

        # Display should show 0 after clear
        last_call = self.mock_display.print_display.call_args[0][0]
        self.assertEqual(last_call, '0')


if __name__ == '__main__':
    unittest.main()
