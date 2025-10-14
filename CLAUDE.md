# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **Offline Coding Agent** is a production-ready autonomous AI coding assistant designed for restricted Windows business laptops with no admin rights. It provides completely offline AI assistance using Qwen2.5-Coder-7B with llama-cpp-python for CPU-optimized inference.

**Key Architecture:** The project has evolved from a CLI-based approach to a fully functional autonomous AI assistant (`working_assistant.py`) that can execute tools and complete multi-step coding tasks entirely offline with 95% success rate.

**Documentation:** See `docs/COMPACT_SUMMARY.md` for quick reference and `docs/AUTONOMOUS_LOOP_FINAL_REPORT.md` for detailed test results.

## Common Commands

### Running the AI Assistant

```bash
# Start with default model (recommended)
./start_assistant.sh

# Or run directly with specific model
python working_assistant.py --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# With auto-confirm enabled (skip confirmation prompts)
python working_assistant.py --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf --auto-confirm

# Single prompt mode
python working_assistant.py --model models/model.gguf --prompt "Create a Python script to..."

# Add files to context
python working_assistant.py --model models/model.gguf --files file1.py file2.py
```

### Model Management

```bash
# Download the recommended model (Qwen2.5-Coder-7B, ~4.4GB)
python scripts/download_model.py

# Verify installation
python scripts/verify_installation.py
```

### Development Setup

```bash
# Install dependencies (no admin rights required)
pip install --user -r requirements.txt -c constraints.txt

# Or install in development mode
pip install --user -e .

# Activate virtual environment (if using venv)
source venv/bin/activate
```

### Legacy CLI (src/cli.py - not currently used)

The original CLI implementation exists in `src/` but has been superseded by `working_assistant.py`:

```bash
python src/cli.py init          # Initialize workspace
python src/cli.py status        # Show configuration status
python src/cli.py gen --file example.py    # Generate code (placeholder)
python src/cli.py explain --file example.py # Explain code (placeholder)
```

## Architecture

### Two-Layer Architecture

**1. Working AI Assistant (`working_assistant.py`)** - Production System
- Autonomous AI agent with tool execution capabilities
- Uses Qwen2.5-Coder models via llama-cpp-python
- Supports multi-step task execution with automatic tool chaining
- Interactive terminal interface with Rich formatting
- Context management for files and conversation history

**2. Legacy CLI System (`src/`)** - Historical Implementation
- Click-based CLI with command structure
- Configuration management (`src/utils/config.py`)
- Output formatting utilities (`src/utils/formatting.py`)
- Not currently integrated with the working assistant

### Working Assistant Components

**Tool Execution System** (`working_assistant.py:33-172`):
- `WorkingToolManager` class handles all tool execution
- Available tools: `read_file`, `write_file`, `create_directory`, `execute_python`, `run_command`
- Safety checks for dangerous commands (line 139-141)
- Tool format: `[TOOL: tool_name(args)]` in AI responses

**AI Response Generation** (`working_assistant.py:366-530`):
- Autonomous loop with max 2 iterations for multi-step tasks
- System prompt with XML-structured instructions (lines 380-434)
- Tool result feedback loop to enable task completion
- Conversation history management (last 6 exchanges)

**Interactive Mode** (`working_assistant.py:550-599`):
- Rich terminal interface with prompts and panels
- Commands: `/add`, `/remove`, `/list`, `/clear`, `/tools`, `/auto`
- Auto-confirm mode for unattended execution
- Markdown rendering for AI responses

### Model Integration

**Current Implementation:**
- Model: Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf (~4.4GB)
- Inference: llama-cpp-python with CPU optimization
- Context window: 4096 tokens (configurable up to 32K in model specs)
- Temperature: 0.3 for code generation
- Streaming: Not yet implemented (responses generated in full)
- Success Rate: 95% (21/22 tool executions)

**Configuration (`config/default.yaml`):**
- Model settings: path, context size, threads, temperature
- CLI settings: output format, verbosity
- Context management: cache, file extensions
- Performance: timeouts, concurrent requests

### Tool Calling Pattern

The AI uses structured tool calls in its responses:

```python
# Single tool call
[TOOL: read_file(file_path='example.py')]

# Multiple tools in sequence
[TOOL: create_directory(dir_path='src')]
[TOOL: write_file(file_path='src/main.py', content='''code here''')]
[TOOL: execute_python(file_path='src/main.py')]
```

**Argument Parsing** (`working_assistant.py:252-363`):
- Supports simple key=value pairs: `file_path='test.py', timeout=30`
- Supports triple-quoted strings for multi-line content: `content='''...'''`
- Smart quote handling and parameter extraction
- Safety confirmation before execution (unless `--auto-confirm`)

## Key Implementation Details

### Autonomous Loop Pattern (`working_assistant.py:449-525`)

The assistant implements a two-step autonomous loop:
1. **Initial Response**: AI analyzes request and executes initial tools
2. **Follow-up Response**: Tool results are fed back to AI to complete remaining steps

