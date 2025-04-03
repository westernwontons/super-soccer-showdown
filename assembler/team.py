from pydantic import BaseModel
from errors import NotEnoughPlayers
from models.player import Player, PlayerType
from models.team import Team
from provider.player_provider import PlayerProvider


class PlayerPool:
    def __init__(self, provider: PlayerProvider, team_size: int) -> None:
        self.provider = provider

        self.goalies: list[Player] = []
        self.attackers: list[Player] = []
        self.defenders: list[Player] = []

        self.goalies_consumed = 0
        self.attackers_consumed = 0
        self.defenders_consumed = 0

    def is_empty(self) -> bool:
        return len(self.attackers) == 0 and len(self.defenders) == 0 and len(self.goalies) == 0

    def reset(self) -> None:
        self.goalies_consumed = 0
        self.attackers_consumed = 0
        self.defenders_consumed = 0

    def get_players(self, player_type: PlayerType, count: int) -> list[Player]:
        match player_type:
            case PlayerType.GOALIE:
                low, high = self.goalies_consumed, self.goalies_consumed + 1
                goalie = self.goalies[low:high]
                self.goalies_consumed += 1
                return goalie

            case PlayerType.OFFENCE:
                low, high = self.attackers_consumed, self.attackers_consumed + count
                attackers = self.attackers[low:high]
                self.attackers_consumed += count
                return attackers

            case PlayerType.DEFENCE:
                low, high = self.defenders_consumed, self.defenders_consumed + count
                defenders = self.defenders[low:high]
                self.defenders_consumed += count
                return defenders

    async def pool(self) -> None:
        players = await self.provider.provide()
        if len(players) < 5:
            raise NotEnoughPlayers

        goalies = sorted(players, key=lambda x: x.height, reverse=True)
        self.goalies = [
            Player(name=p.name, weight=p.weight, height=p.height, type_=PlayerType.GOALIE)
            for p in goalies
        ]

        defenders = sorted(players, key=lambda x: x.weight, reverse=True)
        self.defenders = [
            Player(name=p.name, weight=p.weight, height=p.height, type_=PlayerType.DEFENCE)
            for p in defenders
        ]

        attackers = sorted(players, key=lambda x: x.height)
        self.attackers = [
            Player(name=p.name, weight=p.weight, height=p.height, type_=PlayerType.OFFENCE)
            for p in attackers
        ]


class AssemblyOptions(BaseModel):
    attackers: int
    defenders: int


class TeamAssembler:
    def __init__(self, provider: PlayerProvider, team_size: int) -> None:
        self.pool = PlayerPool(provider, team_size=team_size)

    async def assemble(self, options: AssemblyOptions) -> Team:
        if self.pool.is_empty():
            await self.pool.pool()

        attackers_count = options.attackers
        defenders_count = options.defenders

        goalie = self.pool.get_players(PlayerType.GOALIE, 1)[0]
        attackers = self.pool.get_players(PlayerType.OFFENCE, attackers_count)
        defenders = self.pool.get_players(PlayerType.DEFENCE, defenders_count)

        return Team(goalie=goalie, attackers=attackers, defenders=defenders)
