from fastapi import APIRouter
from starlette.responses import FileResponse

router = APIRouter(prefix="/raw", tags=["Raw"])


@router.get("/heroes")
def get_heroes() -> FileResponse:
    return FileResponse("res/raw_heroes.json")


@router.get("/generic_data")
def get_generic_data() -> FileResponse:
    return FileResponse("res/raw_generic_data.json")


@router.get("/items")
def get_items() -> FileResponse:
    return FileResponse("res/raw_items.json")


@router.get("/colors")
def get_colors() -> FileResponse:
    return FileResponse("res/citadel_shared_colors.css")


@router.get("/steam-info")
def get_steam_info() -> FileResponse:
    return FileResponse("res/steam.inf")
