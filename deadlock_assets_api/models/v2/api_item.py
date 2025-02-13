import json
import logging
from typing import Annotated, Union

from pydantic import Field

from deadlock_assets_api import utils
from deadlock_assets_api.models.v2.api_ability import AbilityV2
from deadlock_assets_api.models.v2.api_upgrade import UpgradeV2
from deadlock_assets_api.models.v2.api_weapon import WeaponV2
from deadlock_assets_api.models.v2.raw_ability import RawAbilityV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_upgrade import RawUpgradeV2
from deadlock_assets_api.models.v2.raw_weapon import RawWeaponV2

ItemV2 = Annotated[Union[AbilityV2, WeaponV2, UpgradeV2], Field(discriminator="type")]

LOGGER = logging.getLogger(__name__)


def test_parse():
    def get_raw_heroes():
        with open("res/raw_heroes.json") as f:
            raw_heroes = json.load(f)
        return [
            RawHeroV2(class_name=k, **v)
            for k, v in raw_heroes.items()
            if k.startswith("hero_") and "base" not in k and "generic" not in k and "dummy" not in k
        ]

    def get_raw_items():
        def parse(class_name, data) -> RawWeaponV2 | RawUpgradeV2 | RawAbilityV2 | None:
            name = utils.strip_prefix(class_name, "citadel_").lower()
            first_word = name.split("_")[0]
            if first_word == "ability":
                return RawAbilityV2(class_name=class_name, **data)
            elif first_word == "upgrade":
                return RawUpgradeV2(class_name=class_name, **data)
            elif first_word == "weapon":
                return RawWeaponV2(class_name=class_name, **data)

            hero_list = [
                "astro",
                "atlas",
                "bebop",
                "bomber",
                "cadence",
                "chrono",
                "dynamo",
                "fathom",
                "forge",
                "ghost",
                "gigawatt",
                "gunslinger",
                "haze",
                "hornet",
                "inferno",
                "kali",
                "kelvin",
                "krill",
                "lash",
                "magician",
                "mirage",
                "nano",
                "operative",
                "orion",
                "rutger",
                "shieldguy",
                "shiv",
                "slork",
                "synth",
                "tengu",
                "thumper",
                "tokamak",
                "trapper",
                "vandal",
                "viper",
                "viscous",
                "warden",
                "wraith",
                "wrecker",
                "yakuza",
                "yamato",
            ]
            if first_word in hero_list:
                return RawAbilityV2(class_name=class_name, **data)
            LOGGER.warning(f"Unknown class name: {class_name}")
            return None

        with open("res/raw_items.json") as f:
            raw_items = json.load(f)
        raw_items = [
            parse(k, v)
            for k, v in raw_items.items()
            if "base" not in k
            and "dummy" not in k
            and ("generic" not in k or "citadel" in k)
            and isinstance(v, dict)
        ]
        return [item for item in raw_items if item is not None]

    raw_heroes = get_raw_heroes()
    raw_items = get_raw_items()

    localization = {}
    with open("res/localization/citadel_gc_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_heroes_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_main_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_mods_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_gc_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_heroes_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_main_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_mods_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])

    def item_from_raw_item(
        raw_item: RawUpgradeV2 | RawAbilityV2 | RawWeaponV2,
        raw_hero: list[RawHeroV2],
        localization,
    ) -> ItemV2:
        if raw_item.type == "ability":
            return AbilityV2.from_raw_item(raw_item, raw_hero, localization)
        elif raw_item.type == "upgrade":
            return UpgradeV2.from_raw_item(raw_item, raw_hero, localization)
        elif raw_item.type == "weapon":
            return WeaponV2.from_raw_item(raw_item, raw_hero, localization)
        else:
            raise ValueError(f"Unknown item type: {raw_item.type}")

    items = [item_from_raw_item(raw_item, raw_heroes, localization) for raw_item in raw_items]

    with open("test.json", "w") as f:
        json.dump([item.model_dump(exclude_none=True) for item in items], f, indent=2)


if __name__ == "__main__":
    test_parse()
