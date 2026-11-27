from zimp.domain.common.contract_events import ContractEvents
from zimp.domain.common.contract_game_state import ContractGameState
from zimp.domain.common.contract_items import ContractItems
from zimp.domain.common.contract_map import ContractMap
from zimp.domain.common.dev_card import CardEffectType
from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.common.result import Result
from zimp.domain.game.attack_action import AttackAction
from zimp.domain.game.discard_item_action import DiscardItemAction
from zimp.domain.game.dont_search_item_action import DontSearchItemAction
from zimp.domain.game.dont_take_item_action import DontTakeItemAction
from zimp.domain.game.flee_action import FleeAction

from zimp.domain.game.game_context import GameContext
from zimp.domain.game.move_player_action import MovePlayerAction
from zimp.domain.game.pick_zombie_door_action import PickZombieDoorAction
from zimp.domain.game.place_tile_action import PlaceTileAction
from zimp.domain.game.rotate_tile_action import RotateTileAction
from zimp.domain.game.search_item_action import SearchItemAction
from zimp.domain.game.take_item_action import TakeItemAction
from zimp.domain.game.end_turn_action import EndTurnAction
from zimp.domain.game.use_item_action import UseItemAction


class Game:
    """Boundary class connecting the controller to domain components"""

    def __init__(self,
                 state: ContractGameState,
                 movement: ContractMap,
                 items: ContractItems,
                 events: ContractEvents,
                 map_seed: int | None = None,
                 debug: bool = False
                 ) -> None:
        self._state = state
        self._events = events
        self._items = items
        self._movement = movement

        self._ctx = GameContext(state, movement, items, events, debug)

        self.reset(map_seed)

    def reset(self, map_seed: int | None = None) -> None:
        """Reset all game components"""
        self._state.reset()
        self._events.reset()
        self._movement.reset(randomizer_seed=map_seed)  # 408
        self._items.reset()

        # Debug code - retained to preserve behaviour
        self._ctx.log = []
        # end yucky debug

    def move_player(self, direction: Direction) -> ErrorCode | None:
        return MovePlayerAction(self._ctx, direction).run()

    def rotate_tile(self) -> ErrorCode | None:
        return RotateTileAction(self._ctx).run()

    def place_tile(self) -> ErrorCode | None:
        return PlaceTileAction(self._ctx).run()

    def pick_zombie_door(self, direction: Direction) -> ErrorCode | None:
        return PickZombieDoorAction(self._ctx, direction).run()

    def attack(self, use_chainsaw: bool = False, instant_kill: bool = False) -> ErrorCode | None:
        return AttackAction(self._ctx, use_chainsaw, instant_kill).run()

    def flee(self, direction: Direction, with_oil: bool = False) -> ErrorCode | None:
        return FleeAction(self._ctx, direction, with_oil).run()

    def perform_search_for_item(self) -> ErrorCode | None:
        return SearchItemAction(self._ctx).run()

    def ignore_search_for_item(self) -> ErrorCode | None:
        return DontSearchItemAction(self._ctx).run()

    def take_item(self) -> ErrorCode | None:
        return TakeItemAction(self._ctx).run()

    def dont_take_item(self) -> ErrorCode | None:
        return DontTakeItemAction(self._ctx).run()

    def discard_item(self, slot_id: int) -> ErrorCode | None:
        return DiscardItemAction(self._ctx, slot_id).run()

    def use_item(self, item_id: ItemCode) -> ErrorCode | None:
        return UseItemAction(self._ctx, item_id).run()

    def end_turn(self, is_cower: bool = False) -> ErrorCode | None:
        return EndTurnAction(self._ctx, is_cower).run()

    def check_win_loss(self) -> Result:
        """To be called after each action; determines if the player has won or lost"""
        if self._state.check_is_won():
            return Result.success("You win!")
        elif self._state.check_is_lost():
            return Result.success("You lose!")

        return Result.fail(ErrorCode.NOT_WON_OR_LOST)

    def get_debug_msgs(self) -> str:
        """Debug method to return game state"""
        hp = self._state.get_hp()
        attack = 1 + self._items.attack_bonus(False).get_data()
        items_tuple = self._items.held_items()
        items = f"{items_tuple[0]}, {items_tuple[1]}"
        time = self._state.get_time() + 9
        cards = self._events.get_remaining_card_count()

        if self._state.get_is_moving():
            player = self._movement._GameMap__calculate_position(self._movement.get_player_position(),
                                                                 self._ctx.last_direction).get_data()
        else:
            player = self._movement.get_player_position()
        doors = self._movement._GameMap__display_tiles.get(player).get_door_directions()
        return f"Health: {hp}, Attack: {attack}, Items: {items}, Time: {time}, Cards: {cards}\n" \
            + f"{doors}\n" \
            + " ".join(self._ctx.log)
