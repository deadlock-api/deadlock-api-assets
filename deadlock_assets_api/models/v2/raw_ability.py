import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from deadlock_assets_api.models.v2.enums import AbilityTypeV2
from deadlock_assets_api.models.v2.raw_item_base import (
    RawItemBaseV2,
)
from deadlock_assets_api.utils import parse_css_ability_icon, parse_css_ability_properties_icon

LOGGER = logging.getLogger(__name__)


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


class RawAbilityV2TooltipDetailsInfoSectionPropertyBlockProperty(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    requires_ability_upgrade: bool | None = Field(
        None, validation_alias="m_bRequiresAbilityUpgrade"
    )
    show_property_value: bool | None = Field(None, validation_alias="m_bShowPropertyValue")
    important_property: str | None = Field(None, validation_alias="m_strImportantProperty")
    status_effect_value: str | None = Field(None, validation_alias="m_strStatusEffectValue")

    @computed_field
    @property
    def important_property_icon_path(self) -> str | None:
        return parse_css_ability_properties_icon(
            "res/ability_property_icons.css", self.important_property
        )


class RawAbilityV2TooltipDetailsInfoSectionPropertyBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    loc_string: str | None = Field(None, validation_alias="m_strPropertiesTitleLocString")
    properties: list[RawAbilityV2TooltipDetailsInfoSectionPropertyBlockProperty] | None = Field(
        None, validation_alias="m_vecAbilityProperties"
    )


class RawAbilityV2TooltipDetailsInfoSection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    property_upgrade_required: str | None = Field(
        None, validation_alias="m_strAbilityPropertyUpgradeRequired"
    )
    loc_string: str | None = Field(None, validation_alias="m_strLocString")
    properties_block: list[RawAbilityV2TooltipDetailsInfoSectionPropertyBlock] | None = Field(
        None, validation_alias="m_vecAbilityPropertiesBlock"
    )
    basic_properties: list[str] | None = Field(None, validation_alias="m_vecBasicProperties")


class RawAbilityV2TooltipDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    info_sections: list[RawAbilityV2TooltipDetailsInfoSection] | None = Field(
        None, validation_alias="m_vecAbilityInfoSections"
    )
    additional_header_properties: list[str] | None = Field(
        None, validation_alias="m_vecAdditionalHeaderProperties"
    )


class DependantAbilities(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    flags: list[str] | None = Field(None, validation_alias="m_eFlags")

    @field_validator("flags", mode="before")
    @classmethod
    def split_flags(cls, v: str | list[str] | None) -> list[str] | None:
        if v is None:
            return None
        if isinstance(v, str):
            return [flag.strip() for flag in v.split("|")]
        return v


class RawAbilityV2(RawItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["ability"] = "ability"
    grant_ammo_on_cast: bool | None = Field(None, validation_alias="m_bGrantAmmoOnCast")
    behaviour_bits: str | None = Field(None, validation_alias="m_AbilityBehaviorsBits")
    upgrades: list[RawAbilityUpgradeV2] = Field(..., validation_alias="m_vecAbilityUpgrades")
    ability_type: AbilityTypeV2 | None = Field(None, validation_alias="m_eAbilityType")
    boss_damage_scale: float | None = Field(None, validation_alias="m_flBossDamageScale")
    dependant_abilities: list[str] | None = Field(None, validation_alias="m_vecDependentAbilities")
    video: str | None = Field(None, validation_alias="m_strMoviePreviewPath")
    tooltip_details: RawAbilityV2TooltipDetails | None = Field(
        None, validation_alias="m_AbilityTooltipDetails"
    )
    dependent_abilities: dict[str, DependantAbilities | None] | None = Field(
        None, validation_alias="m_mapDependentAbilities"
    )

    @model_validator(mode="after")
    def check_image_path(self):
        if self.image is None and self.css_class is not None and self.css_class != "":
            try:
                css_image = parse_css_ability_icon(self.css_class)
                self.image = css_image or self.image
            except Exception as e:
                LOGGER.warning(f"Failed to parse css for {self.css_class}: {e}")
        return self
