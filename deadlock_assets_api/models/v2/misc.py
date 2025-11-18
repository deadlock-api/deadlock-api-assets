import logging

from murmurhash2 import murmurhash2
from pydantic import ConfigDict, Field, BaseModel, computed_field

LOGGER = logging.getLogger(__name__)

Color = tuple[int, int, int] | tuple[int, int, int, int]


class PickupDefinition(BaseModel):
    """Schema for items inside m_vecPrimaryPickups"""

    model_config = ConfigDict(populate_by_name=True)

    pickup_name: str | None = Field(None, validation_alias="m_sPickup")
    pickup_weight: float | None = Field(None, validation_alias="m_flPickupWeight")


class MiscV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str

    # Spawning & Timing
    initial_spawn_time: float | None = Field(None, validation_alias="m_flInitialSpawnTime")
    respawn_time: float | None = Field(None, validation_alias="m_flRespawnTime")
    spawn_interval: float | None = Field(None, validation_alias="m_flSpawnInterval")
    initial_spawn_delay_in_seconds: int | None = Field(
        None, validation_alias="m_iInitialSpawnDelayInSeconds"
    )
    spawn_interval_in_seconds: int | None = Field(
        None, validation_alias="m_iSpawnIntervalInSeconds"
    )
    match_time_mins_for_level2_pickups: int | None = Field(
        None, validation_alias="m_iMatchTimeMinsForLevel2Pickups"
    )
    match_time_mins_for_level3_pickups: int | None = Field(
        None, validation_alias="m_iMatchTimeMinsForLevel3Pickups"
    )
    loot_list_deck_size: int | None = Field(None, validation_alias="m_iLootListDeckSize")
    initial_spawn_delay_seconds: int | None = Field(
        None, validation_alias="m_iInitialSpawnDelayInSeconds"
    )

    # Health & Damage Logic (Breakable Props)
    health: int | None = Field(None, validation_alias="m_iHealth")
    break_on_dodge_touch: bool | None = Field(None, validation_alias="m_bBreakOnDodgeTouch")
    solid_after_death: bool | None = Field(None, validation_alias="m_bSolidAfterDeath")
    render_after_death: bool | None = Field(None, validation_alias="m_bRenderAfterDeath")
    damaged_by_abilities: bool | None = Field(None, validation_alias="m_bDamagedByAbilities")
    damaged_by_melee: bool | None = Field(None, validation_alias="m_bDamagedByMelee")
    damaged_by_bullets: bool | None = Field(None, validation_alias="m_bDamagedByBullets")
    is_mantleable: bool | None = Field(None, validation_alias="m_bIsMantleable")

    # Drops & Loot
    primary_drop_chance: float | None = Field(None, validation_alias="m_flPrimaryDropChance")
    primary_pickups: list[PickupDefinition] | None = Field(
        None, validation_alias="m_vecPrimaryPickups"
    )
    m_vecPickups_lv2: list[PickupDefinition] | None = Field(
        None, validation_alias="m_vecPickups_lv2"
    )
    m_vecPickups_lv3: list[PickupDefinition] | None = Field(
        None, validation_alias="m_vecPickups_lv3"
    )
    roll_type: str | None = Field(None, validation_alias="m_eRollType")

    # Pickup/Powerup Specifics
    pickup_radius: float | None = Field(None, validation_alias="m_flPickupRadius")
    expiration_duration: float | None = Field(None, validation_alias="m_flPickupExpirationDuration")
    show_on_minimap: bool | None = Field(None, validation_alias="m_bShowOnMinimap")
    name_loc_string: str | None = Field(None, validation_alias="m_sNameLocString")

    # XP Orb Specifics
    orb_spawn_delay_min: float | None = Field(None, validation_alias="m_flOrbSpawnDelayMin")
    orb_spawn_delay_max: float | None = Field(None, validation_alias="m_flOrbSpawnDelayMax")
    lifetime: float | None = Field(None, validation_alias="m_flLifeTime")
    collision_radius: float | None = Field(None, validation_alias="m_flCollisionRadius")

    @computed_field
    @property
    def id(self) -> int:
        return murmurhash2(self.class_name.encode(), 0x31415926)
