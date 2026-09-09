from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.component_service import run_component
from backend.app.services.plugin_service import PluginService


router = APIRouter(
    prefix="/api",
    tags=["Component Execution"],
)

plugin_service = PluginService()


class ComponentRunRequest(BaseModel):
    module_id: str
    name: str


@router.post("/run-component")
def run_component_module(data: ComponentRunRequest):
    try:
        file_path = plugin_service.get_plugin(data.module_id)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    result = run_component(
        str(file_path),
        data.name,
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=400,
            detail=result.get(
                "error",
                "Component execution failed.",
            ),
        )

    return {
        "module_id": data.module_id,
        "result": result["result"],
        "execution_time_ms": result["execution_time_ms"],
        "status": result["status"],
    }