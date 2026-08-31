import json
import subprocess
from pathlib import Path


class CompilerService:
    """
    Service for executing Python code through the WasmBox
    Pyodide runtime.
    """

    def compile(self, code: str) -> dict:
        project_root = Path(__file__).resolve().parents[3]

        runner = project_root / "wasmbox-compiler" / "run_python.mjs"

        try:
            process = subprocess.run(
                ["node", str(runner)],
                input=code,
                capture_output=True,
                text=True,
                timeout=30
            )

            if not process.stdout:
                return {
                    "success": False,
                    "output": "",
                    "error": process.stderr or "Runtime produced no output"
                }

            result = json.loads(process.stdout)

            return result

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Python execution timed out"
            }

        except json.JSONDecodeError:
            return {
                "success": False,
                "output": "",
                "error": "Invalid response from Python runtime"
            }

        except Exception as error:
            return {
                "success": False,
                "output": "",
                "error": str(error)
            }