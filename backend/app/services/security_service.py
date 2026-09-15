from wasmtime.component import Component


ALLOWED_IMPORT_PREFIXES = (
    "wasi:io/",
    "wasi:clocks/",
    "wasi:random/",
    "wasi:cli/",
)


FORBIDDEN_IMPORT_PREFIXES = (
    "wasi:filesystem/",
    "wasi:sockets/",
)


def validate_component_security(component: Component, engine) -> None:
    """
    Validate that a WasmBox component does not request
    forbidden host capabilities.

    Filesystem and network access remain blocked.
    """

    imports = component.type.imports(engine)
    unauthorized_imports = []

    for imported in imports:
        import_name = str(imported)

        if import_name.startswith(FORBIDDEN_IMPORT_PREFIXES):
            unauthorized_imports.append(import_name)
        elif not import_name.startswith(ALLOWED_IMPORT_PREFIXES):
            unauthorized_imports.append(import_name)

    if unauthorized_imports:
        raise PermissionError(
            "WASM component requests unauthorized host capabilities: "
            + ", ".join(unauthorized_imports)
        )
