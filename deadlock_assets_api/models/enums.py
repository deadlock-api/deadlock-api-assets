import json
from enum import IntEnum

with open("deploy/client_versions.json") as f:
    ALL_CLIENT_VERSIONS = sorted(json.load(f), reverse=True)

DeadlockAssetsApiRoutesValidClientVersions = IntEnum(
    "DeadlockAssetsApiRoutesValidClientVersions",
    {str(b): int(b) for b in ALL_CLIENT_VERSIONS},
)
ValidClientVersions = DeadlockAssetsApiRoutesValidClientVersions

LATEST_VERSION = max(ALL_CLIENT_VERSIONS)
