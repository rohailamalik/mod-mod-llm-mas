import os
import subprocess
import tempfile
import json
import sys

from langchain_core.messages import AIMessage

def clean_code_fencing(code: str) -> str:
    lines = code.strip().splitlines()

    # Remove triple backticks at the start and end if present
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().endswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()

class ComponentValidator:
    def __init__(self, script_path: str):
        self.script_path = script_path  # Path to validation script

    def validate(self, text_str: str) -> str:
        code_str = clean_code_fencing(text_str)
        with tempfile.TemporaryDirectory() as temp_dir:
            code_path = os.path.join(temp_dir, "generated_component.py")
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code_str)

            result = subprocess.run(
                [sys.executable, self.script_path, code_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return f"Fail: Validation script failed: {result.stderr.strip()}"

            try:
                output = json.loads(result.stdout)
                status = output.get("status", "fail")
                issues = output.get("issues", [])
                if status.lower() == "pass":
                    return "PASS"
                else:
                    return f"FAIL: " + "\n".join(issues)
            except json.JSONDecodeError as e:
                return f"FAIL: Invalid JSON output: {e}\nRaw output:\n{result.stdout.strip()}"

    def invoke(self, text_str: str):
        return AIMessage(content=self.validate(text_str))


validator = ComponentValidator(script_path=r"C:\Users\Fishyman\PycharmProjects\ThesisWork\val_tests.py")
