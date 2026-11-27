from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction
from zimp.domain.game.game_context import GameContext


class DiscardItemAction(GameAction):
    def __init__(self, context: GameContext, slot_id: int) -> None:
        super().__init__(context)
        self._slot_id = slot_id

    def _do_action(self) -> ErrorCode | None:
        return self._is_error(self._ctx.items.discard(self._slot_id))
