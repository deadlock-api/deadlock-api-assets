from murmurhash2 import murmurhash2
from pydantic import BaseModel, ConfigDict, Field

from deadlock_assets_api.glob import IMAGE_BASE_URL, SVGS_BASE_URL
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
    v = v[split_index:]
    v = v.replace('"', "")
    v = v.replace("_psd.", ".")
    v = v.replace("_png.", ".")
    v = v.replace(".psd", ".png")
    v = v.replace(".vsvg", ".svg")
    if v.endswith(".svg"):
        v = f"{SVGS_BASE_URL}/{v.split('/')[-1]}"
    else:
        v = f"{IMAGE_BASE_URL}/{v}"
    return v


class ItemPropertyV2(RawItemPropertyV2):
    model_config = ConfigDict(populate_by_name=True)

    prefix: str | None = Field(None)
    label: str | None = Field(None)
    postfix: str | None = Field(None)
    conditional: str | None = Field(None)
    icon: str | None = Field(None)

    @classmethod
    def from_raw_item_property(
        cls,
        raw_property: dict,
        key: str,
        localization: dict[str, str],
    ) -> dict:
        loc_token_override = raw_property.get("loc_token_override")
        if loc_token_override is not None:
            key = loc_token_override
        raw_property["icon"] = parse_img_path(raw_property["icon_path"])
        del raw_property["icon_path"]
        if key == "BuildUpDuration":
            key = "BuildupDuration"
        if key == "MoveSlowPercent":
            key = "SlowPercent"
        raw_property["label"] = localization.get(f"{key}_label", localization.get(f"{key}_Label"))
        raw_property["prefix"] = localization.get(f"{key}_prefix")
        raw_property["postfix"] = localization.get(f"{key}_postfix") or localization.get(
            f"{key}_postfx"
        )
        raw_property["conditional"] = localization.get(f"{key}_conditional")
        return raw_property


class ItemBaseV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    class_name: str
    name: str
    start_trained: bool | None
    image: str | None
    image_webp: str | None = None
    hero: int | None
    heroes: list[int] | None
    update_time: int | None
    properties: dict[str, ItemPropertyV2] | None
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
        raw_model["name"] = localization.get(raw_model["class_name"], raw_model["class_name"])
        if raw_model["properties"] is not None:
            raw_model["properties"] = {
                k: ItemPropertyV2.from_raw_item_property(v, k, localization)
                for k, v in raw_model["properties"].items()
            }
        raw_model["hero"] = next(
            (h.id for h in raw_heroes if raw_model["class_name"] in h.items.values()),
            None,
        )
        raw_model["heroes"] = [
            h.id for h in raw_heroes if raw_model["class_name"] in h.items.values()
        ]
        raw_model["image"] = parse_img_path(raw_model["image"])
        if raw_model["image"] is not None:
            raw_model["image_webp"] = raw_model["image"].replace(".png", ".webp")
        return raw_model
