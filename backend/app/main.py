from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.app.wasm_service import run_uploaded_wasm
from backend.app.models import RunRequest

import os
import time

app = FastAPI(title="WasmBox API")

# -----------------------------
# CORS Configuration
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Directories
# -----------------------------
UPLOAD_DIR = "backend/uploads"
LOG_DIR = "backend/logs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# -----------------------------
# Logging Function
# -----------------------------
def write_log(module_id, a, b, output, execution_time):

    log_path = "backend/logs/execution.log"

    with open(log_path, "a") as log:
        log.write(
            f"Module: {module_id} | "
            f"a={a} b={b} | "
            f"Output={output} | "
            f"Time={execution_time} ms\n"
        )

# -----------------------------
# Home API
# -----------------------------
@app.get("/")
def home():
    return {"message": "WasmBox API Running"}

# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}

# -----------------------------
# Upload WASM Module
# -----------------------------
@app.post("/upload-wasm")
async def upload_wasm(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "message": "WASM uploaded successfully",
        "module_id": file.filename
    }

# -----------------------------
# Phase 2 Run API
# -----------------------------
@app.post("/api/run")
def run_module(request: RunRequest):

    try:
        start_time = time.time()

        result = run_uploaded_wasm(
            request.module_id,
            request.a,
            request.b
        )

        execution_time = round(
            (time.time() - start_time) * 1000,
            2
        )

        write_log(
            request.module_id,
            request.a,
            request.b,
            result,
            execution_time
        )

        return {
            "module_id": request.module_id,
            "stdout": str(result),
            "stderr": "",
            "execution_time_ms": execution_time
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e)
        }