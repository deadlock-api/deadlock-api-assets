import os
from enum import Enum, StrEnum
from functools import lru_cache
from logging import warning

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    computed_field,
    field_validator,
)

import deadlock_assets_api
from deadlock_assets_api import utils
from deadlock_assets_api.glob import IMAGE_BASE_URL
from deadlock_assets_api.models.languages import Language
from deadlock_assets_api.models.v1.item import ItemV1


class HeroStartingStatsV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    max_move_speed: float = Field(..., validation_alias="EMaxMoveSpeed")
    sprint_speed: float = Field(..., validation_alias="ESprintSpeed")
    crouch_speed: float = Field(..., validation_alias="ECrouchSpeed")
    move_acceleration: float = Field(..., validation_alias="EMoveAcceleration")
    light_melee_damage: int = Field(..., validation_alias="ELightMeleeDamage")
    heavy_melee_damage: int = Field(..., validation_alias="EHeavyMeleeDamage")
    max_health: int = Field(..., validation_alias="EMaxHealth")
    weapon_power: int = Field(..., validation_alias="EWeaponPower")
    reload_speed: int = Field(..., validation_alias="EReloadSpeed")
    weapon_power_scale: int = Field(..., validation_alias="EWeaponPowerScale")
    proc_build_up_rate_scale: int = Field(..., validation_alias="EProcBuildUpRateScale")
    stamina: int = Field(..., validation_alias="EStamina")
    base_health_regen: float = Field(..., validation_alias="EBaseHealthRegen")
    stamina_regen_per_second: float = Field(..., validation_alias="EStaminaRegenPerSecond")
    ability_resource_max: int = Field(..., validation_alias="EAbilityResourceMax")
    ability_resource_regen_per_second: int = Field(
        ..., validation_alias="EAbilityResourceRegenPerSecond"
    )
    crit_damage_received_scale: float = Field(..., validation_alias="ECritDamageReceivedScale")
    tech_duration: int = Field(..., validation_alias="ETechDuration")
    tech_range: int = Field(..., validation_alias="ETechRange")
    bullet_armor_damage_reduction: float | None = Field(
        None, validation_alias="EBulletArmorDamageReduction"
    )


class HeroItemSlotInfoForTierV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    max_purchase_for_tier: list[int] = Field(..., validation_alias="m_arMaxPurchasesForTier")


class HeroItemSlotInfoV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    weapon_mod: HeroItemSlotInfoForTierV1 = Field(..., validation_alias="EItemSlotType_WeaponMod")
    armor: HeroItemSlotInfoForTierV1 = Field(..., validation_alias="EItemSlotType_Armor")
    tech: HeroItemSlotInfoForTierV1 = Field(..., validation_alias="EItemSlotType_Tech")


class HeroPurchaseBonusesModifierV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tier: int = Field(..., validation_alias="m_nTier")
    value: str = Field(..., validation_alias="m_strValue")


class HeroPurchaseBonusesV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    weapon_mod: list[HeroPurchaseBonusesModifierV1] = Field(
        ..., validation_alias="EItemSlotType_WeaponMod"
    )
    armor: list[HeroPurchaseBonusesModifierV1] = Field(..., validation_alias="EItemSlotType_Armor")
    tech: list[HeroPurchaseBonusesModifierV1] = Field(..., validation_alias="EItemSlotType_Tech")


class HeroLevelInfoBonusCurrenciesV1(StrEnum):
    AbilityUnlocks = "EAbilityUnlocks"
    EAbilityPoints = "EAbilityPoints"


class HeroLevelInfoV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    required_gold: int | None = Field(None, validation_alias="m_unRequiredGold")
    bonus_currencies: (
        dict[HeroLevelInfoBonusCurrenciesV1, int] | list[HeroLevelInfoBonusCurrenciesV1] | None
    ) = Field(None, validation_alias="m_mapBonusCurrencies")
    use_standard_upgrade: bool = Field(False, validation_alias="m_bUseStandardUpgrade")

    @field_validator("bonus_currencies")
    @classmethod
    def validate_bonus_currencies(
        cls,
        value: (
            dict[HeroLevelInfoBonusCurrenciesV1, int] | list[HeroLevelInfoBonusCurrenciesV1] | None
        ),
        _,
    ):
        if value is None or len(value) == 0:
            return None
        if isinstance(value, list):
            return value
        return list(value.keys())


