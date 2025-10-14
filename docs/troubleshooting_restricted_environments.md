# Troubleshooting Guide for Restricted Windows Environments

> Comprehensive troubleshooting guide for resolving common issues in restricted Windows business environments with no admin rights.

## 🎯 Overview

This guide addresses common issues that may arise when using the Offline Coding Agent in highly restricted Windows environments. All solutions are designed to work without admin rights.

## 🔧 Installation Issues

### Python and Package Installation

#### Issue: "pip install --user" fails
**Symptoms:**
```
error: could not create [path]: Permission denied
WARNING: Running pip as the 'root' user can result in broken permissions
```

**Solutions:**
1. **Check Python installation location:**
   ```bash
   python -c "import site; print(site.USER_BASE)"
   python -c "import site; print(site.USER_SITE)"
   ```

2. **Ensure user site-packages is enabled:**
   ```bash
   python -m site --user-site
   ```

3. **Force user installation:**
   ```bash
   python -m pip install --user --force-reinstall package_name
   ```

4. **Alternative: Use --target flag:**
   ```bash
   python -m pip install --target ./lib package_name
   export PYTHONPATH="./lib:$PYTHONPATH"
   ```

#### Issue: "Python not found" or "Command not recognized"
**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**
1. **Use python3 instead:**
   ```bash
   python3 scripts/install_aider.py
   ```

2. **Use py launcher (Windows):**
   ```bash
   py scripts/install_aider.py
   ```

3. **Find Python executable:**
   ```bash
   where python
   where python3
   ```

4. **Add Python to PATH temporarily:**
   ```bash
   set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\PythonXX\Scripts
   ```

#### Issue: "SSL certificate verification failed"
**Symptoms:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions:**
1. **Update certificates:**
   ```bash
   # Run this as user (no admin rights needed)
   python -m pip install --user --upgrade certifi
   ```

2. **Use trusted hosts (temporary workaround):**
   ```bash
   python -m pip install --user --trusted-host pypi.org --trusted-host files.pythonhosted.org package_name
   # Or configure pip.ini:
   # [global]
   # trusted-host = pypi.org
   #               files.pythonhosted.org
   ```

3. **Use custom CA bundle (safer alternative):**
   ```bash
   # Option 1: Specify CA bundle with --cert flag
   python -m pip install --user --trusted-host pypi.org --trusted-host files.pythonhosted.org --cert /path/to/ca.pem package_name

   # Option 2: Set PIP_CERT environment variable
   set PIP_CERT=C:\path\to\ca.pem
   python -m pip install --user --trusted-host pypi.org --trusted-host files.pythonhosted.org package_name

   # Or configure pip.ini:
   # [global]
   # trusted-host = pypi.org
   #               files.pythonhosted.org
   # cert = C:\path\to\corp\ca-bundle.pem
   ```

## 🧠 Model Issues

### Model Download Problems

#### Issue: Model download fails or is slow
**Symptoms:**
```
Download failed: timeout
Connection refused
Download speed very slow
```

**Solutions:**
1. **Check internet connection:**
   ```bash
   ping huggingface.co
   ```

2. **Use alternative download method:**
   ```bash
   # Manual download with browser
   # URL: https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-GGUF/blob/main/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
   # Save to: models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
   ```

3. **Download in chunks (script modification):**
   ```python
   # Add to download_model.py if needed
   chunk_size = 1024 * 1024  # 1MB chunks
   ```

4. **Use wget if available:**
   ```bash
   wget -O models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
   ```

#### Issue: "Model file corrupted" or invalid
**Symptoms:**
```
Model validation failed
File size doesn't match expected
GGUF magic number not found
```

**Solutions:**
1. **Check file integrity:**
   ```bash
   # Check file size
   dir models\qwen2.5-coder-8b-instruct.Q4_K_M.gguf
   # Should be ~4.95GB (5,314,969,600 bytes)
   ```

