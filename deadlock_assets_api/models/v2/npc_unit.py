import logging
from typing import Annotated

from murmurhash2 import murmurhash2
from pydantic import ConfigDict, Field, BaseModel, computed_field, WithJsonSchema, field_validator

from deadlock_assets_api.models.v1.colors import ColorV1
from deadlock_assets_api.models.v2.api_weapon import WeaponInfoV2
from deadlock_assets_api.models.v2.enums import HeroItemTypeV2

LOGGER = logging.getLogger(__name__)


class EmpoweredModifierLevel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    max_health: int | None = Field(None, validation_alias="m_nMaxHealth")
    transition_duration: float | None = Field(None, validation_alias="m_flTransitionDuration")
    model_scale: float | None = Field(None, validation_alias="m_flModelScale")


class SubclassEmpoweredModifierLevel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: EmpoweredModifierLevel = Field(None, validation_alias="subclass")


class BulletResistModifier(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bullet_resist: int | None = Field(None, validation_alias="m_BulletResist")
    bullet_resist_reduction_per_hero: int | None = Field(
        None, validation_alias="m_BulletResistReductionPerHero"
    )


class SubclassBulletResistModifier(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: BulletResistModifier = Field(None, validation_alias="subclass")


class TrooperDamageReduction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    damage_reduction_for_troopers: float | None = Field(
        None, validation_alias="m_flDamageReductionForTroopers"
    )


class SubclassTrooperDamageReduction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: TrooperDamageReduction = Field(None, validation_alias="subclass")


class RangedArmorModifier(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    range_min: float | None = Field(None, validation_alias="m_flRangeMin")
    range_max: float | None = Field(None, validation_alias="m_flRangeMax")
    invuln_range: float | None = Field(None, validation_alias="m_flInvulnRange")


class SubclassRangedArmorModifier(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: RangedArmorModifier = Field(None, validation_alias="subclass")


class ScriptValues(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    modifier_value: str | None = Field(None, validation_alias="m_eModifierValue")
    value: float | None = Field(None, validation_alias="m_value")


class IntrinsicModifiers(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    script_values: list[ScriptValues] | None = Field(None, validation_alias="m_vecScriptValues")


class SubclassIntrinsicModifiers(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: IntrinsicModifiers = Field(None, validation_alias="subclass")


class ObjectiveRegen(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    out_of_combat_health_regen: int | None = Field(
        None, validation_alias="m_flOutOfCombatHealthRegen"
    )
    out_of_combat_regen_delay: float | None = Field(
        None, validation_alias="m_flOutOfCombatRegenDelay"
    )


class SubclassObjectiveRegen(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: ObjectiveRegen = Field(None, validation_alias="subclass")


class ObjectiveHealthGrowthPhase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    growth_per_minute: int | None = Field(None, validation_alias="m_iGrowthPerMinute")
    tick_rate: float | None = Field(None, validation_alias="m_flTickRate")
    growth_start_time_in_minutes: int | None = Field(
        None, validation_alias="m_iGrowthStartTimeInMinutes"
    )


class SubclassObjectiveHealthGrowthPhase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: ObjectiveHealthGrowthPhase = Field(None, validation_alias="subclass")


class NPCUnitV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str
    weapon_info: WeaponInfoV2 | None = Field(None, validation_alias="m_WeaponInfo")
    max_health: int | None = Field(None, validation_alias="m_nMaxHealth")
    phase2_health: int | None = Field(None, validation_alias="m_nPhase2Health")
    bound_abilities: dict[HeroItemTypeV2, str] | None = Field(
        None, validation_alias="m_mapBoundAbilities"
    )
    max_health_final: int | None = Field(None, validation_alias="m_iMaxHealthFinal")
    max_health_generator: int | None = Field(None, validation_alias="m_iMaxHealthGenerator")
    enemy_trooper_protection_range: float | None = Field(
        None, validation_alias="m_flEnemyTrooperProtectionRange"
    )
    empowered_modifier_level1: SubclassEmpoweredModifierLevel | None = Field(
        None, validation_alias="m_EmpoweredModifierLevel1"
    )
    empowered_modifier_level2: SubclassEmpoweredModifierLevel | None = Field(
        None, validation_alias="m_EmpoweredModifierLevel2"
    )
    backdoor_bullet_resist_modifier: SubclassBulletResistModifier | None = Field(
        None, validation_alias="m_BackdoorBulletResistModifier"
    )
    objective_regen: SubclassObjectiveRegen | None = Field(
        None, validation_alias="m_ObjectiveRegen"
    )
    objective_health_growth_phase1: SubclassObjectiveHealthGrowthPhase | None = Field(
        None, validation_alias="m_ObjectiveHealthGrowthPhase1"
    )
    objective_health_growth_phase2: SubclassObjectiveHealthGrowthPhase | None = Field(
        None, validation_alias="m_ObjectiveHealthGrowthPhase2"
    )
    enemy_trooper_damage_reduction: SubclassTrooperDamageReduction | None = Field(
        None, validation_alias="m_EnemyTrooperDamageReduction"
    )
    ranged_armor_modifier: SubclassRangedArmorModifier | None = Field(
        None, validation_alias="m_RangedArmorModifier"
    )
    intrinsic_modifiers: list[SubclassIntrinsicModifiers] | None = Field(
        None, validation_alias="m_vecIntrinsicModifiers"
    )
    sight_range_players: float | None = Field(None, validation_alias="m_flSightRangePlayers")
    sight_range_npcs: float | None = Field(None, validation_alias="m_flSightRangeNPCs")
    gold_reward: float | None = Field(None, validation_alias="m_flGoldReward")
    gold_reward_bonus_percent_per_minute: float | None = Field(
        None, validation_alias="m_flGoldRewardBonusPercentPerMinute"
    )
    player_damage_resist_pct: float | None = Field(
        None, validation_alias="m_flPlayerDamageResistPct"
    )
    trooper_damage_resist_pct: float | None = Field(
        None, validation_alias="m_flTrooperDamageResistPct"
    )
    t1_boss_damage_resist_pct: float | None = Field(
        None, validation_alias="m_flT1BossDamageResistPct"
    )
    t2_boss_damage_resist_pct: float | None = Field(
        None, validation_alias="m_flT2BossDamageResistPct"
    )
    t3_boss_damage_resist_pct: float | None = Field(
        None, validation_alias="m_flT3BossDamageResistPct"
    )
    barrack_guardian_damage_resist_pct: float | None = Field(
        None, validation_alias="m_flBarrackGuardianDamageResistPct"
    )
    near_death_duration: float | None = Field(None, validation_alias="m_flNearDeathDuration")
    laser_dps_to_players: float | None = Field(None, validation_alias="m_flLaserDPSToPlayers")
    laser_dps_max_health: float | None = Field(None, validation_alias="m_flLaserDPSMaxHealth")
    no_shield_laser_dps_to_players: float | None = Field(
        None, validation_alias="m_flNoShieldLaserDPSToPlayers"
    )
    stomp_damage: float | None = Field(None, validation_alias="m_flStompDamage")
    stomp_damage_max_health_percent: float | None = Field(
        None, validation_alias="m_flStompDamageMaxHealthPercent"
    )
    stun_duration: float | None = Field(None, validation_alias="m_flStunDuration")
    stomp_impact_radius: float | None = Field(None, validation_alias="m_flStompImpactRadius")
    walk_speed: float | None = Field(None, validation_alias="m_flWalkSpeed")
    run_speed: float | None = Field(None, validation_alias="m_flRunSpeed")
    acceleration: float | None = Field(None, validation_alias="m_flAcceleration")
    melee_damage: float | None = Field(None, validation_alias="m_flMeleeDamage")
    melee_attempt_range: float | None = Field(None, validation_alias="m_flMeleeAttemptRange")
    melee_hit_range: float | None = Field(None, validation_alias="m_flMeleeHitRange")
    melee_duration: float | None = Field(None, validation_alias="m_flMeleeDuration")
    attack_t1_boss_max_range: float | None = Field(
        None, validation_alias="m_flAttackT1BossMaxRange"
    )
    attack_t3_boss_max_range: float | None = Field(
        None, validation_alias="m_flAttackT3BossMaxRange"
    )
    attack_t3_boss_phase2_max_range: float | None = Field(
        None, validation_alias="m_flAttackT3BossPhase2MaxRange"
    )
    attack_trooper_max_range: float | None = Field(
        None, validation_alias="m_flAttackTrooperMaxRange"
    )
    t1_boss_dps: float | None = Field(None, validation_alias="m_flT1BossDPS")
    t1_boss_dpsbase_resist: float | None = Field(None, validation_alias="m_flT1BossDPSBaseResist")
    t1_boss_dpsmax_resist: float | None = Field(None, validation_alias="m_flT1BossDPSMaxResist")
    t1_boss_dpsmax_resist_time_in_seconds: float | None = Field(
        None, validation_alias="m_flT1BossDPSMaxResistTimeInSeconds"
    )
    t2_boss_dps: float | None = Field(None, validation_alias="m_flT2BossDPS")
    t2_boss_dpsbase_resist: float | None = Field(None, validation_alias="m_flT2BossDPSBaseResist")
    t2_boss_dpsmax_resist: float | None = Field(None, validation_alias="m_flT2BossDPSMaxResist")
    t2_boss_dpsmax_resist_time_in_seconds: float | None = Field(
        None, validation_alias="m_flT2BossDPSMaxResistTimeInSeconds"
    )
    t3_boss_dps: float | None = Field(None, validation_alias="m_flT3BossDPS")
    generator_boss_dps: float | None = Field(None, validation_alias="m_flGeneratorBossDPS")
    barrack_boss_dps: float | None = Field(None, validation_alias="m_flBarrackBossDPS")
    player_dps: float | None = Field(None, validation_alias="m_flPlayerDPS")
    trooper_dps: float | None = Field(None, validation_alias="m_flTrooperDPS")
    health_bar_color_friend: ColorV1 | None = Field(None, validation_alias="m_HealthBarColorFriend")
    health_bar_color_enemy: ColorV1 | None = Field(None, validation_alias="m_HealthBarColorEnemy")
    health_bar_color_team1: ColorV1 | None = Field(None, validation_alias="m_HealthBarColorTeam1")
    health_bar_color_team2: ColorV1 | None = Field(None, validation_alias="m_HealthBarColorTeam2")
    health_bar_color_team_neutral: ColorV1 | None = Field(
        None, validation_alias="m_HealthBarColorTeamNeutral"
    )
    glow_color_friend: ColorV1 | None = Field(
        None,
        validation_alias="m_GlowColorFriend",
    )
    glow_color_enemy: ColorV1 | None = Field(
        None,
        validation_alias="m_GlowColorEnemy",
    )
    glow_color_team1: ColorV1 | None = Field(
        None,
        validation_alias="m_GlowColorTeam1",
    )
    glow_color_team2: ColorV1 | None = Field(
        None,
        validation_alias="m_GlowColorTeam2",
    )
    glow_color_team_neutral: ColorV1 | None = Field(
        None,
        validation_alias="m_GlowColorTeamNeutral",
    )

    @computed_field
    @property
    def id(self) -> Annotated[int, WithJsonSchema({"format": "int64", "type": "integer"})]:
        return murmurhash2(self.class_name.encode(), 0x31415926)

    @field_validator(
        "health_bar_color_friend",
        "health_bar_color_enemy",
        "health_bar_color_team1",
        "health_bar_color_team2",
        "health_bar_color_team_neutral",
        "glow_color_friend",
        "glow_color_enemy",
        "glow_color_team1",
        "glow_color_team2",
        "glow_color_team_neutral",
        mode="before",
    )
    @classmethod
    def validate_color(cls, v: ColorV1 | list[int] | None | dict[str, int]) -> ColorV1 | None:
        if v is None:
            return v
        if isinstance(v, ColorV1):
            return v
        if isinstance(v, dict):
            return ColorV1.model_validate(v)
        if isinstance(v, list):
            return ColorV1.from_list(v)
        raise TypeError(f"Invalid type for color field: {type(v)}")
