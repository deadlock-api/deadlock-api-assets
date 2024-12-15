from deadlock_assets_api import utils
from deadlock_assets_api.models.v1.item import ItemV1
from deadlock_assets_api.models.v2.raw_ability import RawAbilityV2
from deadlock_assets_api.models.v2.raw_upgrade import RawUpgradeV2
from deadlock_assets_api.models.v2.raw_weapon import RawWeaponV2


def parse_items(data: dict) -> list[ItemV1]:
    ability_dicts = {
        k: v
        for k, v in data.items()
        if "base" not in k
        and "dummy" not in k
        and ("generic" not in k or "citadel" in k)
        and isinstance(v, dict)
    }
    return [ItemV1(class_name=k, **v) for k, v in ability_dicts.items()]


def parse_items_v2(data: dict) -> list[RawWeaponV2 | RawUpgradeV2 | RawAbilityV2]:
    hero_dicts = {
        k: v
        for k, v in data.items()
        if "base" not in k
        and "dummy" not in k
        and ("generic" not in k or "citadel" in k)
        and isinstance(v, dict)
    }

    def parse(class_name, data) -> RawWeaponV2 | RawUpgradeV2 | RawAbilityV2:
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
            "mirage",
            "nano",
            "orion",
            "rutger",
            "shiv",
            "slork",
            "synth",
            "tengu",
            "thumper",
            "tokamak",
            "viscous",
            "warden",
            "wraith",
            "wrecker",
            "yakuza",
            "yamato",
        ]
        if first_word in hero_list:
            return RawAbilityV2(class_name=class_name, **data)
        print(f"Unknown class name: {class_name}")
        return None

    items = [parse(k, v) for k, v in hero_dicts.items()]
    return [i for i in items if i is not None]
