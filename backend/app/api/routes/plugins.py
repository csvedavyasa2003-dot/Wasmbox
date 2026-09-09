from fastapi import APIRouter, HTTPException

from backend.app.services.plugin_service import PluginService


router = APIRouter(
    prefix="/api/plugins",
    tags=["Plugins"],
)

plugin_service = PluginService()


@router.get("/")
def list_plugins():
    return {
        "success": True,
        "plugins": plugin_service.list_plugins(),
    }


@router.get("/{module_id}")
def get_plugin(module_id: str):
    try:
        plugin_path = plugin_service.get_plugin(module_id)

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

    return {
        "success": True,
        "module_id": plugin_path.name,
        "size_bytes": plugin_path.stat().st_size,
    }