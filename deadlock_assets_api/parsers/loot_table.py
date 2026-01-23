from deadlock_assets_api.models.v2.loot_table import LootTablesV2


def parse_loot_table(data: dict) -> LootTablesV2:
    return LootTablesV2(**data)
