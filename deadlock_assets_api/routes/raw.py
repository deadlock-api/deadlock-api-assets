import os
from enum import Enum

from fastapi import APIRouter
from starlette.responses import FileResponse


ALL_CLIENT_VERSIONS = sorted([int(b) for b in os.listdir("deploy/versions")], reverse=True)
VALID_CLIENT_VERSIONS = Enum(
    "ValidClientVersions", {str(b): int(b) for b in ALL_CLIENT_VERSIONS}, type=int
)
LATEST_VERSION = max(ALL_CLIENT_VERSIONS)

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
