import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor

import vdf
from pydantic import BaseModel

from deadlock_assets_api.kv3parser import KV3Parser
from deadlock_assets_api.parsers.generic_data import parse_generic_data
from deadlock_assets_api.parsers.loot_table import parse_loot_table
from deadlock_assets_api.parsers.heroes import parse_heroes_v2
from deadlock_assets_api.parsers.items import parse_items_v2
from deadlock_assets_api.parsers.accolades import parse_accolades_v2
from deadlock_assets_api.parsers.misc import parse_misc_v2
from deadlock_assets_api.parsers.npc_units import parse_npc_units_v2


def get_version_id():
    with open("res/steam.inf") as f:
        data = [line.split("=") for line in f.read().splitlines()]
    return dict(data)["ClientVersion"]


VERSION_ID = get_version_id()
os.makedirs(f"res/builds/{VERSION_ID}/v2/", exist_ok=True)
VDATA_FILES = (
    [
        (
            parse_generic_data,
            "vdata/generic_data.vdata",
            f"res/builds/{VERSION_ID}/v2/generic_data.json",
            True,
        ),
        (
            parse_loot_table,
            "vdata/loot_table.vdata",
            f"res/builds/{VERSION_ID}/v2/loot_table.json",
            True,
        ),
        (
            parse_heroes_v2,
            "vdata/heroes.vdata",
            f"res/builds/{VERSION_ID}/v2/raw_heroes.json",
            False,
        ),
        (
            parse_items_v2,
            "vdata/abilities.vdata",
            f"res/builds/{VERSION_ID}/v2/raw_items.json",
            False,
        ),
        (
            parse_accolades_v2,
            "vdata/accolades.vdata",
            f"res/builds/{VERSION_ID}/v2/raw_accolades.json",
            False,
        ),
        (
            parse_npc_units_v2,
            "vdata/npc_units.vdata",
            f"res/builds/{VERSION_ID}/v2/npc_units.json",
            False,
        ),
        (
            parse_misc_v2,
            "vdata/misc.vdata",
            f"res/builds/{VERSION_ID}/v2/misc_entities.json",
            False,
        ),
    ]
    # + [
    #     (
    #         parse_heroes_v2,
    #         "vdata/heroes.vdata",
    #         f"res/builds/{build_id}/v2/raw_heroes.json",
    #         False,
    #     )
    #     for build_id in os.listdir("res/builds")
    #     if build_id != get_version_id()
    # ]
    # + [
    #     (
    #         parse_items_v2,
    #         "vdata/abilities.vdata",
    #         f"res/builds/{build_id}/v2/raw_items.json",
    #         False,
    #     )
    #     for build_id in os.listdir("res/builds")
    #     if build_id != get_version_id()
    # ]
)


def parse_vdata():
    def parse(parse_func, file_path, out_path, create_raw):
        vdata_out_path = f"{os.path.dirname(out_path)}/{os.path.basename(file_path)}"
        os.makedirs(os.path.dirname(vdata_out_path), exist_ok=True)
        if not os.path.exists(vdata_out_path) or create_raw:
            shutil.copy(file_path, vdata_out_path)

        with open(vdata_out_path) as f:
            data = KV3Parser(f.read()).parse()

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if create_raw:
            with open(file_path) as f:
                raw_data = KV3Parser(f.read()).parse()
            with open(f"{os.path.dirname(out_path)}/raw_{os.path.basename(out_path)}", "w") as f:
                json.dump(raw_data, f, indent=4)

        data = parse_func(data)
        if isinstance(data, list):
            data = [
                (d.model_dump(exclude={"name"}) if isinstance(d, BaseModel) else d.__dict__)
                for d in data
            ]
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude={"name"})
        with open(out_path, "w") as f:
            json.dump(data, f, indent=4)

    with ThreadPoolExecutor(24) as executor:
        for args in VDATA_FILES:
            executor.submit(parse, *args)


def parse_localization():
    for root, _, files in os.walk("localization"):
        for file in files:
            if not file.endswith(".txt"):
                continue
            file = os.path.join(root, file)
            with open(file, encoding="utf8", errors="ignore") as f:
                data = vdf.loads(f.read().replace("\ufeff", ""))
            for out_file in [
                os.path.join("res", file.replace(".txt", ".json")),
                os.path.join(
                    "res",
                    "builds",
                    VERSION_ID,
                    "v2",
                    file.replace(".txt", ".json"),
                ),
            ]:
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                with open(out_file, "w") as f:
                    json.dump(data, f, indent=4)


if __name__ == "__main__":
    shutil.copyfile(
        "res/ability_icons.css",
        f"res/builds/{VERSION_ID}/v2/ability_icons.css",
    )
    shutil.copyfile(
        "res/ability_property_icons.css",
        f"res/builds/{VERSION_ID}/v2/ability_property_icons.css",
    )
    parse_vdata()
    shutil.copyfile(
        f"res/builds/{VERSION_ID}/v2/raw_items.json",
        "res/raw_items.json",
    )
    shutil.copyfile(
        f"res/builds/{VERSION_ID}/v2/raw_heroes.json",
        "res/raw_heroes.json",
    )
    shutil.copyfile(
        f"res/builds/{VERSION_ID}/v2/raw_accolades.json",
        "res/raw_accolades.json",
    )
    shutil.copyfile(
        f"res/builds/{VERSION_ID}/v2/generic_data.json",
        "res/generic_data.json",
    )
    shutil.copyfile(
        f"res/builds/{VERSION_ID}/v2/loot_table.json",
        "res/loot_table.json",
    )
    shutil.copyfile(
        f"res/builds/{VERSION_ID}/v2/npc_units.json",
        "res/npc_units.json",
    )
    shutil.copyfile(
        f"res/builds/{VERSION_ID}/v2/misc_entities.json",
        "res/misc_entities.json",
    )
    parse_localization()
