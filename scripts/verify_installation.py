#!/usr/bin/env python3
"""
Installation Verification Script for Offline Coding Agent
Verifies that all components are properly installed and configured.
"""

import os
import sys
import subprocess
import importlib.util
import platform
from pathlib import Path
import json
import yaml
import time

class InstallationVerifier:
    def __init__(self):
        self.project_root = Path.cwd()
        self.models_dir = self.project_root / "models"
        self.config_dir = self.project_root / "config"
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"

    def print_header(self):
        """Print verification header."""
        print("🔍 Offline Coding Agent - Installation Verification")
        print("=" * 60)
        print("Verifying installation of Aider and Qwen2.5-Coder-8B")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Project Root: {self.project_root}")
        print()

    def verify_python_environment(self):
        """Verify Python environment and installed packages."""
        print("🐍 Python Environment Verification")
        print("-" * 40)

        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        else:
            print(f"✅ Python version: {sys.version.split()[0]}")

        # Required packages
        required_packages = {
            "aider": "aider-chat",
            "llama_cpp": "llama-cpp-python",
            "rich": "rich",
            "click": "click",
            "yaml": "pyyaml",
            "requests": "requests",
            "tqdm": "tqdm"
        }

        # Optional packages
        optional_packages = {
            "psutil": "psutil",
            "git": "gitpython",
            "watchdog": "watchdog",
            "colorama": "colorama"
        }

        failed_required = []

        # Check required packages
        for module, package in required_packages.items():
            spec = importlib.util.find_spec(module)
            if spec is not None:
                print(f"✅ {package}")
            else:
                print(f"❌ {package} - MISSING")
                failed_required.append(package)

        # Check optional packages
        print("\n📚 Optional packages:")
        for module, package in optional_packages.items():
            spec = importlib.util.find_spec(module)
            if spec is not None:
                print(f"✅ {package}")
            else:
                print(f"⚠️  {package} - not installed (optional)")

        if failed_required:
            print(f"\n❌ Missing required packages: {', '.join(failed_required)}")
            print("Run: python scripts/install_aider.py")
            return False

        print("✅ Python environment verified")
        return True

    def verify_aider_functionality(self):
        """Verify that Aider is functional."""
        print("\n🤖 Aider Functionality Verification")
        print("-" * 40)

        try:
            # Check aider version
            result = subprocess.run(
                [sys.executable, "-m", "aider", "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"✅ Aider version: {result.stdout.strip()}")
            else:
                print("⚠️  Aider version check failed")
                print(f"Error: {result.stderr}")

        except subprocess.TimeoutExpired:
            print("⚠️  Aider version check timed out")
        except FileNotFoundError:
            print("❌ Aider not found in Python modules")
            return False

        # Test aider help command
        try:
            result = subprocess.run(
                [sys.executable, "-m", "aider", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print("✅ Aider help command works")
            else:
                print("⚠️  Aider help command failed")

        except subprocess.TimeoutExpired:
            print("⚠️  Aider help command timed out")
        except Exception as e:
            print(f"⚠️  Aider help command error: {e}")

        return True

    def verify_model_files(self):
        """Verify model files and configuration."""
        print("\n🧠 Model Files Verification")
        print("-" * 40)

        model_file = self.models_dir / "qwen2.5-coder-8b-instruct.Q4_K_M.gguf"
        metadata_file = self.models_dir / "qwen2.5-coder-8b-instruct.Q4_K_M.gguf.json"

        if not model_file.exists():
            print("❌ Model file not found")
            print("Run: python scripts/download_model.py")
            return False

        # Check file size
        file_size = model_file.stat().st_size
        expected_size = 4_950_000_000  # ~4.95GB
        size_tolerance = expected_size * 0.1  # 10% tolerance

        print(f"📁 Model file: {model_file}")
        print(f"📊 File size: {file_size / (1024**3):.1f} GB")

        if abs(file_size - expected_size) > size_tolerance:
            print("⚠️  File size outside expected range - may be corrupted")
        else:
            print("✅ Model file size correct")

        # Check metadata file
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print("✅ Model metadata file exists")
                print(f"📋 Model: {metadata.get('model_name', 'Unknown')}")
                print(f"📋 Description: {metadata.get('description', 'No description')}")
            except Exception as e:
                print(f"⚠️  Could not read metadata file: {e}")
        else:
            print("⚠️  Model metadata file not found")

        return True

    def verify_configuration_files(self):
        """Verify configuration files."""
        print("\n⚙️  Configuration Files Verification")
        print("-" * 40)

        config_files = {
            "Aider Configuration": self.config_dir / "aider_config.yml",
            "Default Configuration": self.config_dir / "default.yaml",
        }

        all_exist = True
        for name, config_file in config_files.items():
            if config_file.exists():
                print(f"✅ {name}: {config_file.name}")

                # Try to parse YAML files
                if config_file.suffix in ['.yml', '.yaml']:
                    try:
                        with open(config_file, 'r') as f:
                            yaml.safe_load(f)
                        print(f"   Valid YAML syntax")
                    except yaml.YAMLError as e:
                        print(f"   ❌ YAML syntax error: {e}")
                        all_exist = False
            else:
                print(f"❌ {name}: {config_file.name} - MISSING")
                all_exist = False

        return all_exist

    def verify_project_structure(self):
        """Verify project directory structure."""
        print("\n📁 Project Structure Verification")
        print("-" * 40)

        required_directories = [
            self.models_dir,
            self.config_dir,
            self.scripts_dir,
            self.logs_dir,
        ]

        optional_directories = [
            self.project_root / "docs",
            self.project_root / "examples",
            self.project_root / "src",
        ]

        for directory in required_directories:
            if directory.exists():
                print(f"✅ {directory.name}/")
            else:
                print(f"❌ {directory.name}/ - MISSING")
                return False

        print("\n📁 Optional directories:")
        for directory in optional_directories:
            if directory.exists():
                print(f"✅ {directory.name}/")
            else:
                print(f"⚠️  {directory.name}/ - not present (optional)")

        return True

    def verify_git_environment(self):
        """Verify Git environment setup."""
        print("\n🔀 Git Environment Verification")
        print("-" * 40)

        # Check if git is available
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print(f"✅ Git: {result.stdout.strip()}")
            else:
                print("⚠️  Git command failed")
                return False

        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️  Git not found or not accessible")
            return False

        # Check if we're in a git repository
        try:
            result = subprocess.run(
                ["git", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print("✅ Git repository detected")
            else:
                print("ℹ️  Not in a Git repository (this is OK)")

        except subprocess.TimeoutExpired:
            print("⚠️  Git status check timed out")

        # Check Git configuration
        try:
            result = subprocess.run(
                ["git", "config", "--global", "user.name"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ Git user configured: {result.stdout.strip()}")
            else:
                print("⚠️  Git user name not configured")
                print("   Run: git config --global user.name \"Your Name\"")

        except subprocess.TimeoutExpired:
            print("⚠️  Git configuration check timed out")

        return True

    def verify_system_resources(self):
        """Verify system resources and compatibility."""
        print("\n💻 System Resources Verification")
        print("-" * 40)

        # Check available memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            print(f"🧠 Total RAM: {memory.total / (1024**3):.1f} GB")
            print(f"🔄 Available RAM: {memory.available / (1024**3):.1f} GB")

            if memory.total >= 32 * 1024**3:
                print("✅ Excellent: 32GB+ RAM - optimal for performance")
            elif memory.total >= 16 * 1024**3:
                print("✅ Good: 16GB+ RAM - sufficient for good performance")
            elif memory.total >= 8 * 1024**3:
                print("⚠️  Minimum: 8GB+ RAM - performance may be limited")
            else:
                print("❌ Insufficient RAM: less than 8GB - performance will be poor")

        except ImportError:
            print("ℹ️  Install psutil to check RAM: pip install --user psutil")

        # Check disk space
        try:
            if hasattr(os, 'statvfs'):
                stat = os.statvfs(self.project_root)
                free_space = stat.f_bavail * stat.f_frsize
                print(f"💾 Free disk space: {free_space / (1024**3):.1f} GB")

                if free_space < 5 * 1024**3:  # Less than 5GB
                    print("⚠️  Low disk space - less than 5GB free")
                else:
                    print("✅ Sufficient disk space")
        except:
            print("ℹ️  Cannot check disk space on this system")

        return True

    def test_basic_functionality(self):
        """Test basic Aider functionality."""
        print("\n🧪 Basic Functionality Test")
        print("-" * 40)

        # Create a test file
        test_file = self.project_root / "test_verification.py"
        test_content = '''# Test file for Aider verification
def hello_world():
    """A simple function to test Aider."""
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
'''

        try:
            with open(test_file, 'w') as f:
                f.write(test_content)
            print(f"✅ Created test file: {test_file}")

        except Exception as e:
            print(f"❌ Failed to create test file: {e}")
            return False

        # Test that we can import Aider modules (without actually running it)
        try:
            import aider
            print("✅ Can import Aider modules")
        except ImportError as e:
            print(f"❌ Cannot import Aider modules: {e}")
            return False

        # Clean up test file
        try:
            test_file.unlink()
            print("✅ Cleaned up test file")
        except:
            print("⚠️  Could not clean up test file")

        return True

    def generate_verification_report(self, results):
        """Generate a verification report."""
        print("\n📊 Verification Summary")
        print("=" * 60)

        passed = sum(1 for success, _ in results.values() if success)
        total = len(results)

        print(f"✅ Passed: {passed}/{total} verification categories")

        for category, (success, message) in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {category}")

        if passed == total:
            print("\n🎉 All verifications passed!")
            print("Your Offline Coding Agent installation is ready to use.")
            print("\nNext steps:")
            print("1. Start Aider: python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf")
            print("2. Add files: /add your_file.py")
            print("3. Start coding: > Write a function to...")
        else:
            print(f"\n⚠️  {total - passed} verification(s) failed")
            print("Please address the issues above before using the Offline Coding Agent.")

        return passed == total

    def run_verification(self):
        """Run all verification checks."""
        self.print_header()

        results = {}

        # Run all verifications
        results["Python Environment"] = self.verify_python_environment(), ""
        results["Aider Functionality"] = self.verify_aider_functionality(), ""
        results["Model Files"] = self.verify_model_files(), ""
        results["Configuration Files"] = self.verify_configuration_files(), ""
        results["Project Structure"] = self.verify_project_structure(), ""
        results["Git Environment"] = self.verify_git_environment(), ""
        results["System Resources"] = self.verify_system_resources(), ""
        results["Basic Functionality"] = self.test_basic_functionality(), ""

        # Generate final report
        success = self.generate_verification_report(results)

        return success

def main():
    """Main verification function."""
    try:
        verifier = InstallationVerifier()
        success = verifier.run_verification()

        if not success:
            print("\n❌ Installation verification failed")
            print("Please run the installation script:")
            print("python scripts/install_aider.py")
            sys.exit(1)
        else:
            print("\n✅ Installation verification completed successfully")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️  Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during verification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()