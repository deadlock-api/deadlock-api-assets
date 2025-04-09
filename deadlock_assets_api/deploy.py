import json
import os
import sys

import css_parser
import stringcase
from css_parser.css import ColorValue, CSSUnknownRule
from pydantic import TypeAdapter

from deadlock_assets_api.glob import SOUNDS_BASE_URL, SVGS_BASE_URL
from deadlock_assets_api.models.languages import Language
from deadlock_assets_api.models.v1.colors import ColorV1
from deadlock_assets_api.models.v1.generic_data import GenericDataV1
from deadlock_assets_api.models.v1.map import MapV1
from deadlock_assets_api.models.v1.steam_info import SteamInfoV1
from deadlock_assets_api.models.v2.api_ability import AbilityV2
from deadlock_assets_api.models.v2.api_hero import HeroV2
from deadlock_assets_api.models.v2.api_item import ItemV2
from deadlock_assets_api.models.v2.api_upgrade import UpgradeV2
from deadlock_assets_api.models.v2.api_weapon import WeaponV2
from deadlock_assets_api.models.v2.rank import RankV2
from deadlock_assets_api.models.v2.raw_ability import RawAbilityV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_upgrade import RawUpgradeV2
from deadlock_assets_api.models.v2.raw_weapon import RawWeaponV2
from deadlock_assets_api.main import app


def load_localizations() -> dict[Language, dict[str, str]]:
    localizations = {}
    for language in Language:
        localizations[language] = {}
        paths = [
            f"res/localization/citadel_gc_{language}.json",
            f"res/localization/citadel_heroes_{language}.json",
            f"res/localization/citadel_main_{language}.json",
            f"res/localization/citadel_mods_{language}.json",
            f"res/localization/citadel_attributes_{language}.json",
        ]
        for path in paths:
            if not os.path.exists(path):
                continue
            with open(path) as f:
                localizations[language].update(json.load(f)["lang"]["Tokens"])
    return localizations


def load_generic_data() -> GenericDataV1:
    with open("res/generic_data.json") as f:
        return GenericDataV1.model_validate_json(f.read())


def load_client_versions() -> list[int]:
    versions_folder = "deploy/versions"
    return sorted(
        [
            int(b)
            for b in os.listdir(versions_folder)
            if not os.path.isfile(os.path.join(versions_folder, b))
        ],
        reverse=True,
    )


def load_map_data() -> MapV1:
    return MapV1.get_default()


def load_sounds_data() -> dict:
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


def load_colors_data() -> dict[str, dict]:
    colors = {}
    css_colors = css_parser.parseFile("res/citadel_shared_colors.css")
    for rule in css_colors.cssRules:
        if not isinstance(rule, CSSUnknownRule):
            continue
        if not rule.cssText.startswith("@define"):
            continue

        # Split CSS Text into key and value
        css_parts = rule.cssText[8:].replace(";", "").strip().split(":")
        css_key, css_value = (v.strip() for v in css_parts)

        # Parse Color Key
        css_key = stringcase.snakecase(css_key)

        # Parse Color Value
        color_value = ColorValue(css_value[:7] if css_value.startswith("#") else css_value)
        color_value._alpha = (
            int(css_value[7:], 16) if css_value.startswith("#") and len(css_value) > 7 else 255
        )

        colors[css_key] = ColorV1(
            red=color_value.red,
            green=color_value.green,
            blue=color_value.blue,
            alpha=color_value.alpha,
        ).model_dump(exclude_none=True)
    return colors


def load_steam_info() -> SteamInfoV1:
    with open("res/steam.inf") as f:
        data = f.read()
    data = dict(line.split("=") for line in data.splitlines() if "=" in line)
    data = {k.strip(): v.strip() for k, v in data.items()}
    return SteamInfoV1.model_validate(data)


def load_icons_data() -> dict:
    all_icons = [i for i in os.listdir("svgs") if i.endswith(".svg") or i.endswith(".png")]
    return {i.rstrip(".svg").rstrip(".png"): f"{SVGS_BASE_URL}/{i}" for i in all_icons}


def load_raw_heroes() -> list[RawHeroV2]:
    path = "res/raw_heroes.json"
    with open(path) as f:
        content = f.read()
    return TypeAdapter(list[RawHeroV2]).validate_json(content)