2. **Re-download the model:**
   ```bash
   del models\qwen2.5-coder-8b-instruct.Q4_K_M.gguf
   python scripts/download_model.py
   ```

3. **Verify with checksum (if available):**
   ```bash
   # If SHA256 checksum is provided
   certutil -hashfile models\qwen2.5-coder-8b-instruct.Q4_K_M.gguf SHA256
   ```

4. **Download from alternative source:**
   - Try different Hugging Face mirror
   - Use torrent if available
   - Download from colleague's copy

### Model Loading Issues

#### Issue: "Out of memory" error
**Symptoms:**
```
CUDA out of memory
Memory allocation failed
Process killed
```

**Solutions:**
1. **Reduce model memory usage:**
   ```yaml
   # Edit config/aider_config.yml
   performance:
     max_model_memory_gb: 4  # Reduce from 6
     context_length: 4096    # Reduce from 8192
   ```

2. **Close other applications:**
   - Close browser tabs
   - Close unnecessary programs
   - Restart computer if needed

3. **Use smaller quantization:**
   - Download Q3_K_M version (~3.7GB)
   - Or Q2_K version (~3.0GB)

4. **Enable memory optimization:**
   ```yaml
   model_settings:
     batch_size: 256         # Reduce from 512
     threads: 4              # Limit CPU threads
   ```

#### Issue: Model loading is very slow
**Symptoms:**
```
Model loading takes >5 minutes
System becomes unresponsive
```

**Solutions:**
1. **Optimize model settings:**
   ```yaml
   performance:
     preload_model: true     # Keep model loaded
     cache_enabled: true     # Enable caching
   ```

2. **Use SSD storage:**
   - Move model to SSD drive
   - Ensure adequate disk space

3. **Reduce context size:**
   ```yaml
   model_settings:
     context_length: 4096    # Reduce from 8192
   ```

## 🤖 Aider Issues

### Aider Startup Problems

#### Issue: "aider command not found"
**Symptoms:**
```
'aider' is not recognized as an internal or external command
ModuleNotFoundError: No module named 'aider'
```

**Solutions:**
1. **Use python -m syntax:**
   ```bash
   python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf
   ```

2. **Check installation:**
   ```bash
   python -c "import aider; print('Aider installed')"
   ```

3. **Reinstall Aider:**
   ```bash
   python -m pip install --user --force-reinstall aider-chat
   ```

4. **Check Python path:**
   ```bash
   echo %PYTHONPATH%
   echo %PATH%
   ```

#### Issue: Aider fails to start or crashes
**Symptoms:**
```
Aider crashed on startup
Configuration file error
Invalid model path
```

**Solutions:**
1. **Run verification script:**
   ```bash
   python scripts/verify_installation.py
   ```

2. **Check configuration:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('config/aider_config.yml'))"
   ```

3. **Start with minimal config:**
   ```bash
   python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf --no-config
   ```

4. **Check model file:**
   ```bash
   dir models\*.gguf
   ```

### Aider Runtime Issues

#### Issue: "No response from model" or timeouts
**Symptoms:**
```
Model not responding
Response timeout after 60 seconds
Empty responses
```

**Solutions:**
1. **Increase timeout:**
   ```yaml
   performance:
     response_timeout: 120  # Increase from 60
   ```

2. **Reduce request complexity:**
   - Use smaller context
   - Shorter prompts
   - Process one file at a time

3. **Check system resources:**
   ```bash
   # Check memory usage
   tasklist
   # Check CPU usage
   wmic cpu get loadpercentage
   ```

4. **Restart Aider:**
   ```bash
   /quit
   python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf
   ```

#### Issue: Poor code quality or irrelevant responses
**Symptoms:**
```
Generated code doesn't work
Responses not related to request
Poor understanding of context
```

**Solutions:**
1. **Adjust model parameters:**
   ```yaml
   model_settings:
     temperature: 0.3       # Reduce from 0.7 for more deterministic responses
     top_p: 0.8            # Reduce from 0.9
   ```

2. **Provide better context:**
   - Add relevant files with `/add`
   - Use specific, clear prompts
   - Provide examples of desired output

3. **Use system prompts:**
   ```bash
   > You are an expert Python developer. Write clean, efficient code with proper error handling.
   > Create a function that [specific task]
   ```

4. **Break complex tasks into smaller steps:**
   ```bash
   > First, create the basic function structure
   > Then add error handling
   > Finally, add documentation
   ```

## 🔀 Git Integration Issues

### Git Command Problems

#### Issue: Git commands fail in restricted environment
**Symptoms:**
```
git: command not found
Git operation failed
Permission denied
```

**Solutions:**
1. **Check Git installation:**
   ```bash
   git --version
   where git
   ```

2. **Use Git Bash if available:**
   - Open Git Bash terminal
   - Navigate to project directory
   - Run commands there

3. **Configure Git user (required for commits):**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@company.com"
   ```

