import json

from pydantic import BaseModel, ConfigDict

from deadlock_assets_api.glob import IMAGE_BASE_URL
from deadlock_assets_api.models.v2.api_item_base import parse_img_path
from deadlock_assets_api.models.v2.enums import HeroItemTypeV2, ItemSlotTypeV2, HeroTypeV2
from deadlock_assets_api.models.v2.raw_hero import (
    RawHeroItemSlotInfoValueV2,
    RawHeroLevelInfoV2,
    RawHeroPurchaseBonusV2,
    RawHeroScalingStatV2,
    RawHeroShopStatDisplayV2,
    RawHeroShopWeaponStatsDisplayV2,
    RawHeroStartingStatsV2,
    RawHeroStatsDisplayV2,
    RawHeroStatsUIV2,
    RawHeroV2,
    RawHeroMapModCostBonusesV2,
)


def extract_image_url(v: str) -> str | None:
    if not v:
        return None
    split_index = v.find("abilities/")
    if split_index == -1:
        split_index = v.find("upgrades/")
    if split_index == -1:
        split_index = v.find("hud/")
    if split_index == -1:
        split_index = v.find("heroes/")
    v = f"{IMAGE_BASE_URL}/{v[split_index:]}"
    v = v.replace('"', "")
    v = v.replace("_psd.", ".")
    v = v.replace("_png.", ".")
    v = v.replace(".psd", ".png")
    return v


class HeroImagesV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    icon_hero_card: str | None = None
    icon_hero_card_webp: str | None = None
    icon_image_small: str | None = None
    icon_image_small_webp: str | None = None
    minimap_image: str | None = None
    minimap_image_webp: str | None = None
    selection_image: str | None = None
    selection_image_webp: str | None = None
    top_bar_image: str | None = None
    top_bar_image_webp: str | None = None
    top_bar_vertical_image: str | None = None
    top_bar_vertical_image_webp: str | None = None
    weapon_image: str | None = None
    weapon_image_webp: str | None = None
    background_image: str | None = None
    background_image_webp: str | None = None
    name_image: str | None = None

    @classmethod
    def from_raw_hero(cls, raw_hero: RawHeroV2) -> HeroImagesV2:
        keys = [
            "icon_hero_card",
            "icon_image_small",
            "minimap_image",
            "selection_image",
            "top_bar_image",
            "top_bar_vertical_image",
            "weapon_image",
            "background_image",
        ]
        images = {k: extract_image_url(v) for k, v in raw_hero.model_dump().items() if k in keys}
        return cls(
            **images,
            **{
                f"{k}_webp": v.replace(".png", ".webp") if v is not None else None
                for k, v in images.items()
            },
            **{
                "name_image": parse_img_path(raw_hero.name_image),
            },
        )


class HeroDescriptionV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lore: str | None = None
    role: str | None = None
    playstyle: str | None = None

    @classmethod
    def from_raw_hero(cls, raw_hero: RawHeroV2, localization: dict[str, str]) -> HeroDescriptionV2:
        return cls(
            lore=localization.get(f"{raw_hero.class_name}_lore"),
            role=localization.get(f"{raw_hero.class_name}_role"),
            playstyle=localization.get(f"{raw_hero.class_name}_playstyle"),
        )


class HeroPhysicsV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    collision_height: float
    collision_radius: float
    stealth_speed_meters_per_second: float
    step_height: float
    footstep_sound_travel_distance_meters: float | None = None
    step_sound_time: float | None = None
    step_sound_time_sprinting: float | None = None

    @classmethod
    def from_raw_hero(cls, raw_hero: RawHeroV2) -> HeroPhysicsV2:
        return cls(
            collision_height=raw_hero.collision_height,
            collision_radius=raw_hero.collision_radius,
            footstep_sound_travel_distance_meters=raw_hero.footstep_sound_travel_distance_meters,
            stealth_speed_meters_per_second=raw_hero.stealth_speed_meters_per_second,
            step_height=raw_hero.step_height,
            step_sound_time=raw_hero.step_sound_time,
            step_sound_time_sprinting=raw_hero.step_sound_time_sprinting,
        )


