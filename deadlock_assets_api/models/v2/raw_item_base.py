import logging
from functools import lru_cache

import css_parser
from css_parser.css import CSSRuleList, CSSStyleRule
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator, field_validator

from deadlock_assets_api.models.v2.enums import StatsUsageFlagV2

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
        icon = parse_css_ability_properties_icon("res/citadel_mod_tooltip_shared.css", value)
        if icon is not None:
            return icon
        return parse_css_ability_properties_icon("res/ability_properties.css", value)

    @field_validator("usage_flags")
    @classmethod
    def validate_usage_flags(cls, value: str | list | None, _) -> list[StatsUsageFlagV2] | None:
        if value is None:
            return None
        if isinstance(value, list):
            return value
        return [StatsUsageFlagV2(member.strip()) for member in value.split("|")]


@lru_cache
def parse_css_rules(filename: str) -> CSSRuleList:
    return css_parser.parseFile(filename).cssRules


def parse_css_ability_properties_icon(file: str, css_class_icon: str) -> str | None:
    for rule in parse_css_rules(file):
        if not isinstance(rule, CSSStyleRule):
            continue
        css_class = next(
            (
                s
                for s in " ".join(rule.selectorText.split(".")).split(" ")
                if s == f"prop_{css_class_icon}" or s == css_class_icon
            ),
            None,
        )
        if css_class is None:
            continue
        rule: CSSStyleRule = rule
        background_image = rule.style.getProperty("background-image")
        if background_image is None:
            continue
        background_image = background_image.value[4:-1]
        background_image = background_image.replace("_psd.vtex", ".psd")
        background_image = background_image.split("images/")[-1]
        return 'panorama:"file://{images}/' + background_image + '"'
    return None


def parse_css_ability_icon(class_name: str) -> str | None:
    for rule in parse_css_rules("res/ability_icons.css"):
        if not isinstance(rule, CSSStyleRule):
            continue
        css_class = next(
            (s for s in " ".join(rule.selectorText.split(".")).split(" ") if s == class_name),
            None,
        )
        if css_class is None:
            continue
        rule: CSSStyleRule = rule
        background_image = rule.style.getProperty("background-image")
        if background_image is None:
            continue
        background_image = background_image.value[4:-1]
        background_image = background_image.replace("_psd.vtex", ".psd")
        background_image = background_image.split("images/")[-1]
        return 'panorama:"file://{images}/' + background_image + '"'
    return None


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

    @model_validator(mode="after")
    def check_image_path(self):
        if self.image is not None and self.css_class is not None and self.css_class != "":
            try:
                css_image = parse_css_ability_icon(self.css_class)
                self.image = css_image or self.image
            except Exception as e:
                LOGGER.warning(f"Failed to parse css for {self.css_class}: {e}")
        return self
