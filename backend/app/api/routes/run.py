from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.app.models import RunRequest
from backend.app.wasm_service import run_uploaded_wasm


router = APIRouter(
    prefix="/api",
    tags=["Execution"]
)


UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads"


@router.post("/run")
def run_module(data: RunRequest):
    file_path = UPLOAD_DIR / data.module_id

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Module not found: {data.module_id}"
        )

    result = run_uploaded_wasm(
        str(file_path),
        data.a,
        data.b
    )

    return {
        "module_id": data.module_id,
        "stdout": str(result),
        "stderr": ""
    }