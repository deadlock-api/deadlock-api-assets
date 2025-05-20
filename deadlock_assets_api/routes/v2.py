import json
import logging
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import TypeAdapter

from deadlock_assets_api import utils
from deadlock_assets_api.models.languages import Language
from deadlock_assets_api.models.v2.api_hero import HeroV2
from deadlock_assets_api.models.v2.api_item import ItemV2
from deadlock_assets_api.models.v2.build_tag import BuildTagV2
from deadlock_assets_api.models.v2.enums import ItemSlotTypeV2, ItemTypeV2
from deadlock_assets_api.models.v2.api_upgrade import UpgradeV2
from deadlock_assets_api.models.v2.rank import RankV2

LOGGER = logging.getLogger(__name__)
with open("deploy/client_versions.json") as f:
    ALL_CLIENT_VERSIONS = sorted(json.load(f), reverse=True)
VALID_CLIENT_VERSIONS = Enum(
    "ValidClientVersions", {str(b): int(b) for b in ALL_CLIENT_VERSIONS}, type=int
)

router = APIRouter(prefix="/v2")


@router.get("/heroes", response_model_exclude_none=True, tags=["Heroes"])
def get_heroes(
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
    only_active: bool | None = None,
) -> list[HeroV2]:
    if only_active is None:
        only_active = False
    language = utils.validate_language(language)
    client_version = utils.validate_client_version(client_version)

    ta = TypeAdapter(list[HeroV2])
    heroes = utils.read_parse_data_ta(
        f"deploy/versions/{client_version}/heroes/{language.value}.json", ta
    )
    if only_active:
        heroes = [h for h in heroes if not only_active or not h.disabled]
    return heroes


@router.get("/heroes/{id}", response_model_exclude_none=True, tags=["Heroes"])
def get_hero(
    id: int,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> HeroV2:
    heroes = get_heroes(language, client_version)
    for hero in heroes:
        if hero.id == id:
            return hero
    raise HTTPException(status_code=404, detail="Hero not found")


@router.get("/heroes/by-name/{name}", response_model_exclude_none=True, tags=["Heroes"])
def get_hero_by_name(
    name: str,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> HeroV2:
    heroes = get_heroes(language, client_version)
    for hero in heroes:
        if hero.class_name.lower() in [name.lower(), f"hero_{name.lower()}"]:
            return hero
        if hero.name.lower() in [name.lower(), f"hero_{name.lower()}"]:
            return hero
    raise HTTPException(status_code=404, detail="Hero not found")


@router.get("/items", response_model_exclude_none=True, tags=["Items"])
def get_items(
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[ItemV2]:
    language = utils.validate_language(language)
    client_version = utils.validate_client_version(client_version)

    ta = TypeAdapter(list[ItemV2])
    return utils.read_parse_data_ta(
        f"deploy/versions/{client_version}/items/{language.value}.json", ta
    )


@router.get("/items/{id_or_class_name}", response_model_exclude_none=True, tags=["Items"])
def get_item(
    id_or_class_name: int | str,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> ItemV2:
    items = get_items(language, client_version=client_version)
    id = int(id_or_class_name) if utils.is_int(id_or_class_name) else id_or_class_name
    for item in items:
        if item.id == id or item.class_name == id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.get("/items/by-type/{type}", response_model_exclude_none=True, tags=["Items"])
def get_items_by_type(
    type: ItemTypeV2,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[ItemV2]:
    items = get_items(language, client_version)
    type = ItemTypeV2(type.capitalize())
    return [c for c in items if c.type == type]


@router.get("/items/by-hero-id/{id}", response_model_exclude_none=True, tags=["Items"])
def get_items_by_hero_id(
    id: int,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[ItemV2]:
    items = get_items_by_type(ItemTypeV2.ABILITY, language, client_version)
    filter_class_names = {
        "citadel_ability_climb_rope",
        "citadel_ability_dash",
        "citadel_ability_sprint",
        "citadel_ability_melee_parry",
        "citadel_ability_jump",
        "citadel_ability_mantle",
        "citadel_ability_slide",
        "citadel_ability_zip_line",
        "citadel_ability_zipline_boost",
    }
    return [i for i in items if id in i.heroes and i.class_name not in filter_class_names]


@router.get("/items/by-slot-type/{slot_type}", response_model_exclude_none=True, tags=["Items"])
def get_items_by_slot_type(
    slot_type: ItemSlotTypeV2,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[ItemV2]:
    items = get_items_by_type(ItemTypeV2.UPGRADE, language, client_version)
    slot_type = ItemSlotTypeV2(slot_type.capitalize())
    return [c for c in items if isinstance(c, UpgradeV2) and c.item_slot_type == slot_type]


@router.get("/client-versions")
def get_client_versions() -> list[int]:
    return ALL_CLIENT_VERSIONS


@router.get("/ranks", response_model_exclude_none=True)
def get_ranks(
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[RankV2]:
    language = utils.validate_language(language)
    client_version = utils.validate_client_version(client_version)
    ta = TypeAdapter(list[RankV2])
    return utils.read_parse_data_ta(
        f"deploy/versions/{client_version}/ranks/{language.value}.json", ta
    )


@router.get("/build-tags", response_model_exclude_none=True)
def get_build_tags(
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[BuildTagV2]:
    language = utils.validate_language(language)
    client_version = utils.validate_client_version(client_version)
    ta = TypeAdapter(list[BuildTagV2])
    return utils.read_parse_data_ta(
        f"deploy/versions/{client_version}/build_tags/{language.value}.json", ta
    )
