from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.app.wasm_service import run_uploaded_wasm
from backend.app.models import RunRequest

app = FastAPI(title="WasmBox API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "WasmBox Backend Running"
    }


@app.post("/upload-wasm")
async def upload_wasm(file: UploadFile = File(...)):

    if not file.filename.endswith(".wasm"):
        return {
            "error": "Only .wasm files are allowed"
        }

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "path": file_path
    }


@app.post("/api/run")
def run_module(data: RunRequest):

    file_path = os.path.join(
        UPLOAD_DIR,
        data.module_id
    )

    result = run_uploaded_wasm(
        file_path,
        data.a,
        data.b
    )

    return {
        "module_id": data.module_id,
        "stdout": str(result),
        "stderr": ""
    }