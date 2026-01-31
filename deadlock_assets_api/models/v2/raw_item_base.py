import logging

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from deadlock_assets_api.models.v2.enums import StatsUsageFlagV2
from deadlock_assets_api.utils import parse_css_ability_properties_icon

LOGGER = logging.getLogger(__name__)


class RawItemWeaponInfoBulletSpeedCurveSplineV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    slope_incoming: float = Field(..., validation_alias="m_flSlopeIncoming")
    slope_outgoing: float = Field(..., validation_alias="m_flSlopeOutgoing")
    x: float = Field(..., validation_alias="x")
    y: float = Field(..., validation_alias="y")


class RawItemWeaponInfoBulletSpeedCurveV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    spline: list[RawItemWeaponInfoBulletSpeedCurveSplineV2] = Field(
        None, validation_alias="m_spline"
    )
    domain_maxs: list[float] = Field(..., validation_alias="m_vDomainMaxs")
    domain_mins: list[float] = Field(..., validation_alias="m_vDomainMins")


class RawItemWeaponInfoV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bullet_speed_curve: RawItemWeaponInfoBulletSpeedCurveV2 | None = Field(
        None, validation_alias="m_BulletSpeedCurve"
    )


class RawItemPropertyScaleFunctionSubclassV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str | None = Field(None, validation_alias="_class")
    subclass_name: str | None = Field(None, validation_alias="_my_subclass_name")
    specific_stat_scale_type: str | None = Field(None, validation_alias="m_eSpecificStatScaleType")
    scaling_stats: list[str] | None = Field(None, validation_alias="m_vecScalingStats")
    stat_scale: float | None = Field(None, validation_alias="m_flStatScale")
    street_brawl_stat_scale: float | None = Field(None, validation_alias="m_flStreetBrawlStatScale")


class RawItemPropertyScaleFunctionV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subclass: RawItemPropertyScaleFunctionSubclassV2 | None = Field(
        None, validation_alias="subclass"
    )


class RawItemPropertyV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: str | float | None = Field(
        None, validation_alias=AliasChoices("m_strValue", "m_strVAlue")
    )
    street_brawl_value: str | float | None = Field(None, validation_alias="m_strStreetBrawlValue")
    can_set_token_override: bool | None = Field(None, validation_alias="m_bCanSetTokenOverride")
    provided_property_type: str | None = Field(None, validation_alias="m_eProvidedPropertyType")
    css_class: str | None = Field(None, validation_alias="m_strCSSClass")
    usage_flags: list[StatsUsageFlagV2] | str | None = Field(
        None, validation_alias="m_eStatsUsageFlags"
    )
    negative_attribute: bool | None = Field(None, validation_alias="m_bIsNegativeAttribute")
    disable_value: str | None = Field(None, validation_alias="m_strDisableValue")
    loc_token_override: str | None = Field(None, validation_alias="m_strLocTokenOverride")
    display_units: str | None = Field(None, validation_alias="m_eDisplayUnits")
    icon_path: str | None = Field(None, validation_alias="m_strCSSClass")
    scale_function: RawItemPropertyScaleFunctionV2 | None = Field(
        None, validation_alias="m_subclassScaleFunction"
    )

    @field_validator("scale_function", mode="before")
    @classmethod
    def validate_scale_function(
        cls, value: RawItemPropertyScaleFunctionV2 | str | None, _
    ) -> RawItemPropertyScaleFunctionV2 | None:
        if value is None or isinstance(value, str):
            return None
        return value

    @field_validator("icon_path")
    @classmethod
    def validate_icon_path(cls, value: str | None, _) -> bool | None:
        if value is None:
            return None
        if value.startswith("panorama"):
            return value
        return parse_css_ability_properties_icon("res/ability_property_icons.css", value)

    @field_validator("usage_flags", mode="before")
    @classmethod
    def validate_usage_flags(cls, value: str | list | None, _) -> list[StatsUsageFlagV2] | None:
        if value is None or value == "":
            return None
        if isinstance(value, list):
            return value
        return [StatsUsageFlagV2(member.strip()) for member in value.split("|")]


class RawItemBaseV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str
    start_trained: bool | None = Field(None, validation_alias="m_bStartTrained")
    image: str | None = Field(None, validation_alias="m_strAbilityImage")
    update_time: int | None = Field(None, validation_alias="m_iUpdateTime")
    properties: dict[str, RawItemPropertyV2] | None = Field(
        None, validation_alias="m_mapAbilityProperties"
    )
    weapon_info: RawItemWeaponInfoV2 | None = Field(None, validation_alias="m_WeaponInfo")
    css_class: str | None = Field(None, validation_alias="m_strCSSClass")
