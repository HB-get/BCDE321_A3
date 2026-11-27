from dataclasses import dataclass

from zimp.domain.common.contract_events import ContractEvents
from zimp.domain.common.contract_game_state import ContractGameState
from zimp.domain.common.contract_items import ContractItems
from zimp.domain.common.contract_map import ContractMap
@dataclass
class GameContext:
    """Container for the domain classes"""
    state: ContractGameState
    movement: ContractMap
    items: ContractItems
    events: ContractEvents