class HeroImagesV1(BaseModel):
    portrait: str | None = Field(None)
    card: str | None = Field(None)
    top_bar: str | None = Field(None)
    minimap: str | None = Field(None)
    small: str | None = Field(None)
    weapon: str | None = Field(None)


class WeaponStatsDisplayV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    weapon_image: str | None = Field(None, validation_alias="m_strWeaponImage")


class HeroShopStatDisplayV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    weapon_stats_display: WeaponStatsDisplayV1 | None = Field(
        None, validation_alias="m_eWeaponStatsDisplay"
    )


class HeroItemTypeV1(str, Enum):
    ESlot_Weapon_Primary = "weapon_primary"
    ESlot_Weapon_Secondary = "weapon_secondary"
    ESlot_Weapon_Melee = "weapon_melee"
    ESlot_Ability_Mantle = "ability_mantle"
    ESlot_Ability_Jump = "ability_jump"
    ESlot_Ability_Slide = "ability_slide"
    ESlot_Ability_ZipLine = "ability_zip_line"
    ESlot_Ability_ZipLineBoost = "ability_zip_line_boost"
    ESlot_Ability_ClimbRope = "ability_climb_rope"
    ESlot_Ability_Innate_1 = "ability_innate1"
    ESlot_Ability_Innate_2 = "ability_innate2"
    ESlot_Ability_Innate_3 = "ability_innate3"
    ESlot_Signature_1 = "signature1"
    ESlot_Signature_2 = "signature2"
    ESlot_Signature_3 = "signature3"
    ESlot_Signature_4 = "signature4"

    @classmethod
    def _missing_(cls, new_value: str):
        new_value = new_value.lower()
        for member in cls:
            if new_value in [member.value.lower(), member.name.lower()]:
                return member
        warning(f"Unknown HeroItemType: {new_value}")
        return None

    def ability_index(self) -> int | None:
        return {
            HeroItemTypeV1.ESlot_Signature_1: 1,
            HeroItemTypeV1.ESlot_Signature_2: 2,
            HeroItemTypeV1.ESlot_Signature_3: 3,
            HeroItemTypeV1.ESlot_Signature_4: 4,
        }.get(self)