class HeroColorsV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    glow_enemy: tuple[int, int, int]
    glow_friendly: tuple[int, int, int]
    glow_team1: tuple[int, int, int]
    glow_team2: tuple[int, int, int]
    ui: tuple[int, int, int]

    @classmethod
    def from_raw_hero(cls, raw_hero: RawHeroV2) -> HeroColorsV2:
        return cls(
            glow_enemy=raw_hero.color_glow_enemy,
            glow_friendly=raw_hero.color_glow_friendly,
            glow_team1=raw_hero.color_glow_team1,
            glow_team2=raw_hero.color_glow_team2,
            ui=raw_hero.color_ui,
        )


class HeroShopWeaponStatsDisplayV2(RawHeroShopWeaponStatsDisplayV2):
    model_config = ConfigDict(populate_by_name=True)

    weapon_attributes: list[str] | None = None
    weapon_image_webp: str | None = None

    @classmethod
    def from_raw_hero_shop_weapon_stats_display(
        cls, raw_hero_shop_weapon_stats_display: RawHeroShopWeaponStatsDisplayV2
    ) -> HeroShopWeaponStatsDisplayV2:
        raw_model = raw_hero_shop_weapon_stats_display.model_dump()
        raw_model["weapon_attributes"] = (
            [i.strip() for i in raw_hero_shop_weapon_stats_display.weapon_attributes.split("|")]
            if raw_hero_shop_weapon_stats_display.weapon_attributes
            else []
        )
        raw_model["weapon_image"] = extract_image_url(
            raw_hero_shop_weapon_stats_display.weapon_image
        )
        if raw_model["weapon_image"] is not None:
            raw_model["weapon_image_webp"] = raw_model["weapon_image"].replace(".png", ".webp")
        return cls(**raw_model)


class HeroShopStatDisplayV2(RawHeroShopStatDisplayV2):
    model_config = ConfigDict(populate_by_name=True)

    weapon_stats_display: HeroShopWeaponStatsDisplayV2

    @classmethod
    def from_raw_hero(cls, raw_hero: RawHeroV2) -> HeroShopStatDisplayV2:
        raw_model = raw_hero.shop_stat_display.model_dump()
        raw_model["weapon_stats_display"] = (
            HeroShopWeaponStatsDisplayV2.from_raw_hero_shop_weapon_stats_display(
                raw_hero.shop_stat_display.weapon_stats_display
            )
        )
        return cls(**raw_model)


class HeroLevelInfoV2(RawHeroLevelInfoV2):
    model_config = ConfigDict(populate_by_name=True)

    bonus_currencies: list[str] | None = None

    @classmethod
    def from_raw_level_info(cls, raw_level_info: RawHeroLevelInfoV2) -> HeroLevelInfoV2:
        raw_model = raw_level_info.model_dump()
        raw_model["bonus_currencies"] = (
            list(raw_level_info.bonus_currencies.keys())
            if raw_level_info.bonus_currencies
            else None
        )
        return cls(**raw_model)


class HeroStartingStatV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: int | float
    display_stat_name: str


class HeroStartingStatsV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    max_move_speed: HeroStartingStatV2
    sprint_speed: HeroStartingStatV2
    crouch_speed: HeroStartingStatV2
    move_acceleration: HeroStartingStatV2
    light_melee_damage: HeroStartingStatV2
    heavy_melee_damage: HeroStartingStatV2
    max_health: HeroStartingStatV2
    weapon_power: HeroStartingStatV2
    reload_speed: HeroStartingStatV2
    weapon_power_scale: HeroStartingStatV2
    proc_build_up_rate_scale: HeroStartingStatV2
    stamina: HeroStartingStatV2
    base_health_regen: HeroStartingStatV2
    stamina_regen_per_second: HeroStartingStatV2
    ability_resource_max: HeroStartingStatV2
    ability_resource_regen_per_second: HeroStartingStatV2
    crit_damage_received_scale: HeroStartingStatV2
    tech_duration: HeroStartingStatV2
    tech_armor_damage_reduction: HeroStartingStatV2 | None = None
    tech_range: HeroStartingStatV2
    bullet_armor_damage_reduction: HeroStartingStatV2 | None = None

    @classmethod
    def from_raw_starting_stats(
        cls, raw_hero_starting_stats: RawHeroStartingStatsV2
    ) -> HeroStartingStatsV2:
        return cls(
            **{
                k: (
                    HeroStartingStatV2(
                        value=v,
                        display_stat_name=raw_hero_starting_stats.model_fields[k].validation_alias,
                    )
                    if v is not None
                    else None
                )
                for k, v in raw_hero_starting_stats.model_dump().items()
            }
        )


