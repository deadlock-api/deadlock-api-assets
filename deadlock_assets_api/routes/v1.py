import os
from enum import Enum

from fastapi import APIRouter
from pydantic import TypeAdapter
from starlette.responses import FileResponse

from deadlock_assets_api.models.v1.colors import ColorV1
from deadlock_assets_api.models.v1.map import MapV1


ALL_CLIENT_VERSIONS = sorted([int(b) for b in os.listdir("deploy/versions")], reverse=True)
VALID_CLIENT_VERSIONS = Enum(
    "ValidClientVersions", {str(b): int(b) for b in ALL_CLIENT_VERSIONS}, type=int
)
LATEST_VERSION = max(ALL_CLIENT_VERSIONS)

router = APIRouter(prefix="/v1")


@router.get("/map", response_model_exclude_none=True)
def get_map(client_version: VALID_CLIENT_VERSIONS | None = None) -> MapV1:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    with open(f"deploy/versions/{client_version.value}/map_data.json") as f:
        return MapV1.model_validate_json(f.read())


@router.get("/colors", response_model_exclude_none=True)
def get_colors(client_version: VALID_CLIENT_VERSIONS | None = None) -> dict[str, ColorV1]:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    ta = TypeAdapter(dict[str, ColorV1])
    with open(f"deploy/versions/{client_version.value}/colors_data.json") as f:
        return ta.validate_json(f.read())


@router.get("/steam-info")
def get_steam_info(client_version: VALID_CLIENT_VERSIONS | None = None) -> FileResponse:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/steam_info.json")


@router.get("/icons", response_model_exclude_none=True)
def get_icons(client_version: VALID_CLIENT_VERSIONS | None = None) -> dict[str, str]:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    ta = TypeAdapter(dict[str, str])
    with open(f"deploy/versions/{client_version.value}/icons_data.json") as f:
        return ta.validate_json(f.read())


@router.get("/sounds", response_model_exclude_none=True)
def get_sounds(client_version: VALID_CLIENT_VERSIONS | None = None) -> dict[str, str | dict]:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    ta = TypeAdapter(dict[str, str | dict])
    with open(f"deploy/versions/{client_version.value}/sounds_data.json") as f:
        return ta.validate_json(f.read())
