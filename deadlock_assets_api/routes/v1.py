from fastapi import APIRouter
from pydantic import TypeAdapter
from starlette.responses import FileResponse

from deadlock_assets_api import utils
from deadlock_assets_api.models.enums import ValidClientVersions, LATEST_VERSION
from deadlock_assets_api.models.v1.colors import ColorV1
from deadlock_assets_api.models.v1.map import MapV1
from deadlock_assets_api.models.v1.steam_info import SteamInfoV1

router = APIRouter(prefix="/v1")

# Pre-compiled TypeAdapters — avoids re-building schemas on every request
_TA_COLORS = TypeAdapter(dict[str, ColorV1])
_TA_ICONS = TypeAdapter(dict[str, str])
_TA_IMAGES = TypeAdapter(dict[str, str])
_TA_SOUNDS = TypeAdapter(dict[str, str | dict])


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
    return utils.read_parse_data_ta(
        f"deploy/versions/{client_version.value}/colors_data.json", _TA_COLORS
    )


@router.get("/steam-info")
def get_steam_info(client_version: ValidClientVersions | None = None) -> SteamInfoV1:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/steam_info.json")


@router.get("/icons", response_model_exclude_none=True)
def get_icons(client_version: ValidClientVersions | None = None) -> dict[str, str]:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return utils.read_parse_data_ta(
        f"deploy/versions/{client_version.value}/icons_data.json", _TA_ICONS
    )


@router.get("/images", response_model_exclude_none=True)
def get_images(client_version: ValidClientVersions | None = None) -> dict[str, str]:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return utils.read_parse_data_ta(
        f"deploy/versions/{client_version.value}/images_data.json", _TA_IMAGES
    )


@router.get("/sounds", response_model_exclude_none=True)
def get_sounds(client_version: ValidClientVersions | None = None) -> dict:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return utils.read_parse_data_ta(
        f"deploy/versions/{client_version.value}/sounds_data.json", _TA_SOUNDS
    )
