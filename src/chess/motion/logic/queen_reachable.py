from chess.geometry.coordinate import Coordinate
from chess.motion.logic.castle_reachable import CastleReachable
from chess.geometry.diagonal import Diagonal
from chess.motion.logic.reachable import Reachable

class QueenReachable(Reachable):

    @staticmethod
    def is_reachable(origin: Coordinate, destination: Coordinate) -> bool:
        return (
                CastleReachable.is_reachable(origin, destination) or
                Diagonal.is_diagonal(origin, destination)
        )