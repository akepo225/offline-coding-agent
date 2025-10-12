# Technical Architecture - Offline Coding Agent

## Core Technology Stack

### Inference Engine: llama.cpp
- **Framework**: llama.cpp (CPU-optimized)
- **Model Format**: GGUF (4-bit quantized)
- **Python Integration**: llama-cpp-python
- **Platform**: Windows native binary support

### Model: Qwen2.5-Coder-8B
- **File Size**: ~4.7GB (Q4_K_M quantized)
- **Memory Usage**: ~8GB RAM
- **Inference**: CPU-only (perfect for 128MB VRAM constraint)
- **Performance**: Professional-grade code generation with 32K context window

### CLI Framework
- **Language**: Python 3.8+
- **CLI Library**: argparse or click
- **Output Formatting**: rich or textual
- **Configuration**: YAML/JSON files

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Codegen   │  │   Explain   │  │     Debug       │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                Context Manager                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │File Scanner │  │   Cache     │  │  Project State  │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│              Model Engine (llama.cpp)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Model     │  │  Prompt     │  │   Generation    │  │
│  │   Loader    │  │  Builder    │  │   Engine        │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                Storage Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Model     │  │   Config    │  │    Cache DB     │  │
│  │   Files     │  │   Files     │  │   (SQLite)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## CLI Command Structure

### Main Commands
```bash
offline-coder <command> [options] [files...]

# Core Commands
offline-coder gen --file "app.py" --language python    # Code generation
offline-coder explain --file "utils.py"                # Code explanation
offline-coder debug --file "main.py" --error "TypeError" # Debug assistance
offline-coder complete --file "script.js" --line 25     # Code completion

# Context Management
offline-coder scan --directory ./src                    # Scan project
offline-coder context --show                            # Show current context
offline-coder clear                                    # Clear context

# Configuration
offline-coder config --show                           # Show config
offline-coder init                                    # Initialize workspace
```

### Command Options
- `--model <path>`: Specify model file path
- `--threads <n>`: Number of CPU threads (default: auto-detect)
- `--context <n>`: Context window size
- `--format <json|text>`: Output format
- `--verbose`: Verbose output
- `--config <file>`: Configuration file

## Project Structure

```
offline-coder/
├── src/
│   ├── __init__.py
│   ├── cli.py                 # Main CLI entry point
│   ├── commands/              # Command implementations
│   │   ├── __init__.py
│   │   ├── generate.py        # Code generation
│   │   ├── explain.py         # Code explanation
│   │   ├── debug.py           # Debug assistance
│   │   └── complete.py        # Code completion
│   ├── model/
│   │   ├── __init__.py
│   │   ├── engine.py          # llama.cpp wrapper
│   │   └── prompts.py         # Prompt templates
│   ├── context/
│   │   ├── __init__.py
│   │   ├── scanner.py         # File scanning
│   │   ├── cache.py           # Context caching
│   │   └── manager.py         # Context management
│   └── utils/
│       ├── __init__.py
│       ├── config.py          # Configuration handling
│       └── formatting.py      # Output formatting
├── models/                    # Model files directory
│   └── deepseek-coder-1.3b.Q4_K_M.gguf
├── config/
│   └── default.yaml          # Default configuration
├── tests/                     # Test files
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
├── setup.py                   # Installation script
└── README.md                  # Project documentation
```

## Implementation Blueprint

### Phase 1: Core CLI Framework
1. **Basic CLI structure** using argparse/click
2. **Configuration system** with YAML support
3. **Model loading** via llama-cpp-python
4. **Simple generation** commands

### Phase 2: Context Management
1. **File scanning** and project awareness
2. **SQLite cache** for project context
3. **Context-aware prompts** generation
4. **Session management** for long-running processes

### Phase 3: Advanced Features
1. **Multi-file understanding**
2. **Project-level refactoring**
3. **Code quality analysis**
4. **Performance optimization**

## Performance Optimizations

### Memory Management
- Load model once, keep in memory during session
- Implement context window optimization
- Use streaming for large file processing
- Periodic memory cleanup for long-running sessions

### CPU Optimization
- Auto-detect optimal thread count
- Implement batch processing for multiple requests
- Use context caching to avoid redundant processing
- Optimize prompt construction for faster inference

## Deployment Strategy

### Package Structure
- **Windows installer** (MSI) with bundled model
- **Portable ZIP** for manual installation
- **Model-only downloads** for existing installations
- **Configuration templates** for different use cases

### Installation Process
1. Download installer or portable package
2. Extract/install to local directory
3. Model auto-download (optional offline mode)
4. VS Code terminal integration setup
5. Configuration verification

### VS Code Integration
- Launch from integrated terminal
- Support for stdin/stdout piping
- Task configuration for common operations
- Extension for enhanced UI (future)

## Success Metrics

### Performance Targets
- Model loading time: < 10 seconds
- First response time: < 5 seconds
- Subsequent responses: < 3 seconds
- Memory usage: < 6GB total

### User Experience Targets
- Setup time: < 5 minutes
- Command execution: Intuitive and fast
- Error handling: Clear and helpful
- Documentation: Comprehensive and accessible