from pydantic import BaseModel, ConfigDict, Field


class ColorV1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    red: int = Field(..., description="The red value of the color.", ge=0, le=255)
    green: int = Field(..., description="The green value of the color.", ge=0, le=255)
    blue: int = Field(..., description="The blue value of the color.", ge=0, le=255)
    alpha: int = Field(..., description="The alpha value of the color.", ge=0, le=255)
