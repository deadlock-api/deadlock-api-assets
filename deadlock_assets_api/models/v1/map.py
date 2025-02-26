from functools import lru_cache

import css_parser
from css_parser.css import CSSStyleRule
from pydantic import BaseModel, ConfigDict, Field, computed_field

from deadlock_assets_api.glob import IMAGE_BASE_URL
from deadlock_assets_api.models.map_data import (
    LANE_COLORS,
    LANE_ORIGINS,
    LANES,
    MAP_RADIUS,
)

TOWER_IDS = {
    **{f"#Team{team_id + 1}Core": f"team{team_id}_core" for team_id in range(2)},
    **{f"#Team{team_id + 1}Titan": f"team{team_id}_titan" for team_id in range(2)},
    **{
        f".ThreeLane #Team{team_id + 1}Tier{tier + 1}_{i}": f"team{team_id}_tier{tier + 1}_{i}"
        for team_id in range(2)
        for tier in range(2)
        for i in range(1, 5)
    },
}


class ObjectivePositionV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    left_relative: float = Field(
        ...,
        description="The relative margin left of the map image.",
    )
    top_relative: float = Field(
        ...,
        description="The relative margin top of the map image.",
    )


class ObjectivePositionsV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    team0_core: ObjectivePositionV1
    team1_core: ObjectivePositionV1
    team0_titan: ObjectivePositionV1
    team1_titan: ObjectivePositionV1
    team0_tier2_1: ObjectivePositionV1
    team0_tier2_2: ObjectivePositionV1 | None = Field(None)
    team0_tier2_3: ObjectivePositionV1
    team0_tier2_4: ObjectivePositionV1
    team1_tier2_1: ObjectivePositionV1
    team1_tier2_2: ObjectivePositionV1 | None = Field(None)
    team1_tier2_3: ObjectivePositionV1
    team1_tier2_4: ObjectivePositionV1
    team0_tier1_1: ObjectivePositionV1
    team0_tier1_2: ObjectivePositionV1 | None = Field(None)
    team0_tier1_3: ObjectivePositionV1
    team0_tier1_4: ObjectivePositionV1
    team1_tier1_1: ObjectivePositionV1
    team1_tier1_2: ObjectivePositionV1 | None = Field(None)
    team1_tier1_3: ObjectivePositionV1
    team1_tier1_4: ObjectivePositionV1


class MapImagesV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    background: str = Field(
        ...,
        description="The background image of the map.",
    )
    frame: str = Field(
        ...,
        description="The frame image of the map.",
    )
    mid: str = Field(
        ...,
        description="The mid image of the map.",
    )


class ZiplanePathV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    origin: tuple[float, float, float] = Field(..., description="The origin of the path.")

    color: str = Field(..., description="The color of the path.")

    P0_points: list[tuple[float, float, float]] = Field(
        ...,
        description="The P0 points of the path.",
    )
    P1_points: list[tuple[float, float, float]] = Field(
        ...,
        description="The P1 points of the path.",
    )
    P2_points: list[tuple[float, float, float]] = Field(
        ...,
        description="The P2 points of the path.",
    )

    @classmethod
    def from_pathnodes(cls, pathnodes: list[list[float]], **kwargs) -> "ZiplanePathV1":
        return cls(
            P0_points=[(n[0], n[1], n[2]) for n in pathnodes],
            P1_points=[(n[3], n[4], n[5]) for n in pathnodes],
            P2_points=[(n[6], n[7], n[8]) for n in pathnodes],
            **kwargs,
        )


class MapV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    radius: int = Field(
        MAP_RADIUS,
        description="The radius of the map.",
    )

    images: MapImagesV1 = Field(
        ...,
        description="The images of the map.",
    )

    @computed_field
    @property
    def objective_positions(self) -> ObjectivePositionsV1:
        objectives = load_objectives()
        print(objectives)

        def parse_percentage(value: str) -> float:
            if value.endswith("%"):
                return float(value[:-1]) / 100
            return float(value)

        return ObjectivePositionsV1.model_validate(
            {
                TOWER_IDS[rule.selectorText]: ObjectivePositionV1(
                    left_relative=parse_percentage(rule.style.marginLeft),
                    top_relative=parse_percentage(rule.style.marginTop),
                )
                for rule in objectives.cssRules
                if isinstance(rule, CSSStyleRule) and rule.selectorText in TOWER_IDS
            }
        )

    @computed_field(
        description="The ziplane paths of the map. Each path is a list of P0, P1, and P2 points, describing the cubic spline."
    )
    @property
    def zipline_paths(self) -> list[ZiplanePathV1]:
        return [
            ZiplanePathV1.from_pathnodes(lane, color=color, origin=origin)
            for lane, color, origin in zip(LANES, LANE_COLORS, LANE_ORIGINS)
        ]

    @classmethod
    def get_default(cls) -> "MapV1":
        return cls(
            images=MapImagesV1(
                background=f"{IMAGE_BASE_URL}/maps/minimap_bg.png",
                frame=f"{IMAGE_BASE_URL}/maps/minimap_frame.png",
                mid=f"{IMAGE_BASE_URL}/maps/minimap_mid.png",
            ),
        )


@lru_cache
def load_objectives():
    return css_parser.parseFile("res/objectives_map.css")
