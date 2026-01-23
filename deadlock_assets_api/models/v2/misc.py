import logging
from typing import Annotated

from murmurhash2 import murmurhash2
from pydantic import ConfigDict, Field, BaseModel, computed_field, WithJsonSchema, field_validator

from deadlock_assets_api.models.v1.colors import ColorV1

LOGGER = logging.getLogger(__name__)


class ModifierValue(BaseModel):
    """
    Handles items within m_vecModifierValues and m_vecScriptValues.
    Captures both fixed values (m_value) and ranged values (m_valueMin/Max).
    """

    model_config = ConfigDict(populate_by_name=True)

    value_type: str | None = Field(None, validation_alias="m_eModifierValue")
    value: float | None = Field(None, validation_alias="m_value")
    value_min: float | None = Field(None, validation_alias="m_valueMin")
    value_max: float | None = Field(None, validation_alias="m_valueMax")


class ModifierDefinition(BaseModel):
    """
    Schema for the m_sModifer block (note the typo in the source key 'Modifer').
    """

    model_config = ConfigDict(populate_by_name=True)

    class_name: str | None = Field(None, validation_alias="_class")
    subclass_name: str | None = Field(None, validation_alias="_my_subclass_name")

    # Timing & Scaling
    duration: float | None = Field(None, validation_alias="m_flDuration")
    time_min: float | None = Field(None, validation_alias="m_flTimeMin")
    time_max: float | None = Field(None, validation_alias="m_flTimeMax")

    # Logic & Configuration
    always_show_in_ui: list[str] | None = Field(
        None, validation_alias="m_vecAlwaysShowInStatModifierUI"
    )

    # Nested Values
    modifier_values: list[ModifierValue] | None = Field(
        None, validation_alias="m_vecModifierValues"
    )
    script_values: list[ModifierValue] | None = Field(None, validation_alias="m_vecScriptValues")


class SubclassModifierDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: ModifierDefinition = Field(None, validation_alias="subclass")


class PickupDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pickup_name: str | None = Field(None, validation_alias="m_sPickup")
    pickup_weight: float | None = Field(None, validation_alias="m_flPickupWeight")


class Curve(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    base: float | None = Field(None, validation_alias="m_flBase")
    per_minute_after_start: float | None = Field(None, validation_alias="m_flPerMinuteAfterStart")


class MiscV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str
    color: ColorV1 | None = Field(None, validation_alias="m_Color")

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
    gold_amount: float | None = Field(None, validation_alias="m_flGoldAmount")
    gold_per_minute_amount: float | None = Field(None, validation_alias="m_flGoldPerMinuteAmount")

    # Pickup/Powerup Specifics
    modifier: SubclassModifierDefinition | None = Field(None, validation_alias="m_sModifer")
    pickup_radius: Curve | float | None = Field(None, validation_alias="m_flPickupRadius")
    expiration_duration: Curve | float | None = Field(
        None, validation_alias="m_flPickupExpirationDuration"
    )
    show_on_minimap: bool | None = Field(None, validation_alias="m_bShowOnMinimap")

    # XP Orb Specifics
    orb_spawn_delay_min: float | None = Field(None, validation_alias="m_flOrbSpawnDelayMin")
    orb_spawn_delay_max: float | None = Field(None, validation_alias="m_flOrbSpawnDelayMax")
    lifetime: float | None = Field(None, validation_alias="m_flLifeTime")
    collision_radius: float | None = Field(None, validation_alias="m_flCollisionRadius")

    @computed_field
    @property
    def id(self) -> Annotated[int, WithJsonSchema({"format": "int64", "type": "integer"})]:
        return murmurhash2(self.class_name.encode(), 0x31415926)

    @field_validator("color", mode="before")
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
