# Installation Guide

## Current Status: Proof of Concept

This is a **proof-of-concept implementation** of the Offline Coding Agent. The CLI framework and configuration system are complete, but model integration is still in development.

## System Requirements

- **OS**: Windows 10/11 (primary target)
- **Python**: 3.8 or higher
- **RAM**: 32GB (for optimal performance)
- **Storage**: 5GB free space

## Quick Start (Proof of Concept)

### 1. Clone or Download
```bash
git clone <repository-url>
cd offline_coder
```

### 2. Install Dependencies
```bash
# For reproducible installs, use constraints.txt
pip install -r requirements.txt -c constraints.txt
# For offline installs, use: pip install --no-index --find-links . -r requirements.txt -c constraints.txt
```

### 3. Test the CLI
```bash
python src/cli.py status
```

### 4. Initialize Workspace
```bash
python src/cli.py init
```

### 5. Try Commands
```bash
# Explain code
python src/cli.py explain --file test_example.py

# Generate code (placeholder)
python src/cli.py gen --file new_script.py --language python
```

## Available Commands (PoC)

### Status Check
```bash
python src/cli.py status
```
Shows current configuration and model status.

### Workspace Initialization
```bash
python src/cli.py init --directory ./src
```
Scans directory for relevant files and sets up cache.

### Code Explanation
```bash
python src/cli.py explain --file path/to/code.py
```
Explains what the code does (placeholder implementation).

### Code Generation
```bash
python src/cli.py gen --file new_file.py --language python
```
Generates code (placeholder implementation).

## Configuration

The configuration file is located at `config/default.yaml`. You can customize:

- Model settings
- File extensions to include
- Cache directories
- Output formatting

## Next Steps (Full Implementation)

To complete the project:

1. **Model Download**: Download DeepSeek-Coder-1.3B GGUF file
2. **Model Integration**: Implement llama.cpp integration
3. **Prompt Engineering**: Develop effective prompt templates
4. **Context Management**: Implement file awareness and caching
5. **Performance Optimization**: Tune for CPU inference

## Troubleshooting

### Common Issues

1. **Module not found errors**: Ensure you're running from the project root
2. **Configuration errors**: Check that `config/default.yaml` exists
3. **Permission errors**: Run with appropriate permissions

### Getting Help

```bash
python src/cli.py --help
```

## Development Setup

For development and testing:

```bash
# Install in development mode
pip install -e .

# Run tests (when available)
pytest tests/

# Code formatting
black src/
flake8 src/
```

## Windows Integration

### VS Code Terminal
1. Open VS Code
2. Open integrated terminal (Ctrl+`)
3. Navigate to project directory
4. Run commands as shown above

### Command Prompt/Powershell
Add the project directory to your PATH for easier access.

## Future Features

- **Model Management**: Automatic model download and updates
- **Advanced Context**: Multi-file project understanding
- **Code Refactoring**: Intelligent code transformations
- **Debug Assistance**: Error analysis and suggestions
- **Performance Tuning**: Adaptive response optimization