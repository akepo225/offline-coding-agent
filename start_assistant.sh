#!/bin/bash
# Convenience script to start the Working AI Assistant

# Activate virtual environment with error checking
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment activation script not found at venv/bin/activate"
    echo "Please ensure the virtual environment is properly set up."
    exit 1
fi

source venv/bin/activate

# Check if virtual environment is actually activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Virtual environment was not activated"
    echo "Please check that the virtual environment is properly configured."
    exit 1
fi

# Run the assistant with the downloaded model
python working_assistant.py \
  --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf \
  --config config/default.yaml \
  "$@"
