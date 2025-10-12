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

    def __init__(self, console=None):
        self.console = console
        self.working_directory = Path.cwd()

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
            path = Path(file_path)
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

    def tool_create_directory(self, dir_path):
        """Create a directory."""
        try:
            path = Path(dir_path)
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

    def tool_run_command(self, command, timeout=30):
        """Run a shell command safely."""
        try:
            # Basic safety check
            dangerous_commands = ['rm -rf', 'sudo', 'chmod 777', 'format', 'del']
            if any(danger in command.lower() for danger in dangerous_commands):
                return {"success": False, "error": "Command blocked for safety reasons"}

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_directory
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

class WorkingAIAssistant:
    """AI Assistant that actually executes tools."""

    def __init__(self, model_path=None, config_path=None):
        self.console = Console() if RICH_AVAILABLE else None
        self.model = None
        self.config = self.load_config(config_path)
        self.model_path = model_path or self.config.get('model', {}).get('path', 'models/qwen2.5-coder-7b-instruct-q4_k_m.gguf')
        self.context_files = []
        self.tool_manager = WorkingToolManager(self.console)
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
                n_ctx=4096,
                n_threads=0,
                temperature=0.3,
                verbose=False
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
                    # Handle different content formats
                    args_str = args_str.strip()

                    # Check for triple-quoted content
                    if "'''" in args_str:
                        # Handle triple single quotes
                        parts = args_str.split("'''", 2)
                        if len(parts) >= 3:
                            # Find the parameter name before the content
                            before_content = parts[0]
                            content = parts[1]
                            after_content = parts[2]

                            # Extract parameter name - look for pattern like "content='''"
                            param_match = re.search(r'(\w+)\s*=\s*\'\'\'$', before_content.strip())
                            if param_match:
                                param_name = param_match.group(1)
                                # Reconstruct the content
                                full_content = "'''" + content + "'''"
                                args[param_name] = full_content
                            else:
                                # Try to find parameter name differently
                                param_matches = re.findall(r'(\w+)\s*=', before_content)
                                if param_matches:
                                    param_name = param_matches[-1]  # Get the last parameter
                                    full_content = "'''" + content + "'''"
                                    args[param_name] = full_content
                    elif '"""' in args_str:
                        # Handle triple double quotes
                        parts = args_str.split('"""', 2)
                        if len(parts) >= 3:
                            before_content = parts[0]
                            content = parts[1]
                            after_content = parts[2]

                            param_match = re.search(r'(\w+)\s*=\s*"""$', before_content.strip())
                            if param_match:
                                param_name = param_match.group(1)
                                full_content = '"""' + content + '"""'
                                args[param_name] = full_content
                            else:
                                # Try to find parameter name differently
                                param_matches = re.findall(r'(\w+)\s*=', before_content)
                                if param_matches:
                                    param_name = param_matches[-1]  # Get the last parameter
                                    full_content = '"""' + content + '"""'
                                    args[param_name] = full_content
                    else:
                        # Simple key=value parsing for regular arguments
                        pairs = [p.strip() for p in args_str.split(',') if p.strip()]
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

                # Handle malformed arguments by fixing common issues
                if tool_name == "write_file" and "file_path" in args and "content" not in args:
                    # Check if content got merged with file_path
                    if "=" not in args["file_path"] and len(args) == 1:
                        # This suggests parsing failed - try to reconstruct from original string
                        original_call = f"[TOOL: {tool_name}({args_str})]"
                        if "file_path=" in original_call and "content=" in original_call:
                            # Extract both parameters using regex
                            file_match = re.search(r"file_path\s*=\s*['\"]([^'\"]*)['\"]", original_call)
                            content_match = re.search(r"content\s*=\s*['\"]([^'\"]*)['\"]", original_call)
                            if file_match and content_match:
                                args["file_path"] = file_match.group(1)
                                args["content"] = content_match.group(1)

                # Confirm before executing
                if not self.auto_confirm:
                    self.print_warning(f"🔧 Execute tool: {tool_name}({args})")
                    if not Confirm.ask("Execute this tool?", default=True):
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

        # System prompt with tool instructions
        system_message = f"""You are a helpful AI assistant that can execute tools.

Available tools: {', '.join(self.tool_manager.get_available_tools())}

To execute a tool, use this format: [TOOL: tool_name(args)]
Examples:
- [TOOL: read_file(file_path='example.py')]
- [TOOL: write_file(file_path='test.py', content='print("Hello")')]
- [TOOL: execute_python(code='print("Hello")')]
- [TOOL: execute_python(file_path='example.py')]
- [TOOL: create_directory(dir_path='new_folder')]

Context: {context if context else "No files in context."}

IMPORTANT GUIDELINES:
1. When user asks to READ files, immediately use read_file tool
2. When user asks to EXECUTE files, use execute_python(file_path=...) directly
3. When user asks to WRITE files, immediately use write_file tool
4. When user asks to RUN Python code, use execute_python tool
5. DO NOT ask for confirmation - the system handles that
6. Be proactive in using tools rather than asking for content

Examples of what to do:
- "Read simple_ai_assistant.py" → Use read_file tool immediately
- "Execute test.py" → Use execute_python(file_path='test.py') immediately
- "Write hello world to file.py" → Use write_file tool immediately
- "Run python code print('hello')" → Use execute_python(code="print('hello')") immediately

Be helpful and take action using tools!"""

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

            # Generate response
            response = self.model.create_chat_completion(
                messages,
                max_tokens=2048,
                temperature=0.3,
                stop=["<|im_end|>"]
            )

            ai_response = response['choices'][0]['message']['content'].strip()

            # Parse and execute tools
            tool_results = self.parse_and_execute_tools(ai_response)

            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            # Return response with tool results
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
  • run_command(command)      - Execute shell command

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