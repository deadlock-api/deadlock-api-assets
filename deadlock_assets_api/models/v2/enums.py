import logging
from enum import Enum, StrEnum
from logging import warning


class StatsUsageFlagV2(str, Enum):
    ConditionallyApplied = "ConditionallyApplied"
    ConditionallyEnemyApplied = "ConditionallyEnemyApplied"
    IntrinsicallyProvidedInAbility = "IntrinsicallyProvidedInAbility"
    IntrinsicallyProvidedInModifier = "IntrinsicallyProvidedInModifier"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if isinstance(value, int) and value == member.value:
                return member
            if isinstance(value, str) and value.lower() == member.name.lower():
                return member
        return None


class ItemTierV2(int, Enum):
    EModTier_1 = 1
    EModTier_2 = 2
    EModTier_3 = 3
    EModTier_4 = 4

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if isinstance(value, int) and value == member.value:
                return member
            if isinstance(value, str) and value.lower() == member.name.lower():
                return member
        return None


class AbilityTypeV2(str, Enum):
    EAbilityType_Innate = "innate"
    EAbilityType_Item = "item"
    EAbilityType_Signature = "signature"
    EAbilityType_Ultimate = "ultimate"
    EAbilityType_Weapon = "weapon"

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if value in [member.value.lower(), member.name.lower()]:
                return member
        return None


class HeroItemTypeV2(str, Enum):
    ESlot_Weapon_Primary = "weapon_primary"
    ESlot_Weapon_Secondary = "weapon_secondary"
    ESlot_Weapon_Melee = "weapon_melee"
    ESlot_Ability_Mantle = "ability_mantle"
    ESlot_Ability_Jump = "ability_jump"
    ESlot_Ability_Slide = "ability_slide"
    ESlot_Ability_ZipLine = "ability_zip_line"
    ESlot_Ability_ZipLineBoost = "ability_zip_line_boost"
    ESlot_Ability_ClimbRope = "ability_climb_rope"
    ESlot_Ability_Innate_1 = "ability_innate1"
    ESlot_Ability_Innate_2 = "ability_innate2"
    ESlot_Ability_Innate_3 = "ability_innate3"
    ESlot_Signature_1 = "signature1"
    ESlot_Signature_2 = "signature2"
    ESlot_Signature_3 = "signature3"
    ESlot_Signature_4 = "signature4"

    @classmethod
    def _missing_(cls, new_value: str):
        new_value = new_value.lower()
        for member in cls:
            if new_value in [member.value.lower(), member.name.lower()]:
                return member
        warning(f"Unknown HeroItemType: {new_value}")
        return None

    def ability_index(self) -> int | None:
        return {
            HeroItemTypeV2.ESlot_Signature_1: 1,
            HeroItemTypeV2.ESlot_Signature_2: 2,
            HeroItemTypeV2.ESlot_Signature_3: 3,
            HeroItemTypeV2.ESlot_Signature_4: 4,
        }.get(self)


class ItemSlotTypeV2(StrEnum):
    EItemSlotType_WeaponMod = "weapon"
    EItemSlotType_Tech = "spirit"
    EItemSlotType_Armor = "vitality"

    @classmethod
    def _missing_(cls, new_value: str):
        new_value = new_value.lower()
        for member in cls:
            if new_value in [member.value.lower(), member.name.lower()]:
                return member
        raise ValueError(f"Unknown ItemSlotType: {new_value}")


class ItemTypeV2(StrEnum):
    WEAPON = "weapon"
    ABILITY = "ability"
    UPGRADE = "upgrade"
    TECH = "tech"
    ARMOR = "armor"

    @classmethod
    def _missing_(cls, value: str):
        value = value.lower()
        for member in cls:
            if value in [member.value.lower(), member.name.lower()]:
                return member
        hero_list = [
            "astro",
            "atlas",
            "bebop",
            "bomber",
            "cadence",
            "chrono",
            "dynamo",
            "fathom",
            "forge",
            "ghost",
            "gigawatt",
            "gunslinger",
            "haze",
            "hornet",
            "inferno",
            "kali",
            "kelvin",
            "krill",
            "lash",
            "magician",
            "mirage",
            "nano",
            "operative",
            "orion",
            "rutger",
            "shieldguy",
            "shiv",
            "slork",
            "synth",
            "tengu",
            "thumper",
            "tokamak",
            "trapper",
            "vandal",
            "viper",
            "viscous",
            "warden",
            "wraith",
            "wrecker",
            "yakuza",
            "yamato",
        ]
        if value.strip() in hero_list:
            return cls.ABILITY
        logging.warning(f"Unknown ItemType: {value}")
        return None
