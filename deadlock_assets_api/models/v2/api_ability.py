from typing import Literal

from pydantic import BaseModel, ConfigDict

from deadlock_assets_api.glob import VIDEO_BASE_URL
from deadlock_assets_api.models.v2.api_item_base import ItemBaseV2
from deadlock_assets_api.models.v2.enums import AbilityTypeV2
from deadlock_assets_api.models.v2.raw_ability import RawAbilityUpgradeV2, RawAbilityV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.v2_utils import replace_templates


def extract_video_url(v: str) -> str | None:
    if not v:
        return None
    return f"{VIDEO_BASE_URL}/{v.split('videos/')[-1]}"


class AbilityDescriptionV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    desc: str | None
    quip: str | None
    t1_desc: str | None
    t2_desc: str | None
    t3_desc: str | None
    active: str | None
    passive: str | None

    @classmethod
    def from_raw_ability(
        cls,
        raw_ability: RawAbilityV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> "AbilityDescriptionV2":
        return cls(
            desc=replace_templates(
                raw_ability,
                raw_heroes,
                localization,
                localization.get(f"{raw_ability.class_name}_desc"),
                None,
            ),
            quip=replace_templates(
                raw_ability,
                raw_heroes,
                localization,
                localization.get(f"{raw_ability.class_name}_quip"),
                None,
            ),
            t1_desc=replace_templates(
                raw_ability,
                raw_heroes,
                localization,
                localization.get(f"{raw_ability.class_name}_t1_desc"),
                1,
            ),
            t2_desc=replace_templates(
                raw_ability,
                raw_heroes,
                localization,
                localization.get(f"{raw_ability.class_name}_t2_desc"),
                2,
            ),
            t3_desc=replace_templates(
                raw_ability,
                raw_heroes,
                localization,
                localization.get(f"{raw_ability.class_name}_t3_desc"),
                3,
            ),
            active=replace_templates(
                raw_ability,
                raw_heroes,
                localization,
                localization.get(f"{raw_ability.class_name}_active_desc")
                or localization.get(f"{raw_ability.class_name}_active")
                or localization.get(f"{raw_ability.class_name}_active1")
                or localization.get(f"{raw_ability.class_name}_active2"),
            ),
            passive=replace_templates(
                raw_ability,
                raw_heroes,
                localization,
                localization.get(f"{raw_ability.class_name}_passive_desc")
                or localization.get(f"{raw_ability.class_name}_passive")
                or localization.get(f"{raw_ability.class_name}_passive1")
                or localization.get(f"{raw_ability.class_name}_passive2"),
            ),
        )


class AbilityVideosV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    webm: str | None
    mp4: str | None

    @classmethod
    def from_raw_video(cls, raw_video: str) -> "AbilityVideosV2":
        webm = extract_video_url(raw_video)
        return cls(
            webm=webm,
            mp4=webm.replace(".webm", "_h264.mp4") if webm else None,
        )


class AbilityV2(ItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    type: Literal["ability"] = "ability"
    behaviours: list[str] | None
    description: AbilityDescriptionV2
    upgrades: list[RawAbilityUpgradeV2] | None
    ability_type: AbilityTypeV2 | None
    boss_damage_scale: float | None
    dependant_abilities: list[str] | None
    videos: AbilityVideosV2 | None

    @classmethod
    def from_raw_item(
        cls,
        raw_ability: RawAbilityV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> "AbilityV2":
        raw_model = super().from_raw_item(raw_ability, raw_heroes, localization)
        raw_model["behaviours"] = (
            [b.strip() for b in raw_ability.behaviour_bits.split("|")]
            if raw_ability.behaviour_bits
            else None
        )
        raw_model["description"] = AbilityDescriptionV2.from_raw_ability(
            raw_ability, raw_heroes, localization
        )
        raw_model["videos"] = (
            AbilityVideosV2.from_raw_video(raw_ability.video) if raw_ability.video else None
        )
        del raw_model["video"]
        return cls(**raw_model)
