import logging

from deadlock_assets_api.models.v2.misc import MiscV2

LOGGER = logging.getLogger(__name__)


def parse_misc_v2(data: dict) -> list[MiscV2]:
    misc_dicts = {
        k: v
        for k, v in data.items()
        if "base" not in k and "dummy" not in k and isinstance(v, dict)
    }
    return [MiscV2(class_name=k, **v) for k, v in misc_dicts.items()]
