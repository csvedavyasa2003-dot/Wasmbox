from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)
WASM_MODULES_DIR = Path(__file__).resolve().parents[1] / "backend" / "wasm_modules"
UPLOADS_DIR = Path(__file__).resolve().parents[1] / "backend" / "uploads"


def prepare_test_module(module_name: str):
    source = WASM_MODULES_DIR / module_name
    destination = UPLOADS_DIR / module_name

    shutil.copy2(source, destination)
    return destination

def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "WasmBox API is running",
        "status": "ok"
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "WasmBox"
    }


def test_plugins():
    response = client.get("/api/plugins/")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["plugins"] == []


def test_compile_success():
    response = client.post(
        "/api/compile/",
        json={"code": "print(2 + 3)"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["output"] == "5\n"


def test_compile_error():
    response = client.post(
        "/api/compile/",
        json={"code": "print(10 / 0)"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert "ZeroDivisionError" in data["error"]


def test_execute():
    response = client.post(
        "/api/execute/",
        json={"module_id": "test-module"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["status"] == "pending"
    assert data["module_id"] == "test-module"

def test_run_wasm_module():
    response = client.post(
        "/api/run",
        json={
            "module_id": "test.wasm",
            "a": 10,
            "b": 20
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["module_id"] == "test.wasm"
    assert data["stdout"] == "30"
    assert data["stderr"] == ""

def test_compile_restricted_os_import():
    response = client.post(
        "/api/compile/",
        json={"code": "import os\nos.listdir('/')"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert data["output"] == ""
    assert data["error"] == "Restricted import not allowed: os"


def test_compile_restricted_socket_import():
    response = client.post(
        "/api/compile/",
        json={"code": "import socket"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "Restricted import not allowed: socket"


def test_compile_restricted_subprocess_import():
    response = client.post(
        "/api/compile/",
        json={"code": "import subprocess"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "Restricted import not allowed: subprocess"


def test_compile_restricted_from_import():
    response = client.post(
        "/api/compile/",
        json={"code": "from os import listdir"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "Restricted import not allowed: os"


def test_compile_syntax_error():
    response = client.post(
        "/api/compile/",
        json={"code": "print(10 /"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert data["output"] == ""
    assert data["error"].startswith("Syntax error:")
def test_run_filesystem_attack_is_blocked():
    response = client.post(
        "/api/run",
        json={
            "module_id": "filesystem_attack.wasm",
            "a": 10,
            "b": 20
        }
    )

    assert response.status_code == 403

    data = response.json()

    assert "Filesystem and network access are denied" in data["detail"]


def test_run_network_attack_is_blocked():
    response = client.post(
        "/api/run",
        json={
            "module_id": "network_attack.wasm",
            "a": 10,
            "b": 20
        }
    )

    assert response.status_code == 403

    data = response.json()

    assert "Filesystem and network access are denied" in data["detail"]


def test_run_infinite_loop_hits_resource_limit():
    response = client.post(
        "/api/run",
        json={
            "module_id": "infinite_loop.wasm",
            "a": 10,
            "b": 20
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "resource_limit"
    assert data["stdout"] == ""
    assert data["fuel_consumed"] == 100000
    assert "all fuel consumed" in data["stderr"]
def test_run_filesystem_attack_is_blocked():
    module = prepare_test_module("filesystem_attack.wasm")

    try:
        response = client.post(
            "/api/run",
            json={
                "module_id": module.name,
                "a": 10,
                "b": 20
            }
        )

        assert response.status_code == 403

        data = response.json()

        assert "Filesystem and network access are denied" in data["detail"]

    finally:
        module.unlink(missing_ok=True)


def test_run_network_attack_is_blocked():
    module = prepare_test_module("network_attack.wasm")

    try:
        response = client.post(
            "/api/run",
            json={
                "module_id": module.name,
                "a": 10,
                "b": 20
            }
        )

        assert response.status_code == 403

        data = response.json()

        assert "Filesystem and network access are denied" in data["detail"]

    finally:
        module.unlink(missing_ok=True)


def test_run_infinite_loop_hits_resource_limit():
    module = prepare_test_module("infinite_loop.wasm")

    try:
        response = client.post(
            "/api/run",
            json={
                "module_id": module.name,
                "a": 10,
                "b": 20
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "resource_limit"
        assert data["stdout"] == ""
        assert data["fuel_consumed"] == 100000
        assert "all fuel consumed" in data["stderr"]

    finally:
        module.unlink(missing_ok=True)
def test_run_component_success():
    source = (
        Path(__file__).resolve().parents[1]
        / "component-poc"
        / "hello.wasm"
    )

    destination = (
        Path(__file__).resolve().parents[1]
        / "backend"
        / "uploads"
        / "hello-component.wasm"
    )

    shutil.copy2(source, destination)

    try:
        response = client.post(
            "/api/run-component",
            json={
                "module_id": "hello-component.wasm",
                "name": "Vedavyasa",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["module_id"] == "hello-component.wasm"
        assert data["result"] == "Hello, Vedavyasa!"
        assert data["status"] == "success"
        assert data["execution_time_ms"] >= 0

    finally:
        destination.unlink(missing_ok=True)


def test_run_component_missing_module():
    response = client.post(
        "/api/run-component",
        json={
            "module_id": "does-not-exist.wasm",
            "name": "Vedavyasa",
        },
    )

    assert response.status_code == 404

    shutil.copy2(source, destination)

    try:
        response = client.post(
            "/api/run-component",
            json={
                "module_id": "hello-component.wasm",
                "name": "Vedavyasa",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["module_id"] == "hello-component.wasm"
        assert data["result"] == "Hello, Vedavyasa!"
        assert data["status"] == "success"
        assert data["execution_time_ms"] >= 0

    finally:
        destination.unlink(missing_ok=True)


def test_run_component_missing_module():
    response = client.post(
        "/api/run-component",
        json={
            "module_id": "does-not-exist.wasm",
            "name": "Vedavyasa",
        },
    )

    assert response.status_code == 404