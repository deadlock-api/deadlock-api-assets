from typing import Annotated

from murmurhash2 import murmurhash2
from pydantic import BaseModel, ConfigDict, computed_field, WithJsonSchema

from deadlock_assets_api.glob import SVGS_BASE_URL


class BuildTagV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_name: str
    label: str

    @computed_field
    @property
    def id(self) -> Annotated[int, WithJsonSchema({"format": "int64", "type": "integer"})]:
        return murmurhash2(self.class_name.encode(), 0x31415926)

    @computed_field
    @property
    def icon(self) -> str:
        return f"{SVGS_BASE_URL}/{self.class_name}.svg"

    @classmethod
    def from_localization(cls, localization: dict[str, str]) -> list[BuildTagV2]:
        return [
            cls(class_name=k, label=v)
            for k, v in localization.items()
            if k.startswith("citadel_build_tag_") and k != "citadel_build_tag_label"
        ]
