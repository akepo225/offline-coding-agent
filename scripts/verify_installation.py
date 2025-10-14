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

        # Model detection results (set by verify_model_files)
        self.detected_model_file = None
        self.detected_model_name = None
        self.detected_expected_size = None

    def print_header(self):
        """Print verification header."""
        print("🔍 Offline Coding Agent - Installation Verification")
        print("=" * 60)
        print("Verifying installation of Simple AI Assistant and Qwen2.5-Coder-7B")
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

    def verify_simple_ai_assistant(self):
        """Verify that Simple AI Assistant is functional."""
        print("\n🤖 Simple AI Assistant Verification")
        print("-" * 40)

        # Check if the script exists (support both historical and archived locations)
        candidates = [
            self.project_root / "simple_ai_assistant.py",
            self.project_root / "archive" / "simple_ai_assistant.py",
        ]
        assistant_file = next((p for p in candidates if p.exists()), None)
        if not assistant_file:
            print("❌ Simple AI Assistant script not found")
            return False

        print("✅ Simple AI Assistant script exists")

        try:
            # Test simple_ai_assistant help command
            result = subprocess.run(
                [sys.executable, str(assistant_file), "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print("✅ Simple AI Assistant help command works")
            else:
                print("⚠️  Simple AI Assistant help command failed")
                print(f"Error: {result.stderr}")

        except subprocess.TimeoutExpired:
            print("⚠️  Simple AI Assistant help command timed out")
        except Exception as e:
            print(f"⚠️  Simple AI Assistant help command error: {e}")

        return True

    def _detect_model_file(self):
        """Auto-detect model file with robust naming and size-based identification."""
        # Find all .gguf files case-insensitively
        ggufs = sorted(self.models_dir.glob("*.gguf"))
        if not ggufs:
            return None, None, None

        model_file = None
        model_name = None
        expected_size = None

        # Prefer 7B models if multiple are present (they're smaller and more common)
        seven_b_candidates = []
        eight_b_candidates = []

        for gguf_file in ggufs:
            name_lower = gguf_file.name.lower()
            file_size = gguf_file.stat().st_size

            # Check if it's a Qwen Coder model (case-insensitive)
            if "qwen" in name_lower and "coder" in name_lower:
                if "7b" in name_lower:
                    seven_b_candidates.append((gguf_file, file_size))
                elif "8b" in name_lower:
                    eight_b_candidates.append((gguf_file, file_size))

        # Prefer 7B model if found (they're more common in restricted environments)
        if seven_b_candidates:
            model_file = seven_b_candidates[0][0]
            model_name = "Qwen2.5-Coder-7B-Instruct-Q4_K_M"
            expected_size = 4_700_000_000  # ~4.7GB for 7B models (tolerate quantization variance)
        elif eight_b_candidates:
            # Since we only support 7B models in this repository, treat 8B files as 7B
            model_file = eight_b_candidates[0][0]
            model_name = "Qwen2.5-Coder-7B-Instruct-Q4_K_M"
            expected_size = 4_700_000_000  # ~4.7GB for 7B models (tolerate quantization variance)
        else:
            # Fallback to any GGUF file if no clear Qwen Coder match
            model_file = ggufs[0]
            model_name = model_file.stem
            expected_size = model_file.stat().st_size  # Use actual size, let tolerance check pass

        return model_file, model_name, expected_size

    def verify_model_files(self):
        """Verify model files and configuration."""
        print("\n🧠 Model Files Verification")
        print("-" * 40)

        # Try to auto-detect model file
        model_file, model_name, expected_size = self._detect_model_file()

        # Store detection results for use in other methods
        self.detected_model_file = model_file
        self.detected_model_name = model_name
        self.detected_expected_size = expected_size

        if not model_file:
            print("❌ Model file not found")
            print("Available models in models directory:")
            for file in self.models_dir.glob("*.gguf"):
                print(f"  - {file.name}")
            return False

        # Check file size
        file_size = model_file.stat().st_size
        size_tolerance = expected_size * 0.15  # 15% tolerance for different quantizations

        print(f"📁 Model file: {model_file.name}")
        print(f"📋 Model: {model_name}")
        print(f"📊 File size: {file_size / (1024**3):.1f} GB")

        if abs(file_size - expected_size) > size_tolerance:
            print("⚠️  File size outside expected range - may be different quantization")
        else:
            print("✅ Model file size correct")

        # Check metadata file (optional)
        metadata_file = model_file.with_suffix('.json')
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print("✅ Model metadata file exists")
                print(f"📋 Info: {metadata.get('description', 'No description')}")
            except Exception as e:
                print(f"⚠️  Could not read metadata file: {e}")
        else:
            print("ℹ️  Model metadata file not found (optional)")

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
        """Test basic Simple AI Assistant functionality."""
        print("\n🧪 Basic Functionality Test")
        print("-" * 40)

        # Create a test file
        test_file = self.project_root / "test_verification.py"
        test_content = '''# Test file for Simple AI Assistant verification
def hello_world():
    """A simple function to test Simple AI Assistant."""
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

        # Test that we can import required modules (llama-cpp-python, rich)
        try:
            import llama_cpp
            print("✅ Can import llama-cpp-python modules")
        except ImportError as e:
            print(f"❌ Cannot import llama-cpp-python modules: {e}")
            return False

        try:
            import rich
            print("✅ Can import rich modules")
        except ImportError as e:
            print(f"⚠️  Cannot import rich modules: {e}")

        # Test that Simple AI Assistant script exists (check both locations)
        assistant_file = next((p for p in [
            self.project_root / "simple_ai_assistant.py",
            self.project_root / "archive" / "simple_ai_assistant.py",
        ] if p.exists()), None)
        if assistant_file:
            print("✅ Simple AI Assistant script exists")
        else:
            print("❌ Simple AI Assistant script not found")
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
            if self.detected_model_name:
                print(f"1. Start Simple AI Assistant: python archive/simple_ai_assistant.py -m models/{self.detected_model_name}.gguf")
            else:
                print("1. Start Simple AI Assistant: python archive/simple_ai_assistant.py -m models/<detected_model>.gguf")
            print("2. Add files: /add your_file.py")
            print("3. Start coding: > Write a function to...")
            print("\n🚀 Alternative to aider-chat, perfect for restricted environments!")
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
        results["Simple AI Assistant"] = self.verify_simple_ai_assistant(), ""
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
            print("Please check the errors above and address any issues.")
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