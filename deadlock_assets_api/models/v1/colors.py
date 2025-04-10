from pydantic import BaseModel, ConfigDict, Field


class ColorV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    red: int = Field(..., description="The red value of the color.")
    green: int = Field(..., description="The green value of the color.")
    blue: int = Field(..., description="The blue value of the color.")
    alpha: int = Field(..., description="The alpha value of the color.")
