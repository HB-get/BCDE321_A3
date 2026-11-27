from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.game.game_action import GameAction
from zimp.domain.game.game_context import GameContext


class UseItemAction(GameAction):
    def __init__(self, context: GameContext, item_id: ItemCode) -> None:
        super().__init__(context)
        self._item_id = item_id

    def _do_action(self) -> ErrorCode | None:
        if error := self._is_error(self._ctx.items.use(self._item_id)):
            return error

        if self._item_id == ItemCode.SODA:
            self._ctx.state.drink_soda()

        return None
