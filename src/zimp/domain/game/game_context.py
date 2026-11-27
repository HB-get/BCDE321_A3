from dataclasses import dataclass, field

from zimp.domain.common.contract_events import ContractEvents
from zimp.domain.common.contract_game_state import ContractGameState
from zimp.domain.common.contract_items import ContractItems
from zimp.domain.common.contract_map import ContractMap
from zimp.domain.common.direction import Direction


@dataclass
class GameContext:
    """Container for the domain classes"""
    state: ContractGameState
    movement: ContractMap
    items: ContractItems
    events: ContractEvents

    # Debug data - these should be removed but are preserved so as to not change behaviour
    debug: bool
    log: list[str] = field(default_factory=list)
    last_direction: Direction = Direction.NORTH