4. **Use Bitbucket web interface:**
   - Commit changes locally
   - Push via web browser
   - Use web-based Git operations

#### Issue: Git integration with Bitbucket fails
**Symptoms:**
```
Authentication failed
Remote repository not found
Push operation failed
```

**Solutions:**
1. **Check remote configuration:**
   ```bash
   git remote -v
   ```

2. **Use HTTPS instead of SSH:**
   ```bash
   git remote set-url origin https://bitbucket.org/company/repo.git
   ```

3. **Configure secure credentials:**
   ```bash
   # Option 1: Global configuration (use only if required for automation)
   # WARNING: Avoid global credential storage unless explicitly needed
   # Risks: Credentials stored in plaintext, accessible to all Git operations
   git config --global credential.helper manager-core

   # Option 2: Per-repository configuration (recommended)
   git config credential.helper manager-core

   # Alternative secure helpers by platform:
   # Windows: git config credential.helper manager-core
   # macOS: git config credential.helper osxkeychain
   # Linux: git config credential.helper libsecret
   # Git will prompt for username/password on first use
   ```

4. **Use web-based workflow:**
   - Work offline with local Git
   - Sync via Bitbucket web interface
   - Download/upload changes manually

## 🖥️ Terminal and Environment Issues

### Terminal Compatibility

#### Issue: Terminal display problems
**Symptoms:**
```
Garbled text output
Colors not displaying
Line formatting issues
Unicode characters not showing
```

**Solutions:**
1. **Check terminal type:**
   ```bash
   echo %TERM%
   ```

2. **Use Windows-specific settings:**
   ```yaml
   terminal:
     windows_compatible: true
     ansi_colors: true
     unicode_support: false  # Disable if causing issues
   ```

3. **Try different terminals:**
   - Command Prompt (cmd.exe)
   - PowerShell
   - Git Bash
   - Windows Terminal (if available)

4. **Adjust character encoding:**
   ```bash
   chcp 65001  # UTF-8 encoding
   ```

#### Issue: Copy/paste not working in terminal
**Solutions:**
1. **Enable Windows terminal features:**
   - Right-click terminal title bar
   - Properties → Options → Enable Ctrl key shortcuts
   - Check "Use Ctrl+Shift+C/V as Copy/Paste"

2. **Use alternative methods:**
   - Right-click context menu
   - Mark and copy in Command Prompt
   - Use PowerShell clipboard commands

## 📁 File and Permission Issues

### File Access Problems

#### Issue: Cannot read/write files
**Symptoms:**
```
Permission denied
Access is denied
Cannot create file
```

**Solutions:**
1. **Check file permissions:**
   ```bash
   icacls filename
   ```

2. **Use user directory:**
   - Work in Documents folder
   - Use Desktop for temporary files
   - Avoid system directories

3. **Check file locks:**
   - Close files that might be open
   - Restart applications
   - Restart computer if needed

4. **Use alternative paths:**
   ```bash
   # Instead of C:\Project
   # Use C:\Users\%USERNAME%\Documents\Project
   ```

