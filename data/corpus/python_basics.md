# Python Basics Guide

## Introduction to Python

Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in web development, data science, artificial intelligence, and automation.

## Getting Started

### Installation

1. **Download Python**: Visit [python.org](https://python.org) and download the latest version
2. **Verify Installation**: Open terminal/command prompt and run:
   ```bash
   python --version
   # or
   python3 --version
   ```

### Your First Python Program

```python
print("Hello, World!")
```

## Basic Syntax

### Variables and Data Types

```python
# Numbers
age = 25
price = 19.99

# Strings
name = "John Doe"
message = 'Hello, World!'

# Booleans
is_active = True
is_completed = False

# Lists
fruits = ["apple", "banana", "orange"]

# Dictionaries
person = {"name": "John", "age": 30}
```

### Control Flow

#### If Statements

```python
age = 18
if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")
```

#### Loops

```python
# For loop
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4

# While loop
count = 0
while count < 5:
    print(count)
    count += 1
```

## Functions

### Defining Functions

```python
def greet(name):
    return f"Hello, {name}!"

# Using the function
message = greet("Alice")
print(message)  # Output: Hello, Alice!
```

### Function with Default Parameters

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Bob"))  # Output: Hello, Bob!
print(greet("Bob", "Hi"))  # Output: Hi, Bob!
```

## Working with Files

### Reading Files

```python
# Read entire file
with open("file.txt", "r") as file:
    content = file.read()

# Read line by line
with open("file.txt", "r") as file:
    for line in file:
        print(line.strip())
```

### Writing Files

```python
# Write to file
with open("output.txt", "w") as file:
    file.write("Hello, World!")

# Append to file
with open("output.txt", "a") as file:
    file.write("\nNew line")
```

## Error Handling

### Try-Except Blocks

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("This always executes")
```

## Common Libraries

### Standard Library

- **os**: Operating system interface
- **sys**: System-specific parameters
- **datetime**: Date and time handling
- **json**: JSON data processing
- **re**: Regular expressions

### Popular Third-Party Libraries

- **requests**: HTTP library
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **matplotlib**: Plotting library
- **flask**: Web framework

## Best Practices

1. **Use meaningful variable names**
2. **Write docstrings for functions**
3. **Follow PEP 8 style guide**
4. **Use virtual environments**
5. **Handle exceptions properly**
6. **Write unit tests**

## Virtual Environments

### Creating a Virtual Environment

```bash
# Create virtual environment
python -m venv myenv

# Activate on Windows
myenv\Scripts\activate

# Activate on macOS/Linux
source myenv/bin/activate

# Deactivate
deactivate
```

### Installing Packages

```bash
# Install package
pip install package_name

# Install from requirements file
pip install -r requirements.txt

# List installed packages
pip list
```

## Debugging

### Using print() for Debugging

```python
def calculate_area(length, width):
    print(f"Length: {length}, Width: {width}")  # Debug print
    area = length * width
    print(f"Area: {area}")  # Debug print
    return area
```

### Using pdb (Python Debugger)

```python
import pdb

def complex_function():
    x = 1
    y = 2
    pdb.set_trace()  # Debugger will stop here
    result = x + y
    return result
```

## Common Issues and Solutions

### Import Errors

```python
# If you get "ModuleNotFoundError"
# Make sure the module is installed:
pip install module_name

# Or check your Python path:
import sys
print(sys.path)
```

### Indentation Errors

```python
# Correct indentation (use spaces, not tabs)
def my_function():
    if True:
        print("This is correct")
    else:
        print("This is also correct")
```

### File Path Issues

```python
# Use os.path for cross-platform compatibility
import os
file_path = os.path.join("folder", "file.txt")

# Get current working directory
current_dir = os.getcwd()
```

## Resources for Learning

1. **Official Documentation**: [docs.python.org](https://docs.python.org)
2. **Python Tutorial**: [python.org/tutorial](https://docs.python.org/3/tutorial/)
3. **Real Python**: [realpython.com](https://realpython.com)
4. **Python for Everybody**: [py4e.com](https://py4e.com)

## Next Steps

After mastering the basics:

1. Learn object-oriented programming
2. Explore web frameworks (Flask, Django)
3. Study data science libraries
4. Practice with real projects
5. Contribute to open source
