# Tests Directory

This directory contains test files and test results for the Offline Coding Agent.

## Contents

- `test_*.py` - Unit and integration tests
- `TEST_RESULTS.md` - Test execution results and summaries
- Test data and fixtures

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
python tests/test_aider.py
```

## Test Coverage

Tests cover:
- Tool execution (read_file, write_file, execute_python, etc.)
- Argument parsing
- Model integration
- CLI functionality
