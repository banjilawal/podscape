from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, List

from geometry import Dimension, GridCoordinate

@dataclass
class GridEntity:
    dimension: Dimension
    top_left_coordinate: Optional[GridCoordinate] = None

@dataclass
class BrickPallet(GridEntity):
    pass


@dataclass(kw_only=True)
class Mover(GridEntity, ABC):
    mover_id: int
    movement_strategy: 'SearchPattern' = field(init=False, repr=False)

    def __init__(self, *, dimension: Dimension, top_left_coordinate: Optional[GridCoordinate] = None, mover_id: int = None):
        if not hasattr(self, 'movement_strategy'):
            raise TypeError(f"{self.__class__.__name__} must initialize movement_strategy")
        super().__init__(dimension=dimension, top_left_coordinate=top_left_coordinate)
        self.mover_id = mover_id

    def move(self, board: 'PodBoard', destination_coordinate: GridCoordinate) -> None:
        if not self.movement_strategy.forward_move_request(self, board, destination_coordinate):
            print(f"Failed to move {self.mover_id} to {destination_coordinate}.")
        else:
            print(f"Moved {self.mover_id} to {destination_coordinate}.")


@dataclass
class VerticalMover(Mover):
    def __init__(self, *, mover_id: int, length: int, top_left_coordinate: Optional[GridCoordinate] = None):
        self.movement_strategy = VerticalMoveStrategy()
        super().__init__(
            mover_id=mover_id,
            dimension=Dimension(length=length, height=1),
            top_left_coordinate=top_left_coordinate
        )

@dataclass
class HorizontalMover(Mover):
    def __init__(self, *, mover_id: int, height: int, top_left_coordinate: Optional[GridCoordinate] = None):
        self.movement_strategy = HorizontalMoveStrategy()
        super().__init__(
            mover_id=mover_id,
            dimension=Dimension(length=1, height=height),
            top_left_coordinate=top_left_coordinate
         )

@dataclass
class UniversalMover(Mover):
    def __init__(self, *, mover_id: int, dimension: Dimension, top_left_coordinate: Optional[GridCoordinate] = None):
        self.movement_strategy = UniversalMoveStrategy()
        super().__init__(
            mover_id=mover_id,
            dimension=Dimension(length=dimension.length, height=dimension.height),
            top_left_coordinate=top_left_coordinate
        )

class MovementStrategy(ABC):
    def __init__(self, rules: List['Reachable']):
        self.rules = rules

    def _check_basic_conditions(self, mover: 'Mover', board: 'PodBoard', destination_coordinate: 'GridCoordinate') -> bool:
        if mover is None:
            print("[Warning] Mover cannot be None. It cannot move.")
            return False
        if board is None:
            print("[Warning] PodBoard cannot be None. Cannot move.")
            return False
        if mover.top_left_coordinate is None:
            print("[Warning] Mover has no top_left_coordinate. Cannot move.")
            return False
        if destination_coordinate is None:
            print("[Warning] Destination top_left_coordinate cannot be None. Cannot move.")
            return False
        if destination_coordinate.column < 0 or destination_coordinate.column >= board.dimension.length:
            print(f"[Warning] Horizontal move out of bounds: {destination_coordinate.column}")
            return False
        if destination_coordinate.row < 0 or destination_coordinate.row >= board.dimension.length:
            print(f"[Warning] Vertical move out of bounds: {destination_coordinate.row}")
            return False
        return True

    @abstractmethod
    def move(self, mover: 'Mover', board: 'PodBoard', destination_coordinate: 'GridCoordinate') -> bool:
        """Perform the move if valid. Return True if successful, False otherwise."""
        pass