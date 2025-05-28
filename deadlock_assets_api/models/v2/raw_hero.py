import json

from pydantic import BaseModel, ConfigDict, Field

from deadlock_assets_api.models.v2.enums import ItemSlotTypeV2, HeroItemTypeV2


class RawHeroStartingStatsV2(BaseModel):
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
    tech_armor_damage_reduction: float | None = Field(
        None, validation_alias="ETechArmorDamageReduction"
    )
    tech_range: int = Field(..., validation_alias="ETechRange")
    bullet_armor_damage_reduction: float | None = Field(
        None, validation_alias="EBulletArmorDamageReduction"
    )


class RawHeroShopSpiritStatsDisplayV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    display_stats: list[str] = Field(..., validation_alias="m_vecDisplayStats")


class RawHeroShopVitalityStatsDisplayV2(RawHeroShopSpiritStatsDisplayV2):
    model_config = ConfigDict(populate_by_name=True)

    other_display_stats: list[str] = Field(..., validation_alias="m_vecOtherDisplayStats")


class RawHeroShopWeaponStatsDisplayV2(RawHeroShopVitalityStatsDisplayV2):
    model_config = ConfigDict(populate_by_name=True)

    weapon_attributes: str | None = Field(None, validation_alias="m_eWeaponAttributes")
    weapon_image: str | None = Field(None, validation_alias="m_strWeaponImage")


class RawHeroShopStatDisplayV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    spirit_stats_display: RawHeroShopSpiritStatsDisplayV2 = Field(
        ..., validation_alias="m_eSpiritStatsDisplay"
    )
    vitality_stats_display: RawHeroShopVitalityStatsDisplayV2 = Field(
        ..., validation_alias="m_eVitalityStatsDisplay"
    )
    weapon_stats_display: RawHeroShopWeaponStatsDisplayV2 = Field(
        ..., validation_alias="m_eWeaponStatsDisplay"
    )


class RawHeroStatsDisplayV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    health_header_stats: list[str] = Field(..., validation_alias="m_vecHealthHeaderStats")
    health_stats: list[str] = Field(..., validation_alias="m_vecHealthHeaderStats")
    magic_header_stats: list[str] = Field(..., validation_alias="m_vecMagicHeaderStats")
    magic_stats: list[str] = Field(..., validation_alias="m_vecMagicStats")
    weapon_header_stats: list[str] = Field(..., validation_alias="m_vecWeaponHeaderStats")
    weapon_stats: list[str] = Field(..., validation_alias="m_vecWeaponStats")


class RawHeroStatsUIDisplayV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category: str = Field(..., validation_alias="m_eStatCategory")
    stat_type: str = Field(..., validation_alias="m_eStatType")


class RawHeroStatsUIV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    weapon_stat_display: str = Field(..., validation_alias="m_eWeaponStatDisplay")
    display_stats: list[RawHeroStatsUIDisplayV2] = Field(..., validation_alias="m_vecDisplayStats")


class RawHeroItemSlotInfoValueV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    max_purchases_for_tier: list[int] = Field(..., validation_alias="m_arMaxPurchasesForTier")


class RawHeroLevelInfoV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    use_standard_upgrade: bool | None = Field(None, validation_alias="m_bUseStandardUpgrade")
    bonus_currencies: dict[str, int] | None = Field(None, validation_alias="m_mapBonusCurrencies")
    required_gold: int = Field(..., validation_alias="m_unRequiredGold")


class RawHeroPurchaseBonusV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value_type: str = Field(..., validation_alias="m_ValueType")
    tier: int = Field(..., validation_alias="m_nTier")
    value: str = Field(..., validation_alias="m_strValue")


class RawHeroScalingStatV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scaling_stat: str = Field(..., validation_alias="eScalingStat")
    scale: float = Field(..., validation_alias="flScale")


class RawHeroMapModCostBonusesV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gold_threshold: int = Field(..., validation_alias="nGoldThreshold")
    bonus: float = Field(..., validation_alias="flBonus")
    percent_on_graph: float = Field(..., validation_alias="flPercentOnGraph")


