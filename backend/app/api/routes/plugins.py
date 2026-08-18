from fastapi import APIRouter

router = APIRouter(
    prefix="/api/plugins",
    tags=["Plugins"]
)


@router.get("/")
def list_plugins():
    return {
        "success": True,
        "plugins": []
    }