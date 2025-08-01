from typing import List

from chess.geometry.board import ChessBoard
from chess.geometry.coordinate import Coordinate
from chess.motion.search.bishop_search_pattern import BishopSearchPattern
from chess.motion.search.castle_search_pattern import CastleSearchPattern
from chess.motion.search.search_pattern import SearchPattern
from chess.piece.piece import ChessPiece


class QueenSearchPattern(SearchPattern):

    def _perform_search(self, piece: ChessPiece, board: ChessBoard) -> List[Coordinate]:
        origin = piece.current_coordinate()
        destinations: List[Coordinate] = []
        quadrants = piece.rank.territories
        print(f"{piece.label} at {origin} will search {len(quadrants)} quadrants for potential destinations")

        bishop_destinations = BishopSearchPattern.search(piece, board)
        castle_destinations = CastleSearchPattern.search(piece.rank, piece.current_coordinate(), board)

        return bishop_destinations + castle_destinations
