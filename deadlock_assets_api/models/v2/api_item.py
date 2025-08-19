from typing import Annotated, Union

from pydantic import Field

from deadlock_assets_api.models.v2.api_ability import AbilityV2
from deadlock_assets_api.models.v2.api_upgrade import UpgradeV2
from deadlock_assets_api.models.v2.api_weapon import WeaponV2

ItemV2 = Annotated[Union[AbilityV2, WeaponV2, UpgradeV2], Field(discriminator="type")]
