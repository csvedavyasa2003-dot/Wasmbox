from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import time
import os

app = FastAPI(title="WasmBox API")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Models
# -----------------------------
class RunRequest(BaseModel):
    module_id: str = Field(..., min_length=1)
    a: int
    b: int


LOG_FILE = "backend/logs/execution.log"

# Create log folder if missing
os.makedirs("backend/logs", exist_ok=True)


# -----------------------------
# Root
# -----------------------------
@app.get("/")
def root():
    return {"message": "WasmBox API Running"}


# -----------------------------
# Run WASM
# -----------------------------
@app.post("/api/run")
def run_module(request: RunRequest):

    # Validation
    if not request.module_id.strip():
        return {
            "stdout": "",
            "stderr": "module_id cannot be empty"
        }

    wasm_path = f"uploads/{request.module_id}"

    if not os.path.exists(wasm_path):
        return {
            "stdout": "",
            "stderr": f"WASM file '{request.module_id}' not found"
        }

    start_time = time.time()

    # Mock execution
    result = request.a + request.b

    execution_time = round(
        (time.time() - start_time) * 1000,
        2
    )

    # Save execution history
    log_entry = (
        f"Module: {request.module_id} | "
        f"a={request.a} b={request.b} | "
        f"Output={result} | "
        f"Time={execution_time} ms\n"
    )

    with open(LOG_FILE, "a") as file:
        file.write(log_entry)

    return {
        "module_id": request.module_id,
        "stdout": str(result),
        "stderr": "",
        "execution_time_ms": execution_time
    }


# -----------------------------
# History API
# -----------------------------
@app.get("/api/history")
def get_history():

    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as file:
        lines = file.readlines()

    return [line.strip() for line in lines]


# -----------------------------
# Metrics API
# -----------------------------
@app.get("/api/metrics")
def get_metrics():

    if not os.path.exists(LOG_FILE):
        return {
            "total_runs": 0,
            "average_execution_time_ms": 0
        }

    with open(LOG_FILE, "r") as file:
        lines = file.readlines()

    total_runs = len(lines)

    execution_times = []

    for line in lines:
        try:
            time_part = line.split("Time=")[1]
            ms_value = float(
                time_part.replace(" ms", "").strip()
            )
            execution_times.append(ms_value)
        except:
            pass

    average_time = (
        sum(execution_times) / len(execution_times)
        if execution_times
        else 0
    )

    return {
        "total_runs": total_runs,
        "average_execution_time_ms": round(
            average_time,
            2
        )
    }