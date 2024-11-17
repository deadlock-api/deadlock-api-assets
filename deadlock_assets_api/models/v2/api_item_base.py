from murmurhash2 import murmurhash2
from pydantic import BaseModel, ConfigDict

from deadlock_assets_api.glob import IMAGE_BASE_URL
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_item_base import (
    RawItemBaseV2,
    RawItemPropertyV2,
    RawItemWeaponInfoV2,
)


def parse_img_path(v):
    if v is None:
        return None
    split_index = v.find("abilities/")
    if split_index == -1:
        split_index = v.find("upgrades/")
    if split_index == -1:
        split_index = v.find("hud/")
    if split_index == -1:
        _, v = v.split("{images}/")
        split_index = 0
    v = f"{IMAGE_BASE_URL}/{v[split_index:]}"
    v = v.replace('"', "")
    v = v.replace("_psd.", ".")
    v = v.replace("_png.", ".")
    v = v.replace(".psd", ".png")
    return v


class ItemBaseV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    class_name: str
    name: str
    start_trained: bool | None
    image: str | None
    image_webp: str | None = None
    hero: int | None
    update_time: int | None
    properties: dict[str, RawItemPropertyV2] | None
    weapon_info: RawItemWeaponInfoV2 | None

    @classmethod
    def from_raw_item(
        cls,
        raw_model: RawItemBaseV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> dict:
        raw_model = raw_model.model_dump()
        raw_model["id"] = murmurhash2(raw_model["class_name"].encode(), 0x31415926)
        raw_model["name"] = localization.get(
            raw_model["class_name"], raw_model["class_name"]
        )
        raw_model["hero"] = next(
            (h.id for h in raw_heroes if raw_model["class_name"] in h.items.values()),
            None,
        )
        raw_model["image"] = parse_img_path(raw_model["image"])
        if raw_model["image"] is not None:
            raw_model["image_webp"] = raw_model["image"].replace(".png", ".webp")
        return raw_model
