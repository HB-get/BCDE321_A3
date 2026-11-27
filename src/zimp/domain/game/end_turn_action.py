from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction
from zimp.domain.game.game_context import GameContext


class EndTurnAction(GameAction):
    def __init__(self, context: GameContext, is_cower: bool) -> None:
        super().__init__(context)
        self._is_cower = is_cower

    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_can_end_turn() else ErrorCode.CANT_END_TURN_NOW

    def _do_action(self) -> ErrorCode | None:
        state = self._ctx.state
        if self._is_cower:
            cower = state.cower()
            if cower.is_fail():
                return cower.get_error_code()
            waste, shuffled = self._ctx.events.waste_time()
            if waste.is_fail():
                return waste.get_error_code()
            if shuffled:
                state.advance_time()

        tile_effect = self._ctx.movement.get_tile_effect()

        # Debug code - retained to preserve behaviour
        self._ctx.log.append(f"TILE {str(tile_effect)} | ")
        # End debug code

        state.do_end_turn_effect(tile_effect)

        if state.get_is_doing_events():  # temple or graveyard
            return self._draw_event_card()
        if not state.get_is_searching_item():  # heal or none; a search waits for the player
            state.start_new_turn()
        return None
