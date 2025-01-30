from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from deadlock_assets_api.models.v2.enums import AbilityTypeV2
from deadlock_assets_api.models.v2.raw_item_base import RawItemBaseV2


class RawAbilityUpgradePropertyUpgradeV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., validation_alias="m_strPropertyName")
    bonus: str | float = Field(..., validation_alias="m_strBonus")
    scale_stat_filter: str | None = Field(None, validation_alias="m_eScaleStatFilter")
    upgrade_type: str | None = Field(None, validation_alias="m_eUpgradeType")


class RawAbilityUpgradeV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    property_upgrades: list[RawAbilityUpgradePropertyUpgradeV2] = Field(
        default_factory=list, validation_alias="m_vecPropertyUpgrades"
    )


class RawAbilityV2(RawItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["ability"] = "ability"
    behaviour_bits: str | None = Field(None, validation_alias="m_AbilityBehaviorsBits")
    upgrades: list[RawAbilityUpgradeV2] | None = Field(
        None, validation_alias="m_vecAbilityUpgrades"
    )
    ability_type: AbilityTypeV2 | None = Field(None, validation_alias="m_eAbilityType")
    boss_damage_scale: float | None = Field(None, validation_alias="m_flBossDamageScale")
    dependant_abilities: list[str] | None = Field(None, validation_alias="m_vecDependentAbilities")
    video: str | None = Field(None, validation_alias="m_strMoviePreviewPath")
