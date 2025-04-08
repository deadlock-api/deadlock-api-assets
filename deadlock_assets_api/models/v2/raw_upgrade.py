from enum import Enum
from typing import Literal

from pydantic import ConfigDict, Field, BaseModel

from deadlock_assets_api.models.v2.enums import ItemTierV2, ItemSlotTypeV2
from deadlock_assets_api.models.v2.raw_item_base import RawItemBaseV2


class RawAbilityActivationV2(str, Enum):
    CITADEL_ABILITY_ACTIVATION_HOLD_TOGGLE = "hold_toggle"
    CITADEL_ABILITY_ACTIVATION_INSTANT_CAST = "instant_cast"
    CITADEL_ABILITY_ACTIVATION_ON_BUTTON_IS_DOWN = "on_button_is_down"
    CITADEL_ABILITY_ACTIVATION_PASSIVE = "passive"
    CITADEL_ABILITY_ACTIVATION_PRESS = "press"
    CITADEL_ABILITY_ACTIVATION_PRESS_TOGGLE = "press_toggle"

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if value in [member.value.lower(), member.name.lower()]:
                return member
        return None


class RawAbilityImbueV2(str, Enum):
    CITADEL_TARGET_ABILITY_BEHAVIOR_IMBUE_ACTIVE = "imbue_active"
    CITADEL_TARGET_ABILITY_BEHAVIOR_IMBUE_MODIFIER_VALUE = "imbue_modifier_value"

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if value in [member.value.lower(), member.name.lower()]:
                return member
        return None


class RawUpgradeTooltipSectionAttributeImportantPropertyV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    important_property: str | None = Field(None, validation_alias="m_strImportantProperty")


class RawUpgradeTooltipSectionAttributeV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    properties: list[str] | None = Field(None, validation_alias="m_vecAbilityProperties")
    elevated_properties: list[str] | None = Field(
        None, validation_alias="m_vecElevatedAbilityProperties"
    )
    important_properties: list[RawUpgradeTooltipSectionAttributeImportantPropertyV2] | None = Field(
        None, validation_alias="m_vecImportantAbilityProperties"
    )


class RawAbilitySectionTypeV2(str, Enum):
    EArea_Innate = "innate"
    EArea_Active = "active"
    EArea_Passive = "passive"

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if value in [member.value.lower(), member.name.lower()]:
                return member
        return None


class RawUpgradeTooltipSectionV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    section_type: RawAbilitySectionTypeV2 | None = Field(
        None, validation_alias="m_eAbilitySectionType"
    )
    section_attributes: list[RawUpgradeTooltipSectionAttributeV2] = Field(
        ..., validation_alias="m_vecSectionAttributes"
    )


class RawUpgradeV2(RawItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["upgrade"] = "upgrade"

    item_slot_type: ItemSlotTypeV2 = Field(..., validation_alias="m_eItemSlotType")
    item_tier: ItemTierV2 = Field(..., validation_alias="m_iItemTier")
    disabled: bool | None = Field(None, validation_alias="m_bDisabled")
    activation: RawAbilityActivationV2 = Field(None, validation_alias="m_eAbilityActivation")
    imbue: RawAbilityImbueV2 | None = Field(None, validation_alias="m_TargetAbilityEffectsToApply")
    component_items: list[str] | None = Field(None, validation_alias="m_vecComponentItems")
    tooltip_sections: list[RawUpgradeTooltipSectionV2] | None = Field(
        None, validation_alias="m_vecTooltipSectionInfo"
    )
