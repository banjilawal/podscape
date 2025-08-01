from typing import List


from chess.geometry.quadrant import Quadrant
from chess.rank.rank import Rank


class Pawn(Rank):

    def __init__(self, name: str, acronym: str, capture_value: int, territories: List[Quadrant]):

        from chess.motion.service.pawn_motion_service import PawnMotionService
        super().__init__(name, acronym, PawnMotionService(), capture_value, territories)
