from pydantic import BaseModel, ConfigDict, Field

from deadlock_assets_api.models.v2.enums import GameMode
from deadlock_assets_api.models.v2.raw_accolade import ThresholdType, TrackedStatName, RawAccoladeV2


class AccoladeV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str

    id: int
    tracked_stat_name: TrackedStatName
    flavor_name: str
    description: str
    threshold_type: ThresholdType
    enabled_game_modes: list[GameMode] | None = Field(None)

    @classmethod
    def from_raw_accolade(
        cls, raw_accolade: RawAccoladeV2, localization: dict[str, str]
    ) -> AccoladeV2:
        raw_model = raw_accolade.model_dump()
        raw_model["flavor_name"] = localization.get(
            raw_accolade.flavor_name.strip("#"), raw_accolade.flavor_name
        )
        raw_model["description"] = localization.get(
            raw_accolade.description.strip("#"), raw_accolade.description
        )
        return cls(**raw_model)
