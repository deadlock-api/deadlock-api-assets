from deadlock_assets_api.models.v2.raw_accolade import RawAccoladeV2


def parse_accolades_v2(data: dict[str, dict]) -> list[RawAccoladeV2]:
    return [
        RawAccoladeV2(class_name=class_name, **v)
        for class_name, v in data.items()
        if class_name != "generic_data_type" and not class_name.startswith("_")
    ]
