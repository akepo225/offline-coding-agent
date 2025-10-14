# Aider Setup Guide for Restricted Windows Environments

> Complete setup guide for installing and configuring Aider with Qwen2.5-Coder-7B in restricted Windows business environments with no admin rights.

## 🎯 Overview

This guide provides step-by-step instructions for setting up the Offline Coding Agent using **Aider** (terminal-based AI assistant) with **Qwen2.5-Coder-7B** local model. This solution is specifically designed for:

- ❌ **No admin rights required**
- ❌ **No VS Code extensions needed**
- ❌ **No internet connectivity after setup**
- ✅ **Complete offline operation**
- ✅ **User-level installation only**
- ✅ **Compatible with Bitbucket web interface**

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 32GB recommended (minimum 16GB)
- **Storage**: 10GB free space
- **Python**: 3.8 or higher (user-level installation)
- **Git**: Available via web interface (Bitbucket)

### Permissions
- ✅ Standard user account (no admin rights required)
- ✅ Internet access for initial setup only
- ✅ Local file system access

## 🚀 Installation Steps

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/akepo225/offline-coding-agent.git
cd offline-coding-agent
```

### Step 2: Automated Installation

#### Option A: Complete Automated Setup
```bash
# Run the automated installation script
python scripts/install_aider.py
```

#### Option B: Manual Step-by-Step Installation

1. **Install Python Dependencies**
   ```bash
   # Install all dependencies (for reproducible installs, use constraints.txt)
   pip install --user -r requirements.txt -c constraints.txt
   # For offline installs, use: pip install --user --no-index --find-links . -r requirements.txt -c constraints.txt
   ```

2. **Download AI Model**
   ```bash
   # Automated model download (4.7GB)
   python scripts/download_model.py
   ```

3. **Verify Installation**
   ```bash
   # Verify everything is working correctly
   python scripts/verify_installation.py
   ```

### Step 3: Configuration Setup

The installation creates several configuration files:

#### Main Configuration
- **File**: `config/aider_config.yml`
- **Purpose**: Main Aider configuration for offline use

#### User Configuration
- **File**: `~/.aider/config.yml` (Windows: `C:\Users\[Username]\.aider\config.yml`)
- **Purpose**: User-specific settings

## 🖥️ Terminal Usage

### Starting Aider

#### Basic Usage
```bash
# Navigate to your project directory
cd path/to/your/project

# Start Aider with local model
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
```

#### With Custom Configuration
```bash
# Start with specific configuration file
python -m aider --config config/aider_config.yml --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
```

#### With Specific Files
```bash
# Start with specific files in context
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf file1.py file2.js
```

### Basic Aider Commands

Once Aider is running, you can use these commands:

#### File Management
```bash
/add file.py              # Add file to context
/add *.py                 # Add all Python files
/add src/                  # Add entire directory
/remove file.py           # Remove file from context
/ls                       # List files in context
```

#### Editing and Generation
```bash
> Write a Python function to validate email addresses
> Refactor this code to be more readable
> Add error handling to this function
> Create a REST API endpoint for user authentication
```

#### Git Operations
```bash
/diff                     # Show changes
/commit                   # Commit changes with AI-generated message
/undo                     # Undo last change
/git                      # Show git status
/commit "Custom message"  # Commit with custom message
```

#### Navigation and Help
```bash
/help                     # Show all commands
/quit                     # Exit aider
/clear                    # Clear context
```

## 🔧 Configuration Options

### Model Settings
```yaml
model_settings:
  temperature: 0.7          # Creativity level (0.0-1.0)
  top_p: 0.9               # Nucleus sampling
  context_length: 8192     # Context window size
  threads: 0               # CPU threads (0 = auto-detect)
```

### Performance Settings
```yaml
performance:
  max_input_tokens: 8192   # Maximum input tokens
  max_output_tokens: 4096  # Maximum output tokens
  max_model_memory_gb: 6   # Maximum memory usage
  cache_enabled: true      # Enable response caching
```

### Editor Configuration
```yaml
editor:
  preferred: notepad        # Windows notepad
  # preferred: code          # VS Code (if installed)
  # preferred: notepad++     # Notepad++ (if installed)
```

## 🎨 Usage Examples

### Example 1: Creating a New Function
```bash
# Start Aider
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Add your file
/add my_script.py

# Generate code
> Create a Python function that validates email addresses using regex
```

### Example 2: Debugging Existing Code
```bash
# Start Aider with problematic file
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf --file buggy_script.py

