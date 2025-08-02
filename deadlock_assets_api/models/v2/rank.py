import os

from pydantic import BaseModel, ConfigDict, Field, computed_field

from deadlock_assets_api.glob import IMAGE_BASE_URL

RANK_COLORS = [
    "#333333",
    "#6A3E1E",
    "#882355",
    "#5C6DAB",
    "#719C47",
    "#DDA326",
    "#EE4F57",
    "#B47FEB",
    "#955138",
    "#7C7C7C",
    "#C39751",
    "#5CE9A9",
]


class RankImagesV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    large: str | None = Field(None)
    large_webp: str | None = Field(None)
    large_subrank1: str | None = Field(None)
    large_subrank1_webp: str | None = Field(None)
    large_subrank2: str | None = Field(None)
    large_subrank2_webp: str | None = Field(None)
    large_subrank3: str | None = Field(None)
    large_subrank3_webp: str | None = Field(None)
    large_subrank4: str | None = Field(None)
    large_subrank4_webp: str | None = Field(None)
    large_subrank5: str | None = Field(None)
    large_subrank5_webp: str | None = Field(None)
    large_subrank6: str | None = Field(None)
    large_subrank6_webp: str | None = Field(None)
    small: str | None = Field(None)
    small_webp: str | None = Field(None)
    small_subrank1: str | None = Field(None)
    small_subrank1_webp: str | None = Field(None)
    small_subrank2: str | None = Field(None)
    small_subrank2_webp: str | None = Field(None)
    small_subrank3: str | None = Field(None)
    small_subrank3_webp: str | None = Field(None)
    small_subrank4: str | None = Field(None)
    small_subrank4_webp: str | None = Field(None)
    small_subrank5: str | None = Field(None)
    small_subrank5_webp: str | None = Field(None)
    small_subrank6: str | None = Field(None)
    small_subrank6_webp: str | None = Field(None)

    @classmethod
    def from_tier(cls, tier: int) -> "RankImagesV2":
        image_folder = f"ranks/rank{tier}"
        images = {
            f.replace("badge_", "")
            .replace("_psd.png", "")
            .replace(".png", "")
            .replace(".webp", "_webp")
            .replace("_psd.webp", "_webp")
            .replace("lg", "large")
            .replace("sm", "small"): f"{IMAGE_BASE_URL}/{image_folder}/{f}"
            for f in os.listdir(f"images/{image_folder}")
        }
        return cls(**images)


class RankV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tier: int
    name: str
    images: RankImagesV2

    @computed_field
    @property
    def color(self) -> str:
        return RANK_COLORS[self.tier]

    @classmethod
    def from_tier(cls, tier: int, localization: dict[str, str]) -> "RankV2":
        return cls(
            tier=tier,
            name=localization[f"Citadel_ranks_rank{tier}"].strip(),
            images=RankImagesV2.from_tier(tier),
        )
