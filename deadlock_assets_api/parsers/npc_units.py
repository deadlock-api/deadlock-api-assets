import logging

from deadlock_assets_api.models.v2.npc_unit import NPCUnitV2

LOGGER = logging.getLogger(__name__)


def parse_npc_units_v2(data: dict) -> list[NPCUnitV2]:
    return [NPCUnitV2(class_name=k, **v) for k, v in data.items() if isinstance(v, dict)]
