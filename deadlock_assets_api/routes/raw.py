import json
from enum import Enum

from fastapi import APIRouter
from starlette.responses import FileResponse

from deadlock_assets_api import utils
from deadlock_assets_api.models.v2.generic_data import GenericDataV2

with open("deploy/client_versions.json") as f:
    ALL_CLIENT_VERSIONS = sorted(json.load(f), reverse=True)
VALID_CLIENT_VERSIONS = Enum(
    "ValidClientVersions", {str(b): int(b) for b in ALL_CLIENT_VERSIONS}, type=int
)
LATEST_VERSION = max(ALL_CLIENT_VERSIONS)

router = APIRouter(prefix="/raw", tags=["Raw"])


@router.get("/heroes")
def get_raw_heroes(client_version: VALID_CLIENT_VERSIONS | None = None) -> FileResponse:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/raw_heroes.json")


@router.get("/items")
def get_raw_items(client_version: VALID_CLIENT_VERSIONS | None = None) -> FileResponse:
    if client_version is None:
        client_version = VALID_CLIENT_VERSIONS(LATEST_VERSION)
    return FileResponse(f"deploy/versions/{client_version.value}/raw_items.json")


# BACKWARD COMPATIBILITY ROUTES
@router.get("/generic_data", response_model_exclude_none=True, include_in_schema=False)
def get_generic_data(client_version: VALID_CLIENT_VERSIONS | None = None) -> GenericDataV2:
    client_version = utils.validate_client_version(client_version)
    return utils.read_parse_data_model(
        f"deploy/versions/{client_version}/generic_data.json", GenericDataV2
    )
