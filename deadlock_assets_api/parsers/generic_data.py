from deadlock_assets_api.models.v2.generic_data import GenericDataV2


def parse_generic_data(data: dict) -> GenericDataV2:
    return GenericDataV2(**data)
