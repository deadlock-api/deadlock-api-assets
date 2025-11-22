from typing import Self

from pydantic import BaseModel, ConfigDict, Field


class ColorV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    red: int = Field(..., description="The red value of the color.", ge=0, le=255)
    green: int = Field(..., description="The green value of the color.", ge=0, le=255)
    blue: int = Field(..., description="The blue value of the color.", ge=0, le=255)
    alpha: int = Field(..., description="The alpha value of the color.", ge=0, le=255)

    @classmethod
    def from_list(cls, color: list[int]) -> Self:
        if len(color) == 3:
            r, g, b = color
            a = 255
        elif len(color) == 4:
            r, g, b, a = color
            if a is None or not isinstance(a, int):
                a = 255
        else:
            raise ValueError("Color must be a tuple or list of 3 or 4 integers.")
        return cls(red=r, green=g, blue=b, alpha=a)

    @classmethod
    def from_hex(cls, hex_str: str) -> Self:
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = 255
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16)
        else:
            raise ValueError("Hex string must be in the format RRGGBB or RRGGBBAA.")
        return cls(red=r, green=g, blue=b, alpha=a)
