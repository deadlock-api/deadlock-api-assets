import os
from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deadlock_assets_api.models.v1.colors import ColorV1
from deadlock_assets_api.models.v2.enums import ItemTierV2


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


class OutcomeToWeights(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    outcomes_to_weights: dict[str, float] = Field(..., validation_alias="m_mapOutcomesToWeights")


class ItemDraftRound(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chance_rare: ItemTierV2 = Field(..., validation_alias="m_eNormalModTier")
    chance_enhanced: ItemTierV2 = Field(..., validation_alias="m_eRareModTier")


class ItemDraftRoundPerGameRound(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chance_rare: OutcomeToWeights = Field(..., validation_alias="m_chanceRare")
    chance_enhanced: OutcomeToWeights = Field(..., validation_alias="m_chanceEnhanced")
    item_draft_rounds: list[ItemDraftRound] = Field(..., validation_alias="m_vecItemDraftRounds")


class StreetBrawl(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    respawn_times: list[int] = Field(..., validation_alias="m_vecRespawnTimes")
    gold_per_round: list[int] = Field(..., validation_alias="m_vecGoldPerRound")
    apper_round: list[int] = Field(..., validation_alias="m_vecAPPerRound")
    item_draft_rerolls_per_round: list[int] = Field(
        ..., validation_alias="m_vecItemDraftRerollsPerRound"
    )
    round_length_minutes: list[int] = Field(..., validation_alias="m_vecRoundLengthMinutes")
    round_length_minutes_urgent: list[float] = Field(
        ..., validation_alias="m_vecRoundLengthMinutesUrgent"
    )
    overtime_respawn_time_increase: list[float] = Field(
        ..., validation_alias="m_flOvertimeRespawnTimeIncrease"
    )
    overtime_respawn_time_increase_urgent: list[float] = Field(
        ..., validation_alias="m_flOvertimeRespawnTimeIncreaseUrgent"
    )
    overtime_trooper_health_scale: list[float] = Field(
        ..., validation_alias="m_flOvertimeTrooperHealthScale"
    )
    overtime_trooper_damage_scale: list[float] = Field(
        ..., validation_alias="m_flOvertimeTrooperDamageScale"
    )
    buy_time: list[int] = Field(..., validation_alias="m_vecBuyTime")
    pre_buy_time: list[float] = Field(..., validation_alias="m_vecPreBuyTime")
    score_to_win: int = Field(..., validation_alias="m_iScoreToWin")
    scoring_time: float = Field(..., validation_alias="m_flScoringTime")
    lane_number: int = Field(..., validation_alias="m_iLaneNumber")
    objective_max_health: list[int] = Field(..., validation_alias="m_vecObjectiveMaxHealth")
    tier2_bonus_health: int = Field(..., validation_alias="m_nTier2BonusHealth")
    comeback_bonus_health: int = Field(..., validation_alias="m_nComebackBonusHealth")
    comeback_bonus_health_critical: int = Field(
        ..., validation_alias="m_nComebackBonusHealthCritical"
    )
    trooper_spawn_timer: list[float] = Field(..., validation_alias="m_flTrooperSpawnTimer")
    trooper_spawn_before_round_start_timer: float = Field(
        ..., validation_alias="m_flTrooperSpawnBeforeRoundStartTimer"
    )
    zip_boost_cooldown_on_start: float = Field(..., validation_alias="m_flZipBoostCooldownOnStart")
    buy_time_grace_period: float = Field(..., validation_alias="m_flBuyTimeGracePeriod")
    tier1_max_resist_time: float = Field(..., validation_alias="m_flTier1MaxResistTime")
    tier2_max_resist_time: float = Field(..., validation_alias="m_flTier2MaxResistTime")
    ultimate_unlock_round: int = Field(..., validation_alias="m_iUltimateUnlockRound")
    item_draft_rounds_per_game_round: list[ItemDraftRoundPerGameRound] = Field(
        ..., validation_alias="m_vecItemDraftRoundsPerGameRound"
    )
    outline_color_friend: list[int] | None = Field(None, validation_alias="m_OutlineColorFriend")
    outline_color_enemy: list[int] | None = Field(None, validation_alias="m_OutlineColorEnemy")
    outline_color_team1: list[int] | None = Field(None, validation_alias="m_OutlineColorTeam1")
    outline_color_team2: list[int] | None = Field(None, validation_alias="m_OutlineColorTeam2")
    outline_color_neutral: list[int] | None = Field(None, validation_alias="m_OutlineColorNeutral")


class GenericDataV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    damage_flash: DamageFlashV2 = Field(..., validation_alias="m_mapDamageFlash")
    glitch_settings: GlitchSettingsV2 = Field(..., validation_alias="m_GlitchSettings")
    lane_info: list[LaneInfoV2] = Field(..., validation_alias="m_LaneInfo")
    new_player_metrics: list[NewPlayerMetricsV2] = Field(..., validation_alias="m_NewPlayerMetrics")
    minimap_team_rebels_color: ColorV1 | None = Field(
        None, validation_alias="m_MinimapTeamRebelsColor"
    )
    minimap_team_combine_color: ColorV1 | None = Field(
        None, validation_alias="m_MinimapTeamCombineColor"
    )
    enemy_objectives_and_zipline_color: ColorV1 | None = Field(
        None, validation_alias="m_enemyObjectivesAndZiplineColor"
    )
    enemy_objectives_color: ColorV1 | None = Field(None, validation_alias="m_enemyObjectivesColor")
    enemy_zipline_color: ColorV1 | None = Field(None, validation_alias="m_enemyZiplineColor")
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
    street_brawl: StreetBrawl | None = Field(None, validation_alias="m_StreetBrawl")

    @field_validator(
        "minimap_team_rebels_color",
        "minimap_team_combine_color",
        "enemy_objectives_and_zipline_color",
        "enemy_objectives_color",
        "enemy_zipline_color",
        mode="before",
    )
    @classmethod
    def validate_color_fields(
        cls, v: ColorV1 | list[int] | dict[str, int] | None
    ) -> ColorV1 | None:
        if v is None:
            return None
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
