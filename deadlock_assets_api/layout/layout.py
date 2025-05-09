import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Self
from xml.etree.ElementTree import Element, ElementTree

from deadlock_assets_api.utils import snake_to_pascal


@dataclass
class Snippet:
    name: str
    body: list[Element]

    @classmethod
    def from_element(cls, element: Element) -> Self:
        name = element.get("name", "")
        body = list(element)
        return cls(name=name, body=body)


@dataclass
class HTMLOutput:
    styles: set[str] = field(default_factory=set)
    snippets: list[Snippet] = field(default_factory=list)
    body: str = ""

    def __add__(self, other: Self) -> Self:
        if not isinstance(other, HTMLOutput):
            return NotImplemented
        return HTMLOutput(
            self.styles.union(other.styles), self.snippets + other.snippets, self.body + other.body
        )

    def __str__(self) -> str:
        style = ""
        for file in self.styles:
            file = file.replace("s2r://", "depots/game/citadel/").replace("vcss_c", "css")
            with open(file, "r") as f:
                lines = list(f.readlines())
                style += "\n" + "\n".join(lines)
        return f"""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style type="text/css">
            {style}
        </style>
    </head>
    <body>
        {self.body}
    </body>
</html>
        """.strip()


@dataclass
class Component(ABC):
    id: str = ""
    class_name: str = ""
    children: list[Element] = field(default_factory=list)

    @classmethod
    def from_element(cls, element: Element) -> Self:
        id = element.get("id", "")
        class_name = element.get("class", "")
        children = list(element)
        return cls(id=id, class_name=class_name, children=children)

    @abstractmethod
    def to_html(self) -> HTMLOutput:
        raise NotImplementedError("Subclasses must implement this method.")


@dataclass
class Panel(Component):
    def to_html(self) -> HTMLOutput:
        sub_html = sum((build_element(c) for c in self.children), start=HTMLOutput())
        return HTMLOutput(
            styles=sub_html.styles,
            body=f'<div id="{self.id}" class="{self.class_name}">{sub_html.body}</div>',
        )


@dataclass
class Image(Component):
    src: str = ""

    @classmethod
    def from_element(cls, element: Element) -> Self:
        label = super().from_element(element)
        label.src = element.get("src", "")
        return label

    def to_html(self) -> HTMLOutput:
        return HTMLOutput(
            body=f'<img id="{self.id}" class="{self.class_name}" src="{self.src}" />',
        )


@dataclass
class Label(Component):
    text: str = ""

    @classmethod
    def from_element(cls, element: Element) -> Self:
        label = super().from_element(element)
        label.text = element.get("text", element.text or "")
        return label

    def to_html(self) -> HTMLOutput:
        return HTMLOutput(body=f'<span id="{self.id}" class="{self.class_name}">{self.text}</span>')


@dataclass
class NoneComponent(Component):
    def to_html(self) -> HTMLOutput:
        return HTMLOutput()


COMPONENTS = {
    "Panel": Panel,
    "Label": Label,
    "GlobalClassListener": NoneComponent,
    "Image": Image,
}


@dataclass
class Layout:
    name: str
    styles: set[str]
    snippets: list[Snippet]
    body: Element
    class_name: str = ""
    id: str = ""

    @classmethod
    def from_layout_file(cls, file_path: str) -> Self:
        root = ElementTree().parse(file_path)
        style_includes = root.findall(".//styles//include")
        styles = {i.get("src") for i in style_includes}

        snippets = [Snippet.from_element(e) for e in root.findall(".//snippets//snippet")]

        body = next(e for e in root if e.tag not in ("styles", "snippets"))

        id = root.get("id", "")
        class_name = root.get("class", "")

        name = body.tag if body.tag not in COMPONENTS else None
        name = name or snake_to_pascal(os.path.basename(file_path).split(".")[0])
        return cls(
            name=name, styles=styles, snippets=snippets, body=body, id=id, class_name=class_name
        )


LAYOUT_DIR = "depots/game/citadel/panorama/layout"


def index_all_layouts() -> list[Layout]:
    all_layouts = []
    for root, dirs, files in os.walk(LAYOUT_DIR):
        for file in files:
            if not file.endswith(".xml"):
                continue
            file_path = os.path.join(root, file)
            all_layouts.append(Layout.from_layout_file(file_path))
    return all_layouts


LAYOUTS = {layout.name: layout for layout in index_all_layouts()}


def build_element(element) -> HTMLOutput:
    if element.tag in COMPONENTS:
        print("building element", element.tag)
        return COMPONENTS[element.tag].from_element(element).to_html()
    elif element.tag in LAYOUTS:
        print("building layout", element.tag)
        return build_layout(LAYOUTS[element.tag])
    raise ValueError(f"Unknown element tag: {element.tag}")


def build_layout(layout: Layout) -> HTMLOutput:
    return HTMLOutput(styles=layout.styles, snippets=layout.snippets) + sum(
        (build_element(elem) for elem in layout.body), start=HTMLOutput()
    )
