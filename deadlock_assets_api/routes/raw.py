from fastapi import APIRouter
from starlette.responses import FileResponse

from deadlock_assets_api.routes import VALID_CLIENT_VERSIONS, LATEST_VERSION

router = APIRouter(prefix="/raw", tags=["Raw"])


@router.get("/heroes")
def get_raw_heroes(client_version: VALID_CLIENT_VERSIONS | None = None) -> FileResponse:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/raw_heroes.json")


@router.get("/items")
def get_raw_items(client_version: VALID_CLIENT_VERSIONS | None = None) -> FileResponse:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/raw_items.json")


@router.get("/generic_data")
def get_generic_data(client_version: VALID_CLIENT_VERSIONS | None = None) -> FileResponse:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/generic_data.json")
