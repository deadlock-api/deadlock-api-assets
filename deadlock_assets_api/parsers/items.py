import logging
from typing import Literal

from deadlock_assets_api.models.v2.raw_ability import RawAbilityV2
from deadlock_assets_api.models.v2.raw_upgrade import RawUpgradeV2
from deadlock_assets_api.models.v2.raw_weapon import RawWeaponV2

LOGGER = logging.getLogger(__name__)


def detect_item_type(data: dict) -> Literal["weapon", "ability", "upgrade"] | None:
    if ability_type := data.get("m_eAbilityType"):
        if ability_type in ["EAbilityType_Weapon", "EAbilityType_Melee"]:
            return "weapon"
        elif (
            ability_type == "EAbilityType_Item"
            and data.get("m_iItemTier")
            and data.get("m_eItemSlotType")
        ):
            return "upgrade"
        elif ability_type in [
            "EAbilityType_Innate",
            "EAbilityType_Signature",
            "EAbilityType_Ultimate",
        ]:
            return "ability"

    if source_name := data.get("m_strAG2SourceName"):
        if source_name == "item" and data.get("m_iItemTier") and data.get("m_eItemSlotType"):
            return "upgrade"
        elif source_name == "weapon":
            return "weapon"
        elif "ability" in source_name:
            return "ability"

    if _ := data.get("m_iItemTier"):
        return "upgrade"

    if _ := data.get("m_eItemSlotType"):
        return "upgrade"

    return None


def parse_items_v2(data: dict) -> list[RawWeaponV2 | RawUpgradeV2 | RawAbilityV2]:
    hero_dicts = {
        k: v
        for k, v in data.items()
        if "base" not in k
        and "dummy" not in k
        and ("generic" not in k or "citadel" in k)
        and isinstance(v, dict)
    }

    def parse(class_name, data) -> RawWeaponV2 | RawUpgradeV2 | RawAbilityV2 | None:
        item_type = detect_item_type(data)
        if item_type == "weapon":
            return RawWeaponV2(class_name=class_name, **data)
        elif item_type == "ability":
            return RawAbilityV2(class_name=class_name, **data)
        elif item_type == "upgrade":
            return RawUpgradeV2(class_name=class_name, **data)
        LOGGER.warning(f"Unknown class name: {class_name}")
        return None

    items = [parse(k, v) for k, v in hero_dicts.items()]
    return [i for i in items if i is not None]
