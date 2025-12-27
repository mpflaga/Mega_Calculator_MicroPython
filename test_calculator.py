"""
Unit tests for Calculator module
Tests all calculator operations and edge cases
"""

import unittest
from calculator import Calculator


class TestCalculator(unittest.TestCase):
    """Test cases for Calculator class"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.calc: Calculator = Calculator(display_size=9)
        self.calc.begin()

    def test_initialization(self) -> None:
        """Test calculator initializes with correct default values"""
        self.assertEqual(self.calc.display_str, "0")
        self.assertEqual(self.calc.num_str0, "0")
        self.assertEqual(self.calc.num_str1, "0")
        self.assertFalse(self.calc.last_key_was_operation)
        self.assertIsNone(self.calc.operation_char)
        self.assertFalse(self.calc.no_new_number_since_last_calc)

    def test_digit_entry(self) -> None:
        """Test entering single and multiple digits"""
        result = self.calc.parse('5')
        self.assertEqual(result, '5')

        result = self.calc.parse('3')
        self.assertEqual(result, '53')

        result = self.calc.parse('7')
        self.assertEqual(result, '537')

    def test_digit_entry_from_zero(self) -> None:
        """Test that entering digit from 0 replaces the 0"""
        self.assertEqual(self.calc.display_str, "0")
        result = self.calc.parse('8')
        self.assertEqual(result, '8')

    def test_max_digit_limit(self) -> None:
        """Test that display respects max digit limit"""
        # Enter 9 digits (max for display_size=9)
        for digit in '123456789':
            self.calc.parse(digit)

        self.assertEqual(self.calc.display_str, '123456789')

        # Try to add one more digit - should be ignored
        result = self.calc.parse('0')
        self.assertEqual(result, '123456789')

    def test_addition(self) -> None:
        """Test basic addition operation"""
        self.calc.parse('5')
        self.calc.parse('+')
        self.calc.parse('3')
        result = self.calc.parse('=')
        self.assertEqual(result, '8')

    def test_subtraction(self) -> None:
        """Test basic subtraction operation"""
        self.calc.parse('9')
        self.calc.parse('-')
        self.calc.parse('4')
        result = self.calc.parse('=')
        self.assertEqual(result, '5')

    def test_multiplication(self) -> None:
        """Test basic multiplication operation"""
        self.calc.parse('6')
        self.calc.parse('*')
        self.calc.parse('7')
        result = self.calc.parse('=')
        self.assertEqual(result, '42')

    def test_division(self) -> None:
        """Test basic division operation"""
        self.calc.parse('8')
        self.calc.parse('/')
        self.calc.parse('2')
        result = self.calc.parse('=')
        self.assertEqual(result, '4')

    def test_division_by_zero(self) -> None:
        """Test division by zero returns Error"""
        self.calc.parse('5')
        self.calc.parse('/')
        self.calc.parse('0')
        result = self.calc.parse('=')
        self.assertEqual(result, 'Error')

    def test_decimal_point(self) -> None:
        """Test decimal point entry"""
        self.calc.parse('3')
        self.calc.parse('.')
        self.calc.parse('1')
        self.calc.parse('4')
        self.assertEqual(self.calc.display_str, '3.14')

    def test_multiple_decimal_points_ignored(self) -> None:
        """Test that only one decimal point is allowed"""
        self.calc.parse('3')
        self.calc.parse('.')
        self.calc.parse('1')
        self.calc.parse('.')  # Second decimal point should be ignored
        self.calc.parse('4')
        self.assertEqual(self.calc.display_str, '3.14')

    def test_decimal_from_zero(self) -> None:
        """Test entering decimal point from initial zero state"""
        result = self.calc.parse('.')
        self.assertEqual(result, '0.')

    def test_decimal_after_operation(self) -> None:
        """Test entering decimal point after an operation"""
        self.calc.parse('5')
        self.calc.parse('+')
        result = self.calc.parse('.')
        self.assertEqual(result, '0.')

    def test_backspace(self) -> None:
        """Test backspace functionality"""
        self.calc.parse('1')
        self.calc.parse('2')
        self.calc.parse('3')
        result = self.calc.parse('b')
        self.assertEqual(result, '12')

        result = self.calc.parse('b')
        self.assertEqual(result, '1')

        result = self.calc.parse('b')
        self.assertEqual(result, '0')

    def test_clear_entry(self) -> None:
        """Test clear entry (c) clears display only"""
        self.calc.parse('1')
        self.calc.parse('2')
        self.calc.parse('3')
        result = self.calc.parse('c')
        self.assertEqual(result, '0')

    def test_clear_all(self) -> None:
        """Test clear all (C) resets calculator state"""
        self.calc.parse('5')
        self.calc.parse('+')
        self.calc.parse('3')
        result = self.calc.parse('C')

        self.assertEqual(result, '0')
        self.assertEqual(self.calc.num_str0, '0')
        self.assertEqual(self.calc.num_str1, '0')
        self.assertFalse(self.calc.last_key_was_operation)
        self.assertIsNone(self.calc.operation_char)

    def test_negate(self) -> None:
        """Test negation toggle"""
        self.calc.parse('5')
        result = self.calc.parse('n')
        self.assertEqual(result, '-5')

        result = self.calc.parse('n')
        self.assertEqual(result, '5')

    def test_negate_from_zero(self) -> None:
        """Test negation from zero creates minus sign"""
        result = self.calc.parse('n')
        self.assertEqual(result, '-')

    def test_operation_clears_display_for_next_number(self) -> None:
        """Test that entering digit after operation starts new number"""
        self.calc.parse('5')
        self.calc.parse('+')
        result = self.calc.parse('3')
        self.assertEqual(result, '3')

    def test_repeated_equals(self) -> None:
        """Test repeated equals repeats last operation"""
        self.calc.parse('5')
        self.calc.parse('+')
        self.calc.parse('3')
        result = self.calc.parse('=')
        self.assertEqual(result, '8')

        # Press equals again - should add 3 again
        result = self.calc.parse('=')
        self.assertEqual(result, '11')

    def test_chain_operations(self) -> None:
        """Test chaining multiple operations"""
        self.calc.parse('2')
        self.calc.parse('+')
        self.calc.parse('3')
        self.calc.parse('*')  # Changes operation to *, keeps 3 as first number
        self.calc.parse('4')
        result = self.calc.parse('=')
        # Calculator uses last operation and doesn't respect precedence
        # So this becomes 3 * 4 = 12 (not (2+3)*4=20 or 2+(3*4)=14)
        self.assertEqual(result, '12')

    def test_decimal_arithmetic(self) -> None:
        """Test arithmetic with decimal numbers"""
        self.calc.parse('2')
        self.calc.parse('.')
        self.calc.parse('5')
        self.calc.parse('+')
        self.calc.parse('1')
        self.calc.parse('.')
        self.calc.parse('5')
        result = self.calc.parse('=')
        self.assertEqual(result, '4')

    def test_negative_number_arithmetic(self) -> None:
        """Test arithmetic with negative numbers"""
        self.calc.parse('n')  # Start with negative
        self.calc.parse('5')
        self.calc.parse('+')
        self.calc.parse('1')
        self.calc.parse('0')
        result = self.calc.parse('=')
        self.assertEqual(result, '5')

    def test_format_number_removes_trailing_zeros(self) -> None:
        """Test that number formatting removes trailing zeros"""
        formatted = self.calc._format_number(5.0)  # noqa: SLF001
        self.assertEqual(formatted, '5')

        formatted = self.calc._format_number(3.14000)  # noqa: SLF001
        self.assertEqual(formatted, '3.14')

    def test_format_number_handles_strings(self) -> None:
        """Test that format_number can handle string input"""
        formatted = self.calc._format_number("42.5")  # noqa: SLF001
        self.assertEqual(formatted, '42.5')

    def test_format_number_handles_invalid_strings(self) -> None:
        """Test that format_number returns 0 for invalid strings"""
        formatted = self.calc._format_number("invalid")  # noqa: SLF001
        self.assertEqual(formatted, '0')

    def test_long_number_truncation(self) -> None:
        """Test that very long results are truncated"""
        # Create a division that results in many decimal places
        self.calc.parse('1')
        self.calc.parse('/')
        self.calc.parse('3')
        result = self.calc.parse('=')
        # Should be truncated to fit display
        self.assertLessEqual(len(result.replace('.', '').replace('-', '')),
                           self.calc.display_size + 5)  # Allow for scientific notation

    def test_format_number_removes_leading_zeros_from_result(self) -> None:
        """Test that format_number properly handles leading zeros in results"""
        # Note: The calculator doesn't store leading zeros in parsed input,
        # but results might have them
        formatted = self.calc._format_number(0.5)  # noqa: SLF001
        # Should be "0.5", not ".5"
        self.assertTrue(formatted.startswith('0.') or not formatted.startswith('.'))

    def test_trailing_zeros_removed_from_decimal_results(self) -> None:
        """Test trailing zeros are removed from decimal calculation results"""
        self.calc.parse('1')
        self.calc.parse('0')
        self.calc.parse('/')
        self.calc.parse('2')
        result = self.calc.parse('=')
        # 10 / 2 = 5.0, should display as "5" not "5.0"
        self.assertEqual(result, '5')


class TestCalculatorEdgeCases(unittest.TestCase):
    """Test edge cases and unusual inputs"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.calc: Calculator = Calculator(display_size=9)
        self.calc.begin()

    def test_operation_without_second_number(self) -> None:
        """Test pressing equals after operation without entering second number"""
        self.calc.parse('5')
        self.calc.parse('+')
        result = self.calc.parse('=')
        # Calculator repeats the first number: 5 + 5 = 10
        self.assertEqual(result, '10')

    def test_multiple_operations_in_sequence(self) -> None:
        """Test entering multiple operation keys in sequence"""
        self.calc.parse('5')
        self.calc.parse('+')
        self.calc.parse('-')  # Change operation
        self.calc.parse('3')
        result = self.calc.parse('=')
        # Should use last operation (subtraction): 5 - 3 = 2
        self.assertEqual(result, '2')

    def test_begin_resets_calculator(self) -> None:
        """Test that begin() resets all state"""
        self.calc.parse('5')
        self.calc.parse('+')
        self.calc.parse('3')

        self.calc.begin()

        self.assertEqual(self.calc.display_str, "0")
        self.assertEqual(self.calc.num_str0, "0")
        self.assertEqual(self.calc.num_str1, "0")

    def test_unknown_characters_ignored(self) -> None:
        """Test that unknown characters don't crash the calculator"""
        self.calc.parse('5')
        self.calc.parse('x')  # Unknown character
        # Should not crash and display should remain
        self.assertEqual(self.calc.display_str, '5')


if __name__ == '__main__':
    unittest.main()
