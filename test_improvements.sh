#!/bin/bash
# Test script for working_assistant.py improvements

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Testing Improved working_assistant.py"
echo "=========================================="
echo "Project root: $PROJECT_ROOT"
echo ""

# Clean up previous test output
rm -f "$PROJECT_ROOT/tests/TEST_RESULTS_SUMMARY.md" 2>/dev/null

# Test the same prompt that showed issues
echo "Running test prompt..."
echo "Prompt: 'read tests/TEST_RESULTS.md and give me a short summary in a file in the same folder'"
echo ""

# Change to project directory with error checking
cd "$PROJECT_ROOT" || {
    echo "Error: Failed to change to project directory: $PROJECT_ROOT"
    exit 1
}

# Activate venv with error checking
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment activation script not found at venv/bin/activate"
    exit 1
fi

source venv/bin/activate || {
    echo "Error: Failed to activate virtual environment"
    exit 1
}

# Run the assistant
python3 working_assistant.py \
  --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf \
  --prompt "read 'tests/TEST_RESULTS.md' and give me a short summary in a file in the same folder" \
  --auto-confirm

echo ""
echo "=========================================="
echo "Test Complete - Checking Results"
echo "=========================================="
echo ""

# Check if output file was created
if [ -f "$PROJECT_ROOT/tests/TEST_RESULTS_SUMMARY.md" ]; then
    echo "✅ Output file created: TEST_RESULTS_SUMMARY.md"
    echo ""
    echo "--- File Contents ---"
    cat "$PROJECT_ROOT/tests/TEST_RESULTS_SUMMARY.md"
    echo ""
    echo "--- End of File ---"
    echo ""

    # Check for escaped newlines
    if grep -q '\\n' "$PROJECT_ROOT/tests/TEST_RESULTS_SUMMARY.md"; then
        echo "⚠️  WARNING: Found escaped newlines (\\n) in output"
    else
        echo "✅ No escaped newlines detected"
    fi

    # Check file size
    SIZE=$(wc -c < "$PROJECT_ROOT/tests/TEST_RESULTS_SUMMARY.md")
    echo "📊 File size: $SIZE bytes"
    if [ $SIZE -lt 100 ]; then
        echo "⚠️  WARNING: File is suspiciously small (< 100 bytes)"
    else
        echo "✅ File size looks good"
    fi
else
    echo "❌ Output file NOT created"
fi

echo ""
echo "=========================================="
echo "Manual Review Required:"
echo "=========================================="
echo "1. Check console output above for tool count"
echo "2. Count how many times 'read_file' was called"
echo "3. Count how many times 'write_file' was called"
echo "4. Expected: 1 read + 1 write = 2 tools total"
echo "5. Previous: 2 reads + 2 writes = 4 tools total"
