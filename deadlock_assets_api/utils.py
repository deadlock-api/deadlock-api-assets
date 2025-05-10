import json
import logging
import os
import re
from enum import Enum
from typing import Type

from fastapi import HTTPException
from py_cachify import cached, lock
from pydantic import TypeAdapter, BaseModel

from deadlock_assets_api.models.languages import Language

with open("deploy/client_versions.json") as f:
    ALL_CLIENT_VERSIONS = sorted(json.load(f), reverse=True)
VALID_CLIENT_VERSIONS = Enum(
    "ValidClientVersions", {str(b): int(b) for b in ALL_CLIENT_VERSIONS}, type=int
)

LOGGER = logging.getLogger(__name__)


def get_translation(key: str, language: Language, return_none: bool = False) -> str:
    for file in [
        f"res/localization/citadel_heroes_{language.value}.json"
        f"res/localization/citadel_gc_{language.value}.json",
        "res/localization/citadel_heroes_english.json",
        "res/localization/citadel_gc_english.json",
    ]:
        if not os.path.exists(file):
            continue
        with open(file) as f:
            language_data = json.load(f)["lang"]["Tokens"]
        name = language_data.get(key, None)
        if name is None:
            continue
        return name
    return key if not return_none else None


def prettify_snake_case(snake_str: str) -> str:
    return " ".join(
        re.sub(r"([a-zA-Z])(\d)", r"\1 \2", w.capitalize()) for w in snake_str.split("_")
    )


def prettify_pascal_case(pascal_string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", pascal_string).lower().strip()


def is_float(element: any) -> bool:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


def is_int(element: any) -> bool:
    if element is None:
        return False
    try:
        int(element)
        return True
    except ValueError:
        return False


def camel_to_snake(s):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")


def strip_prefix(string: str, prefix: str) -> str:
    prefix_index = string.find(prefix)
    if prefix_index != -1:
        return string[prefix_index + len(prefix) :]
    return string


def read_parse_data_ta[T](filepath: str, type_adapter: TypeAdapter[T]) -> T:
    with lock(key=f"ta-{filepath}", nowait=False):
        return _read_parse_data_ta(filepath, type_adapter)


@cached(key="{filepath}", ttl=60 * 60)
def _read_parse_data_ta[T](filepath: str, type_adapter: TypeAdapter[T]) -> T:
    LOGGER.debug(f"Reading {filepath}")
    with open(filepath) as f:
        return type_adapter.validate_json(f.read())


def read_parse_data_model[T: BaseModel](filepath: str, model: Type[T]) -> T:
    with lock(key=f"model-{filepath}", nowait=False):
        return _read_parse_data_model(filepath, model)


@cached(key="{filepath}", ttl=60 * 60)
def _read_parse_data_model[T: BaseModel](filepath: str, model: Type[T]) -> T:
    LOGGER.debug(f"Reading {filepath}")
    with open(filepath) as f:
        return model.model_validate_json(f.read())


def validate_client_version(client_version: VALID_CLIENT_VERSIONS | None = None) -> int:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(max(ALL_CLIENT_VERSIONS))
    if client_version not in ALL_CLIENT_VERSIONS:
        raise HTTPException(status_code=404, detail="Client Version not found")
    return client_version.value


def validate_language(language: Language | None = None) -> Language:
    if language is None:
        language = Language.English
    return language
