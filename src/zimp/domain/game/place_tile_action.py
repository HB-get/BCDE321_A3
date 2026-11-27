from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction


class PlaceTileAction(GameAction):
    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_is_moving() else ErrorCode.CANT_PLACE_NOW

    def _do_action(self) -> ErrorCode | None:
        if error := self._is_error(self._ctx.movement.lock_placement_tile()):
            return error

        self._ctx.state.end_move()
        return self._draw_event_card()
