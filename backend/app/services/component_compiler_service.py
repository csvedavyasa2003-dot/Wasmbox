import shutil
import subprocess
import tempfile
from pathlib import Path


class ComponentCompilerService:
    """
    Compile a WasmBox Python plugin into a WebAssembly Component
    using componentize-py.
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[3]

        self.wit_dir = (
            self.project_root
            / "backend"
            / "component_compiler"
            / "wit"
        )

        self.upload_dir = (
            self.project_root
            / "backend"
            / "uploads"
        )

        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def compile(self, code: str, module_id: str) -> dict:
        """
        Compile Python source into a WASM Component.

        The generated component implements the WasmBox `plugin`
        WIT world.
        """

        if not module_id.endswith(".wasm"):
            module_id = f"{module_id}.wasm"

        if Path(module_id).name != module_id:
            return {
                "success": False,
                "output": "",
                "error": "Invalid module name.",
            }

        if not module_id:
            return {
                "success": False,
                "output": "",
                "error": "Module name is required.",
            }

        componentize = shutil.which("componentize-py")

        if componentize is None:
            return {
                "success": False,
                "output": "",
                "error": "componentize-py executable was not found.",
            }

        if not self.wit_dir.exists():
            return {
                "success": False,
                "output": "",
                "error": "WasmBox WIT definition was not found.",
            }

        output_path = self.upload_dir / module_id

        with tempfile.TemporaryDirectory(
            prefix="wasmbox-component-"
        ) as temp_dir:

            temp_path = Path(temp_dir)
            app_path = temp_path / "app.py"

            app_path.write_text(
                code,
                encoding="utf-8",
            )

            try:
                process = subprocess.run(
                    [
                        componentize,
                        "-d",
                        str(self.wit_dir),
                        "-w",
                        "plugin",
                        "componentize",
                        "--stub-wasi",
                        "app",
                        "-o",
                        str(output_path),
                    ],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

            except subprocess.TimeoutExpired:
                output_path.unlink(missing_ok=True)

                return {
                    "success": False,
                    "output": "",
                    "error": "Component compilation timed out.",
                }

            except Exception as error:
                output_path.unlink(missing_ok=True)

                return {
                    "success": False,
                    "output": "",
                    "error": str(error),
                }

        if process.returncode != 0:
            output_path.unlink(missing_ok=True)

            return {
                "success": False,
                "output": "",
                "error": (
                    process.stderr.strip()
                    or process.stdout.strip()
                    or "Component compilation failed."
                ),
            }

        if not output_path.exists():
            return {
                "success": False,
                "output": "",
                "error": (
                    "Compiler completed without producing "
                    "a WASM component."
                ),
            }

        return {
            "success": True,
            "output": str(output_path),
            "module_id": module_id,
            "size_bytes": output_path.stat().st_size,
        }