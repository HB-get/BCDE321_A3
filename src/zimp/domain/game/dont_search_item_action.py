from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction


class DontSearchItemAction(GameAction):
    settles_events = True

    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_is_searching_item() else ErrorCode.CANT_SEARCH_NOW

    def _do_action(self) -> ErrorCode | None:
        self._ctx.state.end_searching_item()

        # Debug code - retained to preserve behaviour
        self._ctx.log.append("NO SEARCH | ")
        # End debug code

        return None