class HeroV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    class_name: str
    name: str
    description: HeroDescriptionV2
    recommended_upgrades: list[str] | None = None
    recommended_ability_order: list[str] | None = None
    player_selectable: bool
    disabled: bool
    in_development: bool
    needs_testing: bool
    assigned_players_only: bool
    tags: list[str] | None = None
    gun_tag: str | None = None
    hideout_rich_presence: str | None = None
    hero_type: HeroTypeV2 | None = None
    prerelease_only: bool | None = None
    limited_testing: bool
    complexity: int
    skin: int
    images: HeroImagesV2
    items: dict[HeroItemTypeV2, str]
    starting_stats: HeroStartingStatsV2
    item_slot_info: dict[ItemSlotTypeV2, RawHeroItemSlotInfoValueV2]
    physics: HeroPhysicsV2
    colors: HeroColorsV2
    shop_stat_display: HeroShopStatDisplayV2
    cost_bonuses: dict[ItemSlotTypeV2, list[RawHeroMapModCostBonusesV2]] | None = None
    stats_display: RawHeroStatsDisplayV2
    hero_stats_ui: RawHeroStatsUIV2
    level_info: dict[str, HeroLevelInfoV2]
    scaling_stats: dict[str, RawHeroScalingStatV2]
    purchase_bonuses: dict[ItemSlotTypeV2, list[RawHeroPurchaseBonusV2]]
    standard_level_up_upgrades: dict[str, float]

    @classmethod
    def from_raw_hero(cls, raw_hero: RawHeroV2, localization: dict[str, str]) -> HeroV2:
        raw_model = raw_hero.model_dump()
        raw_model["name"] = (
            localization.get(
                f"{raw_hero.class_name}:n",
                localization.get(
                    raw_hero.class_name,
                    localization.get(f"Steam_RP_{raw_hero.class_name}", raw_hero.class_name),
                ),
            )
            .strip()
            .replace("#|f|#", "")
            .replace("#|m|#", "")
        )
        raw_model["description"] = HeroDescriptionV2.from_raw_hero(raw_hero, localization)
        raw_model["starting_stats"] = HeroStartingStatsV2.from_raw_starting_stats(
            raw_hero.starting_stats
        )
        raw_model["tags"] = [localization.get(t.strip("#"), t) for t in raw_hero.tags or []]
        raw_model["gun_tag"] = (
            localization.get(raw_hero.gun_tag.strip("#"), raw_hero.gun_tag)
            if raw_hero.gun_tag
            else None
        )
        raw_model["hideout_rich_presence"] = (
            localization.get(
                raw_hero.hideout_rich_presence.strip("#"),
                localization.get(
                    "Steam_Citadel_Hideout_Ranting"
                    if raw_hero.hideout_rich_presence == "#Steam_Citadel_Hideout_Rant"
                    else raw_hero.hideout_rich_presence,
                    raw_hero.hideout_rich_presence,
                ),
            )
            if raw_hero.hideout_rich_presence
            else None
        )
        raw_model["images"] = HeroImagesV2.from_raw_hero(raw_hero)
        raw_model["physics"] = HeroPhysicsV2.from_raw_hero(raw_hero)
        raw_model["colors"] = HeroColorsV2.from_raw_hero(raw_hero)
        raw_model["level_info"] = {
            k: HeroLevelInfoV2.from_raw_level_info(v) for k, v in raw_hero.level_info.items()
        }
        raw_model["shop_stat_display"] = HeroShopStatDisplayV2.from_raw_hero(raw_hero)
        return cls(**raw_model)


def test_parse():
    def get_raw_heroes():
        with open("res/raw_heroes.json") as f:
            raw_heroes = json.load(f)
        return [
            RawHeroV2(class_name=k, **v)
            for k, v in raw_heroes.items()
            if k.startswith("hero_") and "base" not in k and "generic" not in k and "dummy" not in k
        ]

    raw_heroes = get_raw_heroes()

    localization = {}
    with open("res/localization/citadel_gc_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_heroes_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_gc_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_heroes_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])

    heroes = [HeroV2.from_raw_hero(raw_hero, localization) for raw_hero in raw_heroes]

    with open("test.json", "w") as f:
        json.dump([hero.model_dump(exclude_none=True) for hero in heroes], f, indent=2)
    print(heroes)


if __name__ == "__main__":
    test_parse()
