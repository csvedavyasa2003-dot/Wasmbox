from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.component_service import run_component
from backend.app.services.execution_history_service import (
    execution_history_service,
)
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
    started_at = datetime.now(timezone.utc).isoformat()

    try:
        file_path = plugin_service.get_plugin(data.module_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    result = run_component(str(file_path), data.name)

    history_entry = {
        "timestamp": started_at,
        "module_id": data.module_id,
        "name": data.name,
        "status": result["status"],
        "execution_time_ms": result.get("execution_time_ms", 0),
        "result": result.get("result"),
        "error": result.get("error"),
    }
    execution_history_service.record(history_entry)

    if result["status"] == "security_violation":
        raise HTTPException(
            status_code=403,
            detail=result.get(
                "error",
                "Component security policy rejected the plugin.",
            ),
        )

    if result["status"] == "timeout":
        raise HTTPException(
            status_code=408,
            detail=result.get(
                "error",
                "Component execution timed out.",
            ),
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
