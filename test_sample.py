#!/usr/bin/env python3

# Simple test file for the AI assistant

def hello_world():
    """A simple function that returns hello world message."""
    return "Hello, World!"

def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    print(hello_world())
    result = add_numbers(5, 3)
    print(f"5 + 3 = {result}")