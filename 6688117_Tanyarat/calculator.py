"""
Simple calculator that supports basic arithmetic operations:
add, subtract, multiply, and divide.
"""


def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    return a - b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def divide(a, b):
    """Divide a by b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def main():
    """Main function to run the calculator interactively."""
    print("=== Simple Calculator ===")
    print("Operations: add, subtract, multiply, divide")
    
    while True:
        print("\nEnter operation (add, subtract, multiply, divide) or 'quit' to exit:")
        operation = input().strip().lower()
        
        if operation == 'quit':
            print("Goodbye!")
            break
        
        if operation not in ['add', 'subtract', 'multiply', 'divide']:
            print("Invalid operation. Please choose: add, subtract, multiply, or divide")
            continue
        
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
            
            if operation == 'add':
                result = add(num1, num2)
                print(f"{num1} + {num2} = {result}")
            elif operation == 'subtract':
                result = subtract(num1, num2)
                print(f"{num1} - {num2} = {result}")
            elif operation == 'multiply':
                result = multiply(num1, num2)
                print(f"{num1} * {num2} = {result}")
            elif operation == 'divide':
                result = divide(num1, num2)
                print(f"{num1} / {num2} = {result}")
        
        except ValueError as e:
            print(f"Error: {e}")
        except ValueError:
            print("Error: Please enter valid numbers")


if __name__ == "__main__":
    main()
