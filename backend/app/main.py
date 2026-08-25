from fastapi import FastAPI, UploadFile, File
import os

from backend.app.wasm_service import run_uploaded_wasm
from backend.app.models import WasmRunRequest

app = FastAPI(title="WasmBox API")

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


@app.post("/run-uploaded-wasm")
def execute_uploaded_wasm(data: WasmRunRequest):

    file_path = os.path.join(
        UPLOAD_DIR,
        data.filename
    )

    result = run_uploaded_wasm(
        file_path,
        data.a,
        data.b
    )

    return {
        "filename": data.filename,
        "a": data.a,
        "b": data.b,
        "result": result
    }