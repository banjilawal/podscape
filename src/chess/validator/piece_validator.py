from typing import TYPE_CHECKING

from chess.piece.mobility_status import MobilityStatus
from chess.rank.promotable.promotable_rank import PromotableRank
from chess.transaction.failure import Failure
from chess.transaction.status_code import StatusCode
from chess.transaction.transaction_result import TransactionResult

if TYPE_CHECKING:
    from chess.piece.piece import ChessPiece


class ChessPieceValidator:

    @staticmethod
    def has_player(chess_piece: 'ChessPiece') -> TransactionResult:
        method = "ChessPieceValidator.has_player"

        if chess_piece.player is None:
            return TransactionResult(method, Failure(f"{chess_piece.label} does not have a player assigned to it."))
        return TransactionResult(method, StatusCode.SUCCESS)

    @staticmethod
    def has_rank(chess_piece: 'ChessPiece') -> TransactionResult:
        method = "ChessPieceValidator.has_rank"

        if chess_piece.rank is None:
            return TransactionResult(method, Failure(f"{chess_piece.label} does not have a rank."))
        return TransactionResult(method, StatusCode.SUCCESS)


    @staticmethod
    def is_not_null(piece: 'ChessPiece') -> TransactionResult:
        method = "ChessPieceValidator.is_not_null"

        if piece is None:
            return TransactionResult.failure("ChessPiece does not exist. It is null (None).")
        return TransactionResult(method, StatusCode.SUCCESS)


    @staticmethod
    def can_be_moved(iece: 'ChessPiece') -> TransactionResult:
        method = "ChessPieceValidator.can_move"

        if piece.status == MobilityStatus.FREE and piece.current_coordinate() is not None:
            return TransactionResult(method, StatusCode.SUCCESS)
        return TransactionResult.failure(f"{piece.label} is not free to move.")


    @staticmethod
    def can_place_on_board(chess_piece: 'ChessPiece') -> TransactionResult:
        method = "ChessPieceValidator.can_add_to_board"
        if (
            chess_piece is not None and
            chess_piece.status == MobilityStatus.FREE and
            chess_piece.current_coordinate() is None
        ):
            return TransactionResult(method, StatusCode.SUCCESS)
        return TransactionResult(method, Failure(f"{chess_piece.label} Cannot be added to the board"))


    @staticmethod
    def can_be_promoted(chess_piece: 'ChessPiece') -> TransactionResult:
        method = "ChessPieceValidator.is_promotable"

        rank = chess_piece.rank
        if isinstance(rank, PromotableRank) and not rank.is_promoted():
            return TransactionResult(method, StatusCode.SUCCESS)
        return TransactionResult(method, Failure(f"{chess_piece.label} of rank {rank.name} cannot be promoted."))


    @staticmethod
    def is_on_board(piece: 'ChessPiece') -> TransactionResult:
        method = "ChessPieceValidator.is_on_board"

        if piece.current_coordinate() is None:
            return TransactionResult(method, Failure(f"{piece.label} is not on the board."))
        return TransactionResult(method, StatusCode.SUCCESS)