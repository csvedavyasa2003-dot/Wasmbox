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
# Home
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
# Run WASM Module
# -----------------------------
@app.post("/api/run")
def run_module(request: RunRequest):

    try:

        # Validation
        if not request.module_id:
            return {
                "stdout": "",
                "stderr": "module_id cannot be empty"
            }

        wasm_path = os.path.join(
            UPLOAD_DIR,
            request.module_id
        )

        if not os.path.exists(wasm_path):
            return {
                "stdout": "",
                "stderr": f"WASM file '{request.module_id}' not found"
            }

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

# -----------------------------
# Execution History
# -----------------------------
@app.get("/api/history")
def get_history():

    log_path = "backend/logs/execution.log"

    if not os.path.exists(log_path):
        return []

    history = []

    with open(log_path, "r") as log:
        for line in log.readlines():
            history.append(line.strip())

    return history

# -----------------------------
# Metrics API
# -----------------------------
@app.get("/api/metrics")
def get_metrics():

    log_path = "backend/logs/execution.log"

    if not os.path.exists(log_path):
        return {
            "total_runs": 0,
            "average_execution_time_ms": 0
        }

    with open(log_path, "r") as log:
        lines = log.readlines()

    total_runs = len(lines)

    execution_times = []

    for line in lines:
        try:
            time_part = line.split("Time=")[1]
            execution_time = float(
                time_part.replace(" ms", "").strip()
            )
            execution_times.append(execution_time)
        except:
            pass

    average_time = (
        sum(execution_times) / len(execution_times)
        if execution_times else 0
    )

    return {
        "total_runs": total_runs,
        "average_execution_time_ms": round(
            average_time,
            2
        )
    }