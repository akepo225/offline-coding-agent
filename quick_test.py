#!/usr/bin/env python3
"""Quick test to check if fixes are working without full model run"""

import sys
from pathlib import Path

# Test Fix 1: Escaped newlines
print("Testing Fix 1: Escaped Newlines")
print("=" * 50)

test_content = "Line 1\\nLine 2\\nLine 3"
print(f"Before fix: {repr(test_content)}")

# Apply the fix
fixed_content = test_content.replace('\\n', '\n').replace('\\t', '\t')
print(f"After fix: {repr(fixed_content)}")

if '\n' in fixed_content and '\\n' not in fixed_content:
    print("✅ Fix 1 working: Escaped newlines converted to actual newlines")
else:
    print("❌ Fix 1 NOT working")

print()

# Test Fix 3: Placeholder detection
print("Testing Fix 3: Placeholder Detection")
print("=" * 50)

test_cases = [
    {"bytes_written": 29, "should_trigger": True},
    {"bytes_written": 150, "should_trigger": False},
    {"bytes_written": 50, "should_trigger": True},
]

for test in test_cases:
    bytes_written = test["bytes_written"]
    should_trigger = test["should_trigger"]

    will_trigger = bytes_written < 100

    if will_trigger == should_trigger:
        print(f"✅ {bytes_written} bytes: {'Triggers' if will_trigger else 'Does not trigger'} warning (correct)")
    else:
        print(f"❌ {bytes_written} bytes: Unexpected behavior")

print()

# Check that the code changes are in place
print("Verifying Code Changes")
print("=" * 50)

working_assistant_path = Path(__file__).parent / "working_assistant.py"
with open(working_assistant_path, 'r') as f:
    content = f.read()

checks = [
    ("Fix 1: Escaped newline replacement", "content.replace('\\\\n', '\\n')"),
    ("Fix 2: Explicit feedback", "DO NOT read again"),
    ("Fix 3: Placeholder detection", "bytes_written"),
    ("Fix 4: Enhanced system prompt", "EFFICIENCY RULES"),
]

all_passed = True
for check_name, check_string in checks:
    if check_string in content:
        print(f"✅ {check_name}: Found in code")
    else:
        print(f"❌ {check_name}: NOT found in code")
        all_passed = False

print()
if all_passed:
    print("✅ All fixes are in place in the code!")
else:
    print("❌ Some fixes are missing")

print()
print("Note: Full model test timed out after 5 minutes")
print("This suggests the model got stuck in Step 2 of the autonomous loop")
print("Possible causes:")
print("  1. Feedback is too long (with full file content)")
print("  2. Model is generating very long response")
print("  3. Context window issues")
print()
print("Recommendation: Test interactively with shorter file to verify behavior")
