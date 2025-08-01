from dataclasses import dataclass, field

import pygame
from typing import TYPE_CHECKING, Optional, cast, OrderedDict

from colorama.ansi import clear_line

from constants import GameColor, PlacementStatus
from geometry import GridCoordinate
from grid_entity import GridEntity, Mover, HorizontalMover, VerticalMover

if TYPE_CHECKING:
    from board import Board

@dataclass(frozen=True)
class DragState:
    mover: Mover
    original_coordinate: GridCoordinate
    current_coordinate: GridCoordinate
    offset_x: int = 0
    offset_y: int = 0

    def with_updated_position(self, new_coordinate: GridCoordinate) -> 'DragState':
        return DragState(
            mover=self.mover,
            original_coordinate=self.original_coordinate,
            current_coordinate=new_coordinate,
            offset_x=self.offset_x,
            offset_y=self.offset_y
        )

@dataclass
class GameDisplay:
    board: 'Board'
    cell_px: int = 60
    border_px: int = 2
    screen_width: int = 800
    screen_height: int = 800

    active_drags: OrderedDict[int, DragState] = field(default_factory=OrderedDict)
    is_dragging: bool = False

    def __post_init__(self):
        self.screen_width = self.board.dimension.length * self.cell_px + self.border_px * 2
        self.screen_height = self.board.dimension.height * self.cell_px + self.border_px * 2

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Podscape")
        self.font = pygame.font.SysFont("monospace", 30)

    def load_chess_piece_images(self):
        import os

        base_path = "assets"

        chess_pieces = [
            "white-castle", "white-knight", "white-bishop", "white-king", "white-queen", "white-pawn"
            "black-castle", "black-knight", "black-bishop", "black-king", "black-queen", "black-pawn"
        ]

        for name in chess_pieces:
            try:
                path = os.path.join(base_path, f"{name}.png")  # or .svg if you’re using pygame-svg
                image = pygame.image.load(path)
                scaled = pygame.transform.scale(image, (self.cell_px, self.cell_px))  # auto-scale to square
                self.piece_images[name] = scaled
            except Exception as e:
                print(f"⚠️ Failed to load image {name}: {e}")


    def draw_grid(self):
        screen_color = GameColor.DARK_GRAY_1.value
        self.screen.fill(screen_color)

        cell_color = GameColor.LIGHT_SAND.value
        opposite_cell_color = screen_color

        current_cell_color = cell_color
        previous_cell_color = cell_color
        for row in range(self.board.dimension.height):
            for col in range(self.board.dimension.length):
                cell_rect = pygame.Rect(
                    col * self.cell_px + self.border_px,
                    row * self.cell_px + self.border_px,
                    self.cell_px,
                    self.cell_px
                )

                cell = self.board.cells[row][col]
                current_cell_color = cell_color if (row + col) % 2 == 0 else opposite_cell_color

                pygame.draw.rect(self.screen, current_cell_color, cell_rect)
                # Draw an outlined rectangle
                pygame.draw.rect(self.screen, GameColor.BLACK.value, cell_rect, 1)

    def draw_all_entities(self):
        # First draw board entities
        for entity in self.board.entities:
            self.draw_entity(entity)

        # Then draw any entities being dragged at their current position
        for drag_state in self.active_drags.values():
            rect = pygame.Rect(
                drag_state.current_coordinate.column * self.cell_px + self.border_px,
                drag_state.current_coordinate.row * self.cell_px + self.border_px,
                drag_state.mover.dimension.length * self.cell_px - self.border_px,
                drag_state.mover.dimension.height * self.cell_px - self.border_px
            )
            pygame.draw.rect(self.screen, GameColor.OLIVE.value, rect)
            text_surface = self.font.render(str(drag_state.mover.mover_id), True, GameColor.BLACK.value)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

    def draw_entity(self, entity: 'GridEntity'):
        """Draw a single mover on the board"""
        if entity is None:
            print("[Warning] Entity cannot be None. Cannot draw a null mover to the screen.")
            return
        if entity.top_left_coordinate is None:
            print("[Warning] Entity has no top_left_coordinate. Cannot draw an mover without a top_left_coordinate to the screen.")
            return

        horizontal_mover_color = GameColor.OLIVE.value
        vertical_mover_color = GameColor.DEEP_ORANGE.value
        # print(f"Drawing mover {mover.mover_id_counter} at top_left_coordinate {mover.top_left_coordinate}")
        # Calculate position and dimensions
        rect = pygame.Rect(
            entity.top_left_coordinate.column * self.cell_px + self.border_px,
            entity.top_left_coordinate.row * self.cell_px + self.border_px,
            entity.dimension.length * self.cell_px - self.border_px,
            entity.dimension.height * self.cell_px - self.border_px
        )
        # Draw the mover (fixed the width parameter)

        if isinstance(entity, HorizontalMover):
            pygame.draw.rect(self.screen, horizontal_mover_color, rect)
        if isinstance(entity, VerticalMover):
            pygame.draw.rect(self.screen, vertical_mover_color, rect)

        # Draw mover ID
        text_surface = self.font.render(str(entity.mover_id), True, GameColor.BLACK.value)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def get_entity_at_mouse_position(self, mouse_position: tuple) -> Optional['GridEntity']:
        if mouse_position is None:
            print("[Warning] Mouse position cannot be None. Cannot get an mover at a null position.")
            return None
        coordinate = self.grid_coordinate_at_mouse_position(mouse_position)
        if coordinate is None:
            print("Mouse is outside the game board. Cannot get an mover at a position outside the board.")
            return None
        return self.board.cells[coordinate.row][coordinate.column].occupant

    def handle_mouse_down(self, event: pygame.event.Event):
        if event.button == 1:  # Left mouse button
            entity = self.get_entity_at_mouse_position(event.pos)
            if entity is not None:
                self.start_drag(entity, event.pos)

    def handle_mouse_motion(self, event: pygame.event.Event):
        if self.is_dragging and self.active_drags:
            mover_id = list(self.active_drags.keys())[0]
            self.update_drag(mover_id, event.pos)

    def handle_mouse_up(self, event: pygame.event.Event) -> PlacementStatus | None:
        if event.button == 1 and self.is_dragging and self.active_drags:
            mover_id = list(self.active_drags.keys())[0]
            placement_status = self.end_drag(mover_id)
            self.is_dragging = False
            return placement_status
        return PlacementStatus.RELEASED

    def start_drag(self, mover: Mover, mouse_position: tuple[int, int]) -> None:
        self.active_drags[mover.mover_id] = DragState(
            mover=mover,
            original_coordinate=mover.top_left_coordinate,
            current_coordinate=mover.top_left_coordinate,
            offset_x=mouse_position[0] - (mover.top_left_coordinate.column * self.cell_px),
            offset_y=mouse_position[1] - (mover.top_left_coordinate.row * self.cell_px)
        )
        self.is_dragging = True
        print("mover", mover.mover_id, "dragging started at", self.active_drags[mover.mover_id].original_coordinate)

    def update_drag(self, mover_id: int, mouse_position: tuple[int, int]) -> None:
        if not self.is_dragging or mover_id not in self.active_drags:
            return

        drag_state = self.active_drags[mover_id]
        mover = drag_state.mover

        # Calculate proposed grid position
        proposed_column = (mouse_position[0] - drag_state.offset_x) // self.cell_px
        proposed_row = (mouse_position[1] - drag_state.offset_y) // self.cell_px

        # Boundary checks
        new_column = max(0, min(proposed_column, self.board.dimension.length - mover.dimension.length))
        proposed_row = max(0, min(proposed_row, self.board.dimension.height - mover.dimension.height))

        # Enforce HorizontalMover constraint
        if isinstance(mover, HorizontalMover):
            proposed_row = drag_state.original_coordinate.row

        if isinstance(mover, VerticalMover):
            proposed_column = drag_state.original_coordinate.column

        # Check against both visual and board states
        test_coordinate = GridCoordinate(row=proposed_row, column=new_column)
        if not self.is_position_valid_for_drag(mover, test_coordinate):
            return
        try:
            new_coord = GridCoordinate(row=proposed_row, column=proposed_column)
            self.active_drags[mover_id] = drag_state.with_updated_position(new_coord)
        except ValueError as e:
            print(f"Invalid coordinate: {e}")

    def is_position_valid_for_drag(self, mover: Mover, test_coordinate: GridCoordinate) -> bool:
        """Combined check for visual dragging"""
        # 1. Check board's official position (for static entities)
        if not self.board.can_entity_move_to_cells(mover, test_coordinate):
            return False

        # 2. Check against other dragged entities
        for other_id, other_state in self.active_drags.items():
            if other_id == mover.mover_id:
                continue
            other_cells = self.get_occupied_cells(
                other_state.current_coordinate.row,
                other_state.current_coordinate.column,
                other_state.mover.dimension
            )

            if self.get_occupied_cells(test_coordinate.row, test_coordinate.columnl, mover.dimension) & other_cells:
                return False
        return True
