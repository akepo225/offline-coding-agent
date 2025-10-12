# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Offline Coding Agent** - a terminal-based AI coding assistant designed for restricted Windows business laptops with no admin rights. It combines Qwen2.5-Coder-8B with Aider to deliver professional-grade AI assistance completely offline.

## Common Development Commands

### Installation and Setup
```bash
# Install dependencies locally (no admin rights required)
pip install --user -r requirements.txt

# Install in development mode
pip install --user -e .

# Test installation
python test_example.py
```

### Running the Application
```bash
# Run CLI directly
python src/cli.py --help

# Using installed command (if available)
offline-coder --help

# Initialize workspace
python src/cli.py init

# Generate code for a file
python src/cli.py gen --file example.py

# Explain existing code
python src/cli.py explain --file example.py

# Check status
python src/cli.py status
```

### Testing
```bash
# Run basic test (currently just example)
python test_example.py

# No formal test suite exists yet - this is a development priority
```

## Architecture Overview

### Core Components
- **CLI Layer** (`src/cli.py`): Click-based command-line interface with gen, explain, init, and status commands
- **Configuration System** (`src/utils/config.py`): YAML-based configuration management with dot notation access
- **Output Formatting** (`src/utils/formatting.py`): Rich console output with syntax highlighting and structured formatting
- **Model Integration**: Designed for Qwen2.5-Coder-8B with llama.cpp (not yet implemented)

### Project Structure
```
src/
├── cli.py              # Main CLI entry point
├── utils/
│   ├── config.py       # Configuration management
│   └── formatting.py   # Output formatting
└── model/              # Model integration (placeholder)
config/
└── default.yaml        # Default configuration
docs/                   # Comprehensive documentation
scripts/                # Utility scripts (model download, etc.)
```

### Configuration System
- Uses YAML configuration files in `config/default.yaml`
- Supports dot notation for nested values (`model.name`, `cli.output_format`)
- Environment-aware paths for models and cache
- Validates required fields and model file existence

### Terminal-First Design
The project is specifically designed for terminal-only usage on restricted Windows environments:
- No VS Code extensions or GUI components
- Works with Command Prompt, PowerShell, and Git Bash
- Portable operation (can run from USB drive)
- User-level installation only (no admin rights required)

## Development Guidelines

### Current Implementation Status
- ✅ CLI framework with Click
- ✅ Configuration system with YAML
- ✅ Rich output formatting
- ✅ Basic project structure
- 🚧 Model integration (placeholder implementation)
- 🚧 Context management system
- 📋 Formal test suite
- 📋 Aider integration for terminal workflows

### Key Constraints
- Must work without admin rights on Windows
- Completely offline operation after initial setup
- Terminal-only interface (no GUI components)
- Optimized for 32GB RAM, 128MB VRAM environments

### Configuration Management
All configuration is handled through the `Config` class in `src/utils/config.py`:
- Default config location: `config/default.yaml`
- Use `config.get('key.path')` for nested access
- Model path resolution: `config.get_model_path()`
- Directory creation: `config.ensure_directories()`

### Output Formatting
Use the formatting utilities in `src/utils/formatting.py`:
- `print_error()`, `print_success()`, `print_info()`, `print_warning()`
- `format_response()` for model output
- `format_output()` for syntax-highlighted code blocks

## Model Integration (To Be Implemented)

The current codebase contains placeholder model integration. The intended architecture:
- **Model**: Qwen2.5-Coder-8B-Instruct (GGUF format, ~4.7GB)
- **Inference**: llama-cpp-python for CPU-optimized inference
- **Context**: 32K context window with intelligent file scanning
- **Workflow**: Integration with Aider for terminal-based AI assistance

### Model Integration Points
- Model loading in CLI commands (gen, explain)
- Context window management for large files
- Streaming response handling
- File type detection and language-specific prompting

## Testing Strategy

Currently minimal testing exists. Priority areas for test development:
1. Configuration loading and validation
2. CLI command argument parsing
3. File scanning and language detection
4. Model integration (when implemented)
5. Output formatting and display

## Documentation

Comprehensive documentation exists in the `docs/` directory:
- `technical_architecture.md` - Detailed system architecture
- `implementation_guide.md` - Setup and usage instructions
- `model_evaluation.md` - Model selection research
- `concept.md` - Project goals and constraints

Refer to these documents for detailed implementation guidance and project context.