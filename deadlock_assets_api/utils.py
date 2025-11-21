import json
import logging
import os
import re
from functools import lru_cache

import css_parser
from css_parser.css import CSSRuleList, CSSStyleRule
from pydantic import TypeAdapter, BaseModel

from deadlock_assets_api.models.languages import Language

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
    return re.sub(r"(?<!^)(?=[A-Z])", " ", pascal_string).lower().strip().replace("d p s", "DPS")


def pascal_case_to_snake_case(pascal_string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", pascal_string).lower().strip()


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
    LOGGER.debug(f"Reading {filepath}")
    with open(filepath) as f:
        return type_adapter.validate_json(f.read())


def read_parse_data_model[T: BaseModel](filepath: str, model: type[T]) -> T:
    LOGGER.debug(f"Reading {filepath}")
    with open(filepath) as f:
        return model.model_validate_json(f.read())


def validate_language(language: Language | None = None) -> Language:
    if language is None:
        language = Language.English
    return language


@lru_cache
def parse_css_rules(filename: str) -> CSSRuleList:
    return css_parser.parseFile(filename).cssRules


def parse_css_heroes_background(class_name: str) -> str | None:
    for rule in parse_css_rules("res//hero_background_default.css"):
        if not isinstance(rule, CSSStyleRule):
            continue
        css_class = next(
            (s for s in " ".join(rule.selectorText.split(".")).split(" ") if s == class_name),
            None,
        )
        if css_class is None:
            continue
        rule: CSSStyleRule = rule
        background_image = rule.style.getProperty("background-image")
        if background_image is None:
            continue
        background_image = background_image.value[4:-1]
        background_image = background_image.replace("_psd.vtex", ".psd")
        background_image = background_image.split("images/")[-1]
        return 'panorama:"file://{images}/' + background_image + '"'
    return None


def parse_css_heroes_names(class_name: str) -> str | None:
    for rule in parse_css_rules("res/citadel_popup_roster_select.css"):
        if not isinstance(rule, CSSStyleRule):
            continue
        css_class = next(
            (s for s in " ".join(rule.selectorText.split(".")).split(" ") if s == class_name),
            None,
        )
        if css_class is None:
            continue
        rule: CSSStyleRule = rule
        background_image = rule.style.getProperty("background-image")
        if background_image is None:
            continue
        background_image = background_image.value[4:-1]
        background_image = background_image.replace("_psd.vtex", ".psd")
        background_image = background_image.split("images/")[-1]
        return 'panorama:"file://{images}/' + background_image + '"'
    return None


def parse_css_ability_properties_icon(file: str, css_class_icon: str) -> str | None:
    for rule in parse_css_rules(file):
        if not isinstance(rule, CSSStyleRule):
            continue
        css_class = next(
            (
                s
                for s in " ".join(rule.selectorText.split(".")).split(" ")
                if s == f"prop_{css_class_icon}" or s == css_class_icon
            ),
            None,
        )
        if css_class is None:
            continue
        rule: CSSStyleRule = rule
        background_image = rule.style.getProperty("background-image")
        if background_image is None:
            continue
        background_image = background_image.value[4:-1]
        background_image = background_image.replace("_psd.vtex", ".psd")
        background_image = background_image.split("images/")[-1]
        return 'panorama:"file://{images}/' + background_image + '"'
    return None


def parse_css_ability_icon(class_name: str) -> str | None:
    for rule in parse_css_rules("res/ability_icons.css"):
        if not isinstance(rule, CSSStyleRule):
            continue
        css_class = next(
            (s for s in " ".join(rule.selectorText.split(".")).split(" ") if s == class_name),
            None,
        )
        if css_class is None:
            continue
        rule: CSSStyleRule = rule
        background_image = rule.style.getProperty("background-image")
        if background_image is None:
            continue
        background_image = background_image.value[4:-1]
        background_image = background_image.replace("_psd.vtex", ".psd")
        background_image = background_image.split("images/")[-1]
        return 'panorama:"file://{images}/' + background_image + '"'
    return None
