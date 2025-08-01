from typing import Optional, TYPE_CHECKING


from chess.geometry.coordinate import Coordinate

from chess.transaction.transaction_result import TransactionResult, Failure, StatusCode

if TYPE_CHECKING:
    from chess.geometry.board import ChessBoard

class CoordinateValidator:

    @staticmethod
    def coordinate_exists(coordinate: Optional[Coordinate], board: Optional['ChessBoard']) -> TransactionResult:
        method = "CoordinateValidator.validate_coordinate_on_board"

        if board is None:
            return TransactionResult(method, Failure("ChessBoard cannot be None"))
        if coordinate is None:
            return TransactionResult(method, Failure("Coordinate cannot be None."))

        rows = len(board.grid)
        columns = len(board.grid[0]) if rows > 0 else 0

        if coordinate.row < 0 or coordinate.row >= rows:
            return TransactionResult(
                method,
                Failure(f"Row {coordinate.row} is out of board bounds (0-{rows - 1}).")
            )

        if coordinate.column < 0 or coordinate.column >= columns:
            return TransactionResult(
                method,
                Failure( f"Column {coordinate.column} is out of board bounds (0-{columns - 1}).")
            )

        return TransactionResult(method, StatusCode.SUCCESS)
