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
from zimp.domain.game.dont_search_item_action import DontSearchItemAction
from zimp.domain.game.flee_action import FleeAction

from zimp.domain.game.game_context import GameContext
from zimp.domain.game.move_player_action import MovePlayerAction
from zimp.domain.game.pick_zombie_door_action import PickZombieDoorAction
from zimp.domain.game.place_tile_action import PlaceTileAction
from zimp.domain.game.rotate_tile_action import RotateTileAction
from zimp.domain.game.search_item_action import SearchItemAction


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

        # yucky debug
        self._debug_msgs = []
        self._debug = debug
        self._debug_direction = Direction.NORTH
        # end yucky debug

    def _draw_event_card(self) -> ErrorCode | None:
        draw_result, shuffled = self._events.draw_event(self._state.get_time())
        if draw_result.is_fail():
            return draw_result.get_error_code()

        # yucky debug
        if self._debug:
            effect = draw_result.get_data()
            self._debug_msgs += ["CARD" + (f"{effect.effect_type.name}: {effect.value}"
                                           if effect.effect_type in (CardEffectType.ZOMBIES, CardEffectType.HEALTH)
                                           else effect.effect_type.name) + " | "]
        # end yucky debug

        self._state.apply_card_effect(draw_result.get_data())
        if shuffled:
            self._state.advance_time()

        self._do_post_event_checks()

        return None

    def _do_post_event_checks(self) -> None:
        if self._state.get_can_end_turn():
            if self._movement.need_zombie_door():
                self._state.start_zombie_door()
            elif self._state.get_has_ended_turn():
                self._state.start_new_turn()

    def reset(self, map_seed: int | None = None) -> None:
        """Reset all game components"""
        self._state.reset()
        self._events.reset()
        self._movement.reset(randomizer_seed=map_seed)  # 408
        self._items.reset()

        # yucky debug
        self._debug_msgs = []
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
        """Add the found item to the items"""
        if not self._state.get_has_found_item():
            return ErrorCode.HAVENT_FOUND_ITEM

        add_item = self._items.keep_found_item()
        if isinstance(add_item, ErrorCode):
            return add_item

        self._state.end_found_item()

        self._do_post_event_checks()

        # yucky debug
        self._debug_msgs += [f"KEEP | "]
        # end yucky debug

        return None

    def dont_take_item(self) -> ErrorCode | None:
        """Abandon the item that was found"""
        if not self._state.get_has_found_item():
            return ErrorCode.HAVENT_FOUND_ITEM

        self._items.dont_take_item()
        self._state.end_found_item()

        self._do_post_event_checks()

        # yucky debug
        self._debug_msgs += [f"DON'T KEEP | "]
        # end yucky debug

        return None

    def discard_item(self, slot_id: int) -> ErrorCode | None:
        """Discard the chosen item from the items"""
        discard_result = self._items.discard(slot_id)
        if isinstance(discard_result, ErrorCode):
            return discard_result

        return None

    def use_item(self, item_id: ItemCode) -> ErrorCode | None:
        """Use the chosen item (gasoline or soda)"""
        use = self._items.use(item_id)

        if isinstance(use, ErrorCode):
            return use

        if item_id == ItemCode.SODA:
            self._state.drink_soda()

        return None

    def end_turn(self, is_cower: bool = False) -> ErrorCode | None:
        """End the current turn, optionally cowering"""
        if not self._state.get_can_end_turn():
            return ErrorCode.CANT_END_TURN_NOW

        if is_cower:
            cower_action = self._state.cower()
            if cower_action.is_fail():
                return cower_action.get_error_code()

            cower_event, shuffled = self._events.waste_time()
            if cower_event.is_fail():
                return cower_event.get_error_code()
            if shuffled:
                self._state.advance_time()

        tile_effect = self._movement.get_tile_effect()

        # yucky debug
        self._debug_msgs += [f"TILE {str(tile_effect)} | "]
        # end yucky debug

        self._state.do_end_turn_effect(tile_effect)

        if self._state.get_is_doing_events():  # temple or graveyard
            return self._draw_event_card()
        elif self._state.get_is_searching_item():
            pass
        else:  # heal or none
            self._state.start_new_turn()

        return None

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
                                                                 self._debug_direction).get_data()
        else:
            player = self._movement.get_player_position()
        doors = self._movement._GameMap__display_tiles.get(player).get_door_directions()
        return f"Health: {hp}, Attack: {attack}, Items: {items}, Time: {time}, Cards: {cards}\n" \
            + f"{doors}\n" \
            + " ".join(self._debug_msgs)
