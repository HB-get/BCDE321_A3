from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction
from zimp.domain.game.game_context import GameContext


class PickZombieDoorAction(GameAction):
    def __init__(self, context: GameContext, direction: Direction) -> None:
        super().__init__(context)
        self._direction = direction

    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_is_zombie_door() else ErrorCode.NOT_ZOMBIE_DOOR

    def _do_action(self) -> ErrorCode | None:
        if error := self._is_error(self._ctx.movement.create_zombie_door(self._direction)):
            return error

        self._ctx.state.confirm_zombie_door()
        return None
