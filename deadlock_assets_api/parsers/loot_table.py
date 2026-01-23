from deadlock_assets_api.models.v2.loot_table import LootTablesV2


def parse_loot_table(data: dict) -> LootTablesV2:
    return LootTablesV2(
        **{k: v for k, v in data.items() if k != "all_items" and not k.startswith("generic_")}
    )
