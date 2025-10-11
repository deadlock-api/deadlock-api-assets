from datetime import datetime
from functools import lru_cache

from pydantic import BaseModel, Field, computed_field


class SteamInfoV1(BaseModel):
    client_version: int = Field(..., validation_alias="ClientVersion")
    server_version: int = Field(..., validation_alias="ServerVersion")
    product_name: str = Field(..., validation_alias="ProductName")
    app_id: int = Field(..., validation_alias="appID")
    server_app_id: int = Field(..., validation_alias="ServerAppID")
    tools_app_id: int = Field(..., validation_alias="ToolsAppID")
    source_revision: int = Field(..., validation_alias="SourceRevision")
    version_date: str = Field(..., validation_alias="VersionDate")
    version_time: str = Field(..., validation_alias="VersionTime")

    @computed_field
    @property
    def version_datetime(self) -> datetime:
        date = datetime.strptime(self.version_date, "%b %d %Y").date()
        time = datetime.strptime(self.version_time, "%H:%M:%S").time()
        return datetime.combine(date, time)

    @classmethod
    def load(cls) -> SteamInfoV1:
        return cls.model_validate(
            {
                k.strip(): v.strip()
                for k, v in (line.split("=") for line in load_steam_info() if "=" in line)
            }
        )


@lru_cache
def load_steam_info() -> list[str]:
    with open("res/steam.inf") as f:
        return f.readlines()
