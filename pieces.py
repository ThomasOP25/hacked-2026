from __future__ import annotations


class Piece:
    # parent class: handles similarities in all pieces
    def __init__(self, row: int, col: int, color: str) -> None:
        self.row = row
        self.col = col
        self.color = color
        self.directions = []
        self.alive = True
        self.has_moved = False # Track if piece has moved (for castling, pawn double step)
        self.piece_type: str = self.__class__.__name__.lower()

    def get_valid_moves(self, board: list[list[int | str]], pieces_arr: list[Piece], last_move: tuple | None = None) -> list[tuple[int, int]]:
        valid_moves = []
        for direction in self.directions:
            # each piece can move a maximum number of steps in each direction
            for step in range(1, self.max_steps + 1):
                # calculate the each possible row
                end_row = self.row + (direction[0] * step)
                # calculate the each possible column
                end_col = self.col + (direction[1] * step)
                
                # check if out of grid
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break 
                # look at what is on the target square
                target_square = board[end_row][end_col]
                
                if target_square == 0:
                    # target square is empty (move) -> valid
                    valid_moves.append((end_row, end_col))
                else:
                    # find which piece is occupying the target square
                    target_piece = None
                    for piece in pieces_arr:
                        if piece.alive and end_row == piece.row and end_col == piece.col:
                            target_piece = piece
                            break
                    # check piece collision
                    if target_piece and target_piece.color != self.color:
                        # target square is an enemy piece (take) -> valid
                        valid_moves.append((end_row, end_col))
                        # target square is an friendly piece -> invalid
                        # stop either way
                    break
                    
        return valid_moves

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.row}, {self.col}, '{self.color}', alive={self.alive})"

    def __str__(self) -> str:
        # __class__.__name__ automatically gets the name of the piece
        return f"{self.color[0].lower()}{self.piece_type[0]}"

#########Below are children of Piece:###########

class Rook(Piece):
    def __init__(self, row: int, col: int, color: str) -> None:
        super().__init__(row, col, color)

        # vectors of (row_change, col_change) -> Down, Up, Right, Left
        self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.max_steps = 7


class Bishop(Piece):
    def __init__(self, row: int, col: int, color: str) -> None:
        super().__init__(row, col, color)

        # vectors of (row_change, col_change) -> TopLeft, TopRight, BottomLeft, BottomRight
        self.directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.max_steps = 7
    
        
class Knight(Piece):
    def __init__(self, row: int, col: int, color: str) -> None:
        super().__init__(row, col, color)

        # vectors of (row_change, col_change) ->
        self.directions = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2), 
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        self.max_steps = 1
    
    def __str__(self) -> str:
        # __class__.__name__ automatically gets the name of the piece
        return f"{self.color[0].lower()}{self.piece_type[1]}"


class King(Piece):
    def __init__(self, row: int, col: int, color: str) -> None:
        super().__init__(row, col, color)
        
        # vectors of (row_change, col_change) ->
        self.directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        self.max_steps = 1


class Queen(Piece):
    def __init__(self, row: int, col: int, color: str) -> None:
        super().__init__(row, col, color)
        
        # vectors of (row_change, col_change) ->
        self.directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        self.max_steps = 7

        
class Pawn(Piece): #special case of polymorphism
    def __init__(self, row: int, col: int, color: str) -> None:
        super().__init__(row, col, color)

    def get_valid_moves(self, board: list[list[int | str]], pieces_arr: list[Piece], last_move: tuple | None = None) -> list[tuple[int, int]]:
        valid_moves = []
        
        # Determine direction based on color 
        # (Assuming White starts at bottom of the board (rows 6,7) and moves "up" to row 0)
        move_direction = -1 if self.color == "white" else 1
        
        # 1. Single step forward
        front_row = self.row + move_direction
        if 0 <= front_row < 8:
            if board[front_row][self.col] == 0:
                valid_moves.append((front_row, self.col))
                
                # 2. Double step forward (only if first step is clear AND it hasn't moved)
                if not self.has_moved:
                    double_row = self.row + (move_direction * 2)
                    if board[double_row][self.col] == 0:
                        valid_moves.append((double_row, self.col))
        
        # 3. Diagonal Captures
        capture_cols = [self.col - 1, self.col + 1]
        for col in capture_cols:
            if 0 <= front_row < 8 and 0 <= col < 8:
                target_square = board[front_row][col]
                # Can only move diagonally IF there is an enemy piece there
                if target_square != 0:
                    target_piece = None
                    for piece in pieces_arr:
                        if piece.alive and front_row == piece.row and col == piece.col:
                            target_piece = piece
                            break
                    if target_piece and target_piece.color != self.color:
                        valid_moves.append((front_row, col))
                
                # 4. En Passant
                if target_square == 0 and last_move:
                    lm_piece, lm_start, lm_end = last_move
                    if lm_piece.piece_type == "pawn" and lm_piece.color != self.color:
                        # Check if last move was a double step
                        if abs(lm_start[0] - lm_end[0]) == 2:
                            # Check if the pawn landed next to us
                            if lm_end[0] == self.row and lm_end[1] == col:
                                valid_moves.append((front_row, col))
                        
        return valid_moves
