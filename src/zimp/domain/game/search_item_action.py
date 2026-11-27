from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction


class SearchItemAction(GameAction):
    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_is_searching_item() else ErrorCode.CANT_SEARCH_NOW

    def _do_action(self) -> ErrorCode | None:
        draw_result, shuffled = self._ctx.events.draw_item()
        if draw_result.is_fail():
            return draw_result.get_error_code()

        item = draw_result.get_data()
        self._ctx.items.find_item(item)
        self._ctx.state.find_item()
        if shuffled:
            self._ctx.state.advance_time()

        # Debug code - retained to preserve behaviour
        self._ctx.log.append(f"FOUND {str(item)} | ")
        # End debug code

        return None
