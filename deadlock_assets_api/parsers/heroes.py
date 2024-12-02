from deadlock_assets_api.models.v1.hero import HeroV1
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2


def parse_heroes(data: dict) -> list[HeroV1]:
    hero_dicts = {
        k.removeprefix("hero_"): v
        for k, v in data.items()
        if k.startswith("hero_") and "base" not in k and "generic" not in k and "dummy" not in k
    }
    return [HeroV1(class_name=name, **v) for name, v in hero_dicts.items()]


def parse_heroes_v2(data: dict) -> list[RawHeroV2]:
    hero_dicts = {
        k: v
        for k, v in data.items()
        if k.startswith("hero_") and "base" not in k and "generic" not in k and "dummy" not in k
    }
    return [RawHeroV2(class_name=name, **v) for name, v in hero_dicts.items()]
