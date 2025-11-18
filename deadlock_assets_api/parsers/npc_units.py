import logging

from deadlock_assets_api.models.v2.npc_unit import NPCUnitV2

LOGGER = logging.getLogger(__name__)


def parse_npc_units_v2(data: dict) -> list[NPCUnitV2]:
    npc_dicts = {
        k: v
        for k, v in data.items()
        if "base" not in k and "dummy" not in k and isinstance(v, dict)
    }
    return [NPCUnitV2(class_name=k, **v) for k, v in npc_dicts.items()]
