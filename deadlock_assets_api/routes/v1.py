import json
from enum import Enum

from fastapi import APIRouter
from pydantic import TypeAdapter
from starlette.responses import FileResponse

from deadlock_assets_api import utils
from deadlock_assets_api.models.v1.colors import ColorV1
from deadlock_assets_api.models.v1.map import MapV1


with open("deploy/client_versions.json") as f:
    ALL_CLIENT_VERSIONS = sorted(json.load(f), reverse=True)
VALID_CLIENT_VERSIONS = Enum(
    "ValidClientVersions", {str(b): int(b) for b in ALL_CLIENT_VERSIONS}, type=int
)
LATEST_VERSION = max(ALL_CLIENT_VERSIONS)

router = APIRouter(prefix="/v1")


@router.get("/map", response_model_exclude_none=True)
def get_map(client_version: VALID_CLIENT_VERSIONS | None = None) -> MapV1:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    return utils.read_parse_data_model(
        f"deploy/versions/{client_version.value}/map_data.json", MapV1
    )


@router.get("/colors", response_model_exclude_none=True)
def get_colors(client_version: VALID_CLIENT_VERSIONS | None = None) -> dict[str, ColorV1]:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    ta = TypeAdapter(dict[str, ColorV1])
    return utils.read_parse_data_ta(f"deploy/versions/{client_version.value}/colors_data.json", ta)


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
    return utils.read_parse_data_ta(f"deploy/versions/{client_version.value}/icons_data.json", ta)


@router.get("/sounds", response_model_exclude_none=True)
def get_sounds(client_version: VALID_CLIENT_VERSIONS | None = None) -> dict:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    ta = TypeAdapter(dict[str, str | dict])
    return utils.read_parse_data_ta(f"deploy/versions/{client_version.value}/sounds_data.json", ta)
