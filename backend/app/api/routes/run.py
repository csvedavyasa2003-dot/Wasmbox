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

    try:
        result = run_uploaded_wasm(
            str(file_path),
            data.a,
            data.b
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=403,
            detail=str(error)
        )

    response = {
        "module_id": data.module_id,
        "stdout": (
            str(result["result"])
            if result["result"] is not None
            else ""
        ),
        "stderr": "",
        "status": result["status"],
        "execution_time_ms": result["execution_time_ms"],
        "fuel_consumed": result["fuel_consumed"],
    }

    if result.get("error"):
        response["stderr"] = result["error"]

    return response