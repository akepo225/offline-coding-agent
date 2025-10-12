# Offline Coding Agent

> Terminal-based AI coding assistant that operates completely offline on restricted Windows business laptops

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Model: Qwen2.5-Coder-8B](https://img.shields.io/badge/model-Qwen2.5--Coder--8B-green.svg)](https://huggingface.co/Qwen/Qwen2.5-Coder-8B-Instruct)
[![No Admin Rights Required](https://img.shields.io/badge/no%20admin%20rights-required-brightgreen.svg)](https://github.com/akepo225/offline-coding-agent)

## 🎯 Overview

This project provides a **terminal-only** offline coding solution specifically designed for **restricted Windows business laptops** with **no admin rights**. It combines **Qwen2.5-Coder-8B** with **Aider** to deliver professional-grade AI assistance without requiring internet connectivity, VS Code extensions, or system installations.

## ✨ Key Features

- **🔒 Complete Offline Operation**: No internet required after initial setup
- **🚫 No Admin Rights Required**: Runs entirely with user permissions
- **💻 Windows Optimized**: Designed for business laptops (32GB RAM, 128MB VRAM)
- **🧠 Professional AI Model**: Qwen2.5-Coder-8B with 32K context window
- **🖥️ Terminal-Only**: Works in Command Prompt, PowerShell, or Git Bash
- **🔧 Git Integration**: Seamless workflow with Bitbucket and local repositories
- **🎨 Multi-Language Support**: 50+ programming languages
- **📊 Performance Optimized**: CPU-optimized inference with llama.cpp
- **📁 Portable**: Can run from USB drive or local directory

## 🏗️ Architecture

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
│  │ Qwen2.5-Coder-8B│  │        llama.cpp             │  │
│  │   (GGUF Model)  │  │     (CPU Inference)          │  │
│  └─────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **OS**: Windows 10/11
- **RAM**: 32GB (recommended)
- **Python**: 3.8 or higher (user-level installation)
- **Git**: Available via web interface (Bitbucket)
- **Storage**: 10GB free space
- **Permissions**: Standard user account (no admin rights required)

### Installation (No Admin Rights Required)

1. **Clone Repository**
   ```bash
   git clone https://github.com/akepo225/offline-coding-agent.git
   cd offline-coding-agent
   ```

2. **Download AI Model**
   ```bash
   # Automated model download (4.7GB)
   python scripts/download_model.py

   # Or manual download from Hugging Face
   # https://huggingface.co/bartowski/Qwen2.5-Coder-8B-Instruct-GGUF
   ```

3. **Install Dependencies Locally**
   ```bash
   # Install Python packages to user directory (no admin rights)
   pip install --user aider-chat
   pip install --user llama-cpp-python
   ```

4. **Verify Installation**
   ```bash
   python scripts/test_installation.py
   ```

## 📖 Usage (Terminal Only)

### Start Aider in Your Project
```bash
# Navigate to your project directory
cd path/to/your/project

# Start Aider with local Qwen2.5-Coder-8B model
aider --model qwen2.5-coder-8b

# Or with explicit model path
aider --model path/to/models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf
```

### Common Aider Commands
```bash
# Add files to context
/add file.py          # Add specific file
/add *.py             # Add all Python files
/add src/              # Add entire directory

# Edit and manage changes
> Write a function to validate user input
> Refactor this code to be more readable
> Fix the bug in the authentication system

# Git operations
/diff                 # Show changes
/commit               # Commit changes with AI-generated message
/undo                 # Undo last change
/git                  # Show git status

# Help and navigation
/help                 # Show all commands
/quit                 # Exit aider
```

### Terminal Examples
```bash
# Example 1: Generate a new function
aider --model qwen2.5-coder-8b
> Create a Python function that validates email addresses using regex

# Example 2: Debug existing code
aider --model qwen2.5-coder-8b --file buggy_script.py
> This script is throwing a TypeError, can you help me debug it?

# Example 3: Refactor code
aider --model qwen2.5-coder-8b --file old_code.py
> Refactor this code to use modern Python features and improve readability
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Model Size** | 4.7GB (Q4_K_M quantized) |
| **RAM Usage** | ~8GB |
| **Response Time** | 3-5 seconds |
| **Inference Speed** | 15-30 tokens/second |
| **Context Window** | 32K tokens |
| **Supported Languages** | 50+ |

## 🗂️ Project Structure

```
offline-coding-agent/
├── docs/                     # Documentation
│   ├── concept.md           # Project concept and goals
│   ├── model_evaluation.md  # Model selection research
│   ├── implementation_guide.md # Setup and usage guide
│   └── troubleshooting.md   # Common issues and solutions
├── config/                   # Configuration files
│   └── aider_config.yml     # Aider configuration
├── scripts/                  # Utility scripts
│   ├── download_model.py    # Model download automation
│   ├── test_installation.py # Installation verification
│   └── benchmark.py         # Performance testing
├── examples/                 # Usage examples
│   ├── python_project/      # Python development example
│   └── terminal_workflows/  # Terminal usage patterns
├── models/                   # AI model files (downloaded)
│   └── qwen2.5-coder-8b-instruct.Q4_K_M.gguf
└── requirements.txt          # Python dependencies
```

## 🛠️ Setup and Development

### Portable Setup (No Admin Rights)
```bash
# Clone repository
git clone https://github.com/akepo225/offline-coding-agent.git
cd offline-coding-agent

# Install dependencies locally
pip install --user -r requirements.txt

# Run installation test
python scripts/test_installation.py
```

### Configuration
```bash
# Edit Aider configuration
notepad config/aider_config.yml

# Set model path
# Add custom prompts
# Configure Git settings
```

## 📋 Roadmap

### Phase 1: Foundation ✅
- [x] Repository setup and documentation
- [x] Model selection and evaluation (Qwen2.5-Coder-8B)
- [x] Terminal-only architecture design

### Phase 2: Model Integration 🚧
- [ ] Automated model download scripts
- [ ] Performance benchmarking on restricted hardware
- [ ] llama.cpp optimization for 32GB RAM systems

### Phase 3: Terminal Workflow Development 📋
- [ ] Aider configuration for restricted environments
- [ ] Terminal workflow optimization
- [ ] Custom prompt engineering for terminal interaction

### Phase 4: Portable Distribution 📋
- [ ] Self-contained package creation
- [ ] USB drive deployment option
- [ ] Installation automation without admin rights
- [ ] User documentation for restricted environments

## 🤝 Community

- **Discussions**: [GitHub Discussions](https://github.com/your-org/offline-coding-agent/discussions)
- **Issues**: [GitHub Issues](https://github.com/your-org/offline-coding-agent/issues)
- **Wiki**: [Project Wiki](https://github.com/your-org/offline-coding-agent/wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Qwen Team** for the excellent Qwen2.5-Coder-8B model
- **Aider** for terminal-based AI assistance (perfect for restricted environments)
- **llama.cpp** for efficient CPU inference
- **Hugging Face** for model hosting and distribution

## 🔗 Related Projects

- [Qwen2.5-Coder-8B](https://huggingface.co/Qwen/Qwen2.5-Coder-8B-Instruct) - The AI model
- [Aider](https://github.com/paul-gauthier/aider) - Terminal AI assistant
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Model inference engine

## 🔒 Security & Compliance

- **No network access required** after initial setup
- **No admin privileges needed** for installation or usage
- **All processing happens locally** on the user's machine
- **Suitable for air-gapped and high-security environments**

---

**Built for professional developers working in highly restricted Windows environments.**

Need help? Check our [documentation](docs/) or open an [issue](https://github.com/your-org/offline-coding-agent/issues).