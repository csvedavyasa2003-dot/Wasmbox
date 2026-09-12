import threading
import time
from pathlib import Path

from wasmtime import Config, Engine, Store
from wasmtime.component import Component, Linker

from backend.app.services.security_service import (
    validate_component_security,
)


EXECUTION_TIMEOUT_SECONDS = 5


def run_component(file_path: str, name: str) -> dict:
    """
    Execute a WasmBox WebAssembly Component.

    The component is loaded and executed through Wasmtime's
    Component Model API with security validation and
    execution timeout protection.
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

    # Records whether the timeout thread actually fired.
    timeout_event = threading.Event()

    # Allows the timeout thread to stop waiting when execution
    # finishes before the timeout.
    stop_event = threading.Event()

    try:
        # Enable Wasmtime epoch interruption.
        config = Config()
        config.epoch_interruption = True

        engine = Engine(config)
        store = Store(engine)

        # Set the execution deadline to one epoch tick.
        store.set_epoch_deadline(1)

        # Interrupt execution after the configured timeout.
        def interrupt_execution():
            if not stop_event.wait(EXECUTION_TIMEOUT_SECONDS):
                timeout_event.set()
                engine.increment_epoch()

        timeout_thread = threading.Thread(
            target=interrupt_execution,
            daemon=True,
        )

        timeout_thread.start()

        # Load the WebAssembly Component.
        component = Component.from_file(
            engine,
            str(path),
        )

        # Validate the component's security policy.
        validate_component_security(
            component,
            engine,
        )

        # Create a restricted linker.
        # No host functions are registered.
        linker = Linker(engine)

        # Instantiate the component.
        instance = linker.instantiate(
            store,
            component,
        )

        # Retrieve the expected WasmBox plugin interface.
        greet = instance.get_func(
            store,
            "greet",
        )

        # Execute the plugin.
        result = greet(
            store,
            name,
        )

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "result": result,
            "execution_time_ms": round(
                elapsed_ms,
                3,
            ),
            "status": "success",
        }

    except PermissionError as error:
        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "result": None,
            "execution_time_ms": round(
                elapsed_ms,
                3,
            ),
            "status": "security_violation",
            "error": str(error),
        }

    except Exception as error:
        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        # Only classify the error as a timeout when our
        # timeout thread actually fired.
        if timeout_event.is_set():
            return {
                "result": None,
                "execution_time_ms": round(
                    elapsed_ms,
                    3,
                ),
                "status": "timeout",
                "error": "Component execution timed out.",
            }

        # Other Wasmtime/runtime errors are normal execution errors.
        return {
            "result": None,
            "execution_time_ms": round(
                elapsed_ms,
                3,
            ),
            "status": "error",
            "error": str(error),
        }

    finally:
        # Prevent the timeout thread from firing after
        # successful or failed execution.
        stop_event.set()