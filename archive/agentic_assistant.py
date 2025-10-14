#!/usr/bin/env python3
"""
Agentic AI Assistant for Offline Coding
An advanced assistant that can execute tools and perform actions.

SECURITY CAUTION: Archived reference code. tool_run_command uses argument lists (no shell=True) with basic validations. Do NOT use in production without strict whitelisting and isolation.
"""

import os
import sys
import argparse
import subprocess
import json
import re
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
    from rich.syntax import Syntax
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich not installed. Terminal output will be plain.")

class ToolManager:
    """Manages and executes various tools for the agentic assistant."""

    def __init__(self, console=None):
        self.console = console
        self.working_directory = Path.cwd()
        self.execution_history = []

    def execute_tool(self, tool_name, tool_args):
        """Execute a tool with given arguments."""
        tool_function = getattr(self, f"tool_{tool_name}", None)
        if not tool_function:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}

        try:
            result = tool_function(**tool_args)
            self.execution_history.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === File Operations ===

    def tool_read_file(self, file_path):
        """Read contents of a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_write_file(self, file_path, content):
        """Write content to a file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "message": f"Successfully wrote {len(content)} characters to {file_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_create_directory(self, dir_path, directory_path=None):
        """Create a directory."""
        try:
            # Support both parameter names for flexibility
            path_str = directory_path or dir_path
            path = Path(path_str)
            path.mkdir(parents=True, exist_ok=True)

            return {
                "success": True,
                "message": f"Successfully created directory: {path_str}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_list_files(self, directory=".", pattern="*"):
        """List files in a directory."""
        try:
            path = Path(directory)
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}

            files = list(path.glob(pattern))
            file_list = []

            for file in files:
                if file.is_file():
                    file_list.append({
                        "name": file.name,
                        "path": str(file),
                        "size": file.stat().st_size
                    })

            return {
                "success": True,
                "files": file_list,
                "count": len(file_list)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Code Execution ===

    def tool_execute_python(self, code=None, timeout=30, file_path=None):
        """Execute Python code and capture output."""
        try:
            if not code and not file_path:
                return {"success": False, "error": "Either 'code' or 'file_path' must be provided"}

            if file_path:
                # Execute a Python file
                full_path = Path(file_path)
                if not full_path.exists():
                    return {"success": False, "error": f"File not found: {file_path}"}

                result = subprocess.run(
                    [sys.executable, str(full_path)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.working_directory
                )
            else:
                # Execute Python code string
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.working_directory
                )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_run_command(self, command, timeout=30):
        """Run a shell command with enhanced security measures.

        SECURITY WARNING: This implementation is NOT production-safe despite improvements.
        Limitations that can still be bypassed:
        - Command chaining: 'ls; rm -rf /' or 'command && dangerous_command'
        - Spacing variations: 'rm-rf' or 'rm  -rf'
        - Case mixing: 'RM -RF' or 'SuDo command'
        - Aliases: if shell profiles define dangerous aliases
        - Metacharacters: >, <, |, $, `, $(), &&, ||, ;, etc.
        - Argument injection: commands that interpret arguments as code

        For production use, implement:
        1. Strict whitelist of allowed commands
        2. Parse command into argument list (shlex.split)
        3. Use subprocess.run with list arguments (no shell=True)
        4. Validate each argument against allowed patterns
        5. Run in isolated environment (container/chroot)
        """
        try:
            # Enhanced safety checks - still bypassable but better than before
            dangerous_patterns = [
                # Command chaining and piping
                '&&', '||', ';', '|',
                # Redirection and substitution
                '>', '<', '>>', '<<', '$', '`', '$(',
                # Common dangerous commands (case-insensitive substring check)
                'rm -rf', 'sudo', 'chmod 777', 'format', 'del',
                'mkfs', 'dd ', 'fallocate', 'truncate',
                # Shell builtins that can be dangerous
                'exec', 'eval', 'source', '. ',
            ]

            command_lower = command.lower()
            for pattern in dangerous_patterns:
                if pattern in command_lower:
                    return {"success": False, "error": f"Command blocked: dangerous pattern '{pattern}' detected"}

            # Additional check for shell metacharacters in arguments
            import shlex
            try:
                # Try to parse as shell command to detect complex syntax
                parsed = shlex.split(command)
                if len(parsed) != 1:
                    # Multiple arguments suggest complex command
                    return {"success": False, "error": "Complex shell commands not allowed"}

                # Check for suspicious argument patterns
                for arg in parsed:
                    if any(char in arg for char in ['|', '&', ';', '$', '`']):
                        return {"success": False, "error": f"Dangerous metacharacter in argument: {arg}"}

            except ValueError as e:
                # shlex parsing failed, likely due to unescaped quotes or complex syntax
                return {"success": False, "error": f"Invalid shell syntax: {e}"}

            # Use subprocess with list arguments for better security
            import shlex
            args = shlex.split(command)

            result = subprocess.run(
                args,  # Use parsed arguments instead of shell=True
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_directory,
                # Disable shell features that could be dangerous
                env={k: v for k, v in os.environ.items()
                     if k not in ['BASH_ENV', 'ENV', 'SHELL']}  # Remove shell environment variables
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Git Operations ===

    def tool_git_status(self):
        """Get git repository status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.working_directory
            )

            if result.returncode != 0:
                return {"success": False, "error": "Not a git repository"}

            changed_files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    status = line[:2]
                    file_path = line[3:]
                    changed_files.append({"status": status, "file": file_path})

            return {
                "success": True,
                "changed_files": changed_files,
                "message": f"Found {len(changed_files)} changed files"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_git_add(self, files):
        """Add files to git staging."""
        try:
            if isinstance(files, str):
                files = [files]

            result = subprocess.run(
                ["git", "add"] + files,
                capture_output=True,
                text=True,
                cwd=self.working_directory
            )

            return {
                "success": result.returncode == 0,
                "message": f"Added {len(files)} file(s) to staging",
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tool_git_commit(self, message):
        """Create a git commit."""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                cwd=self.working_directory
            )

            return {
                "success": result.returncode == 0,
                "message": "Commit created successfully",
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Code Analysis ===

    def tool_check_syntax(self, file_path):
        """Check Python syntax of a file."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
                cwd=self.working_directory
            )

            return {
                "success": result.returncode == 0,
                "message": "Syntax is valid" if result.returncode == 0 else "Syntax errors found",
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_available_tools(self):
        """Return a list of all available tools."""
        tools = []
        for attr_name in dir(self):
            if attr_name.startswith('tool_'):
                tool_name = attr_name[5:]  # Remove 'tool_' prefix
                method = getattr(self, attr_name)
                if callable(method):
                    tools.append(tool_name)
        return sorted(tools)

class AgenticAIAssistant:
    """Agentic AI Assistant with tool execution capabilities."""

    def __init__(self, model_path=None, config_path=None):
        self.console = Console() if RICH_AVAILABLE else None
        self.model = None
        self.config = self.load_config(config_path)
        self.model_path = model_path or self.config.get('model', {}).get('path', 'models/qwen2.5-coder-7b-instruct-q4_k_m.gguf')
        self.context_files = []
        self.tool_manager = ToolManager(self.console)
        self.auto_confirm = False  # Safety flag

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
        """Print a message with rich formatting if available."""
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
            self.print_message(f"🧠 Loading model: {model_file.name}")
            self.model = Llama(
                model_path=str(model_file),
                n_ctx=self.config.get('model', {}).get('context_length', 4096),
                n_threads=self.config.get('model', {}).get('threads', 0),
                temperature=self.config.get('model', {}).get('temperature', 0.7),
                verbose=False
            )
            self.print_success("Model loaded successfully!")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False

    def parse_and_execute_tools(self, response):
        """Parse tool calls from AI response and execute them."""
def parse_and_execute_tools(self, response):
    """Parse tool calls from AI response and execute them."""
    # (import re removed—already imported at module level)
    # ...rest of implementation...

        # Look for tool calls in the format: [TOOL: tool_name(args)]
        tool_pattern = r'\[TOOL:\s*(\w+)\((.*?)\)\]'
        matches = re.findall(tool_pattern, response, re.DOTALL)

        results = []
        for tool_name, args_str in matches:
            try:
                # Parse arguments (simple key=value format)
                args = {}
                if args_str.strip():
                    for pair in args_str.split(','):
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            key = key.strip()
                            value = value.strip()

                            # Handle string literals
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]

                            args[key] = value

                # Confirm before executing (unless auto-confirm is enabled)
                if not self.auto_confirm:
                    self.print_warning(f"🔧 About to execute tool: {tool_name}({args})")
                    if not Confirm.ask("Execute this tool?", default=True):
                        results.append({"tool": tool_name, "skipped": True})
                        continue

                # Execute the tool
                result = self.tool_manager.execute_tool(tool_name, args)
                results.append({"tool": tool_name, "result": result})

                if result["success"]:
                    self.print_success(f"✅ {tool_name}: {result.get('message', 'Success')}")
                else:
                    self.print_error(f"❌ {tool_name}: {result.get('error', 'Failed')}")

            except Exception as e:
                self.print_error(f"❌ Failed to execute tool {tool_name}: {e}")
                results.append({"tool": tool_name, "error": str(e)})

        return results

    def generate_response(self, prompt):
        """Generate a response from the model with tool capabilities."""
        if not self.model:
            self.print_error("Model not loaded")
            return ""

        # Build context
        context = ""
        for file_path in self.context_files:
            content = self.tool_manager.execute_tool("read_file", {"file_path": str(file_path)})
            if content["success"]:
                context += f"\n--- File: {file_path} ---\n"
                context += content["content"]
                context += "\n--- End of File ---\n"

        # Available tools info
        available_tools = self.tool_manager.get_available_tools()
        tools_info = "\nAvailable tools: " + ", ".join(available_tools)
        tools_info += "\nUse tools in format: [TOOL: tool_name(args)]"
        tools_info += "\nExample: [TOOL: write_file(file_path='hello.py', content='print(\"Hello World\")')]"

        # Create messages
        messages = [
            {
                "role": "system",
                "content": f"""You are an agentic AI coding assistant that can execute tools to perform actions.
                You can read/write files, run Python code, execute shell commands, and perform Git operations.
                {tools_info}

                Context: {context if context else "No files in context."}

                When responding, think step by step. If you need to perform an action, use the appropriate tool.
                Always explain what you're doing and why."""
            },
            {"role": "user", "content": prompt}
        ]

        try:
            self.print_message("🤔 Thinking...")

            # Use chat completion
            response = self.model.create_chat_completion(
                messages,
                max_tokens=self.config.get('model', {}).get('max_tokens', 2048),
                temperature=self.config.get('model', {}).get('temperature', 0.7),
                stop=["<|im_end|>"]
            )

            ai_response = response['choices'][0]['message']['content'].strip()

            # Parse and execute any tool calls
            tool_results = self.parse_and_execute_tools(ai_response)

            # If tools were executed, provide feedback
            if tool_results:
                ai_response += "\n\n" + "="*50
                ai_response += "\n🔧 Tool Execution Results:"
                for result in tool_results:
                    if result.get("skipped"):
                        ai_response += f"\n⏭️  {result['tool']}: Skipped"
                    elif result.get("result", {}).get("success"):
                        ai_response += f"\n✅ {result['tool']}: Success"
                    else:
                        ai_response += f"\n❌ {result['tool']}: {result.get('result', {}).get('error', 'Failed')}"
                ai_response += "\n" + "="*50

            return ai_response

        except Exception as e:
            self.print_error(f"Generation failed: {e}")
            return "I apologize, but I encountered an error generating a response."

    def display_response(self, response):
        """Display the model response."""
        if not response:
            return

        if self.console:
            try:
                markdown = Markdown(response)
                self.console.print(Panel(markdown, title="🤖 Agentic AI Response"))
            except Exception:
                self.console.print(Panel(response, title="🤖 Agentic AI Response"))
        else:
            print("\n" + "="*50)
            print("AGENTIC AI RESPONSE:")
            print("="*50)
            print(response)
            print("="*50 + "\n")

    def interactive_mode(self):
        """Run in interactive mode."""
        self.print_message("🚀 Agentic AI Assistant - Interactive Mode")
        self.print_message("Type 'help' for commands, 'quit' to exit")
        self.print_message("This assistant can execute tools and perform actions!")
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

🛠️  Special Commands:
  help                  Show this help
  tools                 Show available tools
  auto                  Toggle auto-confirm mode

🤖 Agentic Features:
  This assistant can execute tools to:
  • Read/write files
  • Run Python code
  • Execute shell commands
  • Perform Git operations
  • Check code syntax
        """

        if self.console:
            self.console.print(Panel(help_text, title="📖 Help"))
        else:
            print(help_text)

    def show_tools(self):
        """Show available tools."""
        tools = self.tool_manager.get_available_tools()

        tool_info = """
🛠️  Available Tools:

File Operations:
  • read_file(file_path)      - Read file contents
  • write_file(file_path, content) - Write to file
  • create_directory(dir_path) - Create directory
  • list_files(directory, pattern) - List files

Code Execution:
  • execute_python(code)      - Run Python code
  • run_command(command)      - Execute shell command

Git Operations:
  • git_status()              - Show git status
  • git_add(files)            - Add files to staging
  • git_commit(message)       - Create commit

Code Analysis:
  • check_syntax(file_path)   - Check Python syntax

Usage: [TOOL: tool_name(args)]
        """

        if self.console:
            panel = Panel(tool_info, title=f"🛠️  {len(tools)} Tools Available")
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

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Agentic AI Assistant for Offline Coding")
    parser.add_argument("--model", "-m", help="Path to GGUF model file")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--files", "-f", nargs="+", help="Files to add to context")
    parser.add_argument("--prompt", "-p", help="Single prompt mode")
    parser.add_argument("--auto-confirm", action="store_true", help="Auto-confirm tool execution")

    args = parser.parse_args()

    # Initialize assistant
    assistant = AgenticAIAssistant(model_path=args.model, config_path=args.config)

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