class RawHeroV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(..., validation_alias="m_HeroID")
    class_name: str
    recommended_upgrades: list[str] | None = Field(None, validation_alias="m_RecommendedUpgrades")
    recommended_ability_order: list[str] | None = Field(
        None, validation_alias="m_RecommendedAbilityOrder"
    )
    player_selectable: bool = Field(..., validation_alias="m_bPlayerSelectable")
    disabled: bool = Field(..., validation_alias="m_bDisabled")
    in_development: bool = Field(..., validation_alias="m_bInDevelopment")
    needs_testing: bool = Field(..., validation_alias="m_bNeedsTesting")
    assigned_players_only: bool = Field(..., validation_alias="m_bAssignedPlayersOnly")
    available_in_hero_labs: bool | None = Field(None, validation_alias="m_bAvailableInHeroLabs")
    limited_testing: bool = Field(..., validation_alias="m_bLimitedTesting")
    complexity: int = Field(..., validation_alias="m_nComplexity")
    skin: int = Field(..., validation_alias="m_nModelSkin")
    starting_stats: RawHeroStartingStatsV2 = Field(..., validation_alias="m_mapStartingStats")
    icon_hero_card: str | None = Field(None, validation_alias="m_strIconHeroCard")
    icon_image_small: str | None = Field(None, validation_alias="m_strIconImageSmall")
    minimap_image: str | None = Field(None, validation_alias="m_strMinimapImage")
    selection_image: str | None = Field(None, validation_alias="m_strSelectionImage")
    top_bar_image: str | None = Field(None, validation_alias="m_strTopBarImage")
    top_bar_vertical_image: str | None = Field(None, validation_alias="m_strTopBarVertical")
    shop_stat_display: RawHeroShopStatDisplayV2 = Field(..., validation_alias="m_ShopStatDisplay")
    cost_bonuses: dict[ItemSlotTypeV2, list[RawHeroMapModCostBonusesV2]] = Field(
        ..., validation_alias="m_MapModCostBonuses"
    )
    color_glow_enemy: tuple[int, int, int] = Field(..., validation_alias="m_colorGlowEnemy")
    color_glow_friendly: tuple[int, int, int] = Field(..., validation_alias="m_colorGlowFriendly")
    color_glow_team1: tuple[int, int, int] = Field(..., validation_alias="m_colorGlowTeam1")
    color_glow_team2: tuple[int, int, int] = Field(..., validation_alias="m_colorGlowTeam2")
    color_ui: tuple[int, int, int] = Field(..., validation_alias="m_colorUI")
    collision_height: float = Field(..., validation_alias="m_flCollisionHeight")
    collision_radius: float = Field(..., validation_alias="m_flCollisionRadius")
    footstep_sound_travel_distance_meters: float | None = Field(
        None, validation_alias="m_flFootstepSoundTravelDistanceMeters"
    )
    stealth_speed_meters_per_second: float = Field(
        ..., validation_alias="m_flStealthSpeedMetersPerSecond"
    )
    step_height: float = Field(..., validation_alias="m_flStepHeight")
    step_sound_time: float | None = Field(None, validation_alias="m_flStepSoundTime")
    step_sound_time_sprinting: float | None = Field(
        None, validation_alias="m_flStepSoundTimeSprinting"
    )
    stats_display: RawHeroStatsDisplayV2 = Field(..., validation_alias="m_heroStatsDisplay")
    hero_stats_ui: RawHeroStatsUIV2 = Field(..., validation_alias="m_heroStatsUI")
    items: dict[HeroItemTypeV2, str] = Field(..., validation_alias="m_mapBoundAbilities")
    item_slot_info: dict[ItemSlotTypeV2, RawHeroItemSlotInfoValueV2] = Field(
        ..., validation_alias="m_mapItemSlotInfo"
    )
    level_info: dict[str, RawHeroLevelInfoV2] = Field(..., validation_alias="m_mapLevelInfo")
    purchase_bonuses: dict[ItemSlotTypeV2, list[RawHeroPurchaseBonusV2]] | None = Field(
        None, validation_alias="m_mapPurchaseBonuses"
    )
    scaling_stats: dict[str, RawHeroScalingStatV2] = Field(
        ..., validation_alias="m_mapScalingStats"
    )
    standard_level_up_upgrades: dict[str, float] = Field(
        ..., validation_alias="m_mapStandardLevelUpUpgrades"
    )


def test_parse():
    with open("res/raw_heroes.json") as f:
        raw_heroes = json.load(f)
    raw_heroes = [
        RawHeroV2(class_name=k, **v)
        for k, v in raw_heroes.items()
        if k.startswith("hero_") and "base" not in k and "generic" not in k and "dummy" not in k
    ]
    print(raw_heroes)


if __name__ == "__main__":
    test_parse()
