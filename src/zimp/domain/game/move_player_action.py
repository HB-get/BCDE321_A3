from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction
from zimp.domain.game.game_context import GameContext


class MovePlayerAction(GameAction):
    def __init__(self, context: GameContext, direction: Direction) -> None:
        super().__init__(context)
        self._direction = direction

    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_can_move() else ErrorCode.CANT_MOVE_NOW

    def _do_action(self) -> ErrorCode | None:
        if error := self._is_error(self._ctx.movement.move(self._direction)):
            return error

        if self._ctx.movement.is_placement_mode_on():
            self._ctx.state.start_move()
            return None

        # Debug code - retained to preserve behaviour
        self._ctx.last_direction = self._direction
        # End debug

        return self._draw_event_card()

