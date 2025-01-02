import re

from deadlock_assets_api.models.v2.raw_ability import RawAbilityV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_item_base import RawItemBaseV2


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
                    print(f"Failed to find hero name for {raw_item.class_name}")
            else:
                var_to_loc = {
                    "key_duck": "citadel_keybind_crouch",
                    "in_mantle": "citadel_keybind_mantle",
                    "key_innate_1": "citadel_keybind_roll",
                    "in_move_down": "citadel_keybind_down",
                }
                replaced = localization.get(var_to_loc.get(variable, variable))
        if replaced is None:
            print(f"Failed to replace {variable}")
        return str(replaced) if replaced else match.group(0)

    input_str = re.sub(r"\{s:([^}]+)}", replacer, input_str)
    input_str = re.sub(r"\{i:([^}]+)}", replacer, input_str)
    return input_str
