from typing import Literal

from pydantic import ConfigDict, Field, computed_field, BaseModel

from deadlock_assets_api.models.v1.generic_data import load_generic_data
from deadlock_assets_api.models.v1.item import ItemSlotTypeV1
from deadlock_assets_api.models.v2.api_item_base import ItemBaseV2
from deadlock_assets_api.models.v2.enums import ItemTierV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_upgrade import (
    RawAbilityActivationV2,
    RawUpgradeV2,
    RawAbilityImbueV2,
)
from deadlock_assets_api.models.v2.v2_utils import replace_templates


class UpgradeDescriptionV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    desc: str | None
    active: str | None
    passive: str | None

    @classmethod
    def from_raw_upgrade(
        cls,
        raw_upgrade: RawUpgradeV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> "UpgradeDescriptionV2":
        return cls(
            desc=replace_templates(
                raw_upgrade,
                raw_heroes,
                localization,
                localization.get(f"{raw_upgrade.class_name}_desc"),
            ),
            active=replace_templates(
                raw_upgrade,
                raw_heroes,
                localization,
                localization.get(f"{raw_upgrade.class_name}_active_desc")
                or localization.get(f"{raw_upgrade.class_name}_active")
                or localization.get(f"{raw_upgrade.class_name}_active1")
                or localization.get(f"{raw_upgrade.class_name}_active2"),
            ),
            passive=replace_templates(
                raw_upgrade,
                raw_heroes,
                localization,
                localization.get(f"{raw_upgrade.class_name}_passive_desc")
                or localization.get(f"{raw_upgrade.class_name}_passive")
                or localization.get(f"{raw_upgrade.class_name}_passive1")
                or localization.get(f"{raw_upgrade.class_name}_passive2"),
            ),
        )


class UpgradeV2(ItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["upgrade"] = "upgrade"

    item_slot_type: ItemSlotTypeV1
    item_tier: ItemTierV2
    disabled: bool | None
    description: UpgradeDescriptionV2 | None = Field(None)
    activation: RawAbilityActivationV2
    imbue: RawAbilityImbueV2 | None
    component_items: list[str] | None

    @computed_field
    @property
    def is_active_item(self) -> bool:
        return self.activation is not RawAbilityActivationV2.CITADEL_ABILITY_ACTIVATION_PASSIVE

    @computed_field
    @property
    def shopable(self) -> bool:
        return (
            (self.disabled is None or self.disabled is False)
            and self.item_slot_type
            in [
                ItemSlotTypeV1.EItemSlotType_Armor,
                ItemSlotTypeV1.EItemSlotType_WeaponMod,
                ItemSlotTypeV1.EItemSlotType_Tech,
            ]
            and self.image is not None
        )

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
    ) -> "UpgradeV2":
        raw_model = super().from_raw_item(raw_upgrade, raw_heroes, localization)
        raw_model["description"] = UpgradeDescriptionV2.from_raw_upgrade(
            raw_upgrade, raw_heroes, localization
        )
        return cls(**raw_model)

    @computed_field
    @property
    def cost(self) -> int | None:
        generic_data = load_generic_data()
        return generic_data.item_price_per_tier[self.item_tier]
