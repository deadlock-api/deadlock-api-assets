from pydantic import BaseModel, ConfigDict, Field, RootModel


class LootTableV2Entry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item: str = Field(..., validation_alias="m_strItem")


class LootTableV2Entity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    entries: list[LootTableV2Entry] = Field(..., validation_alias="m_vecEntries")


class LootTableV2(RootModel):
    root: dict[str, LootTableV2Entity]