#### Issue: Path length limitations
**Symptoms:**
```
Path too long
Filename too long
Cannot access file
```

**Solutions:**
1. **Use shorter paths:**
   - Move project closer to root directory
   - Use shorter folder names
   - Avoid deep nesting

2. **Use Windows long path support:**
   ```bash
   # Use \\?\ prefix for long paths
   \\?\C:\Very\Long\Path\To\File
   ```

3. **Enable long path support in registry** (if possible):
   - This requires admin rights, may not be possible
   - Alternative: restructure project

## 🔍 Debugging and Diagnostics

### Diagnostic Commands

#### System Information
```bash
# Python environment
python --version
python -c "import sys; print(sys.executable)"
python -c "import site; print(site.USER_SITE)"

# Package verification
python -c "import aider; print('Aider:', aider.__version__)"
python -c "import llama_cpp; print('llama-cpp-python:', llama_cpp.__version__)"

# System resources
python -c "import psutil; print('Memory:', psutil.virtual_memory().total / (1024**3), 'GB')"
wmic computersystem get TotalPhysicalMemory
wmic diskdrive get size
```

#### Installation Verification
```bash
# Run comprehensive verification
python scripts/verify_installation.py

# Check individual components
python scripts/test_model.py
python scripts/test_aider.py
```

#### Log Analysis
```bash
# Check error logs
type logs\aider_errors.log
type logs\installation.log

# Monitor system resources
tasklist /fi "imagename eq python.exe"
wmic process where "name='python.exe'" get PageFileUsage,WorkingSetSize
```

### Creating Bug Reports

When reporting issues, include:

1. **System Information:**
   - Windows version
   - Python version
   - Available RAM and disk space

2. **Error Messages:**
   - Full error traceback
   - Commands that failed
   - Expected vs actual behavior

3. **Configuration:**
   - Content of config files
   - Model being used
   - Terminal type

4. **Steps to Reproduce:**
   - Exact commands used
   - Files being processed
   - Sequence of actions

## 🚀 Performance Optimization

### Memory Optimization

1. **Reduce model memory usage:**
   ```yaml
   performance:
     max_model_memory_gb: 4
     context_length: 4096
     max_output_tokens: 2048
   ```

2. **Enable memory management:**
   ```yaml
   performance:
     cache_enabled: true
     context_compression: true
     remove_redundant_content: true
   ```

### Speed Optimization

1. **Optimize model settings:**
   ```yaml
   model_settings:
     batch_size: 256
     threads: 4  # Don't use all CPU cores
   ```

2. **Use smaller contexts:**
   - Add files selectively
   - Clear context regularly
   - Work with one file at a time

3. **Enable caching:**
   ```yaml
   performance:
     cache_enabled: true
     cache_size_mb: 200
   ```

## 📞 Getting Help

### Self-Help Resources

1. **Run diagnostic script:**
   ```bash
   python scripts/verify_installation.py
   ```

2. **Check configuration:**
   ```bash
   type config\aider_config.yml
   ```

3. **Review logs:**
   ```bash
   type logs\aider_errors.log
   ```

### Community Support

1. **GitHub Issues:**
   - https://github.com/akepo225/offline-coding-agent/issues
   - Include diagnostic information
   - Provide steps to reproduce

2. **Documentation:**
   - `docs/aider_setup_guide.md`
   - `docs/terminal_workflows.md`
   - `README.md`

### Emergency Procedures

If nothing works:

1. **Fresh installation:**
   ```bash
   # Backup configuration
   copy config\aider_config.yml config\aider_config.yml.backup

   # Remove and reinstall
   rmdir /s models
   python -m pip uninstall --user aider-chat llama-cpp-python
   python scripts/install_aider.py
   python scripts/download_model.py
   ```

2. **Minimal configuration:**
   - Start with default settings
   - Use basic commands only
   - Gradually add features

---

**Remember:** All solutions in this guide are designed to work without admin rights in restricted Windows environments. If a solution requires admin privileges, look for alternative approaches or contact your IT department.