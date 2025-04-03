from typing import Any

from models.player import BasePlayer
from errors import PlayerHasNoHeight, PlayerHasNoName, PlayerHasNoWeight
from provider.player_provider import PlayerProvider


class PokePlayerProvider(PlayerProvider):
    def validate_player(self, data: dict[str, Any]) -> BasePlayer | None:
        if (weight := data.get("weight")) is None:
            raise PlayerHasNoWeight

        if (name := data.get("name")) is None:
            raise PlayerHasNoName

        if (height := data.get("height")) is None:
            raise PlayerHasNoHeight

        return BasePlayer.model_validate(
            {
                "weight": weight,
                "name": name,
                "height": height,
            },
            by_name=True,
            by_alias=True,
        )
