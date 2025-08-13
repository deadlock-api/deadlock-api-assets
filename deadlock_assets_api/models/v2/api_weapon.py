from typing import Literal

from pydantic import ConfigDict

from deadlock_assets_api.models.v2.api_item_base import ItemBaseV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_weapon import RawWeaponInfoV2, RawWeaponV2


class WeaponV2(ItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["weapon"] = "weapon"

    weapon_info: RawWeaponInfoV2 | None = None

    @classmethod
    def from_raw_item(
        cls,
        raw_weapon: RawWeaponV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> "WeaponV2":
        raw_model = super().from_raw_item(raw_weapon, raw_heroes, localization)
        raw_model["name"] = localization.get(
            raw_model["class_name"],
            localization.get(
                raw_model["class_name"].replace("citadel_weapon", "citadel_weapon_hero"),
                raw_model["class_name"],
            ).strip(),
        ).strip()
        return cls(**raw_model)
