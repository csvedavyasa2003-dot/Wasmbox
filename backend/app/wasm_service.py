import time

import wasmtime


MAX_FUEL = 100_000
MAX_MEMORY_MB = 10

def run_uploaded_wasm(file_path: str, a: int, b: int):
    config = wasmtime.Config()
    config.consume_fuel = True

    engine = wasmtime.Engine(config)
    store = wasmtime.Store(engine)
    # Limit WASM memory to 10 MB.
    max_memory_bytes = MAX_MEMORY_MB * 1024 * 1024
    store.set_limits(memory_size=max_memory_bytes)
    # Limit the amount of WebAssembly execution.
    store.set_fuel(MAX_FUEL)

    module = wasmtime.Module.from_file(engine, file_path)

    # Security policy: deny all host imports.
    # This prevents the WASM module from receiving host capabilities
    # such as filesystem or network access.
    imports = list(module.imports)

    if imports:
        raise PermissionError(
            "WASM module requests host capabilities. "
            "Filesystem and network access are denied."
        )

    start_time = time.perf_counter()

    try:
        instance = wasmtime.Instance(store, module, [])

        add = instance.exports(store)["add"]
        result = add(store, a, b)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        remaining_fuel = store.get_fuel()
        fuel_consumed = MAX_FUEL - remaining_fuel

        return {
            "result": result,
            "execution_time_ms": round(elapsed_ms, 3),
            "fuel_consumed": fuel_consumed,
            "status": "success",
        }

    except (wasmtime.WasmtimeError, wasmtime.Trap) as error:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            "result": None,
            "execution_time_ms": round(elapsed_ms, 3),
            "fuel_consumed": MAX_FUEL - store.get_fuel(),
            "status": "resource_limit",
            "error": str(error),
        }