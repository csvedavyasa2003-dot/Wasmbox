import wasmtime

def run_python_plugin(source_code: str) -> dict:
    """
    Executes untrusted Python source code inside a WASI-sandboxed
    CPython interpreter running in Wasmtime.
    Returns a dict with captured stdout, stderr, and success status.
    """
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)

    wasi_config = wasmtime.WasiConfig()
    wasi_config.argv = ["python", "-c", source_code]

    wasi_config.stdout_file = "plugin_stdout.txt"
    wasi_config.stderr_file = "plugin_stderr.txt"
    wasi_config.preopen_dir(".", "/")
    store.set_wasi(wasi_config)

    linker = wasmtime.Linker(engine)
    linker.define_wasi()

    module = wasmtime.Module.from_file(engine, "python.wasm")
    instance = linker.instantiate(store, module)

    success = True
    error_message = None
    try:
        start = instance.exports(store)["_start"]
        start(store)
    except Exception as e:
        success = False
        error_message = str(e)

    with open("plugin_stdout.txt", "r") as f:
        stdout = f.read()
    with open("plugin_stderr.txt", "r") as f:
        stderr = f.read()

    return {
        "success": success,
        "stdout": stdout,
        "stderr": stderr,
        "error": error_message,
    }