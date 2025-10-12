#!/usr/bin/env python3
"""
Aider Installation Script for Restricted Windows Environments
Installs Aider and all dependencies without requiring admin rights.
"""

import os
import sys
import subprocess
import platform
import importlib.util
from pathlib import Path
import json

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_system_requirements():
    """Check system requirements and display information."""
    print("\n📋 System Requirements Check")
    print("=" * 50)

    # OS Information
    print(f"🖥️  OS: {platform.system()} {platform.release()}")
    print(f"🏗️  Architecture: {platform.machine()}")
    print(f"💻 Processor: {platform.processor()}")

    # Memory check (Windows specific)
    if platform.system() == "Windows":
        try:
            import psutil
            memory = psutil.virtual_memory()
            print(f"🧠 Total RAM: {memory.total / (1024**3):.1f} GB")
            print(f"🔄 Available RAM: {memory.available / (1024**3):.1f} GB")

            if memory.total < 8 * 1024**3:  # Less than 8GB
                print("⚠️  Warning: Less than 8GB RAM detected. Performance may be limited.")
            elif memory.total >= 32 * 1024**3:  # 32GB or more
                print("✅ Excellent: 32GB+ RAM detected - optimal for Qwen2.5-Coder-8B")
            else:
                print("✅ Sufficient RAM detected")
        except ImportError:
            print("ℹ️  Install psutil to check RAM: pip install --user psutil")

    # Disk space check
    current_dir = Path.cwd()
    try:
        stat = os.statvfs(current_dir) if hasattr(os, 'statvfs') else None
        if stat:
            free_space = stat.f_bavail * stat.f_frsize / (1024**3)
            print(f"💾 Free disk space: {free_space:.1f} GB")

            if free_space < 10:
                print("⚠️  Warning: Less than 10GB free space available")
            else:
                print("✅ Sufficient disk space available")
    except:
        print("ℹ️  Cannot check disk space on this system")

    print()

def install_package(package_name, user_flag=True, upgrade=False):
    """Install a Python package using pip."""
    cmd = [sys.executable, "-m", "pip", "install"]

    if user_flag:
        cmd.append("--user")

    if upgrade:
        cmd.append("--upgrade")

    cmd.append(package_name)

    print(f"📦 Installing {package_name}...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}")
        print(f"Error: {e.stderr}")
        return False

def check_package_installed(package_name):
    """Check if a package is already installed."""
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        print(f"✅ {package_name} is already installed")
        return True
    return False

def install_aider():
    """Install Aider and its dependencies."""
    print("\n🚀 Installing Aider and Dependencies")
    print("=" * 50)

    # Core dependencies to install
    packages = [
        "aider-chat",
        "llama-cpp-python",
        "rich",           # For better terminal output
        "click",          # CLI framework
        "pyyaml",         # Configuration file support
        "requests",       # For model downloads
        "tqdm",           # Progress bars
        "psutil",         # System information
    ]

    # Optional but recommended packages
    optional_packages = [
        "gitpython",      # Git integration
        "watchdog",       # File watching
        "colorama",       # Cross-platform colored terminal text
    ]

    failed_packages = []

    # Install core packages
    for package in packages:
        if not check_package_installed(package.replace("-", "_")):
            if not install_package(package):
                failed_packages.append(package)

    # Install optional packages
    print("\n📚 Installing optional packages...")
    for package in optional_packages:
        if not check_package_installed(package.replace("-", "_")):
            if not install_package(package):
                print(f"⚠️  Optional package {package} failed to install (non-critical)")

    if failed_packages:
        print(f"\n❌ Installation failed for packages: {', '.join(failed_packages)}")
        print("Please check your internet connection and try again.")
        return False

    print("\n✅ Core installation completed successfully!")
    return True

def verify_aider_installation():
    """Verify that Aider was installed correctly."""
    print("\n🔍 Verifying Aider Installation")
    print("=" * 50)

    try:
        # Try to run aider --version
        result = subprocess.run(
            [sys.executable, "-m", "aider", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"✅ Aider version: {result.stdout.strip()}")
        else:
            print("⚠️  Aider installed but version check failed")
            print(f"Output: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️  Aider version check timed out")
    except FileNotFoundError:
        print("❌ Aider installation verification failed")
        return False

    # Check if we can import aider modules
    try:
        import aider
        print("✅ Aider Python modules can be imported")
    except ImportError as e:
        print(f"❌ Cannot import Aider modules: {e}")
        return False

    return True

def create_directories():
    """Create necessary directories for the offline coding agent."""
    print("\n📁 Creating Project Directories")
    print("=" * 50)

    directories = [
        "models",
        "cache",
        "logs",
        "examples/terminal_workflows",
        "examples/python_workflows",
        "config",
    ]

    for directory in directories:
        dir_path = Path(directory)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")

def generate_user_config():
    """Generate user-specific configuration file."""
    print("\n⚙️  Generating User Configuration")
    print("=" * 50)

    # Get user home directory
    home_dir = Path.home()
    config_dir = home_dir / ".aider"

    try:
        config_dir.mkdir(exist_ok=True)
        print(f"✅ Created Aider config directory: {config_dir}")
    except Exception as e:
        print(f"⚠️  Could not create config directory: {e}")
        config_dir = Path.cwd() / "config"

    # Generate basic configuration
    config_content = """# Aider Configuration for Offline Coding Agent
# Generated automatically by install_aider.py

# Model Configuration
model: qwen2.5-coder-8b-instruct.Q4_K_M.gguf
model_path: ./models/

# Output Settings
output_format: text
dark_mode: true
show_model_warnings: false

# Editor Settings
editor: notepad  # Windows default, can be changed to vscode, code, etc.

# Git Settings
gitignore: true
auto_commits: false  # Disabled for manual control in restricted environments

# File Settings
file_watch: true
encoding: utf-8

# Performance Settings for 32GB RAM
max_input_tokens: 8192
max_output_tokens: 4096
"""

    config_file = config_dir / "config.yml"
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"✅ Created Aider config file: {config_file}")
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")

def print_next_steps():
    """Print next steps for the user."""
    print("\n🎉 Installation Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Download the AI model:")
    print("   python scripts/download_model.py")
    print()
    print("2. Verify installation:")
    print("   python scripts/verify_installation.py")
    print()
    print("3. Start using Aider:")
    print("   python -m aider --model qwen2.5-coder-8b-instruct.Q4_K_M.gguf")
    print()
    print("4. For help and troubleshooting:")
    print("   Check docs/troubleshooting_restricted_environments.md")
    print()
    print("📚 Documentation: docs/aider_setup_guide.md")

def main():
    """Main installation function."""
    print("🤖 Offline Coding Agent - Aider Installation")
    print("=" * 50)
    print("Installing Aider for restricted Windows environments")
    print("No admin rights required - user-level installation only")
    print()

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check system requirements
    check_system_requirements()

    # Install Aider and dependencies
    if not install_aider():
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)

    # Verify installation
    if not verify_aider_installation():
        print("\n⚠️  Installation completed with warnings. Some features may not work.")

    # Create directories
    create_directories()

    # Generate configuration
    generate_user_config()

    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()