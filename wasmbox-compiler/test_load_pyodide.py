import wasmtime

engine = wasmtime.Engine()
store = wasmtime.Store(engine)

module = wasmtime.Module.from_file(
    engine,
    "wasmbox-compiler/pyodide/pyodide.asm.wasm"
)
print("Pyodide module loaded successfully!")
print("Module imports:", [imp.name for imp in module.imports][:10])