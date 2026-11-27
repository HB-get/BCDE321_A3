from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction


class RotateTileAction(GameAction):
    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_is_moving() else ErrorCode.CANT_ROTATE_NOW

    def _do_action(self) -> ErrorCode | None:
        return self._ctx.movement.rotate_placement_tile()
