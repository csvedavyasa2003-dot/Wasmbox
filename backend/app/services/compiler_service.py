import ast
import json
import subprocess
from pathlib import Path


RESTRICTED_IMPORTS = {
    "os",
    "socket",
    "subprocess",
    "sys",
    "shutil",
    "ctypes",
}


def validate_python_code(source_code: str) -> tuple[bool, str | None]:
    """
    Validate Python source code before sending it to the Pyodide runtime.

    Restricted modules are rejected to prevent plugins from requesting
    potentially unsafe host-related functionality.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        return False, f"Syntax error: {error}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]

                if module_name in RESTRICTED_IMPORTS:
                    return False, f"Restricted import not allowed: {alias.name}"

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split(".")[0]

                if module_name in RESTRICTED_IMPORTS:
                    return False, f"Restricted import not allowed: {node.module}"

    return True, None


class CompilerService:
    """
    Service for executing Python code through the WasmBox
    Pyodide runtime.
    """

    def compile(self, code: str) -> dict:
        # Validate Python source before execution.
        is_valid, validation_error = validate_python_code(code)

        if not is_valid:
            return {
                "success": False,
                "output": "",
                "error": validation_error,
            }

        project_root = Path(__file__).resolve().parents[3]
        runner = project_root / "wasmbox-compiler" / "run_python.mjs"

        try:
            process = subprocess.run(
                ["node", str(runner)],
                input=code,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if not process.stdout:
                return {
                    "success": False,
                    "output": "",
                    "error": process.stderr or "Runtime produced no output",
                }

            result = json.loads(process.stdout)
            return result

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Python execution timed out",
            }

        except json.JSONDecodeError:
            return {
                "success": False,
                "output": "",
                "error": "Invalid response from Python runtime",
            }

        except Exception as error:
            return {
                "success": False,
                "output": "",
                "error": str(error),
            }