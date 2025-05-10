import logging
import re
from functools import lru_cache

from css_parser.css import CSSStyleRule

from deadlock_assets_api.models.v2.api_item_base import parse_img_path
from deadlock_assets_api.models.v2.raw_ability import RawAbilityV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_item_base import RawItemBaseV2, parse_css_rules
from deadlock_assets_api.utils import prettify_pascal_case

LOGGER = logging.getLogger(__name__)

css_rules = parse_css_rules("res/citadel_base_styles.css")
color_definitions = {}
for rule in css_rules:
    if not rule.cssText or not rule.cssText.startswith("@define"):
        continue
    color_definition = rule.cssText.strip("@define").strip(";").split(":")
    if len(color_definition) == 2:
        name, value = color_definition
        color_definitions[name.strip()] = value.strip()


@lru_cache
def parse_css_base_styles(css_class_selector: str) -> (str | None, str | None):
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

        if variable.startswith("citadel_inline_attribute"):
            css_class = variable.split(":")[-1].strip("'")
            label = prettify_pascal_case(css_class)
            css_class = f".InlineAttributeIcon.{css_class}"
            background_image, wash_color = parse_css_base_styles(css_class)
            background_image = parse_img_path(background_image)
            if background_image.endswith(".svg"):
                background_image = background_image.replace(".svg", "_unfilled.svg")
            if wash_color:
                img_tag = f'<img src="{background_image}" class="inline-attribute" style="color: {wash_color};" alt="{label}"/>'
                label_tag = f'<span class="inline-attribute-label" style="color: {wash_color};">{label}</span>'
            else:
                img_tag = f'<img src="{background_image}" class="inline-attribute" alt="{label}"/>'
                label_tag = f'<span class="inline-attribute-label">{label}</span>'
            if css_class.lower().endswith("icon"):
                return img_tag
            else:
                return img_tag + label_tag

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
                        localization.get(h.class_name, h.class_name)
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
    return input_str
