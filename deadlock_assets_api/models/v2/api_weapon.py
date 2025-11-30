from typing import Literal

from pydantic import ConfigDict, computed_field

from deadlock_assets_api.models.v2.api_item_base import ItemBaseV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_weapon import RawWeaponInfoV2, RawWeaponV2


class WeaponInfoV2(RawWeaponInfoV2):
    model_config = ConfigDict(populate_by_name=True)

    @computed_field(description="Calculates the shots per second of the weapon")
    @property
    def shots_per_second(self) -> float | None:
        if self.cycle_time is None:
            return None
        intra_burst_cycle_time = self.intra_burst_cycle_time or 0
        burst_shot_count = self.burst_shot_count or 1
        adjusted_cycle_time = (burst_shot_count * intra_burst_cycle_time) + self.cycle_time
        return burst_shot_count / adjusted_cycle_time if adjusted_cycle_time else 0

    @computed_field(
        description="Calculates the shots per second of the weapon adjusted for reload time"
    )
    @property
    def shots_per_second_with_reload(self) -> float | None:
        if self.cycle_time is None or self.reload_duration is None or self.clip_size is None:
            return None
        intra_burst_cycle_time = self.intra_burst_cycle_time or 0
        burst_shot_count = self.burst_shot_count or 1
        recoil_shot_index_recovery_time_factor = self.recoil_shot_index_recovery_time_factor or 0
        adjusted_cycle_time = (burst_shot_count * intra_burst_cycle_time) + self.cycle_time
        total_time_per_clip = (
            (self.clip_size / burst_shot_count) * adjusted_cycle_time
            + recoil_shot_index_recovery_time_factor
            + self.reload_duration
        )
        return self.clip_size / total_time_per_clip if total_time_per_clip else 0

    @computed_field(
        description="Calculates the bullets per second of the weapon, by multiplying shots per second by bullets per shot."
    )
    @property
    def bullets_per_second(self) -> float | None:
        return (
            self.shots_per_second * self.bullets if self.shots_per_second and self.bullets else None
        )

    @computed_field(
        description="Calculates the bullets per second of the weapon adjusted for reload time."
    )
    @property
    def bullets_per_second_with_reload(self) -> float | None:
        return (
            self.shots_per_second_with_reload * self.bullets
            if self.shots_per_second_with_reload and self.bullets
            else None
        )

    @computed_field(
        description="Calculates the damage per second of the weapon, by multiplying bullets per second by bullet damage."
    )
    @property
    def damage_per_second(self) -> float | None:
        return (
            self.bullets_per_second * self.bullet_damage
            if self.bullets_per_second and self.bullet_damage
            else None
        )

    @computed_field(
        description="Calculates the damage per second of the weapon adjusted for reload time."
    )
    @property
    def damage_per_second_with_reload(self) -> float | None:
        return (
            self.bullets_per_second_with_reload * self.bullet_damage
            if self.bullets_per_second_with_reload and self.bullet_damage
            else None
        )

    @computed_field(
        description="Calculates the damage per shot of the weapon, by multiplying bullets per shot by bullet damage."
    )
    @property
    def damage_per_shot(self) -> float | None:
        return self.bullets * self.bullet_damage if self.bullets and self.bullet_damage else None

    @computed_field(
        description="Calculates the damage per magazine of the weapon, by multiplying clip size by damage per shot."
    )
    @property
    def damage_per_magazine(self) -> float | None:
        return (
            self.clip_size * self.damage_per_shot
            if self.clip_size and self.clip_size > 0 and self.damage_per_shot
            else None
        )


class WeaponV2(ItemBaseV2):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["weapon"] = "weapon"

    weapon_info: WeaponInfoV2 | None = None

    @classmethod
    def from_raw_item(
        cls,
        raw_weapon: RawWeaponV2,
        raw_heroes: list[RawHeroV2],
        localization: dict[str, str],
    ) -> WeaponV2:
        raw_model = super().from_raw_item(raw_weapon, raw_heroes, localization)
        raw_model["name"] = localization.get(
            raw_model["class_name"],
            localization.get(
                raw_model["class_name"].replace("citadel_weapon", "citadel_weapon_hero"),
                localization.get(
                    raw_model["class_name"]
                    .replace("citadel_weapon", "citadel_weapon_hero")
                    .replace("_alt", "_set"),
                    localization.get(
                        raw_model["class_name"]
                        .replace("citadel_weapon", "citadel_weapon_hero")
                        .replace("_alt", "_set")
                        .replace("set2", "set"),
                        raw_model["class_name"],
                    ).strip(),
                ).strip(),
            ).strip(),
        ).strip()
        return cls(**raw_model)
