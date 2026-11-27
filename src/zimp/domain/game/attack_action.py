from zimp.domain.common.error_code import ErrorCode
from zimp.domain.game.game_action import GameAction
from zimp.domain.game.game_context import GameContext


class AttackAction(GameAction):
    settles_events = True

    def __init__(self, context: GameContext, use_chainsaw: bool, instant_kill: bool) -> None:
        super().__init__(context)
        self._use_chainsaw = use_chainsaw
        self._instant_kill = instant_kill

    def _can_run(self) -> ErrorCode | None:
        return None if self._ctx.state.get_can_attack() else ErrorCode.CANT_ATTACK

    def _do_action(self) -> ErrorCode | None:
        items = self._ctx.items
        if self._instant_kill:
            if not items.get_has_instant_kill():
                return ErrorCode.NO_INSTANT_KILL
            items.discard(0)
            items.discard(1)

        bonus = items.attack_bonus(self._use_chainsaw)
        if bonus.is_fail():
            return bonus.get_error_code()

        self._ctx.state.attack(bonus.get_data(), self._instant_kill)
        items.record_battle()

        # Debug code - retained to preserve behaviour
        self._ctx.log.append("ATTACKED | ")
        # End debug code

        return None
