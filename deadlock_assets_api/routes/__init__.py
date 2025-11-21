import json
from enum import Enum

with open("deploy/client_versions.json") as f:
    ALL_CLIENT_VERSIONS = sorted(json.load(f), reverse=True)
VALID_CLIENT_VERSIONS = Enum(
    "ValidClientVersions", {str(b): int(b) for b in ALL_CLIENT_VERSIONS}, type=int
)
LATEST_VERSION = max(ALL_CLIENT_VERSIONS)
