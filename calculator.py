"""
Calculator Logic Module
MicroPython version - simplified without BigNumber library
"""

from __future__ import annotations

try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from typing import Optional, Union
except ImportError:
    # MicroPython doesn't have typing module
    TYPE_CHECKING = False


class Calculator:
    """Standard 9-digit calculator with decimal points"""

    def __init__(self, display_size: int) -> None:
        """
        Initialize calculator

        Args:
            display_size: Maximum number of digits in display
        """
        self.display_size: int = display_size
        self.last_key_was_operation: bool = False
        self.operation_char: Optional[str] = None
        self.no_new_number_since_last_calc: bool = False
        self.display_str: str = "0"
        self.num_str0: str = "0"
        self.num_str1: str = "0"

    def begin(self) -> None:
        """Initialize the calculator state"""
        self.display_str = "0"
        self.num_str0 = "0"
        self.num_str1 = "0"
        self.last_key_was_operation = False
        self.operation_char = None
        self.no_new_number_since_last_calc = False

    def _format_number(self, value: Union[float, str]) -> str:
        """
        Format a number to fit display size

        Args:
            value: Float or string number to format

        Returns:
            String representation of the number
        """
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return "0"

        # Format with appropriate precision
        result = str(value)

        # Remove trailing zeros after decimal point
        if '.' in result:
            result = result.rstrip('0').rstrip('.')

        # Limit to display size
        if len(result) > self.display_size + 1:  # +1 for decimal point
            # Try scientific notation or truncate
            result = f"{value:.{self.display_size-5}e}"
            if len(result) > self.display_size + 1:
                result = result[:self.display_size + 1]

        return result if result else "0"

    def _handle_operator(self, in_byte: str) -> None:
        """Handle arithmetic operators (+, -, *, /)"""
        self.operation_char = in_byte
        self.last_key_was_operation = True
        self.num_str0 = self.display_str
        print(f"Detected operationChar = \"{self.operation_char}\"")

    def _handle_equals(self) -> None:
        """Handle equals operation and perform calculation"""
        print("Equal detected")

        if not self.no_new_number_since_last_calc:
            self.num_str1 = self.display_str

        self.no_new_number_since_last_calc = True
        self.display_str = "0"

        # Dispatcher table for arithmetic operations
        operations = {
            '+': (lambda a, b: a + b, "Adding"),
            '-': (lambda a, b: a - b, "Subtracting"),
            '*': (lambda a, b: a * b, "Multiplying"),
            '/': (lambda a, b: a / b if b != 0 else None, "Dividing")
        }

        try:
            num0: float = float(self.num_str0)
            num1: float = float(self.num_str1)

            if self.operation_char in operations:
                op_func, op_name = operations[self.operation_char]
                print(op_name)
                result = op_func(num0, num1)

                if result is None:  # Division by zero
                    self.display_str = "Error"
                else:
                    self.num_str0 = self._format_number(result)
                    self.display_str = self.num_str0

        except (ValueError, ZeroDivisionError) as e:
            print(f"Calculation error: {e}")
            self.display_str = "Error"

    def _handle_backspace(self) -> None:
        """Handle backspace operation"""
        print("Detected Backspace")
        if len(self.display_str) > 1:
            self.display_str = self.display_str[:-1]
        else:
            self.display_str = "0"

    def _handle_clear_entry(self) -> None:
        """Handle clear entry operation"""
        print("Detected Clear Entry")
        self.display_str = "0"

    def _handle_clear_all(self) -> None:
        """Handle clear all operation"""
        print("Detected Clear All")
        self.display_str = "0"
        self.num_str0 = "0"
        self.num_str1 = "0"
        self.last_key_was_operation = False
        self.operation_char = None
        self.no_new_number_since_last_calc = False

    def _handle_negate(self) -> None:
        """Handle negative toggle operation"""
        print("Detected negate")
        if self.display_str == "0":
            self.display_str = "-"
        elif self.display_str.startswith('-'):
            self.display_str = self.display_str[1:]
        else:
            self.display_str = '-' + self.display_str

    def _handle_decimal(self) -> None:
        """Handle decimal point input"""
        if self.last_key_was_operation:
            self.display_str = "0."
            self.last_key_was_operation = False
        elif self.no_new_number_since_last_calc:
            self.display_str = "0."
            self.no_new_number_since_last_calc = False
        elif '.' not in self.display_str:
            self.display_str += '.'

    def _handle_digit(self, in_byte: str) -> None:
        """Handle digit input (0-9)"""
        print("Sensed a digit")

        # Clear display if last key was an operation
        if self.last_key_was_operation:
            print("Clearing prior work from display")
            self.display_str = "0"
            self.last_key_was_operation = False

        # Clear display if showing previous result
        if self.no_new_number_since_last_calc:
            print("Clearing prior resultant from display")
            self.display_str = "0"
            self.no_new_number_since_last_calc = False

        # Check if there's room to add the digit
        current_len: int = len(self.display_str.replace('.', '').replace('-', ''))
        if current_len < self.display_size:
            if self.display_str == "0":
                self.display_str = in_byte
            else:
                self.display_str += in_byte

    def parse(self, in_byte: str) -> str:
        """
        Parse a character input and update calculator state

        Args:
            in_byte: Character input (digit, operator, or command)

        Returns:
            String to display
        """
        # Dispatcher table mapping input characters to handler methods
        dispatch_table = {
            '+': lambda: self._handle_operator(in_byte),
            '-': lambda: self._handle_operator(in_byte),
            '*': lambda: self._handle_operator(in_byte),
            '/': lambda: self._handle_operator(in_byte),
            '=': self._handle_equals,
            'b': self._handle_backspace,
            'c': self._handle_clear_entry,
            'C': self._handle_clear_all,
            'n': self._handle_negate,
            '.': self._handle_decimal,
        }

        # Check if input is in dispatch table
        if in_byte in dispatch_table:
            dispatch_table[in_byte]()
        # Check if input is a digit
        elif in_byte.isdigit():
            self._handle_digit(in_byte)

        # Debug output
        print(f"displayStr=\"{self.display_str}\", numStr0=\"{self.num_str0}\", "
              f"numStr1=\"{self.num_str1}\", operationChar=\"{self.operation_char}\", "
              f"lastKeyWasOp=\"{self.last_key_was_operation}\"")

        return self.display_str
