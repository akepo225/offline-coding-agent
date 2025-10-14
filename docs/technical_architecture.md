# Technical Architecture - Offline Coding Agent

## Core Technology Stack

### Inference Engine: llama.cpp
- **Framework**: llama.cpp (CPU-optimized)
- **Model Format**: GGUF (4-bit quantized)
- **Python Integration**: llama-cpp-python
- **Platform**: Windows native binary support
- **Installation**: User-level pip install (no admin rights required)

### Model: Qwen2.5-Coder-7B
- **File Size**: ~4.7GB (Q4_K_M quantized)
- **Memory Usage**: ~8GB RAM
- **Inference**: CPU-only (perfect for 128MB VRAM constraint)
- **Performance**: Professional-grade code generation with 32K context window

### Terminal Agent: Aider
- **Framework**: Terminal-based AI assistant
- **Installation**: pip install --user aider-chat
- **Integration**: Git workflow management
- **Interface**: Command-line interaction
- **Permissions**: User-level only (no admin rights required)

### Environment Constraints
- **OS**: Windows 10/11
- **Permissions**: Standard user account (no admin rights)
- **Network**: Offline operation after initial setup
- **Installation**: Portable, can run from USB drive

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│               Terminal Environment Only                 │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │  Command Prompt │  │       Aider Agent            │  │
│  │  PowerShell     │  │  (Terminal-based AI Assistant) │  │
│  │  Git Bash       │  └──────────────────────────────┘  │
│  └─────────────────┘                                 │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│              Local AI Engine                             │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │ Qwen2.5-Coder-7B│  │        llama.cpp             │  │
│  │   (GGUF Model)  │  │     (CPU Inference)          │  │
│  └─────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                User Interface Layer                     │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │   Terminal I/O  │  │        Git Integration        │  │
│  │   (Input/Output)│  │    (Bitbucket Compatible)    │  │
│  └─────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│              Storage Layer                               │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │   Model Files   │  │     Configuration Files      │  │
│  │   (Local)       │  │      (Local Settings)       │  │
│  └─────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Terminal Workflow Architecture

### Aider Command Structure
```bash
# Basic Aider usage with local model
aider --model qwen2.5-coder-8b

# With specific file context
aider --model qwen2.5-coder-8b --file script.py

# With directory context
aider --model qwen2.5-coder-8b src/

# With configuration file
aider --model qwen2.5-coder-8b --config config/aider_config.yml
```

### Interactive Commands
```bash
# Within Aider session
/add file.py              # Add file to context
/add *.py                 # Add multiple files
/remove file.py           # Remove file from context
/diff                     # Show changes
/commit                   # Commit changes
/undo                     # Undo last change
/help                     # Show help
/quit                     # Exit
```

### Natural Language Interaction
```bash
# Code generation examples
> Create a Python function to validate email addresses
> Write a REST API endpoint for user authentication
> Generate unit tests for this module

# Code modification examples
> Refactor this function to be more efficient
> Add error handling to this code
> Update this code to use modern JavaScript syntax

# Debugging examples
> This function is throwing a TypeError, can you fix it?
> Why is this SQL query so slow?
> Help me understand this compilation error
```

## Project Structure (Terminal-Optimized)

```
offline-coding-agent/
├── scripts/                    # Utility scripts
│   ├── download_model.py     # Model download automation
│   ├── setup_env.py          # Environment setup (no admin rights)
│   ├── test_installation.py  # Installation verification
│   └── benchmark.py          # Performance testing
├── config/                    # Configuration files
│   ├── aider_config.yml      # Aider configuration
│   └── model_config.yaml     # Model settings
├── models/                    # Model files directory
│   └── qwen2.5-coder-8b-instruct.Q4_K_M.gguf
├── examples/                  # Usage examples
│   ├── python_workflows/     # Python development examples
│   ├── terminal_scripts/     # Terminal usage patterns
│   └── git_workflows/        # Git integration examples
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies (user install)
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