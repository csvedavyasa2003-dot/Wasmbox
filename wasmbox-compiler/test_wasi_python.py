import wasmtime

engine = wasmtime.Engine()
store = wasmtime.Store(engine)

wasi_config = wasmtime.WasiConfig()
wasi_config.argv = ["python", "-c", "print('hello world')"]
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