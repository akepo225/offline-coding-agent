"""
Offline Coding Agent

An AI-powered coding assistant that operates completely offline.
"""

__version__ = "0.1.0"
__author__ = "Offline Coder Team"
__email__ = "contact@offline-coder.com"

from .cli import main
from .model.engine import ModelEngine
from .context.manager import ContextManager

__all__ = ["main", "ModelEngine", "ContextManager"]