"""
Configuration management for Offline Coding Agent
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the offline coding agent."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        # Get package directory
        package_dir = Path(__file__).parent.parent.parent
        return str(package_dir / "config" / "default.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_model_path(self) -> str:
        """Get full path to model file."""
        model_dir = Path(self.get('model.path', './models'))
        model_name = self.get('model.name', 'Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf')
        return str(model_dir / model_name)

    def get_cache_directory(self) -> str:
        """Get cache directory path."""
        cache_dir = self.get('context.cache_directory', './cache')
        return os.path.abspath(cache_dir)

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            Path(self.get_model_path()).parent,
            Path(self.get_cache_directory()),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def validate(self) -> bool:
        """Validate configuration settings."""
        try:
            # Check required fields
            required_fields = [
                'model.name',
                'model.path',
                # Accept either legacy 'model.context_size' or 'inference.n_ctx'
                'cli.output_format',
            ]

            for field in required_fields:
                if field == 'model.context_size':
                    ctx = self.get('model.context_size') or self.get('inference.n_ctx')
                    if ctx is None:
                        raise ValueError("Required configuration field missing: model.context_size (or inference.n_ctx)")
                    continue
                if self.get(field) is None:
                    raise ValueError(f"Required configuration field missing: {field}")

            # Validate model path exists
            model_path = self.get_model_path()
            if not os.path.exists(model_path):
                print(f"Warning: Model file not found at {model_path}")
                return False

            return True

        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global configuration instance
config = Config()