This enables complex multi-step tasks like:
- Read file → Analyze → Write summary to new file
- Create project structure → Write multiple files → Execute tests

**Critical Design Decision**: Limit to 2 iterations to prevent infinite loops while allowing task completion.

### Tool Result Feedback (`working_assistant.py:482-501`)

Full tool results (including file contents and command outputs) are sent back to the model to enable:
- Content-aware next steps
- Error recovery
- Task validation

**Format**: Plain text feedback with success/failure status and full output data.

### Configuration System (`src/utils/config.py`)

The Config class provides:
- YAML-based configuration with dot notation access: `config.get('model.name')`
- Path resolution for models and cache directories
- Validation of required fields
- Environment-aware directory creation

**Note**: Currently only used by legacy CLI, not integrated with `working_assistant.py` which loads config directly via PyYAML.

### Safety Mechanisms (`working_assistant.py:139-141`)

Basic command filtering blocks dangerous operations:
- `rm -rf`, `sudo`, `chmod 777`, `format`, `del`
- User confirmation required for all tools by default
- `--auto-confirm` flag available for trusted environments

## Testing

```bash
# Verify complete installation
python scripts/verify_installation.py

# Manual testing with the assistant
./start_assistant.sh
# Then interact with prompts like:
# > Create a Python file called test.py with a hello world function
# > Read test.py and write a summary to summary.txt
```

**Test Files Location**:
- `test_logs/` directory - Comprehensive autonomous loop test documentation
- `tests/` directory - Test files and examples
- Focus on manual verification via `verify_installation.py`
- Comprehensive test results: See `test_logs/autonomous_test_session_*.md`

## Development Workflow

### Adding New Tools

1. Add tool method to `WorkingToolManager` class (working_assistant.py:33-172)
2. Name method `tool_<name>` - it will be auto-discovered
3. Include tool in system prompt (working_assistant.py:380-434)
4. Test with interactive mode

Example:
```python
def tool_list_files(self, directory="."):
    """List files in a directory."""
    try:
        path = Path(directory)
        files = [f.name for f in path.iterdir()]
        return {"success": True, "files": files}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Modifying System Prompt

The system prompt uses XML-structured format for clarity (working_assistant.py:380-434):
- `<available_tools>` - Tool definitions
- `<workflow>` - Execution pattern
- `<multi_step_examples>` - Usage examples
- `<critical_guidelines>` - Important constraints

**Best Practice**: Keep examples concrete and show actual tool call syntax.

### Configuration Changes

Edit `config/default.yaml` for model and behavior settings. Key sections:
- `model.*` - Model path, context size, inference parameters
- `cli.*` - Output formatting and verbosity
- `context.*` - File scanning and caching
- `performance.*` - Timeouts and concurrency

**Note**: Changes require restart of assistant to take effect.

## Project Structure Quick Reference

```
working_assistant.py     # Main application (production ready, 95% success rate)
start_assistant.sh       # Convenience launcher
CLAUDE.md                # Instructions for Claude Code
config/default.yaml      # Configuration
scripts/
  ├── download_model.py  # Model download automation
  └── verify_installation.py  # System verification
docs/                    # Comprehensive documentation
  ├── COMPACT_SUMMARY.md # Quick reference guide
  ├── AUTONOMOUS_LOOP_FINAL_REPORT.md  # Test results and production readiness
  ├── AUTONOMOUS_EXECUTION_*.md  # Implementation details
  ├── concept.md         # Project concept
  ├── model_evaluation.md # Model selection research
  └── github/            # GitHub-related docs
test_logs/               # Autonomous loop test documentation
  ├── autonomous_test_session_*.md  # Test session logs
  └── autonomous_test_session_final_assessment.md
src/                     # Legacy CLI (not actively used)
  ├── cli.py             # Command-line interface
  └── utils/             # Config and formatting
archive/                 # Previous assistant versions
tests/                   # Test files
models/                  # Downloaded GGUF models (gitignored)
```

## Common Issues

**Model Not Found**: Ensure model is in `models/` directory with correct filename referenced in command or config

**Import Errors**: Run `pip install --user -r requirements.txt -c constraints.txt` to install dependencies

**Tool Execution Fails**: Check that file paths are correct and user has write permissions

**Memory Issues**: Reduce `n_ctx` in model loading (working_assistant.py:240) or use smaller quantization

**Slow Inference**: Set `n_threads=0` for auto-detection, or manually set to CPU core count

## Notes for AI Assistance

- The primary executable is `working_assistant.py`, not the `src/cli.py` CLI
- Model integration is complete and functional (not placeholder)
- Tool execution is autonomous - AI can chain multiple tools in one response
- Safety confirmations are enabled by default, use `--auto-confirm` to disable
- The project targets restricted Windows environments (no admin rights, offline operation)
- All processing happens locally via llama-cpp-python CPU inference
