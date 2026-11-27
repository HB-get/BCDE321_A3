from abc import ABC, abstractmethod

from zimp.domain.common.dev_card import CardEffectType
from zimp.domain.common.error_code import ErrorCode

from zimp.domain.game.game_context import GameContext


class GameAction(ABC):
    settles_events = False

    def __init__(self, ctx : GameContext) -> None:
        self._ctx = ctx

    def run(self) -> ErrorCode | None:
        """Template method: check can run, do action, settle"""
        can_run = self._can_run()
        if can_run is not None:
            return can_run

        error = self._do_action()
        if error is None and self.settles_events:
            self._do_post_event_checks()
        return error

    def _can_run(self) -> ErrorCode | None:
        """Hook: return an ErrorCode if the current mode does not allow this action (default is allowed)"""
        return None

    @abstractmethod
    def _do_action(self) -> ErrorCode | None:
        """Primitive: carry out the action"""

    def _draw_event_card(self) -> ErrorCode | None:
        """Concrete: Draw a dev card for the current time, apply its effect, then run the post-event checks"""
        draw_result, shuffled = self._ctx.events.draw_event(self._ctx.state.get_time())
        if draw_result.is_fail():
            return draw_result.get_error_code()

        effect = draw_result.get_data()

        # Debug code - retained to preserve behaviour
        if self._ctx.debug:
            self._ctx.log.append("CARD" + (f"{effect.effect_type.name}: {effect.value}"
                                   if effect.effect_type in (CardEffectType.ZOMBIES, CardEffectType.HEALTH)
                                   else effect.effect_type.name) + " | ")
        # End debug code

        self._ctx.state.apply_card_effect(effect)
        if shuffled:
            self._ctx.state.advance_time()

        self._do_post_event_checks()

        return None

    def _do_post_event_checks(self) -> None:
        """Concrete: Once events are finished, open a zombie door if needed, else start the next turn if it has ended"""
        if self._ctx.state.get_can_end_turn():
            if self._ctx.movement.need_zombie_door():
                self._ctx.state.start_zombie_door()
            elif self._ctx.state.get_has_ended_turn():
                self._ctx.state.start_new_turn()