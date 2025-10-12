#!/usr/bin/env python3
"""
Smart Agentic AI Assistant - Improved Version
Addresses behavioral issues and provides better user experience.
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

class SmartToolManager:
    """Improved tool manager with better result handling."""

    def __init__(self, console=None):
        self.console = console
        self.working_directory = Path.cwd()
        self.execution_history = []

    def execute_tool(self, tool_name, tool_args):
        """Execute a tool and return detailed results."""
        tool_function = getattr(self, f"tool_{tool_name}", None)
        if not tool_function:
            return {"success": False, "error": f"Tool '{tool_name}' not found", "output": ""}

        try:
            result = tool_function(**tool_args)

            # Add execution to history
            self.execution_history.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })

            # Ensure result has output field for AI to use
            if "output" not in result:
                if result.get("success"):
                    if "content" in result:
                        result["output"] = result["content"]
                    elif "stdout" in result:
                        result["output"] = result["stdout"]
                    elif "files" in result:
                        result["output"] = f"Found {len(result['files'])} files: {', '.join([f['name'] for f in result['files'][:5]])}"
                    elif result.get("message"):
                        result["output"] = result["message"]
                    else:
                        result["output"] = "Operation completed successfully"
                else:
                    result["output"] = result.get("error", "Operation failed")

            return result
        except Exception as e:
            error_result = {"success": False, "error": str(e), "output": f"Error: {str(e)}"}
            return error_result

    # === File Operations ===

    def tool_read_file(self, file_path):
        """Read contents of a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}", "output": ""}

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines()),
                "output": content  # Important: Include content in output for AI
            }
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    def tool_write_file(self, file_path, content):
        """Write content to a file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "message": f"Successfully wrote {len(content)} characters to {file_path}",
                "output": f"File created: {file_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    def tool_create_directory(self, dir_path):
        """Create a directory."""
        try:
            path = Path(dir_path)
            path.mkdir(parents=True, exist_ok=True)

            return {
                "success": True,
                "message": f"Successfully created directory: {dir_path}",
                "output": f"Directory created: {dir_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    def tool_list_files(self, directory=".", pattern="*"):
        """List files in a directory."""
        try:
            path = Path(directory)
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {directory}", "output": ""}

            files = list(path.glob(pattern))
            file_list = []

            for file in files:
                if file.is_file():
                    file_list.append({
                        "name": file.name,
                        "path": str(file),
                        "size": file.stat().st_size
                    })

            output = f"Files in {directory}:\n"
            for file in file_list[:10]:  # Limit to 10 files
                output += f"  • {file['name']} ({file['size']} bytes)\n"

            if len(file_list) > 10:
                output += f"  ... and {len(file_list) - 10} more files"

            return {
                "success": True,
                "files": file_list,
                "count": len(file_list),
                "output": output.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    # === Code Execution ===

    def tool_execute_python(self, code=None, timeout=30, file_path=None):
        """Execute Python code and capture output."""
        try:
            if not code and not file_path:
                return {"success": False, "error": "Either 'code' or 'file_path' must be provided", "output": ""}

            if file_path:
                full_path = Path(file_path)
                if not full_path.exists():
                    return {"success": False, "error": f"File not found: {file_path}", "output": ""}

                result = subprocess.run(
                    [sys.executable, str(full_path)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.working_directory
                )
            else:
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.working_directory
                )

            output = result.stdout if result.returncode == 0 else result.stderr
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "output": output.strip()
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timed out", "output": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    def tool_run_command(self, command, timeout=30):
        """Run a shell command safely."""
        try:
            # Basic safety check
            dangerous_commands = ['rm -rf', 'sudo', 'chmod 777', 'format', 'del']
            if any(danger in command.lower() for danger in dangerous_commands):
                return {"success": False, "error": "Command blocked for safety reasons", "output": ""}

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_directory
            )

            output = result.stdout if result.returncode == 0 else result.stderr
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "output": output.strip()
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "output": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

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
                return {"success": False, "error": "Not a git repository", "output": ""}

            changed_files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    status = line[:2]
                    file_path = line[3:]
                    changed_files.append({"status": status, "file": file_path})

            output = f"Git Status: {len(changed_files)} changed files\n"
            for file in changed_files[:10]:
                output += f"  {file['status']} {file['file']}\n"

            return {
                "success": True,
                "changed_files": changed_files,
                "output": output.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    def get_available_tools(self):
        """Return a list of all available tools."""
        tools = []
        for attr_name in dir(self):
            if attr_name.startswith('tool_'):
                tool_name = attr_name[5:]
                method = getattr(self, attr_name)
                if callable(method):
                    tools.append(tool_name)
        return sorted(tools)

class SmartAIAssistant:
    """Improved AI Assistant with better conversation handling."""

    def __init__(self, model_path=None, config_path=None):
        self.console = Console() if RICH_AVAILABLE else None
        self.model = None
        self.config = self.load_config(config_path)
        self.model_path = model_path or self.config.get('model', {}).get('path', 'models/qwen2.5-coder-7b-instruct-q4_k_m.gguf')
        self.context_files = []
        self.tool_manager = SmartToolManager(self.console)
        self.auto_confirm = False
        self.conversation_history = []  # Track conversation for better context

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
                temperature=self.config.get('model', {}).get('temperature', 0.3),  # Lower temperature for more reliable responses
                verbose=False
            )
            self.print_success("Model loaded successfully!")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False

    def should_use_tools(self, user_input):
        """Determine if tools are needed for this request."""
        tool_keywords = [
            'create', 'write', 'read', 'file', 'directory', 'folder',
            'run', 'execute', 'test', 'check', 'list', 'show',
            'git', 'commit', 'status', 'add', 'push', 'pull',
            'build', 'compile', 'install', 'setup'
        ]

        return any(keyword in user_input.lower() for keyword in tool_keywords)

    def execute_tools_intelligently(self, user_input, max_tools=3):
        """Execute tools intelligently based on user intent."""
        if not self.should_use_tools(user_input):
            return []

        # Parse user intent and generate appropriate tool calls
        tools_to_execute = []
        user_lower = user_input.lower()

        # File reading
        if any(word in user_lower for word in ['read', 'show', 'summarize', 'analyze', 'explain']):
            # Look for file paths in the input
            file_paths = re.findall(r'[/\\]?[\w\-./\\]+\.?\w*', user_input)
            for file_path in file_paths:
                if Path(file_path).exists():
                    tools_to_execute.append(('read_file', {'file_path': file_path}))
                    if len(tools_to_execute) >= max_tools:
                        break

        # File writing - Only execute if we have content from previous reads
        if any(word in user_lower for word in ['write', 'create', 'modify']) and 'file' in user_lower:
            # Look for file paths in the input
            file_paths = re.findall(r'[/\\]?[\w\-./\\]+\.?\w*', user_input)
            for file_path in file_paths:
                # Only write if we have content to write (simplified approach)
                # For now, just read the file to see current content
                if Path(file_path).exists():
                    tools_to_execute.append(('read_file', {'file_path': file_path}))
                    if len(tools_to_execute) >= max_tools:
                        break

        # Execute at most max_tools tools
        results = []
        for tool_name, tool_args in tools_to_execute[:max_tools]:
            if not self.auto_confirm:
                self.print_warning(f"🔧 Executing: {tool_name}({tool_args})")
                if not Confirm.ask("Execute this tool?", default=True):
                    continue

            result = self.tool_manager.execute_tool(tool_name, tool_args)
            results.append({"tool": tool_name, "result": result})

            if result["success"]:
                self.print_success(f"✅ {tool_name}: Success")
            else:
                self.print_error(f"❌ {tool_name}: {result.get('error', 'Failed')}")

        return results

    def generate_response(self, prompt):
        """Generate a response with improved context handling."""
        if not self.model:
            self.print_error("Model not loaded")
            return ""

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": prompt})

        # Execute relevant tools first
        tool_results = self.execute_tools_intelligently(prompt)
        tool_context = ""

        if tool_results:
            tool_context = "\n\nTool Results:\n"
            for tool_result in tool_results:
                tool_result_data = tool_result["result"]
                if tool_result_data["success"] and tool_result_data.get("output"):
                    tool_context += f"[{tool_result['tool']}]: {tool_result_data['output']}\n"
            tool_context += "\n"

        # Create context from files
        file_context = ""
        for file_path in self.context_files:
            content = self.tool_manager.execute_tool("read_file", {"file_path": str(file_path)})
            if content["success"]:
                file_context += f"\n--- File: {file_path} ---\n{content['output']}\n--- End of File ---\n"

        # Build system prompt with context
        system_message = f"""You are a helpful AI assistant that can analyze code and assist with technical tasks.

