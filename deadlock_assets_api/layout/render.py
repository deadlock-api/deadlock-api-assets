from deadlock_assets_api.layout.layout import build_layout, index_all_layouts

if __name__ == "__main__":
    all_layouts = index_all_layouts()
    layout_to_render = next(
        layout for layout in all_layouts if layout.name == "AbilityDetailsPanel"
    )
    rendered_layout = build_layout(layout_to_render)
    html = str(rendered_layout)
    html = (
        html.replace("s2r://", "depots/game/citadel/")
        .replace("vcss_c", "css")
        .replace("vsvg", "svg")
        .replace("vtex", "png")
    )
    with open("output.html", "w") as f:
        f.write(html)
    print(rendered_layout)
    breakpoint()
