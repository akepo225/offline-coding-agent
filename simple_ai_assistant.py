#!/usr/bin/env python3
"""
Simple AI Assistant for Offline Coding
A lightweight alternative to aider-chat that uses local models.
"""

import os
import sys
import argparse
from pathlib import Path
import json
import yaml

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("Warning: llama-cpp-python not installed. Model loading will not work.")

try:
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich not installed. Terminal output will be plain.")

class SimpleAIAssistant:
    def __init__(self, model_path=None, config_path=None):
        self.console = Console() if RICH_AVAILABLE else None
        self.model = None
        self.config = self.load_config(config_path)
        self.model_path = model_path or self.config.get('model', {}).get('path', 'models/qwen2.5-coder-7b-instruct-q4_k_m.gguf')
        self.context_files = []

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
                temperature=self.config.get('model', {}).get('temperature', 0.7),
                verbose=False
            )
            self.print_success("Model loaded successfully!")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False

    def add_file(self, file_path):
        """Add a file to the context."""
        path = Path(file_path)
        if not path.exists():
            self.print_error(f"File not found: {file_path}")
            return False

        if path not in self.context_files:
            self.context_files.append(path)
            self.print_success(f"Added to context: {file_path}")
        else:
            self.print_message(f"File already in context: {file_path}")
        return True

    def remove_file(self, file_path):
        """Remove a file from the context."""
        path = Path(file_path)
        if path in self.context_files:
            self.context_files.remove(path)
            self.print_success(f"Removed from context: {file_path}")
        else:
            self.print_message(f"File not in context: {file_path}")

    def list_context(self):
        """List all files in context."""
        if not self.context_files:
            self.print_message("No files in context")
            return

        self.print_message("📁 Files in context:")
        for i, file_path in enumerate(self.context_files, 1):
            self.print_message(f"  {i}. {file_path}")

    def read_file_content(self, file_path):
        """Read content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.print_error(f"Failed to read {file_path}: {e}")
            return ""

    def build_context(self):
        """Build context from all files."""
        context = ""
        for file_path in self.context_files:
            content = self.read_file_content(file_path)
            if content:
                context += f"\n--- File: {file_path} ---\n"
                context += content
                context += "\n--- End of File ---\n"
        return context

    def generate_response(self, prompt):
        """Generate a response from the model."""
        if not self.model:
            self.print_error("Model not loaded")
            return ""

        # Build context part
        context = self.build_context()

        # Create messages list for chat template
        messages = []

        # Add system message with context if available
        system_message = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant specialized in coding and technical tasks."
        if context:
            system_message += f"\n\nHere are the files in context for reference:\n{context}\nPlease use this context to provide accurate and helpful responses."

        messages.append({"role": "system", "content": system_message})

        # Add user message
        messages.append({"role": "user", "content": prompt})

        try:
            self.print_message("🤔 Thinking...")

            # Use the model's chat template directly
            response = self.model.create_chat_completion(
                messages,
                max_tokens=self.config.get('model', {}).get('max_tokens', 2048),
                temperature=self.config.get('model', {}).get('temperature', 0.7),
                stop=["<|im_end|>"]
            )

            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            self.print_error(f"Chat completion failed: {e}")
            # Fallback to simple prompt if chat completion fails
            return self._fallback_generation(prompt, context)

    def _fallback_generation(self, prompt, context):
        """Fallback generation using simple prompt format."""
        try:
            # Simple format as fallback
            if context:
                full_prompt = f"Context: {context}\n\nUser: {prompt}\nAssistant: "
            else:
                full_prompt = f"User: {prompt}\nAssistant: "

            response = self.model(
                full_prompt,
                max_tokens=self.config.get('model', {}).get('max_tokens', 2048),
                stop=["User:", "\n\n"],
                temperature=self.config.get('model', {}).get('temperature', 0.7),
                echo=False
            )

            return response['choices'][0]['text'].strip()
        except Exception as e:
            self.print_error(f"Fallback generation also failed: {e}")
            return "I apologize, but I encountered an error generating a response."

    def display_response(self, response):
        """Display the model response."""
        if not response:
            return

        if self.console:
            # Try to display as Markdown
            try:
                markdown = Markdown(response)
                self.console.print(Panel(markdown, title="🤖 AI Response"))
            except:
                # Fallback to plain text
                self.console.print(Panel(response, title="🤖 AI Response"))
        else:
            print("\n" + "="*50)
            print("AI RESPONSE:")
            print("="*50)
            print(response)
            print("="*50 + "\n")

    def interactive_mode(self):
        """Run in interactive mode."""
        self.print_message("🚀 Simple AI Assistant - Interactive Mode")
        self.print_message("Type 'help' for commands, 'quit' to exit")
        self.print_message("-" * 50)

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

    def handle_command(self, command):
        """Handle special commands."""
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == '/add' and len(parts) > 1:
            self.add_file(parts[1])
        elif cmd == '/remove' and len(parts) > 1:
            self.remove_file(parts[1])
        elif cmd == '/list':
            self.list_context()
        elif cmd == '/clear':
            self.context_files.clear()
            self.print_success("Context cleared")
        elif cmd == '/model' and len(parts) > 1:
            self.model_path = parts[1]
            self.load_model()
        else:
            self.print_error(f"Unknown command: {command}")
            self.show_help()

    def show_help(self):
        """Show help information."""
        help_text = """
📖 Available Commands:
  /add <file>     Add file to context
  /remove <file>  Remove file from context
  /list           List files in context
  /clear          Clear all context
  /model <path>   Load different model
  /quit or exit   Exit the assistant

📝 Usage Tips:
  - Add source files with /add before asking questions
  - Be specific in your requests
  - Use clear, concise language
        """

        if self.console:
            self.console.print(Panel(help_text, title="📖 Help"))
        else:
            print(help_text)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simple AI Assistant for Offline Coding")
    parser.add_argument("--model", "-m", help="Path to GGUF model file")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--files", "-f", nargs="+", help="Files to add to context")
    parser.add_argument("--prompt", "-p", help="Single prompt mode")

    args = parser.parse_args()

    # Initialize assistant
    assistant = SimpleAIAssistant(model_path=args.model, config_path=args.config)

    # Load model
    if not assistant.load_model():
        sys.exit(1)

    # Add files to context
    if args.files:
        for file_path in args.files:
            assistant.add_file(file_path)

    # Single prompt mode
    if args.prompt:
        response = assistant.generate_response(args.prompt)
        assistant.display_response(response)
        return

    # Interactive mode
    assistant.interactive_mode()

if __name__ == "__main__":
    main()