# Ask for help
> This script is throwing a TypeError, can you help me debug it?
```

### Example 3: Refactoring Code
```bash
# Start Aider
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Add files to refactor
/add old_code.py

# Request refactoring
> Refactor this code to use modern Python features and improve readability
```

### Example 4: Working with Git
```bash
# In a Git repository
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Make changes and commit
/add src/
> Add input validation to all user-facing functions
/diff                    # Review changes
/commit                  # Commit with AI-generated message
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Aider Not Found
```bash
# Error: 'aider' is not recognized
# Solution: Use python -m instead
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
```

#### 2. Model Not Found
```bash
# Error: Model file not found
# Solution: Download the model
python scripts/download_model.py
```

#### 2.1. Filename Case Sensitivity
**Important**: GGUF model filenames are case-sensitive on most systems. Ensure the filename exactly matches:
- ✅ Correct: `models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf`
- ❌ Incorrect: `models/qwen2.5-coder-7b-instruct.q4_k_m.gguf`

If you encounter "Model not found" errors, verify the exact casing of the downloaded file matches the above.

#### 3. Memory Issues
```bash
# Error: Out of memory
# Solution: Reduce context size in config
# Edit config/aider_config.yml:
# model_settings:
#   context_length: 4096  # Reduce from 8192
```

#### 4. Slow Performance
```bash
# Solution: Optimize settings
# Reduce context length
# Enable caching
# Close other applications
```

### Getting Help

1. **Check verification script**:
   ```bash
   python scripts/verify_installation.py
   ```

2. **Review configuration**:
   ```bash
   # Check config files
   cat config/aider_config.yml
   ```

3. **Check logs**:
   ```bash
   # View error logs
   cat logs/aider_errors.log
   ```

4. **Detailed troubleshooting**:
   See `docs/troubleshooting_restricted_environments.md`

## 📊 Performance Tips

### Optimizing for 32GB RAM
```yaml
performance:
  max_model_memory_gb: 6   # Leave memory for system
  context_length: 8192     # Balanced size
  cache_enabled: true      # Enable caching
  preload_model: true      # Keep model loaded
```

### Improving Response Speed
- Reduce `context_length` if responses are slow
- Enable `cache_enabled` to cache responses
- Close unnecessary applications
- Use SSD storage for better performance

### Managing Large Projects
- Add files selectively with `/add`
- Use exclude patterns in configuration
- Clear context regularly with `/clear`
- Work with smaller file chunks

## 🔒 Security and Privacy

### Local Operation Only
- ✅ No internet access required after setup
- ✅ All processing happens locally
- ✅ No data sent to external servers
- ✅ Suitable for air-gapped environments

### Data Protection
- ✅ No telemetry or analytics
- ✅ No crash reporting
- ✅ Local file access only
- ✅ User-controlled data retention

## 🚀 Advanced Usage

### Custom Prompts
Create custom prompts in `config/prompts.yml`:
```yaml
custom_prompts:
  code_review: "Review this code for security vulnerabilities and best practices"
  documentation: "Generate comprehensive documentation for this code"
```

### Batch Processing
```bash
# Process multiple files
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf *.py

# Process directory
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf src/
```

### Integration with Bitbucket
- Use Git commands for Bitbucket compatibility
- Manual commits work with web interface
- Branch operations supported
- Merge workflows compatible

## 📚 Additional Resources

### Documentation
- `docs/troubleshooting_restricted_environments.md` - Detailed troubleshooting
- `docs/terminal_workflows.md` - Terminal-specific usage patterns
- `config/aider_config.yml` - Configuration options reference

### Examples
- `examples/terminal_workflows/` - Terminal usage examples
- `examples/python_workflows/` - Python development examples

### External Resources
- [Aider Documentation](https://aider.chat/)
- [Qwen2.5-Coder-7B Model](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)

## 🎉 Next Steps

1. **Complete Installation**: Follow all steps in this guide
2. **Test Functionality**: Run verification script
3. **Explore Examples**: Check example workflows
4. **Customize Configuration**: Adjust settings to your needs
5. **Start Coding**: Begin using Aider for your projects

## 📞 Support

If you encounter issues:

1. Run `python scripts/verify_installation.py`
2. Check `docs/troubleshooting_restricted_environments.md`
3. Review GitHub Issues: https://github.com/akepo225/offline-coding-agent/issues
4. Create new issue with detailed information

---

**Built for professional developers working in highly restricted Windows environments.**