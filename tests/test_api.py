from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


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