class HeroV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    id: int = Field(..., validation_alias="m_HeroID")
    class_name: str = Field()
    name: str | None = Field(None)
    lore: str | None = Field(None)
    role: str | None = Field(None)
    playstyle: str | None = Field(None)
    player_selectable: bool = Field(..., validation_alias="m_bPlayerSelectable")
    disabled: bool = Field(..., validation_alias="m_bDisabled")
    in_development: bool = Field(..., validation_alias="m_bInDevelopment")
    needs_testing: bool = Field(..., validation_alias="m_bNeedsTesting")
    assigned_players_only: bool = Field(..., validation_alias="m_bAssignedPlayersOnly")
    available_in_hero_labs: bool | None = Field(None, validation_alias="m_bAvailableInHeroLabs")
    limited_testing: bool = Field(..., validation_alias="m_bLimitedTesting")
    complexity: int = Field(..., validation_alias="m_nComplexity")
    starting_stats: HeroStartingStatsV1 = Field(..., validation_alias="m_mapStartingStats")
    collision_radius: float = Field(..., validation_alias="m_flCollisionRadius")
    collision_height: float = Field(..., validation_alias="m_flCollisionHeight")
    step_height: float = Field(..., validation_alias="m_flStepHeight")
    items: dict[str, int | None] = Field(..., validation_alias="m_mapBoundAbilities")
    item_slot_info: HeroItemSlotInfoV1 = Field(..., validation_alias="m_mapItemSlotInfo")
    purchase_bonuses: HeroPurchaseBonusesV1 = Field(..., validation_alias="m_mapPurchaseBonuses")
    level_info: dict[int, HeroLevelInfoV1] = Field(..., validation_alias="m_mapLevelInfo")
    stealth_speed_meters_per_second: float = Field(
        ..., validation_alias="m_flStealthSpeedMetersPerSecond"
    )
    footstep_sound_travel_distance_meters: float = Field(
        ..., validation_alias="m_flFootstepSoundTravelDistanceMeters"
    )
    step_sound_time: float = Field(..., validation_alias="m_flStepSoundTime")
    color_ui: tuple[int, int, int] = Field(..., validation_alias="m_colorUI")
    color_glow_friendly: tuple[int, int, int] = Field(..., validation_alias="m_colorGlowFriendly")
    color_glow_enemy: tuple[int, int, int] = Field(..., validation_alias="m_colorGlowEnemy")
    color_glow_team1: tuple[int, int, int] = Field(..., validation_alias="m_colorGlowTeam1")
    color_glow_team2: tuple[int, int, int] = Field(..., validation_alias="m_colorGlowTeam2")
    standard_level_up_upgrades: dict[str, float] = Field(
        ..., validation_alias="m_mapStandardLevelUpUpgrades"
    )
    hero_shop_stat_display: HeroShopStatDisplayV1 | None = Field(
        None, validation_alias="m_ShopStatDisplay"
    )
    selection_image: str | None = Field(None, validation_alias="m_strSelectionImage")
    icon_image_small: str | None = Field(None, validation_alias="m_strIconImageSmall")
    minimap_image: str | None = Field(None, validation_alias="m_strMinimapImage")
    icon_hero_card: str | None = Field(None, validation_alias="m_strIconHeroCard")
    top_bar_image: str | None = Field(None, validation_alias="m_strTopBarImage")

    @field_validator("items", mode="before")
    @classmethod
    def validate_items(cls, value: dict[str, str | ItemV1]) -> dict[str, int]:
        items = deadlock_assets_api.models.v1.item.load_items()

        def convert_key(k):
            if k.startswith("E"):
                return HeroItemTypeV1(k).value
            return k

        def convert_val(v: int | str | ItemV1) -> int | None:
            if items is None:
                return None
            if isinstance(v, int):
                return v
            if isinstance(v, ItemV1):
                return v.id
            return next((i.id for i in items if i.class_name == v), None)

        return {convert_key(k): convert_val(v) for k, v in value.items()}

    def set_language(self, language: Language):
        self.name = self.get_name(language)
        self.lore = self.get_lore(language)
        self.role = self.get_role(language)
        self.playstyle = self.get_playstyle(language)

    def model_post_init(self, _):
        self.set_language(Language.English)

    def get_name(self, language: Language) -> str:
        return utils.get_translation(f"hero_{self.class_name}", language)

    def get_lore(self, language: Language) -> str:
        return utils.get_translation(f"hero_{self.class_name}_lore", language, True)

    def get_role(self, language: Language) -> str:
        return utils.get_translation(f"hero_{self.class_name}_role", language, True)

    def get_playstyle(self, language: Language) -> str:
        return utils.get_translation(f"hero_{self.class_name}_playstyle", language, True)

    @computed_field
    @property
    def images(self) -> HeroImagesV1:
        img_dict = {
            "portrait": self.selection_image,
            "small": self.icon_image_small,
            "minimap": self.minimap_image,
            "card": self.icon_hero_card,
            "top_bar": self.top_bar_image,
            "weapon": self.hero_shop_stat_display.weapon_stats_display.weapon_image,
        }

        def parse_img_path(v):
            if v is None:
                return None
            v = utils.strip_prefix(v, "heroes/")
            v = utils.strip_prefix(v, "hero_portraits/")
            v = utils.strip_prefix(v, "hud/")
            v = v.replace('"', "")
            v = v.replace("_psd.", ".")
            v = v.replace("_png.", ".")
            v = v.replace(".psd", ".png")
            return f"{IMAGE_BASE_URL}/heroes/{v}"

        return HeroImagesV1(**{k: parse_img_path(v) for k, v in img_dict.items()})


@lru_cache
def load_heroes() -> list[HeroV1] | None:
    if not os.path.exists("res/heroes.json"):
        return None
    with open("res/heroes.json") as f:
        content = f.read()
    ta = TypeAdapter(list[HeroV1])
    return ta.validate_json(content)
