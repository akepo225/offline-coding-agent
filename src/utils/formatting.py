"""
Output formatting utilities for Offline Coding Agent
"""

import json
from typing import Dict, Any, Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text


console = Console()


def format_output(
    content: str,
    format_type: str = "text",
    language: Optional[str] = None,
    title: Optional[str] = None
) -> None:
    """
    Format and print output to console.

    Args:
        content: Content to display
        format_type: Output format (text, json, code)
        language: Programming language (for code highlighting)
        title: Optional title for panels
    """
    if format_type == "json":
        try:
            # Try to parse and pretty-print JSON
            json_data = json.loads(content)
            console.print(json.dumps(json_data, indent=2))
        except json.JSONDecodeError:
            # If not valid JSON, print as text
            console.print(content)
    elif format_type == "code" and language:
        # Display with syntax highlighting
        syntax = Syntax(content, language, theme="monokai", line_numbers=True)
        if title:
            console.print(Panel(syntax, title=title, border_style="blue"))
        else:
            console.print(syntax)
    else:
        # Display as plain text
        if title:
            console.print(Panel(content, title=title, border_style="green"))
        else:
            console.print(content)


def colorize_text(text: str, color: str = "white") -> Text:
    """
    Apply color formatting to text.

    Args:
        text: Text to colorize
        color: Color name

    Returns:
        Rich Text object with color applied
    """
    return Text(text, style=color)


def print_error(message: str) -> None:
    """Print error message in red."""
    console.print(f"[red]Error: {message}[/red]")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    console.print(f"[yellow]Warning: {message}[/yellow]")


def print_success(message: str) -> None:
    """Print success message in green."""
    console.print(f"[green]Success: {message}[/green]")


def print_info(message: str) -> None:
    """Print info message in blue."""
    console.print(f"[blue]Info: {message}[/blue]")


def format_response(response: Dict[str, Any], format_type: str = "text") -> None:
    """
    Format model response for display.

    Args:
        response: Response dictionary from model
        format_type: Output format (text, json)
    """
    if format_type == "json":
        console.print(json.dumps(response, indent=2))
    else:
        # Extract content from response
        if "content" in response:
            content = response["content"]

            # Check if response contains code
            if "```" in content:
                # Extract code blocks and format them
                parts = content.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        # Regular text
                        if part.strip():
                            console.print(part.strip())
                    else:
                        # Code block - extract language and content
                        lines = part.split("\n", 1)
                        if len(lines) == 2:
                            language = lines[0].strip()
                            code = lines[1].strip()
                            format_output(code, "code", language)
                        else:
                            format_output(part.strip(), "code", "text")
            else:
                # Regular text response
                console.print(content)
        else:
            console.print("No content in response")