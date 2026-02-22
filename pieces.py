
class Piece:
    # parent class: handles similarities in all pieces
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.directions = []
        self.alive = True

    def get_valid_moves(self, board, pieces_arr):
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
                    for piece in pieces_arr:
                        if piece.alive and end_row == piece.row and end_col == piece.col:
                            target_piece = piece
                    # check piece collision
                    if target_piece.color != self.color:
                        # target square is an enemy piece (take) -> valid
                        valid_moves.append((end_row, end_col))
                        # target square is an friendly piece -> invalid
                        # stop either way
                    break
                    
        return valid_moves
        
    def __str__(self):
        # __class__.__name__ automatically gets the name of the piece
        return f"{self.color[0].lower()}{self.__class__.__name__.lower()[0]}"

#########Below are children of Piece:###########

class Rook(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        # vectors of (row_change, col_change) -> Down, Up, Right, Left
        self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.max_steps = 7


class Bishop(Piece):
    def __init__(self, posx, posy, color):
        super().__init__(posx, posy, color)

        # vectors of (row_change, col_change) -> TopLeft, TopRight, BottomLeft, BottomRight
        self.directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.max_steps = 7
    
        
class Knight(Piece):
    def __init__(self, posx, posy, color):
        super().__init__(posx, posy, color)

        # vectors of (row_change, col_change) ->
        self.directions = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2), 
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        self.max_steps = 1
    
    def __str__(self):
        # __class__.__name__ automatically gets the name of the piece
        return f"{self.color[0].lower()}{self.__class__.__name__.lower()[1]}"


class King(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        
        # vectors of (row_change, col_change) ->
        self.directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        self.max_steps = 1


class Queen(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        
        # vectors of (row_change, col_change) ->
        self.directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        self.max_steps = 7

        
class Pawn(Piece): #special case of polymorphism
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

    def get_valid_moves(self, board, pieces_arr):
        valid_moves = []
        
        # Determine direction based on color 
        # (Assuming White starts at bottom of the board (rows 6,7) and moves "up" to row 0)
        move_direction = -1 if self.color == "white" else 1
        
        # 1. Single step forward
        front_row = self.row + move_direction
        if 0 <= front_row < 8:
            if board[front_row][self.col] == 0:
                valid_moves.append((front_row, self.col))
                
                # 2. Double step forward (only if first step is clear AND it's on starting row)
                starting_row = 6 if self.color == "white" else 1
                if self.row == starting_row:
                    double_row = self.row + (move_direction * 2)
                    if board[double_row][self.col] == 0:
                        valid_moves.append((double_row, self.col))
        
        # 3. Diagonal Captures
        capture_cols = [self.col - 1, self.col + 1]
        for col in capture_cols:
            if 0 <= front_row < 8 and 0 <= col < 8:
                target_square = board[front_row][col]
                # Can only move diagonally IF there is an enemy piece there
                if target_square == 0:
                    continue
                else: # find which piece is occupying the target square
                    for piece in pieces_arr:
                        if piece.alive and front_row == piece.row and col == piece.col:
                            target_piece = piece
                    if target_piece.color != self.color:
                        valid_moves.append((front_row, col))
                    
        return valid_moves
