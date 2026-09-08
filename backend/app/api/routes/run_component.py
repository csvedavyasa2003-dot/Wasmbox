from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.component_service import run_component


router = APIRouter(
    prefix="/api",
    tags=["Component Execution"],
)


UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads"


class ComponentRunRequest(BaseModel):
    module_id: str
    name: str


@router.post("/run-component")
def run_component_module(data: ComponentRunRequest):
    file_path = UPLOAD_DIR / data.module_id

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Component not found: {data.module_id}",
        )

    if file_path.suffix.lower() != ".wasm":
        raise HTTPException(
            status_code=400,
            detail="Only .wasm components are supported.",
        )

    result = run_component(str(file_path), data.name)

    if result["status"] == "error":
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Component execution failed."),
        )

    return {
        "module_id": data.module_id,
        "result": result["result"],
        "execution_time_ms": result["execution_time_ms"],
        "status": result["status"],
    }