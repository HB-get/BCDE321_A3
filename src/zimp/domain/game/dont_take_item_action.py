from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction


class DontTakeItemAction(GameAction):
    settles_events = True

    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_has_found_item() else ErrorCode.HAVENT_FOUND_ITEM

    def _do_action(self) -> ErrorCode | None:
        self._ctx.items.dont_take_item()
        self._ctx.state.end_found_item()

        # Debug code - retained to preserve behaviour
        self._ctx.log.append("DON'T KEEP | ")
        # End debug code

        return None
