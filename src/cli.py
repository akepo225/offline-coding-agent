#!/usr/bin/env python3
"""
Main CLI entry point for Offline Coding Agent
"""

import click
import os
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import config
from utils.formatting import print_error, print_success, print_info, format_response


@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """Offline Coding Agent - AI-powered coding assistant that operates completely offline."""
    ctx.ensure_object(dict)

    # Load configuration
    try:
        if config:
            from utils.config import Config
            ctx.obj['config'] = Config(config)
        else:
            ctx.obj['config'] = ctx.obj.get('config', ctx.obj['config'])

        ctx.obj['verbose'] = verbose

        if verbose:
            print_info(f"Using configuration: {ctx.obj['config'].config_file}")

    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, help='File to analyze/generate code for')
@click.option('--language', '-l', help='Programming language')
@click.option('--prompt', '-p', help='Additional prompt context')
@click.option('--format', 'output_format', default='text', type=click.Choice(['text', 'json']))
@click.pass_context
def gen(ctx, file, language, prompt, output_format):
    """Generate code based on existing file or description."""
    try:
        file_path = Path(file)

        if not file_path.exists():
            print_error(f"File not found: {file}")
            return

        # Detect language if not specified
        if not language:
            language = _detect_language(file_path)

        if ctx.obj.get('verbose'):
            print_info(f"Generating code for {file} (language: {language})")

        # TODO: Implement actual model inference
        # For now, return a placeholder response
        response = {
            "content": f"""# Generated code for {file}

```{language}
# This is a placeholder response
# The actual implementation will use DeepSeek-Coder-1.3B model
# to generate intelligent code based on your input

def example_function():
    # Generated code will appear here
    pass
```

*Note: This is a proof-of-concept. Full model integration coming soon.*""",
            "model": "deepseek-coder-1.3b",
            "file": str(file_path),
            "language": language
        }

        format_response(response, output_format)

    except Exception as e:
        print_error(f"Code generation failed: {e}")


@cli.command()
@click.option('--file', '-f', required=True, help='File to explain')
@click.option('--format', 'output_format', default='text', type=click.Choice(['text', 'json']))
@click.pass_context
def explain(ctx, file, output_format):
    """Explain what a piece of code does."""
    try:
        file_path = Path(file)

        if not file_path.exists():
            print_error(f"File not found: {file}")
            return

        if ctx.obj.get('verbose'):
            print_info(f"Explaining code in {file}")

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # TODO: Implement actual model inference
        response = {
            "content": f"""# Code Explanation for {file}

This file contains code that would be analyzed and explained by the DeepSeek-Coder model.

**Current content preview:**
```
{content[:200]}{'...' if len(content) > 200 else ''}
```

*Note: This is a proof-of-concept. Full model integration coming soon.*""",
            "model": "deepseek-coder-1.3b",
            "file": str(file_path),
            "language": _detect_language(file_path)
        }

        format_response(response, output_format)

    except Exception as e:
        print_error(f"Code explanation failed: {e}")


@cli.command()
@click.option('--directory', '-d', default='.', help='Directory to initialize')
@click.pass_context
def init(ctx, directory):
    """Initialize workspace and scan for project files."""
    try:
        dir_path = Path(directory).resolve()

        if ctx.obj.get('verbose'):
            print_info(f"Initializing workspace in {dir_path}")

        # Create necessary directories
        ctx.obj['config'].ensure_directories()

        # Scan directory for files
        extensions = ctx.obj['config'].get('context.file_extensions', [])
        files = []

        for ext in extensions:
            files.extend(dir_path.rglob(f"*{ext}"))

        print_success(f"Workspace initialized. Found {len(files)} relevant files.")

        if ctx.obj.get('verbose'):
            for file in files[:10]:  # Show first 10 files
                print(f"  - {file.relative_to(dir_path)}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")

    except Exception as e:
        print_error(f"Workspace initialization failed: {e}")


@cli.command()
@click.pass_context
def status(ctx):
    """Show current status and configuration."""
    try:
        config_obj = ctx.obj['config']

        print_info("Offline Coding Agent Status")
        print(f"Model: {config_obj.get('model.name')}")
        print(f"Model Path: {config_obj.get_model_path()}")
        print(f"Context Size: {config_obj.get('model.context_size')}")
        print(f"Cache Directory: {config_obj.get_cache_directory()}")

        # Check if model exists
        model_path = config_obj.get_model_path()
        if os.path.exists(model_path):
            model_size = os.path.getsize(model_path) / (1024 * 1024 * 1024)  # GB
            print_success(f"Model found: {model_size:.1f} GB")
        else:
            print_warning(f"Model not found at {model_path}")

        # Check configuration validity
        if config_obj.validate():
            print_success("Configuration is valid")
        else:
            print_warning("Configuration has issues")

    except Exception as e:
        print_error(f"Status check failed: {e}")


def _detect_language(file_path: Path) -> str:
    """Detect programming language from file extension."""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bat': 'batch',
        '.ps1': 'powershell',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.less': 'less',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.md': 'markdown',
    }

    suffix = file_path.suffix.lower()
    return extension_map.get(suffix, 'text')


def main():
    """Main entry point."""
    # Initialize config with default instance
    cli(obj={'config': config})


if __name__ == '__main__':
    main()