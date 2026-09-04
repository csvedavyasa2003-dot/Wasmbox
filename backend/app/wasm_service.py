from wasmtime import Store, Module, Instance


def run_uploaded_wasm(file_path: str, a: int, b: int):
    store = Store()

    module = Module.from_file(store.engine, file_path)

    # Security policy: deny all host imports.
    # This prevents the WASM module from receiving host capabilities
    # such as filesystem or network access.
    imports = list(module.imports)

    if imports:
        raise PermissionError(
            "WASM module requests host capabilities. "
            "Filesystem and network access are denied."
        )

    instance = Instance(store, module, [])

    add = instance.exports(store)["add"]

    result = add(store, a, b)

    return result