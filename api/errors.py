from fastapi import HTTPException, status

from assembler.team import AssemblyOptions


class NotEnoughTeamsError(HTTPException):
    def __init__(self, expected_team_size: int, actual_team_size: int) -> None:
        detail = {
            "error": f"Expected minimum {expected_team_size} to commence a battle, found {actual_team_size}"
        }
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class TooManyPlayersError(HTTPException):
    def __init__(self, expected: int, actual: int, options: AssemblyOptions) -> None:
        detail = {
            "error": f"Maximum player count is {expected}, found {actual}",
            "attackers": options.attackers,
            "defenders": options.defenders,
            "total": sum((options.attackers, options.defenders, 1)),
        }
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
