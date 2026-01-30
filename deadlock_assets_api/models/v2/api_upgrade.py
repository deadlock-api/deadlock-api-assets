from typing import Literal

from pydantic import ConfigDict, Field, computed_field, BaseModel

from deadlock_assets_api.models.v2.api_item_base import ItemBaseV2, ItemPropertyV2, parse_img_path
from deadlock_assets_api.models.v2.enums import ItemTierV2, ItemSlotTypeV2
from deadlock_assets_api.models.v2.generic_data import load_generic_data
from deadlock_assets_api.models.v2.raw_ability import RawAbilityUpgradeV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_item_base import RawItemPropertyV2
from deadlock_assets_api.models.v2.raw_upgrade import (
    RawAbilityActivationV2,
    RawUpgradeV2,
    RawAbilityImbueV2,
    RawAbilitySectionTypeV2,
    RawUpgradeTooltipSectionV2,
    RawUpgradeTooltipSectionAttributeV2,
)
from deadlock_assets_api.models.v2.v2_utils import replace_templates


class UpgradeDescriptionV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    desc: str | None = None
    desc2: str | None = None
    active: str | None = None
    passive: str | None = None

    @classmethod
    def from_raw_upgrade(
        cls,
        raw_upgrade: RawUpgradeV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> UpgradeDescriptionV2:
        return cls(
            desc=replace_templates(
                raw_upgrade,
                raw_heroes,
                localization,
                localization.get(f"{raw_upgrade.class_name}_desc")
                or localization.get(f"{raw_upgrade.class_name}_headshots_desc")
                or localization.get(f"{raw_upgrade.class_name}_desc1")
                or localization.get(f"{raw_upgrade.class_name}_headshots_desc1"),
            ),
            desc2=replace_templates(
                raw_upgrade,
                raw_heroes,
                localization,
                localization.get(f"{raw_upgrade.class_name}_desc2")
                or localization.get(f"{raw_upgrade.class_name}_headshots_desc2"),
            ),
            active=replace_templates(
                raw_upgrade,
                raw_heroes,
                localization,
                localization.get(f"{raw_upgrade.class_name}_active_desc")
                or localization.get(f"{raw_upgrade.class_name}_active")
                or localization.get(f"{raw_upgrade.class_name}_active1")
                or localization.get(f"{raw_upgrade.class_name}_active2")
                or localization.get(f"{raw_upgrade.class_name}_ambush_desc"),
            ),
            passive=replace_templates(
                raw_upgrade,
                raw_heroes,
                localization,
                localization.get(f"{raw_upgrade.class_name}_passive_desc")
                or localization.get(f"{raw_upgrade.class_name}_passive")
                or localization.get(f"{raw_upgrade.class_name}_desc_passive")
                or localization.get(f"{raw_upgrade.class_name}_passive1")
                or localization.get(f"{raw_upgrade.class_name}_desc_passive1")
                or localization.get(f"{raw_upgrade.class_name}_passive2")
                or localization.get(f"{raw_upgrade.class_name}_desc_passive2")
                or localization.get(f"{raw_upgrade.class_name}_high_health_passive_desc")
                or localization.get(f"{raw_upgrade.class_name}_component_passive_desc"),
            ),
        )


class UpgradePropertyV2(ItemPropertyV2):
    model_config = ConfigDict(populate_by_name=True)

    tooltip_section: RawAbilitySectionTypeV2 | None = None
    tooltip_is_elevated: bool | None = None
    tooltip_is_important: bool | None = None

    @classmethod
    def from_raw_upgrade(
        cls,
        name: str,
        raw_property: RawItemPropertyV2,
        tooltip_sections: list[RawUpgradeTooltipSectionV2] | None,
        localization: dict[str, str],
    ) -> UpgradePropertyV2:
        def in_important_properties(name: str, sa: RawUpgradeTooltipSectionAttributeV2) -> bool:
            return any(
                name == p.get("important_property")
                for p in sa.get("important_properties", []) or []
            )

        def in_elevated_properties(name: str, sa: RawUpgradeTooltipSectionAttributeV2) -> bool:
            return name in (sa.get("elevated_properties", []) or [])

        def has_property(name: str, sa: RawUpgradeTooltipSectionAttributeV2) -> bool:
            return (
                name in (sa.get("properties", []) or [])
                or in_important_properties(name, sa)
                or in_elevated_properties(name, sa)
            )

        try:
            tooltip_section = (
                next(
                    ts
                    for ts in tooltip_sections
                    if any(has_property(name, sa) for sa in ts["section_attributes"])
                )
                if tooltip_sections
                else None
            )
        except StopIteration:
            tooltip_section = None
        return cls(
            **ItemPropertyV2.from_raw_item_property(raw_property.model_dump(), name, localization),
            tooltip_section=tooltip_section.get("section_type") if tooltip_section else None,
            tooltip_is_elevated=any(
                in_elevated_properties(name, sa)
                for sa in tooltip_section.get("section_attributes") or []
            )
            if tooltip_section
            else None,
            tooltip_is_important=any(
                in_important_properties(name, sa)
                for sa in tooltip_section.get("section_attributes") or []
            )
            if tooltip_section
            else None,
        )


class UpgradeTooltipSectionAttributeV2ImportantPropertyWithIcon(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    icon: str | None = None
    localized_name: str | None = None

    @classmethod
    def from_raw_important_property_with_icon(
        cls, raw_important_property_with_icon: dict, localization: dict[str, str]
    ):
        raw_important_property_with_icon["icon"] = parse_img_path(
            raw_important_property_with_icon["icon_path"]
        )
        del raw_important_property_with_icon["icon_path"]
        localized_name = localization.get(
            f"Citadel_{raw_important_property_with_icon['name']}",
            localization.get(raw_important_property_with_icon["name"]),
        )
        raw_important_property_with_icon["localized_name"] = (
            localized_name.strip() if localized_name else None
        )
        return cls(**raw_important_property_with_icon)


class UpgradeTooltipSectionAttributeV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    loc_string: str | None = None
    properties: list[str] | None = None
    elevated_properties: list[str] | None = None
    important_properties: list[str] | None = None
    important_properties_with_icon: (
        list[UpgradeTooltipSectionAttributeV2ImportantPropertyWithIcon] | None
    ) = None

    @classmethod
    def from_raw_section_attribute(
        cls,
        raw_upgrade: RawUpgradeV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
        raw_section_attribute: RawUpgradeTooltipSectionAttributeV2,
    ):
        return cls(
            loc_string=replace_templates(
                raw_upgrade,
                raw_heroes,
                localization,
                localization.get(raw_section_attribute.loc_string.strip("#")),
            )
            if raw_section_attribute.loc_string
            else None,
            properties=raw_section_attribute.properties,
            elevated_properties=raw_section_attribute.elevated_properties,
            important_properties=[
                p.important_property
                for p in raw_section_attribute.important_properties or []
                if p.important_property
            ]
            if raw_section_attribute.important_properties
            else None,
            important_properties_with_icon=[
                UpgradeTooltipSectionAttributeV2ImportantPropertyWithIcon.from_raw_important_property_with_icon(
                    p.model_dump(), localization
                )
                for p in raw_section_attribute.important_properties_with_icon_path or []
            ]
            if raw_section_attribute.important_properties_with_icon_path
            else None,
        )


class UpgradeTooltipSectionV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    section_type: RawAbilitySectionTypeV2 | None = None
    section_attributes: list[UpgradeTooltipSectionAttributeV2] | None = None

    @classmethod
    def from_raw_section(
        cls,
        raw_upgrade: RawUpgradeV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
        raw_section: RawUpgradeTooltipSectionV2,
    ):
        return cls(
            section_type=raw_section.section_type,
            section_attributes=[
                UpgradeTooltipSectionAttributeV2.from_raw_section_attribute(
                    raw_upgrade, raw_heroes, localization, s
                )
                for s in raw_section.section_attributes or []
            ],
        )


class UpgradeV2(ItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["upgrade"] = "upgrade"

    shop_image: str | None = None
    shop_image_webp: str | None = None
    shop_image_small: str | None = None
    shop_image_small_webp: str | None = None
    item_slot_type: ItemSlotTypeV2
    item_tier: ItemTierV2
    properties: dict[str, UpgradePropertyV2] | None = None
    disabled: bool | None = None
    description: UpgradeDescriptionV2 | None = Field(None)
    activation: RawAbilityActivationV2
    imbue: RawAbilityImbueV2 | None = None
    component_items: list[str] | None = None
    tooltip_sections: list[UpgradeTooltipSectionV2] | None = None
    upgrades: list[RawAbilityUpgradeV2] | None = None

    @computed_field
    @property
    def is_active_item(self) -> bool:
        return self.activation is not RawAbilityActivationV2.CITADEL_ABILITY_ACTIVATION_PASSIVE

    @computed_field
    @property
    def shopable(self) -> bool:
        return (self.disabled is None or self.disabled is False) and self.shop_image is not None

    def load_description(
        self,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> str:
        return replace_templates(
            self,
            raw_heroes,
            localization,
            localization.get(f"{self.class_name}_desc"),
            None,
        )

    @classmethod
    def from_raw_item(
        cls,
        raw_upgrade: RawUpgradeV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> UpgradeV2:
        raw_model = super().from_raw_item(raw_upgrade, raw_heroes, localization)
        raw_model["shop_image"] = parse_img_path(raw_model["shop_image"])
        if raw_model["shop_image"] is not None:
            raw_model["shop_image_webp"] = raw_model["shop_image"].replace(".png", ".webp")
        raw_model["shop_image_small"] = parse_img_path(raw_model["shop_image_small"])
        if raw_model["shop_image_small"] is not None:
            raw_model["shop_image_small_webp"] = raw_model["shop_image_small"].replace(
                ".png", ".webp"
            )
        raw_model["description"] = UpgradeDescriptionV2.from_raw_upgrade(
            raw_upgrade, raw_heroes, localization
        )
        raw_model["properties"] = {
            k: UpgradePropertyV2.from_raw_upgrade(k, v, raw_model["tooltip_sections"], localization)
            for k, v in raw_upgrade.properties.items()
        }
        raw_model["tooltip_sections"] = [
            UpgradeTooltipSectionV2.from_raw_section(raw_upgrade, raw_heroes, localization, s)
            for s in raw_upgrade.tooltip_sections or []
        ]
        return cls(**raw_model)

    @computed_field
    @property
    def cost(self) -> int | None:
        generic_data = load_generic_data()
        if not generic_data:
            return None
        return generic_data.item_price_per_tier[self.item_tier]
