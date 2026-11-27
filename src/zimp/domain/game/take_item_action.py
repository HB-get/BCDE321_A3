from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction


class TakeItemAction(GameAction):
    settles_events = True

    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_has_found_item() else ErrorCode.HAVENT_FOUND_ITEM

    def _do_action(self) -> ErrorCode | None:
        if error := self._is_error(self._ctx.items.keep_found_item()):
            return error

        self._ctx.state.end_found_item()

        # Debug code - retained to preserve behaviour
        self._ctx.log.append("KEEP | ")
        # End debug code

        return None
