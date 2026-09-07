from wasmtime import Store, Module, Instance
import os


def run_uploaded_wasm(module_id: str, a: int, b: int):

    store = Store()

    file_path = os.path.join(
        "backend",
        "uploads",
        module_id
    )

    module = Module.from_file(
        store.engine,
        file_path
    )

    instance = Instance(store, module, [])

    add = instance.exports(store)["add"]

    result = add(store, a, b)

    return result