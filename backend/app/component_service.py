import time
from pathlib import Path

from wasmtime import Config, Engine, Store
from wasmtime.component import Component, Linker


def run_component(file_path: str, name: str) -> dict:
    """
    Execute a WasmBox WebAssembly Component.

    The component is loaded and executed through Wasmtime's
    Component Model API.
    """

    path = Path(file_path)

    if not path.exists():
        return {
            "result": None,
            "execution_time_ms": 0,
            "status": "error",
            "error": f"Component not found: {file_path}",
        }

    if path.suffix.lower() != ".wasm":
        return {
            "result": None,
            "execution_time_ms": 0,
            "status": "error",
            "error": "Only .wasm components are supported.",
        }

    start_time = time.perf_counter()

    try:
        # Create Wasmtime engine and store.
        config = Config()
        engine = Engine(config)
        store = Store(engine)

        # Load the WebAssembly Component.
        component = Component.from_file(engine, str(path))

        # Create a restricted linker.
        # No host functions are registered here.
        linker = Linker(engine)

        # Instantiate the component.
        instance = linker.instantiate(store, component)

        # Retrieve the expected WasmBox plugin interface.
        greet = instance.get_func(store, "greet")

        # Execute the plugin.
        result = greet(store, name)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "result": result,
            "execution_time_ms": round(elapsed_ms, 3),
            "status": "success",
        }

    except Exception as error:
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "result": None,
            "execution_time_ms": round(elapsed_ms, 3),
            "status": "error",
            "error": str(error),
        }