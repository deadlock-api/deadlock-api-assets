import os
from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deadlock_assets_api.models.v1.colors import ColorV1


class FlashDataV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    duration: float = Field(..., validation_alias="m_flDuration")
    coverage: float = Field(..., validation_alias="m_flCoverage")
    hardness: float = Field(..., validation_alias="m_flHardness")
    brightness: float = Field(..., validation_alias="m_flBrightness")
    color: ColorV1 = Field(..., validation_alias="m_Color")
    brightness_in_light_sensitivity_mode: float | None = Field(
        None, validation_alias="m_flBrightnessInLightSensitivityMode"
    )

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, v: ColorV1 | list[int] | dict[str, int]) -> ColorV1:
        if isinstance(v, ColorV1):
            return v
        if isinstance(v, dict):
            return ColorV1.model_validate(v)
        if isinstance(v, list):
            return ColorV1.from_list(v)
        raise TypeError(f"Invalid type for color field: {type(v)}")


class DamageFlashV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bullet_damage: FlashDataV2 = Field(..., validation_alias="EFlashType_BulletDamage")
    tech_damage: FlashDataV2 = Field(..., validation_alias="EFlashType_TechDamage")
    healing_damage: FlashDataV2 = Field(..., validation_alias="EFlashType_Healing")
    crit_damage: FlashDataV2 = Field(..., validation_alias="EFlashType_CritDamage")
    melee_damage: FlashDataV2 = Field(..., validation_alias="EFlashType_MeleeActivate")


class GlitchSettingsV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    strength: float = Field(..., validation_alias="m_flStrength")
    uantize_type: float = Field(..., validation_alias="m_nQuantizeType")
    quantize_scale: float = Field(..., validation_alias="m_flQuantizeScale")
    quantize_strength: float = Field(..., validation_alias="m_flQuantizeStrength")
    frame_rate: float = Field(..., validation_alias="m_flFrameRate")
    speed: float = Field(..., validation_alias="m_flSpeed")
    jump_strength: float = Field(..., validation_alias="m_flJumpStrength")
    distort_strength: float = Field(..., validation_alias="m_flDistortStrength")
    white_noise_strength: float = Field(..., validation_alias="m_flWhiteNoiseStrength")
    scanline_strength: float = Field(..., validation_alias="m_flScanlineStrength")
    breakup_strength: float = Field(..., validation_alias="m_flBreakupStrength")


class NewPlayerMetricsV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_tier_name: str = Field(..., validation_alias="m_strSkillTierName")
    net_worth: int = Field(..., validation_alias="m_NetWorth")
    damage_taken: int = Field(..., validation_alias="m_DamageTaken")
    boss_damage: int = Field(..., validation_alias="m_BossDamage")
    player_damage: int = Field(..., validation_alias="m_PlayerDamage")
    last_hits: int = Field(..., validation_alias="m_LastHits")
    orbs_secured: int = Field(..., validation_alias="m_OrbsSecured")
    orbs_denied: int = Field(..., validation_alias="m_OrbsDenied")
    abilities_upgraded: int = Field(..., validation_alias="m_AbilitiesUpgraded")
    mods_purchased: int = Field(..., validation_alias="m_ModsPurchased")


class LaneInfoV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lane_name: str = Field(..., validation_alias="m_strLaneName")
    css_class: str | None = Field(None, validation_alias="m_strCSSClass")
    color: ColorV1 = Field(..., validation_alias="m_Color")
    minimap_zipline_color_override: ColorV1 | None = Field(
        None, validation_alias="m_MinimapZiplineColorOverride"
    )
    objective_color: ColorV1 | None = Field(None, validation_alias="m_ObjectiveColor")

    @field_validator("color", "minimap_zipline_color_override", "objective_color", mode="before")
    @classmethod
    def validate_color(cls, v: ColorV1 | list[int] | dict[str, int] | None) -> ColorV1 | None:
        if v is None:
            return None
        if isinstance(v, ColorV1):
            return v
        if isinstance(v, dict):
            return ColorV1.model_validate(v)
        if isinstance(v, list):
            return ColorV1.from_list(v)
        raise TypeError(f"Invalid type for color field: {type(v)}")


class ObjectiveParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gold_per_orb: int = Field(..., validation_alias="m_GoldPerOrb")
    near_player_split_pct: float = Field(..., validation_alias="m_NearPlayerSplitPct")
    tier1_gold_kill: int = Field(..., validation_alias="m_nTier1GoldKill")
    tier1_gold_orbs: int = Field(..., validation_alias="m_nTier1GoldOrbs")
    tier2_gold_kill: int = Field(..., validation_alias="m_nTier2GoldKill")
    tier2_gold_orbs: int = Field(..., validation_alias="m_nTier2GoldOrbs")
    base_guardians_gold_kill: int = Field(..., validation_alias="m_nBaseGuardiansGoldKill")
    base_guardians_gold_orbs: int = Field(..., validation_alias="m_nBaseGuardiansGoldOrbs")
    shrines_gold_kill: int = Field(..., validation_alias="m_nShrinesGoldKill")
    shrines_gold_orbs: int = Field(..., validation_alias="m_nShrinesGoldOrbs")
    patron_phase1_gold_kill: int = Field(..., validation_alias="m_nPatronPhase1GoldKill")
    patron_phase1_gold_orbs: int = Field(..., validation_alias="m_nPatronPhase1GoldOrbs")


class RejuvParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rejuvinator_expiration_warning_timing: float = Field(
        ..., validation_alias="m_flRejuvinatorExpirationWarningTiming"
    )
    rejuvinator_buff_duration: float = Field(..., validation_alias="m_flRejuvinatorBuffDuration")
    rejuvinator_drop_height: float = Field(..., validation_alias="m_flRejuvinatorDropHeight")
    rejuvinator_drop_duration: float = Field(..., validation_alias="m_flRejuvinatorDropDuration")
    trooper_health_mult: list[float] = Field(..., validation_alias="m_TrooperHealthMult")
    player_respawn_mult: list[float] = Field(..., validation_alias="m_PlayerRespawnMult")
    rejuvinator_rebirth_duration: list[float] = Field(
        ..., validation_alias="m_flRejuvinatorRebirthDuration"
    )


class MiniMapOffsets(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    entity_class: str = Field(..., validation_alias="eEntityClass")
    offset_2d: list[float] = Field(..., validation_alias="vOffset2D")
    lane_index: int | None = Field(None, validation_alias="iLane")


class ItemGroup(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    shop_group: str = Field(..., validation_alias="m_eShopGroup")
    upgrades: list[str] = Field(..., validation_alias="m_vecUpgrades")


class GenericDataV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    damage_flash: DamageFlashV2 = Field(..., validation_alias="m_mapDamageFlash")
    glitch_settings: GlitchSettingsV2 = Field(..., validation_alias="m_GlitchSettings")
    lane_info: list[LaneInfoV2] = Field(..., validation_alias="m_LaneInfo")
    new_player_metrics: list[NewPlayerMetricsV2] = Field(..., validation_alias="m_NewPlayerMetrics")
    minimap_team_rebels_color: ColorV1 = Field(..., validation_alias="m_MinimapTeamRebelsColor")
    minimap_team_combine_color: ColorV1 = Field(..., validation_alias="m_MinimapTeamCombineColor")
    enemy_objectives_and_zipline_color: ColorV1 = Field(
        ..., validation_alias="m_enemyObjectivesAndZiplineColor"
    )
    enemy_objectives_color: ColorV1 = Field(..., validation_alias="m_enemyObjectivesColor")
    enemy_zipline_color: ColorV1 = Field(..., validation_alias="m_enemyZiplineColor")
    item_price_per_tier: list[int] = Field(..., validation_alias="m_nItemPricePerTier")
    trooper_kill_gold_share_frac: list[float] = Field(
        ..., validation_alias="m_flTrooperKillGoldShareFrac"
    )
    hero_kill_gold_share_frac: list[float] = Field(
        ..., validation_alias="m_flHeroKillGoldShareFrac"
    )
    aim_spring_strength: list[float] = Field(..., validation_alias="m_AimSpringStrength")
    targeting_spring_strength: list[float] = Field(
        ..., validation_alias="m_TargetingSpringStrength"
    )
    objective_params: ObjectiveParams = Field(..., validation_alias="m_ObjectiveParams")
    rejuv_params: RejuvParams = Field(..., validation_alias="m_RejuvParams")
    mini_map_offsets: list[MiniMapOffsets] = Field(..., validation_alias="m_MiniMapOffsets")
    weapon_groups: list[ItemGroup] = Field(..., validation_alias="m_vecWeaponGroups")
    armor_groups: list[ItemGroup] = Field(..., validation_alias="m_vecArmorGroups")
    spirit_groups: list[ItemGroup] = Field(..., validation_alias="m_vecSpiritGroups")

    @field_validator(
        "minimap_team_rebels_color",
        "minimap_team_combine_color",
        "enemy_objectives_and_zipline_color",
        "enemy_objectives_color",
        "enemy_zipline_color",
        mode="before",
    )
    @classmethod
    def validate_color_fields(cls, v: ColorV1 | list[int] | dict[str, int]) -> ColorV1:
        if isinstance(v, ColorV1):
            return v
        if isinstance(v, dict):
            return ColorV1.model_validate(v)
        if isinstance(v, list):
            return ColorV1.from_list(v)
        raise TypeError(f"Invalid type for color field: {type(v)}")


@lru_cache
def load_generic_data() -> GenericDataV2 | None:
    if not os.path.exists("res/generic_data.json"):
        return None
    with open("res/generic_data.json") as f:
        return GenericDataV2.model_validate_json(f.read())
