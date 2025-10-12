#!/usr/bin/env python3
"""
Model Download Script for Qwen2.5-Coder-8B
Downloads the GGUF quantized model from Hugging Face.
"""

import os
import sys
import hashlib
import requests
from pathlib import Path
from tqdm import tqdm
import yaml
import json

# Model configuration
MODEL_CONFIG = {
    "name": "Qwen2.5-Coder-8B-Instruct-GGUF",
    "repo_id": "bartowski/Qwen2.5-Coder-8B-Instruct-GGUF",
    "filename": "qwen2.5-coder-8b-instruct.Q4_K_M.gguf",
    "expected_size": 4_950_000_000,  # ~4.95GB
    "sha256_checksum": None,  # Will be populated if available
    "description": "Qwen2.5-Coder-8B 4-bit quantized (Q4_K_M) - Optimal for CPU inference"
}

class ModelDownloader:
    def __init__(self, models_dir="models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.model_file = self.models_dir / MODEL_CONFIG["filename"]
        self.temp_file = self.model_file.with_suffix(".gguf.tmp")

    def get_model_info(self):
        """Display model information."""
        print("🧠 Model Information")
        print("=" * 50)
        print(f"Name: {MODEL_CONFIG['name']}")
        print(f"Repository: {MODEL_CONFIG['repo_id']}")
        print(f"Filename: {MODEL_CONFIG['filename']}")
        print(f"Expected Size: {MODEL_CONFIG['expected_size'] / (1024**3):.1f} GB")
        print(f"Description: {MODEL_CONFIG['description']}")
        print(f"Download Path: {self.model_file}")
        print()

    def check_existing_model(self):
        """Check if model already exists and is valid."""
        if not self.model_file.exists():
            return False

        file_size = self.model_file.stat().st_size
        expected_size = MODEL_CONFIG["expected_size"]

        print(f"📁 Found existing model file: {self.model_file}")
        print(f"📊 File size: {file_size / (1024**3):.1f} GB")
        print(f"📊 Expected size: {expected_size / (1024**3):.1f} GB")

        # Check file size (allow 5% tolerance)
        size_tolerance = expected_size * 0.05
        if abs(file_size - expected_size) > size_tolerance:
            print("⚠️  File size doesn't match expected size - may be corrupted")
            return False

        print("✅ Model file exists with correct size")
        return True

    def get_download_url(self):
        """Get the direct download URL from Hugging Face."""
        base_url = "https://huggingface.co"
        repo_id = MODEL_CONFIG["repo_id"]
        filename = MODEL_CONFIG["filename"]

        # Try the direct URL first
        direct_url = f"{base_url}/{repo_id}/resolve/main/{filename}"

        return direct_url

    def download_with_requests(self, url):
        """Download file using requests with progress bar."""
        try:
            # Get file size first
            with requests.get(url, stream=True, timeout=10) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))

            # Download with progress bar
            with requests.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()

                with open(self.temp_file, 'wb') as f:
                    with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        desc="Downloading Model"
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))

            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Download failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n⚠️  Download cancelled by user")
            if self.temp_file.exists():
                self.temp_file.unlink()
            return False

    def download_with_curl(self, url):
        """Alternative download method using curl (if available)."""
        try:
            # Check if curl is available
            subprocess.run(["curl", "--version"], capture_output=True, check=True)

            cmd = [
                "curl", "-L", "-o", str(self.temp_file), url,
                "--progress-bar"
            ]

            print("🔄 Using curl for download (may be more reliable)...")
            result = subprocess.run(cmd)

            return result.returncode == 0

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  curl not available, falling back to requests")
            return None

    def verify_download(self):
        """Verify the downloaded file."""
        if not self.temp_file.exists():
            print("❌ Downloaded file not found")
            return False

        file_size = self.temp_file.stat().st_size
        expected_size = MODEL_CONFIG["expected_size"]

        print(f"📊 Downloaded size: {file_size / (1024**3):.1f} GB")
        print(f"📊 Expected size: {expected_size / (1024**3):.1f} GB")

        # Size verification
        size_tolerance = expected_size * 0.05
        if abs(file_size - expected_size) > size_tolerance:
            print("❌ File size verification failed - download may be incomplete")
            return False

        print("✅ File size verification passed")

        # Optional: Checksum verification if available
        if MODEL_CONFIG["sha256_checksum"]:
            print("🔍 Verifying SHA256 checksum...")
            sha256_hash = hashlib.sha256()

            with open(self.temp_file, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            calculated_checksum = sha256_hash.hexdigest()
            expected_checksum = MODEL_CONFIG["sha256_checksum"]

            if calculated_checksum == expected_checksum:
                print("✅ SHA256 checksum verification passed")
            else:
                print("❌ SHA256 checksum verification failed")
                print(f"Expected: {expected_checksum}")
                print(f"Calculated: {calculated_checksum}")
                return False

        return True

    def finalize_download(self):
        """Move temporary file to final location."""
        try:
            self.temp_file.rename(self.model_file)
            print(f"✅ Model saved to: {self.model_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to save model: {e}")
            return False

    def create_model_metadata(self):
        """Create metadata file for the downloaded model."""
        metadata = {
            "model_name": MODEL_CONFIG["name"],
            "filename": MODEL_CONFIG["filename"],
            "repo_id": MODEL_CONFIG["repo_id"],
            "download_date": str(Path().absolute()),
            "file_size": self.model_file.stat().st_size,
            "expected_size": MODEL_CONFIG["expected_size"],
            "description": MODEL_CONFIG["description"],
            "quantization": "Q4_K_M",
            "context_length": 32768,
            "recommended_ram": "32GB",
            "inference_engine": "llama.cpp",
            "platform": "CPU-only"
        }

        metadata_file = self.model_file.with_suffix(".json")
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"✅ Created metadata file: {metadata_file}")
        except Exception as e:
            print(f"⚠️  Could not create metadata file: {e}")

    def download_model(self):
        """Main download function."""
        self.get_model_info()

        # Check if model already exists
        if self.check_existing_model():
            response = input("Model already exists. Re-download? (y/N): ")
            if response.lower() != 'y':
                print("✅ Using existing model file")
                return True

        # Get download URL
        url = self.get_download_url()
        print(f"📥 Download URL: {url}")

        # Check disk space
        required_space = MODEL_CONFIG["expected_size"] * 1.1  # 10% extra
        try:
            stat = os.statvfs(self.models_dir) if hasattr(os, 'statvfs') else None
            if stat:
                free_space = stat.f_bavail * stat.f_frsize
                if free_space < required_space:
                    print(f"❌ Insufficient disk space")
                    print(f"Required: {required_space / (1024**3):.1f} GB")
                    print(f"Available: {free_space / (1024**3):.1f} GB")
                    return False
        except:
            pass

        # Download attempt
        print("\n🚀 Starting model download...")
        print("This may take a while depending on your internet connection.")
        print("Press Ctrl+C to cancel.\n")

        # Try requests first, then curl if available
        success = self.download_with_requests(url)

        if not success:
            print("⚠️  Primary download method failed")
            curl_result = self.download_with_curl(url)
            if curl_result is False:  # curl failed
                success = False
            elif curl_result is True:  # curl succeeded
                success = True
            # None means curl not available, stay with requests result

        if not success:
            print("❌ Model download failed")
            return False

        # Verify download
        print("\n🔍 Verifying download...")
        if not self.verify_download():
            print("❌ Download verification failed")
            if self.temp_file.exists():
                self.temp_file.unlink()
            return False

        # Finalize
        if not self.finalize_download():
            return False

        # Create metadata
        self.create_model_metadata()

        print("\n🎉 Model download completed successfully!")
        return True

def print_usage_instructions():
    """Print instructions for using the downloaded model."""
    print("\n📖 Usage Instructions")
    print("=" * 50)
    print("1. Start Aider with the downloaded model:")
    print("   python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf")
    print()
    print("2. Or specify the full path:")
    print(f"   python -m aider --model {Path.cwd()}/models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf")
    print()
    print("3. Add files to context:")
    print("   /add your_file.py")
    print()
    print("4. Start coding with natural language:")
    print("   > Write a Python function to validate email addresses")
    print()
    print("5. For more help:")
    print("   python -m aider --help")
    print("   Check docs/aider_setup_guide.md")

def main():
    """Main function."""
    print("🤖 Offline Coding Agent - Model Downloader")
    print("=" * 50)
    print("Downloading Qwen2.5-Coder-8B for offline coding")
    print()

    try:
        downloader = ModelDownloader()

        if downloader.download_model():
            print_usage_instructions()
        else:
            print("\n❌ Model download failed")
            print("Please check:")
            print("- Internet connection")
            print("- Available disk space (at least 6GB free)")
            print("- Hugging Face accessibility")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Download cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()