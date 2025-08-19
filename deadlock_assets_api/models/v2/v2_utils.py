import logging
import os
import re
from functools import lru_cache

from css_parser.css import CSSStyleRule

from deadlock_assets_api.glob import SVGS_BASE_URL
from deadlock_assets_api.models.v2.api_item_base import parse_img_path
from deadlock_assets_api.models.v2.raw_ability import RawAbilityV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_item_base import RawItemBaseV2
from deadlock_assets_api.utils import (
    prettify_pascal_case,
    pascal_case_to_snake_case,
    parse_css_rules,
)

LOGGER = logging.getLogger(__name__)


@lru_cache
def load_base_css():
    css_rules = parse_css_rules("res/citadel_base_styles.css")
    color_definitions = {}
    for rule in css_rules:
        if not rule.cssText or not rule.cssText.startswith("@define"):
            continue
        color_definition = rule.cssText.strip("@define").strip(";").split(":")
        if len(color_definition) == 2:
            name, value = color_definition
            color_definitions[name.strip()] = value.strip()
    return css_rules, color_definitions


@lru_cache
def parse_css_base_styles(css_class_selector: str) -> (str | None, str | None):
    css_rules, color_definitions = load_base_css()
    for rule in css_rules:
        if not isinstance(rule, CSSStyleRule):
            continue
        selector = rule.selectorText.strip().replace("\n", "")
        if css_class_selector == selector or any(
            s.lower().strip() == css_class_selector.lower() for s in selector.split(",")
        ):
            rule: CSSStyleRule = rule
            background_image = rule.style.getProperty("background-image")
            if background_image is None:
                continue
            background_image = background_image.value[4:-1]
            background_image = (
                background_image.replace("_psd.vtex", ".psd")
                .replace("_png.vtex", ".png")
                .replace(".vsvg", ".svg")
            )
            background_image = background_image.split("panorama/")[-1]

            wash_color = rule.style.getProperty("wash-color")
            if wash_color:
                wash_color = color_definitions.get(wash_color.value, wash_color.value)
            return background_image, wash_color
    return None, None


def add_fill_to_svg(svg: str, fill: str) -> str:
    fill = fill or "white"
    if not svg:
        return svg
    if "fill" in svg:
        return re.sub(r'fill="[^"]+"', rf'fill="{fill}"', svg, flags=re.DOTALL)
    else:
        return svg.replace("<svg", f'<svg fill="{fill}"')


KEYBIND_SVGS = {
    "Attack": "mouse1.svg",
    "ADS": "mouse2.svg",
    "AltCast": "mouse3.svg",
    "SpectateFlyUp": "mouse4.svg",
    "SpectateFlyDown": "mouse5.svg",
}


