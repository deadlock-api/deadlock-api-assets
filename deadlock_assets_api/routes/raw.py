from fastapi import APIRouter
from starlette.responses import FileResponse

from deadlock_assets_api import utils
from deadlock_assets_api.models.enums import LATEST_VERSION, ValidClientVersions
from deadlock_assets_api.models.v2.generic_data import GenericDataV2
from deadlock_assets_api.models.v2.raw_ability import RawAbilityV2
from deadlock_assets_api.models.v2.raw_accolade import RawAccoladeV2
from deadlock_assets_api.models.v2.raw_hero import RawHeroV2
from deadlock_assets_api.models.v2.raw_upgrade import RawUpgradeV2
from deadlock_assets_api.models.v2.raw_weapon import RawWeaponV2

router = APIRouter(prefix="/raw", tags=["Raw"])


@router.get("/heroes")
def get_raw_heroes(client_version: ValidClientVersions | None = None) -> list[RawHeroV2]:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/raw_heroes.json")


@router.get("/items")
def get_raw_items(
    client_version: ValidClientVersions | None = None,
) -> list[RawAbilityV2 | RawWeaponV2 | RawUpgradeV2]:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/raw_items.json")


@router.get("/accolades")
def get_raw_accolades(client_version: ValidClientVersions | None = None) -> list[RawAccoladeV2]:
    if client_version is None:
        client_version = ValidClientVersions(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/raw_accolades.json")


# BACKWARD COMPATIBILITY ROUTES
@router.get("/generic_data", response_model_exclude_none=True, include_in_schema=False)
def get_generic_data(client_version: ValidClientVersions | None = None) -> GenericDataV2:
    client_version = utils.validate_client_version(client_version)
    return utils.read_parse_data_model(
        f"deploy/versions/{client_version}/generic_data.json", GenericDataV2
    )
