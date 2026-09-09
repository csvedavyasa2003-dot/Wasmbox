from pathlib import Path


class PluginService:
    """
    Manage compiled WebAssembly plugin artifacts stored by WasmBox.
    """

    def __init__(self):
        self.upload_dir = (
            Path(__file__).resolve().parents[3]
            / "backend"
            / "uploads"
        )

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _resolve_plugin(self, module_id: str) -> Path:
        """
        Resolve a plugin ID safely inside the upload directory.
        """

        if not module_id:
            raise ValueError("Plugin ID is required.")

        if Path(module_id).name != module_id:
            raise ValueError("Invalid plugin ID.")

        if not module_id.endswith(".wasm"):
            raise ValueError("Only .wasm plugins are supported.")

        plugin_path = self.upload_dir / module_id

        if plugin_path.parent != self.upload_dir:
            raise ValueError("Invalid plugin path.")

        return plugin_path

    def list_plugins(self) -> list[dict]:
        """
        Return metadata for all stored WASM plugins.
        """

        plugins = []

        for path in sorted(self.upload_dir.glob("*.wasm")):
            plugins.append(
                {
                    "module_id": path.name,
                    "size_bytes": path.stat().st_size,
                }
            )

        return plugins

    def get_plugin(self, module_id: str) -> Path:
        """
        Return the path of a stored plugin.
        """

        plugin_path = self._resolve_plugin(module_id)

        if not plugin_path.exists():
            raise FileNotFoundError(
                f"Plugin not found: {module_id}"
            )

        return plugin_path

    def delete_plugin(self, module_id: str) -> None:
        """
        Delete a stored plugin.
        """

        plugin_path = self.get_plugin(module_id)
        plugin_path.unlink()