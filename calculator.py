"""
Calculator Logic Module
MicroPython version - simplified without BigNumber library
"""

from typing import Optional, Union


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

    def parse(self, in_byte: str) -> str:
        """
        Parse a character input and update calculator state

        Args:
            in_byte: Character input (digit, operator, or command)

        Returns:
            String to display
        """
        # Handle operators
        if in_byte in ['+', '-', '*', '/']:
            self.operation_char = in_byte
            self.last_key_was_operation = True
            self.num_str0 = self.display_str
            print(f"Detected operationChar = \"{self.operation_char}\"")

        # Handle equals
        elif in_byte == '=':
            print("Equal detected")

            if not self.no_new_number_since_last_calc:
                self.num_str1 = self.display_str

            self.no_new_number_since_last_calc = True
            self.display_str = "0"

            did_calculation: bool = False
            result: float = 0

            try:
                num0: float = float(self.num_str0)
                num1: float = float(self.num_str1)

                if self.operation_char == '+':
                    print("Adding")
                    result = num0 + num1
                    did_calculation = True

                elif self.operation_char == '-':
                    print("Subtracting")
                    result = num0 - num1
                    did_calculation = True

                elif self.operation_char == '*':
                    print("Multiplying")
                    result = num0 * num1
                    did_calculation = True

                elif self.operation_char == '/':
                    print("Dividing")
                    if num1 != 0:
                        result = num0 / num1
                        did_calculation = True
                    else:
                        self.display_str = "Error"
                        return self.display_str

            except (ValueError, ZeroDivisionError) as e:
                print(f"Calculation error: {e}")
                self.display_str = "Error"
                return self.display_str

            if did_calculation:
                self.num_str0 = self._format_number(result)
                self.display_str = self.num_str0

        # Handle backspace
        elif in_byte == 'b':
            print("Detected Backspace")
            if len(self.display_str) > 1:
                self.display_str = self.display_str[:-1]
            else:
                self.display_str = "0"

        # Handle clear entry
        elif in_byte == 'c':
            print("Detected Clear Entry")
            self.display_str = "0"

        # Handle clear all
        elif in_byte == 'C':
            print("Detected Clear All")
            self.display_str = "0"
            self.num_str0 = "0"
            self.num_str1 = "0"
            self.last_key_was_operation = False
            self.operation_char = None
            self.no_new_number_since_last_calc = False

        # Handle negative toggle
        elif in_byte == 'n':
            print("Detected negate")
            if self.display_str == "0":
                self.display_str = "-"
            elif self.display_str.startswith('-'):
                self.display_str = self.display_str[1:]
            else:
                self.display_str = '-' + self.display_str

        # Handle decimal point
        elif in_byte == '.':
            if self.last_key_was_operation:
                self.display_str = "0."
                self.last_key_was_operation = False
            elif self.no_new_number_since_last_calc:
                self.display_str = "0."
                self.no_new_number_since_last_calc = False
            elif '.' not in self.display_str:
                self.display_str += '.'

        # Handle digits
        elif in_byte.isdigit():
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

        # Debug output
        print(f"displayStr=\"{self.display_str}\", numStr0=\"{self.num_str0}\", "
              f"numStr1=\"{self.num_str1}\", operationChar=\"{self.operation_char}\", "
              f"lastKeyWasOp=\"{self.last_key_was_operation}\"")

        return self.display_str
