#!/usr/bin/env python3
"""
Working AI Assistant - Actually executes tools when AI requests them
"""

import os
import sys
import argparse
import subprocess
import json
import re
import shlex
from pathlib import Path
import yaml
from datetime import datetime

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("Warning: llama-cpp-python not installed. Model loading will not work.")

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich not installed. Terminal output will be plain.")

class WorkingToolManager:
    """Tool manager that actually executes tools."""

    def __init__(self, console=None, sandbox_root=None, allowed_git_subcommands=None):
        self.console = console
        self.working_directory = Path.cwd()
        # Sandbox limits file operations; default to current working directory
        self.sandbox_root = Path(sandbox_root).resolve() if sandbox_root else Path.cwd().resolve()
        # Restrict git subcommands to a safe subset
        self.allowed_git_subcommands = set(allowed_git_subcommands or {
            "init", "config", "status", "add", "commit", "diff", "log", "restore"
        })

    def execute_tool(self, tool_name, tool_args):
        """Execute a tool and return results."""
        tool_function = getattr(self, f"tool_{tool_name}", None)
        if not tool_function:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}

        try:
            result = tool_function(**tool_args)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_read_file(self, file_path):
        """Read contents of a file."""
        try:
            path = self._resolve_within_sandbox(file_path)
            if path is None:
                return {"success": False, "error": "Access denied: path is outside sandbox"}
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "message": f"Successfully read {len(content)} characters"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_write_file(self, file_path, content):
        """Write content to a file."""
        try:
            path = self._resolve_within_sandbox(file_path)
            if path is None:
                return {"success": False, "error": "Access denied: path is outside sandbox"}
            path.parent.mkdir(parents=True, exist_ok=True)

            # Conditionally fix escaped characters from model output
            # Only unescape if content appears to be model-generated (contains \\n/\\t but lacks
            # contexts where literal escapes are common like code blocks, LaTeX, etc.)
            if self._should_unescape_model_output(content):
                content = content.replace('\\n', '\n').replace('\\t', '\t')

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "message": f"Successfully wrote {len(content)} characters to {file_path}",
                "bytes_written": len(content)  # For validation
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_append_file(self, file_path, content):
        """Append content to a file (creates it if missing)."""
        try:
            path = self._resolve_within_sandbox(file_path)
            if path is None:
                return {"success": False, "error": "Access denied: path is outside sandbox"}
            path.parent.mkdir(parents=True, exist_ok=True)

            if self._should_unescape_model_output(content):
                content = content.replace('\\n', '\n').replace('\\t', '\t')

            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "message": f"Successfully appended {len(content)} characters to {file_path}",
                "bytes_written": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_list_directory(self, dir_path):
        """List directory entries."""
        try:
            path = self._resolve_within_sandbox(dir_path)
            if path is None:
                return {"success": False, "error": "Access denied: path is outside sandbox"}
            if not path.exists() or not path.is_dir():
                return {"success": False, "error": f"Directory not found: {dir_path}"}

            entries = sorted([p.name for p in path.iterdir()])
            return {"success": True, "entries": entries, "message": f"Found {len(entries)} entries"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_create_directory(self, dir_path):
        """Create a directory."""
        try:
            path = self._resolve_within_sandbox(dir_path)
            if path is None:
                return {"success": False, "error": "Access denied: path is outside sandbox"}
            path.mkdir(parents=True, exist_ok=True)

            return {
                "success": True,
                "message": f"Successfully created directory: {dir_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_execute_python(self, code=None, file_path=None, timeout=30):
        """Execute Python code."""
        try:
            # Normalize and validate timeout
            if isinstance(timeout, str):
                try:
                    timeout = float(timeout)
                except ValueError:
                    return {"success": False, "error": "Timeout must be a valid number"}
            if timeout <= 0:
                return {"success": False, "error": "Timeout must be a positive number"}

            if file_path:
                if not Path(file_path).exists():
                    return {"success": False, "error": f"File not found: {file_path}"}

                result = subprocess.run(
                    [sys.executable, file_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.working_directory
                )
            elif code:
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.working_directory
                )
            else:
                return {"success": False, "error": "Either 'code' or 'file_path' must be provided"}

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "message": "Execution completed"
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_run_command(self, command, timeout=30, cwd=None, input=None):
        """Run a shell command with basic hardening (no shell, simple allow-list).

        Args:
            command (str): Command to execute
            timeout (int): Timeout in seconds (default: 30)
            cwd (str, optional): Working directory for command execution
            input (str, optional): Input to pass to command via stdin
        """
        try:
            # Parameter validation and type conversion
            if not isinstance(command, str) or not command.strip():
                return {"success": False, "error": "Command must be a non-empty string"}
            
            # Convert timeout to int if it's a string
            if isinstance(timeout, str):
                try:
                    timeout = int(timeout)
                except ValueError:
                    return {"success": False, "error": "Timeout must be a valid number"}
            
            if timeout <= 0:
                return {"success": False, "error": "Timeout must be a positive number"}
            
            # Handle cwd parameter - convert string 'None' to actual None
            if cwd == 'None' or cwd == 'none':
                cwd = None
            elif cwd is not None and not isinstance(cwd, str):
                return {"success": False, "error": "cwd must be a string or None"}
            
            # Handle input parameter - convert string 'None' to actual None
            if input == 'None' or input == 'none':
                input = None
            elif input is not None and not isinstance(input, str):
                return {"success": False, "error": "input must be a string or None"}

            parts = shlex.split(command)
            if not parts:
                return {"success": False, "error": "Empty command"}

            # Allow‑list of programs (extend conservatively)
            allowed = {"python", "python3", "pip", "pytest", "echo", "git"}
            prog = Path(parts[0]).name.lower()
            if prog not in allowed:
                return {"success": False, "error": f"Command '{prog}' is not allowed"}

            # Normalize Python interpreter to the current interpreter for reliability
            if prog in {"python", "python3"}:
                parts[0] = sys.executable

            # Restrict git subcommands to safe set
            if prog == 'git':
                if len(parts) < 2 or parts[1].startswith('-'):
                    return {"success": False, "error": "git subcommand required"}
                if parts[1] not in self.allowed_git_subcommands:
                    return {"success": False, "error": f"git subcommand '{parts[1]}' is not allowed"}

            # Determine working directory (enforce sandbox if provided)
            if cwd is not None:
                resolved_cwd = self._resolve_within_sandbox(cwd)
                if resolved_cwd is None:
                    return {"success": False, "error": "Access denied: cwd is outside sandbox"}
                working_dir = resolved_cwd
            else:
                working_dir = self.working_directory

            # Prepare stdin input
            stdin_input = input if input is not None else None

            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
                input=stdin_input
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "message": "Command executed"
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_available_tools(self):
        """Return available tools."""
        tools = []
        for attr_name in dir(self):
            if attr_name.startswith('tool_'):
                tool_name = attr_name[5:]
                method = getattr(self, attr_name)
                if callable(method):
                    tools.append(tool_name)
        return sorted(tools)

    def _resolve_within_sandbox(self, input_path):
        """Resolve a path and ensure it stays within the sandbox root."""
        try:
            root = self.sandbox_root
            p = Path(input_path)
            if not p.is_absolute():
                p = (Path.cwd() / p).resolve()
            else:
                p = p.resolve()
            try:
                # Python 3.9+
                if p.is_relative_to(root):
                    return p
            except AttributeError:
                # Fallback for older Pythons
                if str(p).startswith(str(root) + os.sep):
                    return p
            return None
        except Exception:
            return None

    def _should_unescape_model_output(self, content):
        """Determine if content should have escape sequences unescaped.

        Uses heuristics to detect model-generated content vs. files with legitimate
        literal escape sequences (like code files, LaTeX, etc.).
        """
        # Check if content contains escaped sequences
        has_escaped_newlines = '\\n' in content
        has_escaped_tabs = '\\t' in content

        if not (has_escaped_newlines or has_escaped_tabs):
            return False

        # Heuristics that suggest this is NOT model output (so don't unescape)
        # 1. Contains code blocks (backticks)
        if '```' in content:
            return False

        # 2. Contains LaTeX-like markers
        if '\\begin{' in content or '\\end{' in content:
            return False

        # 3. Contains many double backslashes (escaped backslashes)
        double_backslash_count = content.count('\\\\')
        if double_backslash_count > 2:
            return False

        # 4. Contains file format tokens that suggest structured content
        format_indicators = [
            '---',  # YAML frontmatter
            '{\\',  # JSON-like
            'import ',  # Python imports
            '#include',  # C/C++ includes
            '<?php',  # PHP
            '<!DOCTYPE',  # HTML/XML
            'function ',  # JavaScript/TypeScript
            'def ',  # Python functions
            'class ',  # Class definitions
            'public class',  # Java
            'interface ',  # Interface definitions
        ]

        for indicator in format_indicators:
            if indicator in content:
                return False

        # 5. Contains explicit metadata flags or comments
        metadata_indicators = [
            '# ',  # Comments
            '// ',  # Comments
            '/* ',  # Block comments
            '-- ',  # SQL comments
            'TODO:',  # TODO comments
            'FIXME:',  # FIXME comments
            'NOTE:',  # NOTE comments
        ]

        for indicator in metadata_indicators:
            if indicator in content:
                return False

        # 6. Contains legitimate escape sequences in strings (not just newlines/tabs)
        # If there are other escapes like \" or \' , it's likely intentional formatting
        if '\\"' in content or "\\'" in content or '\\\\' in content:
            return False

        # If we get here, it looks like model-generated content with escaped newlines/tabs
        return True

class WorkingAIAssistant:
    """AI Assistant that actually executes tools."""

    def __init__(self, model_path=None, config_path=None):
        self.console = Console() if RICH_AVAILABLE else None
        self.model = None
        self.config = self.load_config(config_path)
        # Model path: prefer explicit file path in args; else combine config model.path + model.name; fallback to default file
        if model_path:
            self.model_path = model_path
        else:
            model_cfg = self.config.get('model', {})
            cfg_dir = model_cfg.get('path', './models')
            cfg_name = model_cfg.get('name', 'Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf')
            self.model_path = str(Path(cfg_dir) / cfg_name)
        self.context_files = []
        # Initialize sandbox and git allowlist from config
        security_cfg = self.config.get('security', {})
        sandbox_root = security_cfg.get('sandbox_root', '.')
        allowed_git_subcommands = security_cfg.get('allowed_git_subcommands', None)

        # Ensure logs directory exists (for verifier compatibility)
        try:
            (Path.cwd() / 'logs').mkdir(exist_ok=True)
        except Exception:
            pass

        self.tool_manager = WorkingToolManager(self.console, sandbox_root=sandbox_root, allowed_git_subcommands=allowed_git_subcommands)
        self.auto_confirm = False
        self.conversation_history = []

    def load_config(self, config_path):
        """Load configuration from YAML file."""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.print_error(f"Failed to load config: {e}")
                return {}
        return {}

    def print_message(self, message, style=None):
        """Print a message with rich formatting."""
        if self.console:
            self.console.print(message, style=style)
        else:
            print(message)

    def print_error(self, message):
        """Print an error message."""
        if self.console:
            self.console.print(f"❌ {message}", style="red")
        else:
            print(f"ERROR: {message}")

    def print_success(self, message):
        """Print a success message."""
        if self.console:
            self.console.print(f"✅ {message}", style="green")
        else:
            print(f"SUCCESS: {message}")

    def print_warning(self, message):
        """Print a warning message."""
        if self.console:
            self.console.print(f"⚠️  {message}", style="yellow")
        else:
            print(f"WARNING: {message}")

    def _ask_confirm(self, prompt, default=True):
        """Ask for user confirmation with fallback to plain input if Rich unavailable."""
        if RICH_AVAILABLE and self.console:
            return Confirm.ask(prompt, default=default)
        try:
            resp = input(f"{prompt} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
            if resp == "":
                return default
            return resp in ("y", "yes")
        except Exception:
            return default

    def load_model(self):
        """Load the local language model."""
        if not LLAMA_AVAILABLE:
            self.print_error("llama-cpp-python not installed")
            return False

        model_file = Path(self.model_path)
        if not model_file.exists():
            self.print_error(f"Model file not found: {self.model_path}")
            return False

        try:
            # Get inference parameters from config with fallback defaults
            inference_config = self.config.get('inference', {})
            model_settings = self.config.get('model_settings', {})

            # Support both old and new config keys for backward compatibility
            n_ctx = inference_config.get('n_ctx', model_settings.get('context_length', 4096))
            n_threads = inference_config.get('n_threads', 0)
            n_batch = inference_config.get('n_batch', 512)
            verbose = inference_config.get('verbose', False)

            self.print_message(f"🧠 Loading model: {model_file.name}")
            self.print_message(f"   Context: {n_ctx} tokens, Threads: {n_threads if n_threads > 0 else 'auto'}, Batch: {n_batch}")

            self.model = Llama(
                model_path=str(model_file),
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_batch=n_batch,
                verbose=verbose
            )
            self.print_success("Model loaded successfully!")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False

    def parse_and_execute_tools(self, response):
        """Parse tool calls from AI response and execute them."""
        # Pattern to match tool calls: [TOOL: tool_name(args)]
        tool_pattern = r'\[TOOL:\s*(\w+)\((.*?)\)\]'
        matches = re.findall(tool_pattern, response, re.DOTALL)

        results = []
        for tool_name, args_str in matches:
            try:
                # Parse arguments
                args = {}
                if args_str.strip():
                    args_str = args_str.strip()

                    # Check for triple-quoted content
                    if "'''" in args_str or '"""' in args_str:
                        # Determine which quote type
                        quote_type = "'''" if "'''" in args_str else '"""'

                        # Split on triple quotes
                        parts = args_str.split(quote_type, 2)
                        if len(parts) >= 3:
                            before_content = parts[0]
                            content = parts[1]

                            # First, parse any simple parameters BEFORE the triple-quoted content
                            # Example: "file_path='test.py', content='''"
                            # We want to extract file_path='test.py'
                            if before_content.strip():
                                # Remove trailing comma and parameter name for the triple-quoted param
                                # Match pattern like: "file_path='value', content=" or "file_path='value',content="
                                simple_params_match = re.match(r'(.*?),?\s*\w+\s*=\s*$', before_content)
                                if simple_params_match:
                                    simple_params_str = simple_params_match.group(1)
                                    # Parse the simple parameters
                                    pairs = [p.strip() for p in simple_params_str.split(',') if p.strip()]
                                    for pair in pairs:
                                        if '=' in pair:
                                            key, value = pair.split('=', 1)
                                            key = key.strip()
                                            value = value.strip()
                                            # Remove quotes from string literals
                                            if (value.startswith('"') and value.endswith('"')) or \
                                               (value.startswith("'") and value.endswith("'")):
                                                value = value[1:-1]
                                            args[key] = value

                                # Extract the parameter name for the triple-quoted content
                                param_match = re.search(r'(\w+)\s*=\s*$', before_content.strip())
                                if param_match:
                                    param_name = param_match.group(1)
                                    args[param_name] = content  # Store content without triple quotes
                    else:
                        # Simple key=value parsing for regular arguments (no triple quotes)
                        # Smart split that respects quotes
                        pairs = []
                        current_pair = ""
                        in_quote = False
                        quote_char = None

                        for char in args_str:
                            if char in ['"', "'"] and (not in_quote or char == quote_char):
                                in_quote = not in_quote
                                quote_char = char if in_quote else None
                                current_pair += char
                            elif char == ',' and not in_quote:
                                if current_pair.strip():
                                    pairs.append(current_pair.strip())
                                current_pair = ""
                            else:
                                current_pair += char

                        # Add last pair
                        if current_pair.strip():
                            pairs.append(current_pair.strip())

                        # Parse each pair
                        for pair in pairs:
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                key = key.strip()
                                value = value.strip()

                                # Handle string literals
                                if (value.startswith('"') and value.endswith('"')) or \
                                   (value.startswith("'") and value.endswith("'")):
                                    value = value[1:-1]

                                args[key] = value

                # Confirm before executing
                if not self.auto_confirm:
                    self.print_warning(f"🔧 Execute tool: {tool_name}({args})")
                    if not self._ask_confirm("Execute this tool?", default=True):
                        results.append({"tool": tool_name, "skipped": True})
                        continue

                # Execute the tool
                result = self.tool_manager.execute_tool(tool_name, args)
                results.append({"tool": tool_name, "result": result})

                # Show result
                if result["success"]:
                    self.print_success(f"✅ {tool_name}: {result.get('message', 'Success')}")
                else:
                    self.print_error(f"❌ {tool_name}: {result.get('error', 'Failed')}")

            except Exception as e:
                self.print_error(f"❌ Failed to execute tool {tool_name}: {e}")
                results.append({"tool": tool_name, "error": str(e)})

        return results

    def generate_response(self, prompt):
        """Generate response and execute tools."""
        if not self.model:
            self.print_error("Model not loaded")
            return ""

        # Build context
        context = ""
        for file_path in self.context_files:
            result = self.tool_manager.execute_tool("read_file", {"file_path": str(file_path)})
            if result["success"]:
                context += f"\n--- File: {file_path} ---\n{result['content']}\n--- End of File ---\n"

        # System prompt with tool instructions (structured with XML tags)
        system_message = f"""You are an autonomous AI assistant that executes tools to complete multi-step tasks.

<available_tools>
1. read_file(file_path) - Read contents of a file
2. write_file(file_path, content) - Write content to a file (IMPORTANT: Use actual newlines (\n), not escaped newlines (\\n) in content)
3. create_directory(dir_path) - Create a directory
4. execute_python(code) OR execute_python(file_path) - Run Python code
5. run_command(command, timeout, cwd, input) - Execute shell command
</available_tools>

<workflow>
1. ANALYZE THE REQUEST
<request_analysis>
- Break down the user's query into components
- Identify required tools and sequence
- Determine if clarification is needed
- Plan the complete workflow before starting
</request_analysis>

2. EXECUTE TOOLS IN SEQUENCE
<tool_execution>
- Use [TOOL: tool_name(args)] format
- Execute tools one after another in the SAME response
- Don't stop until the task is complete
- Each tool result will be fed back to you
- Use ONLY the parameters shown in available_tools
</tool_execution>

3. MULTI-STEP TASK EXAMPLES
<multi_step_examples>
Example 1: "Read file.py and write summary to summary.md"
[TOOL: read_file(file_path='file.py')]
[TOOL: write_file(file_path='summary.md', content='Summary of file.py...')]

Example 2: "Create project structure"
[TOOL: create_directory(dir_path='src')]
[TOOL: create_directory(dir_path='tests')]
[TOOL: write_file(file_path='README.md', content='# Project')]

Example 3: "Create and run Python script"
[TOOL: write_file(file_path='script.py', content='print("test")')]
[TOOL: execute_python(file_path='script.py')]
</multi_step_examples>
</workflow>

Context: {context if context else "No files in context."}

<critical_guidelines>
- COMPLETE THE FULL TASK - don't stop after one step
- Use MULTIPLE tool calls in one response when needed
- After reading files, immediately use the content
- DO NOT explain plans - EXECUTE with tool calls
- Be AUTONOMOUS - chain tools together
- IMPORTANT: Use ONLY the parameters listed in <available_tools>

EFFICIENCY RULES (CRITICAL):
- Do NOT write placeholder text like "Summary of..." - Write COMPLETE content immediately
- Do NOT re-read files you already read - use content from feedback messages
- PLAN before executing: Count how many tools needed, execute all in ONE iteration if possible
- Use actual newlines (\n) not escaped newlines (\\n) in write_file content
- For summaries/documentation, write minimum 150 characters with full details
- If you read a file, the content will be shown in feedback - DO NOT read it again
</critical_guidelines>"""

        # Create messages
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        # Add conversation history
        for exchange in self.conversation_history[-6:]:
            messages.append(exchange)

        try:
            self.print_message("🤔 Thinking...")

            # Autonomous loop iterations from config
            perf_cfg = self.config.get('performance', {})
            max_iterations = int(perf_cfg.get('max_autonomous_iterations', 2))
            all_responses = []
            all_tool_results = []

            for iteration in range(max_iterations):
                # Generate response
                if iteration > 0:
                    self.print_message(f"🔄 Step {iteration + 1} - Generating response...")

                # Get generation parameters from config
                inference_config = self.config.get('inference', {})
                performance_config = self.config.get('performance', {})

                max_tokens = inference_config.get('max_tokens', 1024)
                temperature = inference_config.get('temperature', 0.3)
                top_p = inference_config.get('top_p', 0.9)
                top_k = inference_config.get('top_k', 0)
                repeat_penalty = inference_config.get('repeat_penalty', 1.1)

                # Support both old and new config keys for response timeout
                response_timeout = performance_config.get('response_timeout_sec', performance_config.get('response_timeout', 60))

                response = self.model.create_chat_completion(
                    messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repeat_penalty=repeat_penalty,
                    stop=["<|im_end|>"]
                )

                ai_response = response['choices'][0]['message']['content'].strip()
                all_responses.append(ai_response)

                # Debug: Show response length
                self.print_message(f"📝 Generated {len(ai_response)} characters")

                # Parse and execute tools
                tool_results = self.parse_and_execute_tools(ai_response)

                if not tool_results:
                    # No more tools to execute, task complete
                    break

                all_tool_results.extend(tool_results)

                # Check if we should continue (only on first iteration)
                if iteration >= max_iterations - 1:
                    break

                # Feed tool results back to model for next iteration
                messages.append({"role": "assistant", "content": ai_response})

                # Create feedback with FULL tool results (critical for multi-step tasks)
                feedback_parts = []
                for result in tool_results:
                    tool_name = result['tool']
                    if result.get("result", {}).get("success"):
                        tool_result = result['result']

                        # Check for placeholder writes (Fix 3)
                        if tool_name == 'write_file' and tool_result.get('bytes_written', 0) < 100:
                            bytes_written = tool_result['bytes_written']
                            feedback_parts.append(
                                f"❌ ERROR: You wrote only {bytes_written} characters. "
                                f"This is TOO SHORT and looks like a placeholder. "
                                f"Write the COMPLETE content NOW (minimum 100 characters for summaries)."
                            )
                            continue  # Skip normal success message

                        # Include FULL data so model can use it (Fix 2: Explicit messaging)
                        if 'content' in tool_result:
                            # Make it CRYSTAL CLEAR not to re-read
                            # Truncate very long content to prevent context overflow
                            content = tool_result['content']
                            if len(content) > 2000:
                                content = content[:2000] + f"\n... (truncated, total {len(tool_result['content'])} chars)"

                            feedback_parts.append(
                                f"📄 File content below (DO NOT re-read this file):\n"
                                f"---\n{content}\n---"
                            )
                        elif 'stdout' in tool_result:
                            feedback_parts.append(f"✓ Command output:\n{tool_result['stdout']}")
                        else:
                            feedback_parts.append(f"✓ {tool_name}: {tool_result.get('message', 'Done')}")
                    else:
                        error_msg = result.get('result', {}).get('error', 'Unknown error')
                        feedback_parts.append(f"Tool '{tool_name}' failed: {error_msg}")

                feedback = "\n\n".join(feedback_parts) + "\n\nNow complete the remaining steps of the task."
                messages.append({"role": "user", "content": feedback})

                # Show progress
                self.print_message(f"🔄 Step {iteration + 2}...")

            # Combine all responses
            final_response = "\n\n".join(all_responses)

            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": final_response})

            # Add summary of tool executions
            if all_tool_results:
                final_response += "\n\n" + "="*50
                final_response += "\n🔧 Tool Execution Summary:"
                for result in all_tool_results:
                    if result.get("skipped"):
                        final_response += f"\n⏭️  {result['tool']}: Skipped"
                    elif result.get("result", {}).get("success"):
                        final_response += f"\n✅ {result['tool']}: Success"
                    else:
                        final_response += f"\n❌ {result['tool']}: {result.get('result', {}).get('error', 'Failed')}"
                final_response += "\n" + "="*50

            return final_response

        except Exception as e:
            self.print_error(f"Generation failed: {e}")
            return "I encountered an error generating a response."

    def display_response(self, response):
        """Display the response."""
        if not response:
            return

        if self.console:
            try:
                markdown = Markdown(response)
                self.console.print(Panel(markdown, title="🤖 Working AI Response"))
            except:
                self.console.print(Panel(response, title="🤖 Working AI Response"))
        else:
            print("\n" + "="*50)
            print("AI RESPONSE:")
            print("="*50)
            print(response)
            print("="*50 + "\n")

    def interactive_mode(self):
        """Run interactive mode."""
        self.print_message("🚀 Working AI Assistant - Interactive Mode")
        self.print_message("Type 'help' for commands, 'quit' to exit")
        self.print_message("This assistant actually executes tools when requested!")
        self.print_message("-" * 60)

        while True:
            try:
                if self.console:
                    prompt = Prompt.ask("💬 You", default="")
                else:
                    prompt = input("💬 You: ").strip()

                if not prompt:
                    continue

                if prompt.lower() in ['quit', 'exit', 'q']:
                    self.print_message("👋 Goodbye!")
                    break

                if prompt.lower() == 'help':
                    self.show_help()
                    continue

                if prompt.lower() == 'tools':
                    self.show_tools()
                    continue

                if prompt.lower() == 'auto':
                    self.auto_confirm = not self.auto_confirm
                    status = "enabled" if self.auto_confirm else "disabled"
                    self.print_message(f"🔧 Auto-confirm {status}")
                    continue

                if prompt.startswith('/'):
                    self.handle_command(prompt)
                    continue

                # Generate and display response
                response = self.generate_response(prompt)
                self.display_response(response)

            except KeyboardInterrupt:
                self.print_message("\n👋 Goodbye!")
                break
            except EOFError:
                self.print_message("\n👋 Goodbye!")
                break

    def show_help(self):
        """Show help information."""
        help_text = """
📖 Available Commands:
  /add <file>           Add file to context
  /remove <file>        Remove file from context
  /list                 List files in context
  /clear                Clear all context
  /tools                Show available tools
  /auto                 Toggle auto-confirm for tools
  /quit or exit         Exit the assistant

🤖 Tool Usage:
  The AI can execute tools using this format:
  [TOOL: tool_name(args)]

  Examples:
  • "Read the file example.py" → AI will use read_file tool
  • "Write hello world to test.py" → AI will use write_file tool
  • "Run Python code print('hello')" → AI will use execute_python tool
        """

        if self.console:
            self.console.print(Panel(help_text, title="📖 Help"))
        else:
            print(help_text)

    def show_tools(self):
        """Show available tools."""
        tools = self.tool_manager.get_available_tools()

        tool_info = f"""
🛠️  {len(tools)} Available Tools:

File Operations:
  • read_file(file_path)      - Read file contents
  • write_file(file_path, content) - Write to file
  • create_directory(dir_path) - Create directory

Code Execution:
  • execute_python(code or file_path) - Run Python code
  • run_command(command, timeout, cwd, input) - Execute shell command

The AI will use these tools automatically when needed!
        """

        if self.console:
            panel = Panel(tool_info, title="🛠️  Available Tools")
            self.console.print(panel)
        else:
            print(tool_info)

    def handle_command(self, command):
        """Handle special commands."""
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == '/add' and len(parts) > 1:
            self.context_files.append(Path(parts[1]))
            self.print_success(f"Added to context: {parts[1]}")
        elif cmd == '/remove' and len(parts) > 1:
            path = Path(parts[1])
            if path in self.context_files:
                self.context_files.remove(path)
                self.print_success(f"Removed from context: {parts[1]}")
        elif cmd == '/list':
            if self.context_files:
                self.print_message("📁 Files in context:")
                for file_path in self.context_files:
                    self.print_message(f"  • {file_path}")
            else:
                self.print_message("No files in context")
        elif cmd == '/clear':
            self.context_files.clear()
            self.conversation_history.clear()
            self.print_success("Context cleared")
        elif cmd == '/tools':
            self.show_tools()
        elif cmd == '/auto':
            self.auto_confirm = not self.auto_confirm
            status = "enabled" if self.auto_confirm else "disabled"
            self.print_message(f"🔧 Auto-confirm {status}")
        else:
            self.print_error(f"Unknown command: {command}")
            self.show_help()

    def _should_unescape_model_output(self, content):
        """Determine if content should have escape sequences unescaped.

        Uses heuristics to detect model-generated content vs. files with legitimate
        literal escape sequences (like code files, LaTeX, etc.).
        """
        # Check if content contains escaped sequences
        has_escaped_newlines = '\\n' in content
        has_escaped_tabs = '\\t' in content

        if not (has_escaped_newlines or has_escaped_tabs):
            return False

        # Heuristics that suggest this is NOT model output (so don't unescape)
        # 1. Contains code blocks (backticks)
        if '```' in content:
            return False

        # 2. Contains LaTeX-like markers
        if '\\begin{' in content or '\\end{' in content:
            return False

        # 3. Contains many double backslashes (escaped backslashes)
        double_backslash_count = content.count('\\\\')
        if double_backslash_count > 2:
            return False

        # 4. Contains file format tokens that suggest structured content
        format_indicators = [
            '---',  # YAML frontmatter
            '{\\' ,  # JSON-like
            'import ',  # Python imports
            '#include',  # C/C++ includes
            '<?php',  # PHP
            '<!DOCTYPE',  # HTML/XML
            'function ',  # JavaScript/TypeScript
            'def ',  # Python functions
            'class ',  # Class definitions
            'public class',  # Java
            'interface ',  # Interface definitions
        ]

        for indicator in format_indicators:
            if indicator in content:
                return False

        # 5. Contains explicit metadata flags or comments
        metadata_indicators = [
            '# ',  # Comments
            '// ',  # Comments
            '/* ',  # Block comments
            '-- ',  # SQL comments
            'TODO:',  # TODO comments
            'FIXME:',  # FIXME comments
            'NOTE:',  # NOTE comments
        ]

        for indicator in metadata_indicators:
            if indicator in content:
                return False

        # 6. Contains legitimate escape sequences in strings (not just newlines/tabs)
        # If there are other escapes like \\" or \\', it's likely intentional formatting
        if '\\"' in content or "\\'" in content or '\\\\' in content:
            return False

        # If we get here, it looks like model-generated content with escaped newlines/tabs
        return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Working AI Assistant - Actually Executes Tools")
    parser.add_argument("--model", "-m", help="Path to GGUF model file")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--files", "-f", nargs="+", help="Files to add to context")
    parser.add_argument("--prompt", "-p", help="Single prompt mode")
    parser.add_argument("--auto-confirm", action="store_true", help="Auto-confirm tool execution")

    args = parser.parse_args()

    # Initialize assistant
    assistant = WorkingAIAssistant(model_path=args.model, config_path=args.config)

    if args.auto_confirm:
        assistant.auto_confirm = True

    # Load model
    if not assistant.load_model():
        sys.exit(1)

    # Add files to context
    if args.files:
        for file_path in args.files:
            assistant.context_files.append(Path(file_path))

    # Single prompt mode
    if args.prompt:
        response = assistant.generate_response(args.prompt)
        assistant.display_response(response)
        return

    # Interactive mode
    assistant.interactive_mode()

if __name__ == "__main__":
    main()