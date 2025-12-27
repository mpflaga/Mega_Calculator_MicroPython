"""
MicroPython Calculator Main Program
Refactored from Arduino Mega Calculator

Author: Michael Flaga
Refactored to MicroPython
"""

import sys
import select
import time
from typing import List, Tuple
from machine import Pin

# Compatibility for standard Python vs MicroPython
try:
    # MicroPython has sys.print_exception
    _print_exception = sys.print_exception  # type: ignore[attr-defined]
except AttributeError:
    # Standard Python uses traceback module
    import traceback

    def _print_exception(e):
        traceback.print_exception(type(e), e, e.__traceback__)
from config import (
    DISPLAY_SIZE, LED_PIN, LEDS_PER_DIGIT, BUTTON_PINS,
    DEBOUNCE_MS, DEFAULT_BRIGHTNESS, DEFAULT_COLOR, TEST_COLOR_WHITE
)
from led_display import LEDDisplay
from calculator import Calculator


class DebouncedButton:
    """Simple debounced button class"""

    def __init__(self, pin_num: int, debounce_ms: int = 50) -> None:
        """
        Initialize debounced button

        Args:
            pin_num: GPIO pin number
            debounce_ms: Debounce time in milliseconds
        """
        self.pin: Pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.debounce_ms: int = debounce_ms
        self.last_state: int = self.pin.value()
        self.current_state: int = self.last_state
        self.last_change_time: int = time.ticks_ms()
        self.pressed: bool = False
        self.released: bool = False

    def update(self) -> None:
        """Update button state and handle debouncing"""
        self.pressed = False
        self.released = False

        current_reading: int = self.pin.value()
        current_time: int = time.ticks_ms()

        # Check if state changed
        if current_reading != self.last_state:
            self.last_change_time = current_time

        # Check if enough time has passed for debouncing
        if time.ticks_diff(current_time, self.last_change_time) > self.debounce_ms:
            # State is stable
            if current_reading != self.current_state:
                self.current_state = current_reading

                # Detect edges (buttons are active low with pull-up)
                if self.current_state == 0:  # Pressed (low)
                    self.pressed = True
                else:  # Released (high)
                    self.released = True

        self.last_state = current_reading

    def is_pressed(self) -> bool:
        """Check if button was just pressed"""
        return self.pressed

    def is_released(self) -> bool:
        """Check if button was just released"""
        return self.released


class CalculatorApp:
    """Main calculator application"""

    def __init__(self) -> None:
        """Initialize calculator application"""
        print("Mega Calculator is starting (MicroPython)")

        # Initialize LED display
        try:
            led_pin: Pin = Pin(LED_PIN, Pin.OUT)
            self.display: LEDDisplay = LEDDisplay(DISPLAY_SIZE, led_pin, LEDS_PER_DIGIT)
            self.display.begin(DEFAULT_BRIGHTNESS)
            self.display.set_color(*DEFAULT_COLOR)
        except (ValueError, OSError, AttributeError, ImportError) as e:
            print(f"Error initializing display: {e}")
            sys.exit(1)

        # Initialize calculator
        self.calculator: Calculator = Calculator(DISPLAY_SIZE)
        self.calculator.begin()

        # Run display test
        self.display.set_color(*TEST_COLOR_WHITE)
        self.display.print_test()

        # Set display color and show initial value
        self.display.set_color(*DEFAULT_COLOR)
        self.display.print_display("0")

        # Initialize buttons
        self.buttons: List[Tuple[DebouncedButton, str]] = []
        for pin_num, char in BUTTON_PINS:
            try:
                button: DebouncedButton = DebouncedButton(pin_num, DEBOUNCE_MS)
                self.buttons.append((button, char))
            except (ValueError, OSError, AttributeError) as e:
                print(f"Error initializing button on pin {pin_num}: {e}")

        print("Calculator initialization complete")

    def process_key(self, key_char: str) -> None:
        """
        Process a key press

        Args:
            key_char: Character representing the key pressed
        """
        print(f"Processing key: '{key_char}'")
        display_str: str = self.calculator.parse(key_char)
        print(f"Display: \"{display_str}\"")
        self.display.print_display(display_str)

    def run(self) -> None:
        """Main application loop"""
        print("Entering main loop...")

        while True:
            try:
                # Check all buttons
                for button, char in self.buttons:
                    button.update()

                    if button.is_pressed():
                        print(f"Button '{char}' pressed")
                        self.process_key(char)

                # Check for serial input (if available)
                # Note: sys.stdin.read() behavior may vary by MicroPython implementation
                # This is a simplified version - you may need to adapt for your board
                try:
                    result = select.select([sys.stdin], [], [], 0)
                    if result and sys.stdin in result[0]:
                        key: str = sys.stdin.read(1)
                        if key:
                            self.process_key(key)
                except (AttributeError, OSError, TypeError):
                    pass  # Serial input not available or not implemented

                # Small delay to prevent excessive CPU usage
                time.sleep_ms(10)

            except KeyboardInterrupt:
                print("\nCalculator stopped by user")
                self.display.clear()
                self.display.show()
                break
            except Exception as e:  # noqa: BLE001
                # Broad exception to keep calculator running despite errors
                print(f"Error in main loop: {e}")
                _print_exception(e)


def main() -> None:
    """Main entry point"""
    try:
        app: CalculatorApp = CalculatorApp()
        app.run()
    except Exception as e:  # noqa: BLE001
        # Catch-all for fatal errors at top level
        print(f"Fatal error: {e}")
        _print_exception(e)


if __name__ == "__main__":
    main()
