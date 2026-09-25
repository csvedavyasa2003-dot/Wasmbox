import os
import pytest

from backend.app.wasm_service import run_uploaded_wasm


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WASM_DIR = os.path.join(PROJECT_ROOT, "backend", "wasm_modules")


def wasm_file(name):
    return os.path.join(WASM_DIR, name)


def test_normal_wasm_execution():
    result = run_uploaded_wasm(
        wasm_file("add.wasm"),
        5,
        3
    )

    assert result == 8


def test_filesystem_attack_blocked():
    with pytest.raises(PermissionError):
        run_uploaded_wasm(
            wasm_file("filesystem_attack.wasm"),
            5,
            3
        )


def test_network_attack_blocked():
    with pytest.raises(PermissionError):
        run_uploaded_wasm(
            wasm_file("network_attack.wasm"),
            5,
            3
        )


def test_timeout_attack_blocked():
    with pytest.raises(TimeoutError):
        run_uploaded_wasm(
            wasm_file("timeout_attack.wasm"),
            5,
            3
        )


def test_memory_attack_blocked():
    result = run_uploaded_wasm(
        wasm_file("memory_attack.wasm"),
        5,
        3
    )

    # memory.grow returns -1 when the requested growth is denied.
    assert result == -1
 