from fastapi import APIRouter
from pydantic import TypeAdapter
from starlette.responses import FileResponse

from deadlock_assets_api import utils
from deadlock_assets_api.models.enums import ValidClientVersions, LATEST_VERSION
from deadlock_assets_api.models.v1.colors import ColorV1
from deadlock_assets_api.models.v1.map import MapV1

router = APIRouter(prefix="/v1")


@router.get("/map", response_model_exclude_none=True)
def get_map(client_version: ValidClientVersions | None = None) -> MapV1:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return utils.read_parse_data_model(
        f"deploy/versions/{client_version.value}/map_data.json", MapV1
    )


@router.get("/colors", response_model_exclude_none=True)
def get_colors(client_version: ValidClientVersions | None = None) -> dict[str, ColorV1]:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    ta = TypeAdapter(dict[str, ColorV1])
    return utils.read_parse_data_ta(f"deploy/versions/{client_version.value}/colors_data.json", ta)


@router.get("/steam-info")
def get_steam_info(client_version: ValidClientVersions | None = None) -> FileResponse:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/steam_info.json")


@router.get("/icons", response_model_exclude_none=True)
def get_icons(client_version: ValidClientVersions | None = None) -> dict[str, str]:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    ta = TypeAdapter(dict[str, str])
    return utils.read_parse_data_ta(f"deploy/versions/{client_version.value}/icons_data.json", ta)


@router.get("/sounds", response_model_exclude_none=True)
def get_sounds(client_version: ValidClientVersions | None = None) -> dict:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    ta = TypeAdapter(dict[str, str | dict])
    return utils.read_parse_data_ta(f"deploy/versions/{client_version.value}/sounds_data.json", ta)