def replace_templates(
    raw_item: RawItemBaseV2,
    raw_heroes: list[RawHeroV2],
    localization,
    input_str: str | None,
    tier: int | None = None,
) -> str | None:
    if not input_str:
        return None

    def replacer(match):
        variable = match.group(1)

        if variable.startswith("citadel_keybind"):
            key = variable.split(":")[-1].strip("'")
            if key in KEYBIND_SVGS:
                svg = KEYBIND_SVGS[key]
                if os.path.exists(f"svgs/{svg}"):
                    with open(f"svgs/{svg}", "r") as f:
                        return f.read()
            res = localization.get(
                "citadel_keybind_" + pascal_case_to_snake_case(key).lower(),
                prettify_pascal_case(key),
            ).strip()
            if key == "MoveForward" and res.lower() == "move forward":
                return " [W] "
            if key == "MoveDown" and res.lower() == "move down":
                return " [S] "
            return " " + res + " "

        if variable.startswith("citadel_inline_attribute"):
            css_class = variable.split(":")[-1].strip("'")
            localization_key = f"InlineAttribute_{css_class}"
            label = localization.get(localization_key, prettify_pascal_case(css_class))
            background_image, wash_color = parse_css_base_styles(
                f".InlineAttributeIcon.{css_class}"
            )
            background_image = parse_img_path(background_image)
            if wash_color:
                if background_image.endswith(".svg"):
                    background_image_path = "svgs" + background_image.replace(SVGS_BASE_URL, "")
                    if os.path.exists(background_image_path):
                        with open(background_image_path, "r") as f:
                            img_tag = add_fill_to_svg(f.read(), wash_color)
                    else:
                        img_tag = f'<img src="{background_image}" class="inline-attribute {css_class}" alt="{label}"/>'
                else:
                    img_tag = f'<img src="{background_image}" class="inline-attribute {css_class}" alt="{label}"/>'
                label_tag = f'<span class="inline-attribute-label {css_class}" style="color: {wash_color};">{label}</span>'
            else:
                if background_image.endswith(".svg"):
                    background_image_path = "svgs" + background_image.replace(SVGS_BASE_URL, "")
                    if os.path.exists(background_image_path):
                        with open(background_image_path, "r") as f:
                            img_tag = add_fill_to_svg(f.read(), wash_color)
                    else:
                        img_tag = f'<object data="{background_image}" class="inline-attribute {css_class}" alt="{label}"/>'
                else:
                    img_tag = f'<img src="{background_image}" class="inline-attribute {css_class}" alt="{label}"/>'
                label_tag = f'<span class="inline-attribute-label {css_class}">{label}</span>'
            if css_class.lower().endswith("icon"):
                return img_tag
            else:
                return img_tag + label_tag

        replaced = None
        if isinstance(raw_item, RawAbilityV2):
            variable = variable.replace("_scale", "")
            property = next(
                (
                    k
                    for k, v in raw_item.properties.items()
                    if v.loc_token_override and v.loc_token_override == variable or k == variable
                ),
                "",
            )
            replaced = next(
                (
                    p.bonus
                    for i in raw_item.upgrades
                    for p in i.property_upgrades
                    if p.name.lower() == variable.lower() or p.name.lower() == property.lower()
                ),
                None,
            )
        if replaced is None:
            replaced = raw_item.properties.get(variable)
            if replaced is None:
                replaced = next(
                    (
                        v
                        for k, v in raw_item.properties.items()
                        if v.loc_token_override and v.loc_token_override == variable
                    ),
                    None,
                )
            if replaced is not None:
                replaced = replaced.value
        if (
            isinstance(raw_item, RawAbilityV2)
            and tier is not None
            and len(raw_item.upgrades) >= tier
        ):
            replaced = next(
                (
                    i.bonus.rstrip("m") if isinstance(i.bonus, str) else i.bonus
                    for i in raw_item.upgrades[tier - 1].property_upgrades
                    if i.name.lower() == variable.lower()
                ),
                replaced,
            )
        if replaced is None:
            if variable == "iv_attack":
                replaced = "LMC"
            elif variable == "iv_attack2":
                replaced = "RMC"
            elif variable == "key_alt_cast":
                replaced = "M3"
            elif variable == "key_reload":
                replaced = "R"
            elif variable == "ability_key":
                hero_items = next(
                    h.items for h in raw_heroes if raw_item.class_name in h.items.values()
                )
                if hero_items is not None:
                    ability_key = next(
                        (
                            k.ability_index()
                            for k, v in hero_items.items()
                            if v == raw_item.class_name
                        ),
                        None,
                    )
                    replaced = ability_key
            elif variable.startswith("in_ability"):
                index = int(variable[-1])
                replaced = localization.get(f"citadel_keybind_ability{index}")
            elif variable == "hero_name":
                replaced = next(
                    (
                        (
                            localization.get(
                                f"{h.class_name}:n",
                                localization.get(
                                    h.class_name,
                                    localization.get(f"Steam_RP_{h.class_name}", h.class_name),
                                ),
                            )
                            .strip()
                            .replace("#|f|#", "")
                            .replace("#|m|#", "")
                        )
                        for h in raw_heroes
                        if raw_item.class_name in h.items.values()
                    ),
                    None,
                )
                if replaced is None:
                    try:
                        _, hero_name, *_ = raw_item.class_name.split("_")
                        replaced = localization.get(
                            hero_name, localization.get(f"hero_{hero_name}")
                        )
                    except ValueError:
                        pass
                if replaced is None:
                    LOGGER.warning(f"Failed to find hero name for {raw_item.class_name}")
            else:
                var_to_loc = {
                    "key_duck": "citadel_keybind_crouch",
                    "in_mantle": "citadel_keybind_mantle",
                    "key_innate_1": "citadel_keybind_roll",
                    "in_move_down": "citadel_keybind_down",
                }
                replaced = localization.get(var_to_loc.get(variable, variable))
        if replaced is None:
            LOGGER.warning(f"Failed to replace {variable}")
        return str(replaced) if replaced else match.group(0)

    input_str = re.sub(r"\{s:([^}]+)}", replacer, input_str)
    input_str = re.sub(r"\{i:([^}]+)}", replacer, input_str)
    input_str = re.sub(r"\{g:([^}]+)}", replacer, input_str)
    input_str = input_str.replace("  ", " ")
    return input_str