def load_raw_items() -> list[RawAbilityV2 | RawWeaponV2 | RawUpgradeV2]:
    path = "res/raw_items.json"
    with open(path) as f:
        content = f.read()
    return TypeAdapter(list[RawAbilityV2 | RawWeaponV2 | RawUpgradeV2]).validate_json(content)


def build_ranks(localization: dict[str, str]) -> list[dict]:
    return [RankV2.from_tier(i, localization).model_dump(exclude_none=True) for i in range(12)]


def build_heroes(raw_heroes, localization: dict[str, str]) -> list[HeroV2]:
    return [HeroV2.from_raw_hero(r, localization).model_dump(exclude_none=True) for r in raw_heroes]


def build_items(raw_items, raw_heroes, localization: dict[str, str]) -> list[ItemV2]:
    def item_from_raw_item(raw_item: RawUpgradeV2 | RawAbilityV2 | RawWeaponV2) -> ItemV2:
        if raw_item.type == "ability":
            return AbilityV2.from_raw_item(raw_item, raw_heroes, localization)
        elif raw_item.type == "upgrade":
            return UpgradeV2.from_raw_item(raw_item, raw_heroes, localization)
        elif raw_item.type == "weapon":
            return WeaponV2.from_raw_item(raw_item, raw_heroes, localization)
        else:
            raise ValueError(f"Unknown item type: {raw_item.type}")

    return [item_from_raw_item(r).model_dump(exclude_none=True) for r in raw_items]


if __name__ == "__main__":
    out_folder = sys.argv[1]

    steam_info = load_steam_info()
    version_id = steam_info.client_version

    # Prepare Folders
    os.makedirs(f"{out_folder}/versions/{version_id}/ranks", exist_ok=True)
    os.makedirs(f"{out_folder}/versions/{version_id}/heroes", exist_ok=True)
    os.makedirs(f"{out_folder}/versions/{version_id}/items", exist_ok=True)

    # Load Data
    localizations = load_localizations()
    generic_data = load_generic_data()
    map_data = load_map_data()
    sounds_data = load_sounds_data()
    colors_data = load_colors_data()
    client_versions = load_client_versions()
    icons_data = load_icons_data()
    raw_heroes = load_raw_heroes()
    raw_items = load_raw_items()

    # Write Data files
    with open(f"{out_folder}/latest_version.txt", "w") as f:
        f.write(str(version_id))

    with open(f"{out_folder}/client_versions.json", "w") as f:
        json.dump(client_versions, f)

    with open(f"{out_folder}/versions/{version_id}/generic_data.json", "w") as f:
        f.write(generic_data.model_dump_json())

    with open(f"{out_folder}/versions/{version_id}/map_data.json", "w") as f:
        f.write(map_data.model_dump_json())

    with open(f"{out_folder}/versions/{version_id}/sounds_data.json", "w") as f:
        json.dump(sounds_data, f)

    with open(f"{out_folder}/versions/{version_id}/colors_data.json", "w") as f:
        json.dump(colors_data, f)

    with open(f"{out_folder}/versions/{version_id}/steam_info.json", "w") as f:
        f.write(steam_info.model_dump_json())

    with open(f"{out_folder}/versions/{version_id}/icons_data.json", "w") as f:
        json.dump(icons_data, f)

    with open(f"{out_folder}/versions/{version_id}/raw_heroes.json", "w") as f:
        json.dump([h.model_dump(exclude_none=True) for h in raw_heroes], f)

    with open(f"{out_folder}/versions/{version_id}/raw_items.json", "w") as f:
        json.dump([i.model_dump(exclude_none=True) for i in raw_items], f)

    with open(f"{out_folder}/versions/{version_id}/raw_items.json", "w") as f:
        json.dump([h.model_dump(exclude_none=True) for h in raw_items], f)

    for language, localization in localizations.items():
        localization = localizations[Language.English] | localization
        ranks = build_ranks(localization)
        with open(f"{out_folder}/versions/{version_id}/ranks/{language.value}.json", "w") as f:
            json.dump(ranks, f)

        heroes = build_heroes(raw_heroes, localization)
        with open(f"{out_folder}/versions/{version_id}/heroes/{language.value}.json", "w") as f:
            json.dump(heroes, f)

        items = build_items(raw_items, raw_heroes, localization)
        with open(f"{out_folder}/versions/{version_id}/items/{language.value}.json", "w") as f:
            json.dump(items, f)

    openapi_scheme = app.openapi()
    with open(f"{out_folder}/openapi.json", "w") as f:
        json.dump(openapi_scheme, f)
