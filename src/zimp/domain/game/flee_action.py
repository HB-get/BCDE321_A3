from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.game.game_action import GameAction
from zimp.domain.game.game_context import GameContext


class FleeAction(GameAction):
    settles_events = True

    def __init__(self, context: GameContext, direction: Direction, with_oil: bool) -> None:
        super().__init__(context)
        self._direction = direction
        self._with_oil = with_oil

    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_can_flee() else ErrorCode.CANT_FLEE

    def _do_action(self) -> ErrorCode | None:
        if self._with_oil and not self._ctx.items.get_has_oil():
            return ErrorCode.NO_OIL
        if error := self._is_error(self._ctx.movement.flee(self._direction)):
            return error

        self._ctx.state.flee(self._with_oil)
        if self._with_oil:
            self._ctx.items.use(ItemCode.OIL)

        # Debug code - retained to preserve behaviour
        self._ctx.log.append("FLED | ")
        # End debug code

        return None
