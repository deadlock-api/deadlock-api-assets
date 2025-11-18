import logging

from murmurhash2 import murmurhash2
from pydantic import ConfigDict, Field, BaseModel, computed_field

from deadlock_assets_api.models.v2.raw_weapon import RawWeaponInfoV2

LOGGER = logging.getLogger(__name__)

Color = tuple[int, int, int] | tuple[int, int, int, int]


class NPCUnitV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str
    weapon_info: RawWeaponInfoV2 | None = Field(None, validation_alias="m_WeaponInfo")
    max_health: int | None = Field(None, validation_alias="m_nMaxHealth")
    sight_range_players: float | None = Field(None, validation_alias="m_flSightRangePlayers")
    sight_range_npcs: float | None = Field(None, validation_alias="m_flSightRangeNPCs")
    m_flPlayerDamageResistPct: float | None = Field(
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
    health_bar_color_friend: Color | None = Field(None, validation_alias="m_HealthBarColorFriend")
    health_bar_color_enemy: Color | None = Field(None, validation_alias="m_HealthBarColorEnemy")
    health_bar_color_team1: Color | None = Field(None, validation_alias="m_HealthBarColorTeam1")
    health_bar_color_team2: Color | None = Field(None, validation_alias="m_HealthBarColorTeam2")
    health_bar_color_team_neutral: Color | None = Field(
        None, validation_alias="m_HealthBarColorTeamNeutral"
    )
    glow_color_friend: Color | None = Field(None, validation_alias="m_GlowColorFriend")
    glow_color_enemy: Color | None = Field(None, validation_alias="m_GlowColorEnemy")
    glow_color_team1: Color | None = Field(None, validation_alias="m_GlowColorTeam1")
    glow_color_team2: Color | None = Field(None, validation_alias="m_GlowColorTeam2")
    glow_color_team_neutral: Color | None = Field(None, validation_alias="m_GlowColorTeamNeutral")

    @computed_field
    @property
    def id(self) -> int:
        return murmurhash2(self.class_name.encode(), 0x31415926)
