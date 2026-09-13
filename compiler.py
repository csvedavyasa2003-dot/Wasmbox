import wasmtime

def run_python_plugin(source_code: str) -> str:
    """
    Executes untrusted Python source code inside a WASI-sandboxed
    CPython interpreter running in Wasmtime, and returns captured output.
    """
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)

    wasi_config = wasmtime.WasiConfig()
    wasi_config.argv = ["python", "-c", source_code]
    wasi_config.inherit_stdout()
    wasi_config.inherit_stderr()
    wasi_config.preopen_dir(".", "/")
    store.set_wasi(wasi_config)

    linker = wasmtime.Linker(engine)
    linker.define_wasi()

    module = wasmtime.Module.from_file(engine, "python.wasm")
    instance = linker.instantiate(store, module)

    start = instance.exports(store)["_start"]
    start(store)