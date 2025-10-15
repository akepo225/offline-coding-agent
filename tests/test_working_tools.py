#!/usr/bin/env python3
"""
Functional tests for WorkingToolManager and related components.

These tests are designed to run without loading the model and to avoid
modifying the repository state. Git tests are performed in a temporary
repository under the project's temp/ directory.
"""

import json
import os
import sys
import time
from pathlib import Path
import shutil
import tempfile

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from working_assistant import WorkingToolManager, WorkingAIAssistant  # noqa: E402


def _new_temp_dir(prefix: str) -> Path:
    base = PROJECT_ROOT / "temp" / "tool_tests"
    base.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f"{prefix}_", dir=str(base)))
    return tmp


def test_file_operations() -> dict:
    mgr = WorkingToolManager()
    tmp = _new_temp_dir("files")

    # create_directory - nested
    nested_dir = tmp / "a" / "b" / "c"
    r1 = mgr.tool_create_directory(str(nested_dir))

    # write_file with unescape (should unescape) and verify newline
    file1 = tmp / "unescape.txt"
    r2 = mgr.tool_write_file(str(file1), "line1\\nline2")
    if Path(file1).exists():
        with open(file1, "r", encoding="utf-8") as f:
            content_unescaped = f.read()
    else:
        content_unescaped = None

    # write_file with code block (should NOT unescape)
    file2 = tmp / "codeblock.txt"
    codeblock_text = """```python\nprint('x')\n```"""
    r3 = mgr.tool_write_file(str(file2), codeblock_text.replace("\n", "\\n"))
    if Path(file2).exists():
        with open(file2, "r", encoding="utf-8") as f:
            content_codeblock = f.read()
    else:
        content_codeblock = None

    # read_file: missing
    r4 = mgr.tool_read_file(str(tmp / "missing.txt"))

    # read_file: small binary (intentional decode error)
    bin_path = tmp / "bin.dat"
    with open(bin_path, "wb") as f:
        f.write(b"\x00\xff\xfe\x01\x02")
    r5 = mgr.tool_read_file(str(bin_path))

    return {
        "create_directory": r1,
        "write_file_unescape": {
            "result": r2,
            "content": content_unescaped,
            "newline_present": ("\n" in content_unescaped) if content_unescaped is not None else False,
        },
        "write_file_codeblock": {
            "result": r3,
            "content": content_codeblock,
            "literal_backslash_n": ("\\n" in content_codeblock) if content_codeblock is not None else False,
        },
        "read_file_missing": r4,
        "read_file_binary": r5,
        "tmp_dir": str(tmp),
    }


def test_execute_python() -> dict:
    mgr = WorkingToolManager()
    tmp = _new_temp_dir("execpy")

    # code: success
    r1 = mgr.tool_execute_python(code="print('ok')")

    # code: error returncode
    r2 = mgr.tool_execute_python(code="import sys; sys.exit(2)")

    # file_path: success
    script = tmp / "script.py"
    script.write_text("print('file-ok')", encoding="utf-8")
    r3 = mgr.tool_execute_python(file_path=str(script))

    # timeout: should timeout
    r4 = mgr.tool_execute_python(code="import time; time.sleep(2)", timeout=1)

    # timeout as string (should error in current implementation)
    r5 = mgr.tool_execute_python(code="print('x')", timeout="1")

    return {"code_ok": r1, "code_err": r2, "file_ok": r3, "timeout": r4, "timeout_str": r5}


def _init_git_repo(base: Path) -> Path:
    repo = base / "git_repo"
    repo.mkdir(parents=True, exist_ok=True)
    # Initialize repo
    mgr = WorkingToolManager()
    mgr.tool_run_command("git init", cwd=str(repo))
    # Minimal user config
    mgr.tool_run_command("git config user.name test-user", cwd=str(repo))
    mgr.tool_run_command("git config user.email test@example.com", cwd=str(repo))
    # Create a file
    (repo / "README.md").write_text("# Test Repo\n", encoding="utf-8")
    mgr.tool_run_command("git add README.md", cwd=str(repo))
    mgr.tool_run_command("git commit -m initial", cwd=str(repo))
    return repo


def test_run_command() -> dict:
    mgr = WorkingToolManager()
    tmp = _new_temp_dir("cmd")

    # echo
    r1 = mgr.tool_run_command("echo hello")

    # python -c
    r2 = mgr.tool_run_command("python -c \"print('123')\"")

    # blocked command
    r3 = mgr.tool_run_command("ls -la")

    # timeout coercion
    r4 = mgr.tool_run_command("python -c \"import time; time.sleep(0.1); print('t')\"", timeout="2")

    # cwd and input parameters
    r5 = mgr.tool_run_command("python -c \"print(input())\"", timeout=5, cwd='None', input="hi")

    # git workflow in isolated repo
    repo = _init_git_repo(tmp)
    r6 = mgr.tool_run_command("git status --porcelain", cwd=str(repo))
    (repo / "file.txt").write_text("x\n", encoding="utf-8")
    r7 = mgr.tool_run_command("git add file.txt", cwd=str(repo))
    r8 = mgr.tool_run_command("git commit -m added", cwd=str(repo))

    return {
        "echo": r1,
        "python_c": r2,
        "blocked_ls": r3,
        "timeout_str": r4,
        "stdin_input": r5,
        "git_status": r6,
        "git_add": r7,
        "git_commit": r8,
        "repo": str(repo),
    }


def test_parse_and_execute_tools() -> dict:
    assistant = WorkingAIAssistant()
    assistant.auto_confirm = True
    # Compose tool call with triple-quoted content
    resp = (
        "[TOOL: create_directory(dir_path='temp/pae_test')]"
        "[TOOL: write_file(file_path='temp/pae_test/x.txt', content='''a\\nb\\n''')]"
        "[TOOL: read_file(file_path='temp/pae_test/x.txt')]"
    )
    r1 = assistant.parse_and_execute_tools(resp)

    # execute_python with string timeout (expected error in current code)
    resp2 = "[TOOL: execute_python(code=\"print('hi')\", timeout='1')]"
    r2 = assistant.parse_and_execute_tools(resp2)

    return {"chain_write_read": r1, "exec_timeout_str": r2}


def test_handle_command() -> dict:
    assistant = WorkingAIAssistant()
    # Add, list, remove, clear
    target_file = PROJECT_ROOT / "tests" / "test_aider.py"
    assistant.handle_command(f"/add {target_file}")
    added_after = [str(p) for p in assistant.context_files]
    assistant.handle_command(f"/remove {target_file}")
    removed_after = [str(p) for p in assistant.context_files]
    assistant.handle_command("/clear")
    cleared_after = [str(p) for p in assistant.context_files]
    return {
        "added_after": added_after,
        "removed_after": removed_after,
        "cleared_after": cleared_after,
    }


def test_large_write() -> dict:
    mgr = WorkingToolManager()
    tmp = _new_temp_dir("large")
    payload = ("0123456789" * 500)  # 5,000 chars
    path = tmp / "large.txt"
    r = mgr.tool_write_file(str(path), payload)
    return {"result": r, "path": str(path), "size": len(payload)}


def main() -> None:
    results = {
        "file_operations": test_file_operations(),
        "execute_python": test_execute_python(),
        "run_command": test_run_command(),
        "parse_and_execute_tools": test_parse_and_execute_tools(),
        "handle_command": test_handle_command(),
        "large_write": test_large_write(),
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()


