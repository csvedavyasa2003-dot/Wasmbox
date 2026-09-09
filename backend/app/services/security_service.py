from wasmtime.component import Component


def validate_component_security(component: Component, engine) -> None:
    """
    Validate that a WasmBox component does not request
    unauthorized host capabilities.

    WasmBox components are expected to be self-contained and
    must not require host-provided filesystem or network access.
    """

    imports = component.type.imports(engine)

    if imports:
        import_names = []

        for name in imports:
            import_names.append(str(name))

        raise PermissionError(
            "WASM component requests unauthorized host capabilities: "
            + ", ".join(import_names)
        )