import threading
from wasmtime import Config, Engine, Store, Module, Instance


MAX_MEMORY_MB = 10
EXECUTION_TIMEOUT_SECONDS = 5


def run_uploaded_wasm(file_path: str, a: int, b: int):

    # Configure Wasmtime
    config = Config()
    config.epoch_interruption = True

    engine = Engine(config)
    store = Store(engine)

    # Limit WASM memory to 10 MB
    max_memory_bytes = MAX_MEMORY_MB * 1024 * 1024
    store.set_limits(memory_size=max_memory_bytes)

    # Set execution deadline
    store.set_epoch_deadline(1)

    # Load WASM module
    module = Module.from_file(engine, file_path)

    # Security policy: deny all host imports
    imports = list(module.imports)

    if imports:
        raise PermissionError(
            "WASM module requests host capabilities. "
            "Filesystem and network access are denied."
        )

    # Create timeout event
    timeout_triggered = threading.Event()

    def timeout_worker():
        if not timeout_triggered.wait(EXECUTION_TIMEOUT_SECONDS):
            timeout_triggered.set()
            engine.increment_epoch()

    timeout_thread = threading.Thread(
        target=timeout_worker,
        daemon=True
    )

    timeout_thread.start()

    try:
        # Create WASM instance
        instance = Instance(store, module, [])

        # Get the add function
        add = instance.exports(store)["add"]

        # Execute WASM function
        result = add(store, a, b)

        return result

    except Exception as exc:

        if timeout_triggered.is_set():
            raise TimeoutError(
                f"WASM execution exceeded "
                f"{EXECUTION_TIMEOUT_SECONDS} seconds."
            ) from exc

        raise

    finally:
        timeout_triggered.set()
