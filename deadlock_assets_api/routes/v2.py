import logging
import os
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import TypeAdapter

from deadlock_assets_api import utils
from deadlock_assets_api.models.languages import Language
from deadlock_assets_api.models.v2.api_hero import HeroV2
from deadlock_assets_api.models.v2.api_item import ItemV2
from deadlock_assets_api.models.v2.enums import ItemSlotTypeV2, ItemTypeV2
from deadlock_assets_api.models.v2.api_upgrade import UpgradeV2
from deadlock_assets_api.models.v2.rank import RankV2

LOGGER = logging.getLogger(__name__)
ALL_CLIENT_VERSIONS = sorted([int(b) for b in os.listdir("res/builds")], reverse=True)
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
    if language is None:
        language = Language.English
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(max(ALL_CLIENT_VERSIONS))
    if only_active is None:
        only_active = False
    if client_version not in ALL_CLIENT_VERSIONS:
        raise HTTPException(status_code=404, detail="Client Version not found")

    ta = TypeAdapter(list[HeroV2])
    with open(f"deploy/versions/{client_version.value}/heroes/{language.value}.json") as f:
        heroes = ta.validate_json(f.read())
    if only_active:
        heroes = [h for h in heroes if not only_active or not h.disabled]
    return sorted(heroes, key=lambda x: x.id)


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
    if language is None:
        language = Language.English
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(max(ALL_CLIENT_VERSIONS))
    if client_version not in ALL_CLIENT_VERSIONS:
        raise HTTPException(status_code=404, detail="Client Version not found")

    ta = TypeAdapter(list[ItemV2])
    with open(f"deploy/versions/{client_version.value}/items/{language.value}.json") as f:
        items = ta.validate_json(f.read())
    return sorted(items, key=lambda x: x.id)


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


@router.get("/items/by-hero-id/{id}", response_model_exclude_none=True, tags=["Items"])
def get_items_by_hero_id(
    id: int,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[ItemV2]:
    items = get_items(language, client_version)
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


@router.get("/items/by-type/{type}", response_model_exclude_none=True, tags=["Items"])
def get_items_by_type(
    type: ItemTypeV2,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[ItemV2]:
    items = get_items(language, client_version)
    type = ItemTypeV2(type.capitalize())
    return [c for c in items if c.type == type]


@router.get("/items/by-slot-type/{slot_type}", response_model_exclude_none=True, tags=["Items"])
def get_items_by_slot_type(
    slot_type: ItemSlotTypeV2,
    language: Language | None = None,
    client_version: VALID_CLIENT_VERSIONS | None = None,
) -> list[ItemV2]:
    items = get_items(language, client_version)
    slot_type = ItemSlotTypeV2(slot_type.capitalize())
    return [c for c in items if isinstance(c, UpgradeV2) and c.item_slot_type == slot_type]


@router.get("/client-versions")
def get_client_versions() -> list[int]:
    return ALL_CLIENT_VERSIONS


@router.get("/ranks", response_model_exclude_none=True)
def get_ranks(language: Language | None = None) -> list[RankV2]:
    if language is None:
        language = Language.English
    ta = TypeAdapter(list[RankV2])
    with open(f"deploy/versions/{max(ALL_CLIENT_VERSIONS)}/ranks/{language.value}.json") as f:
        return ta.validate_json(f.read())
