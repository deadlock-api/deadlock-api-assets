import os
from functools import lru_cache

from fastapi import APIRouter

from deadlock_assets_api.glob import SVGS_BASE_URL, SOUNDS_BASE_URL
from deadlock_assets_api.models.v1 import colors
from deadlock_assets_api.models.v1.colors import ColorV1
from deadlock_assets_api.models.v1.map import MapV1
from deadlock_assets_api.models.v1.steam_info import SteamInfoV1

router = APIRouter(prefix="/v1", tags=["V1"])


@router.get("/map", response_model_exclude_none=True)
def get_map() -> MapV1:
    return MapV1.get_default()


@router.get("/colors", response_model_exclude_none=True)
def get_colors() -> dict[str, ColorV1]:
    return colors.get_colors()


@router.get("/steam-info")
def get_steam_info() -> SteamInfoV1:
    return SteamInfoV1.load()


@router.get("/icons", response_model_exclude_none=True)
def get_icons() -> dict[str, str]:
    return {i.rstrip(".svg").rstrip(".png"): f"{SVGS_BASE_URL}/{i}" for i in get_all_icons()}


@lru_cache
def get_all_icons() -> list[str]:
    return [i for i in os.listdir("svgs") if i.endswith(".svg") or i.endswith(".png")]


@router.get("/sounds", response_model_exclude_none=True)
def get_sounds() -> dict[str, str | dict]:
    return get_all_sounds()


@lru_cache
def get_all_sounds() -> dict:
    def build_folder(folder: str) -> dict:
        def parse_key(file: str) -> str:
            if "." not in file:
                return file
            return "".join(file.split(".")[:-1])

        return {
            parse_key(file): f"{SOUNDS_BASE_URL}/{os.path.join(folder, file)}"
            if os.path.isfile(os.path.join(folder, file))
            else build_folder(os.path.join(folder, file))
            for file in os.listdir(folder)
        }

    return build_folder("sounds")
