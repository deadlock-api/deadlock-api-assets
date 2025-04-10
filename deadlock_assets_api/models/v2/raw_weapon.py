from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, AliasChoices

from deadlock_assets_api.models.v2.raw_item_base import (
    RawItemBaseV2,
    RawItemWeaponInfoBulletSpeedCurveV2,
)


class RawWeaponInfoHorizontalRecoilV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    range: list[float] | float | None = Field(None, validation_alias="m_Range")
    burst_exponent: float | None = Field(None, validation_alias="m_flBurstExponent")


class RawWeaponInfoVerticalRecoilV2(RawWeaponInfoHorizontalRecoilV2):
    model_config = ConfigDict(populate_by_name=True)

    burst_constant: float | None = Field(None, validation_alias="m_flBurstConstant")
    burst_slope: float | None = Field(None, validation_alias="m_flBurstSlope")


class RawWeaponInfoV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    can_zoom: bool | None = Field(None, validation_alias="m_bCanZoom")
    bullet_damage: float | None = Field(None, validation_alias="m_flBulletDamage")
    bullet_gravity_scale: float | None = Field(None, validation_alias="m_flBulletGravityScale")
    bullet_inherit_shooter_velocity_scale: float | None = Field(
        None, validation_alias="m_flBulletInheritShooterVelocityScale"
    )
    bullet_lifetime: float | None = Field(None, validation_alias="m_flBulletLifetime")
    bullet_radius: float | None = Field(None, validation_alias="m_flBulletRadius")
    bullet_radius_vs_world: float | None = Field(None, validation_alias="m_flBulletRadiusVsWorld")
    bullet_reflect_amount: float | None = Field(None, validation_alias="m_flBulletReflectAmount")
    bullet_reflect_scale: float | None = Field(None, validation_alias="m_flBulletReflectScale")
    bullet_whiz_distance: float | None = Field(None, validation_alias="m_flBulletWhizDistance")
    burst_shot_cooldown: float | None = Field(None, validation_alias="m_flBurstShotCooldown")
    crit_bonus_against_npcs: float | None = Field(None, validation_alias="m_flCritBonusAgainstNpcs")
    crit_bonus_end: float | None = Field(None, validation_alias="m_flCritBonusEnd")
    crit_bonus_end_range: float | None = Field(None, validation_alias="m_flCritBonusEndRange")
    crit_bonus_start: float | None = Field(None, validation_alias="m_flCritBonusStart")
    crit_bonus_start_range: float | None = Field(None, validation_alias="m_flCritBonusStartRange")
    cycle_time: float | None = Field(None, validation_alias="m_flCycleTime")
    intra_burst_cycle_time: float | None = Field(None, validation_alias="m_flIntraBurstCycleTime")
    max_spin_cycle_time: float | None = Field(None, validation_alias="m_flMaxSpinCycleTime")
    damage_falloff_bias: float | None = Field(None, validation_alias="m_flDamageFalloffBias")
    damage_falloff_end_range: float | None = Field(
        None, validation_alias="m_flDamageFalloffEndRange"
    )
    damage_falloff_end_scale: float | None = Field(
        None, validation_alias="m_flDamageFalloffEndScale"
    )
    damage_falloff_start_range: float | None = Field(
        None, validation_alias="m_flDamageFalloffStartRange"
    )
    damage_falloff_start_scale: float | None = Field(
        None, validation_alias="m_flDamageFalloffStartScale"
    )
    horizontal_punch: float | None = Field(None, validation_alias="m_flHorizontalPunch")
    range: float | None = Field(None, validation_alias="m_flRange")
    recoil_recovery_delay_factor: float | None = Field(
        None, validation_alias="m_flRecoilRecoveryDelayFactor"
    )
    recoil_recovery_speed: float | None = Field(None, validation_alias="m_flRecoilRecoverySpeed")
    recoil_shot_index_recovery_time_factor: float | None = Field(
        None, validation_alias="m_flRecoilShotIndexRecoveryTimeFactor"
    )
    recoil_speed: float | None = Field(None, validation_alias="m_flRecoilSpeed")
    reload_move_speed: float | None = Field(None, validation_alias="m_flReloadMoveSpeed")
    scatter_yaw_scale: float | None = Field(None, validation_alias="m_flScatterYawScale")
    aiming_shot_spread_penalty: list[float] | str | None = Field(
        None, validation_alias="m_AimingShootSpreadPenalty"
    )
    standing_shot_spread_penalty: list[float] | str | None = Field(
        None, validation_alias="m_StandingShootSpreadPenalty"
    )
    shoot_move_speed_percent: float | None = Field(
        None, validation_alias="m_flShootMoveSpeedPercent"
    )
    shoot_spread_penalty_decay: float | None = Field(
        None, validation_alias="m_flShootSpreadPenaltyDecay"
    )
    shoot_spread_penalty_decay_delay: float | None = Field(
        None, validation_alias="m_flShootSpreadPenaltyDecayDelay"
    )
    shoot_spread_penalty_per_shot: float | None = Field(
        None, validation_alias="m_flShootSpreadPenaltyPerShot"
    )
    shooting_up_spread_penalty: float | None = Field(
        None, validation_alias="m_flShootingUpSpreadPenalty"
    )
    vertical_punch: float | None = Field(None, validation_alias="m_flVerticalPunch")
    zoom_fov: float | None = Field(None, validation_alias="m_flZoomFov")
    zoom_move_speed_percent: float | None = Field(None, validation_alias="m_flZoomMoveSpeedPercent")
    bullets: int | None = Field(None, validation_alias="m_iBullets")
    burst_shot_count: int | None = Field(None, validation_alias="m_iBurstShotCount")
    clip_size: int | None = Field(None, validation_alias="m_iClipSize")
    spread: float | None = Field(None, validation_alias="m_flSpread")
    standing_spread: float | None = Field(None, validation_alias="m_flStandingSpread")
    low_ammo_indicator_threshold: float | None = Field(
        None, validation_alias="m_flLowAmmoIndicatorThreshold"
    )
    recoil_seed: float | None = Field(None, validation_alias="m_flRecoilSeed")
    reload_duration: float | None = Field(
        None, validation_alias=AliasChoices("m_flReloadDuration", "m_reloadDuration")
    )
    bullet_speed_curve: RawItemWeaponInfoBulletSpeedCurveV2 = Field(
        ..., validation_alias="m_BulletSpeedCurve"
    )
    horizontal_recoil: RawWeaponInfoHorizontalRecoilV2 | None = Field(
        None, validation_alias="m_HorizontalRecoil"
    )
    vertical_recoil: RawWeaponInfoVerticalRecoilV2 | None = Field(
        None, validation_alias="m_VerticalRecoil"
    )

    @field_validator("aiming_shot_spread_penalty", "standing_shot_spread_penalty")
    @classmethod
    def validate_shot_spread_penalty(
        cls, values: list[float] | str | None = None
    ) -> list[float] | str | None:
        if isinstance(values, str):
            if len(values) == 0:
                return None
            if "," in values:
                return list(map(float, values.split(",")))
        return values


class RawWeaponV2(RawItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["weapon"] = "weapon"

    weapon_info: RawWeaponInfoV2 | None = Field(None, validation_alias="m_WeaponInfo")
