from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from deadlock_assets_api.models.v2.enums import GameMode


class TrackedStatName(StrEnum):
    ability_damage = "ability_damage"
    ability_kills = "ability_kills"
    assists = "assists"
    breakables_destroyed = "breakables_destroyed"
    bullet_damage = "bullet_damage"
    closeup_damage = "closeup_damage"
    closeup_kills = "closeup_kills"
    damage_absorbed = "damage_absorbed"
    damage_mitigated = "damage_mitigated"
    denies = "denies"
    first_blood = "first_blood"
    gun_kills = "gun_kills"
    headshot_damage = "headshot_damage"
    headshots = "headshots"
    healing = "healing"
    kills = "kills"
    killstreak_kills = "killstreak_kills"
    last_hits = "last_hits"
    long_distance_damage = "long_distance_damage"
    long_distance_kills = "long_distance_kills"
    melee_damage = "melee_damage"
    melee_kills = "melee_kills"
    net_worth = "net_worth"
    neutral_last_hits = "neutral_last_hits"
    pickups_collected_powerup = "pickups_collected_powerup"
    player_damage = "player_damage"
    returned_idol = "returned_idol"
    secures = "secures"
    sinners_sacrifice_jackpot = "sinners_sacrifice_jackpot"
    trooper_last_hits = "trooper_last_hits"
    weapon_damage = "weapon_damage"

    @classmethod
    def _missing_(cls, new_value: str):
        new_value = new_value.lower()
        for member in cls:
            if new_value in [member.value.lower(), member.name.lower()]:
                return member
        raise ValueError(f"Unknown TrackedStatName: {new_value}")


class ThresholdType(StrEnum):
    Automatic = "automatic"
    Manual = "manual"

    @classmethod
    def _missing_(cls, new_value: str):
        new_value = new_value.lower()
        for member in cls:
            if new_value in [member.value.lower(), member.name.lower()]:
                return member
        raise ValueError(f"Unknown ThresholdType: {new_value}")


class RawAccoladeV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str

    id: int = Field(..., validation_alias="m_unAccoladeID")
    tracked_stat_name: TrackedStatName = Field(..., validation_alias="m_sTrackedStatName")
    flavor_name: str = Field(..., validation_alias="m_sFlavorName")
    description: str = Field(..., validation_alias="m_sDescription")
    threshold_type: ThresholdType = Field(..., validation_alias="m_eThresholdType")
    enabled_game_modes: list[GameMode] | None = Field(
        None, validation_alias="m_vecEnabledGameModes"
    )
