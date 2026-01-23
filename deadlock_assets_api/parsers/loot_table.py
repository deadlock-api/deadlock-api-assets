from deadlock_assets_api.models.v2.loot_table import LootTableV2


def parse_loot_table(data: dict) -> LootTableV2:
    return LootTableV2(**data)
