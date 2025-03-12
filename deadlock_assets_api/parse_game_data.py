import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor

import vdf
from kv3parser import KV3Parser
from pydantic import BaseModel

from deadlock_assets_api.parsers.generic_data import parse_generic_data
from deadlock_assets_api.parsers.heroes import parse_heroes, parse_heroes_v2
from deadlock_assets_api.parsers.items import parse_items, parse_items_v2


def get_version_id():
    with open("res/steam.inf") as f:
        data = [line.split("=") for line in f.read().splitlines()]
    return dict(data)["ClientVersion"]


VDATA_FILES = (
    [
        (parse_generic_data, "vdata/generic_data.vdata", "res/generic_data.json", True),
        (parse_heroes, "vdata/heroes.vdata", "res/heroes.json", True),
        (
            parse_heroes_v2,
            "vdata/heroes.vdata",
            f"res/builds/{get_version_id()}/v2/raw_heroes.json",
            False,
        ),
        (parse_items, "vdata/abilities.vdata", "res/items.json", True),
        (
            parse_items_v2,
            "vdata/abilities.vdata",
            f"res/builds/{get_version_id()}/v2/raw_items.json",
            False,
        ),
    ]
    + [
        (
            parse_heroes_v2,
            "vdata/heroes.vdata",
            f"res/builds/{build_id}/v2/raw_heroes.json",
            False,
        )
        for build_id in os.listdir("res/builds")
        if build_id != get_version_id()
    ]
    + [
        (
            parse_items_v2,
            "vdata/abilities.vdata",
            f"res/builds/{build_id}/v2/raw_items.json",
            False,
        )
        for build_id in os.listdir("res/builds")
        if build_id != get_version_id()
    ]
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
                    get_version_id(),
                    "v2",
                    file.replace(".txt", ".json"),
                ),
            ]:
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                with open(out_file, "w") as f:
                    json.dump(data, f, indent=4)


if __name__ == "__main__":
    os.makedirs(f"res/builds/{get_version_id()}/v2/", exist_ok=True)
    shutil.copyfile(
        "res/ability_icons.css",
        f"res/builds/{get_version_id()}/v2/ability_icons.css",
    )
    shutil.copyfile(
        "res/ability_properties.css",
        f"res/builds/{get_version_id()}/v2/ability_properties.css",
    )
    parse_vdata()
    parse_localization()