{tool_context if tool_context else ""}

{file_context if file_context else ""}

Guidelines:
1. Answer questions directly and accurately
2. If tool results are provided above, use them in your response
3. Be concise but thorough
4. If you need to perform actions, ask for permission first
5. Focus on what the user actually asked for

Available tools: {', '.join(self.tool_manager.get_available_tools())}
Use tools only when explicitly requested."""

        # Create messages for chat completion
        messages = [
            {"role": "system", "content": system_message}
        ]

        # Add recent conversation history (last 5 exchanges)
        for exchange in self.conversation_history[-10:]:
            messages.append(exchange)

        try:
            self.print_message("🤔 Thinking...")

            response = self.model.create_chat_completion(
                messages,
                max_tokens=self.config.get('model', {}).get('max_tokens', 2048),
                temperature=self.config.get('model', {}).get('temperature', 0.3),
                stop=["<|im_end|>"]
            )

            ai_response = response['choices'][0]['message']['content'].strip()

            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})

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
                self.console.print(Panel(markdown, title="🤖 Smart AI Response"))
            except:
                self.console.print(Panel(response, title="🤖 Smart AI Response"))
        else:
            print("\n" + "="*50)
            print("SMART AI RESPONSE:")
            print("="*50)
            print(response)
            print("="*50 + "\n")

    def print_warning(self, message):
        """Print a warning message."""
        if self.console:
            self.console.print(f"⚠️  {message}", style="yellow")
        else:
            print(f"WARNING: {message}")

    def interactive_mode(self):
        """Run in interactive mode."""
        self.print_message("🚀 Smart AI Assistant - Interactive Mode")
        self.print_message("Type 'help' for commands, 'quit' to exit")
        self.print_message("This assistant analyzes context and uses tools intelligently!")
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

🤖 Smart Features:
  • Intelligent tool usage based on context
  • Better conversation understanding
  • Reduced unnecessary tool calls
  • Improved file reading and analysis
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
  • list_files(directory, pattern) - List files

Code Execution:
  • execute_python(code/file_path) - Run Python code
  • run_command(command)      - Execute shell command

Git Operations:
  • git_status()              - Show git status

Tools are used automatically when needed!
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

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Smart AI Assistant with Improved Behavior")
    parser.add_argument("--model", "-m", help="Path to GGUF model file")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--files", "-f", nargs="+", help="Files to add to context")
    parser.add_argument("--prompt", "-p", help="Single prompt mode")
    parser.add_argument("--auto-confirm", action="store_true", help="Auto-confirm tool execution")

    args = parser.parse_args()

    # Initialize assistant
    assistant = SmartAIAssistant(model_path=args.model, config_path=args.config)

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