"""
Serial Console Calculator
A version that runs purely through serial console without hardware buttons or LED display
Perfect for testing the calculator logic without physical hardware
"""

from calculator import Calculator


def main() -> None:
    """Run calculator in serial console mode"""
    print("=" * 60)
    print("MicroPython Calculator - Serial Console Mode")
    print("=" * 60)
    print("\nThis mode simulates the calculator using only serial input/output")
    print("No physical buttons or LED display required.\n")

    calc = Calculator(display_size=9)
    calc.begin()

    print("Available commands:")
    print("  Digits: 0-9")
    print("  Operations: + - * /")
    print("  Functions: = (equals), . (decimal point)")
    print("             n (negate), c (clear entry), C (clear all)")
    print("             b (backspace)")
    print("  Control: q or quit (exit)")
    print("\nCurrent display: 0")
    print("-" * 60)

    try:
        while True:
            # Read input from console
            try:
                user_input = input("\nEnter key: ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            # Check for exit commands
            if user_input.lower() in ('q', 'quit', 'exit'):
                print("\nExiting calculator...")
                break

            # Process each character
            for char in user_input:
                result = calc.parse(char)
                print(f"Key: '{char}' -> Display: \"{result}\"")

    except KeyboardInterrupt:
        print("\n\nCalculator stopped by user")

    print("\nThank you for using the calculator!")


if __name__ == "__main__":
    main()
