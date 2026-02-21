class Piece:
    # parent class: handles similarities in all pieces
    def __init__(self, posx, posy, color):
        self.posx = posx
        self.posy = posy
        self.color = color
        self.directions = []
        self.max_step = 0

    def get_valid_moves(self, board):
        valid_moves = []
        for direction in self.directions:
            # each piece can move a maximum number of steps in each direction
            for step in range(1, self.max_steps + 1):
                # calculate the each possible row
                end_row = self.posx + (direction[0] * step)
                # calculate the each possible column
                end_col = self.posy + (direction[1] * step)
                
                # check if out of grid
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break 
                # look at what is on the target square
                target_square = board[end_row][end_col]
                
                if target_square == 0:
                    # target square is empty (move) -> valid
                    valid_moves.append((end_row, end_col))
                else:
                    # check piece collision
                    if target_square.color != self.color:
                        # target square is an enemy piece (take) -> valid
                        valid_moves.append((end_row, end_col))
                        # target square is an friendly piece -> invalid
                        # stop either way
                    break
                    
        return valid_moves
        
    def __str__(self):
        # __class__.__name__ automatically gets the name of the piece
        return f"This is a {self.__class__.__name__.lower()} with position {self.posx}{self.posy}"

#########Below are children of Piece:###########

class Rook(Piece):
    def __init__(self, posx, posy, color):
        super().__init__(posx, posy, color)

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


class King(Piece):
    def __init__(self, posx, posy, color):
        super().__init__(posx, posy, color)
        
        # vectors of (row_change, col_change) ->
        self.directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        self.max_steps = 1


class Queen(Piece):
    def __init__(self, posx, posy, color):
        super().__init__(posx, posy, color)
        
        # vectors of (row_change, col_change) ->
        self.directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        self.max_steps = 7

        
class Pawn(Piece): #special case of polymorphism
    def __init__(self, posx, posy, color):
        super().__init__(posx, posy, color)

    def get_valid_moves(self, board):
        valid_moves = []
        
        # Determine direction based on color 
        # (Assuming White starts at bottom of the board (rows 6,7) and moves "up" to row 0)
        move_direction = -1 if self.color == "White" else 1
        
        # 1. Single step forward
        front_row = self.posx + move_direction
        if 0 <= front_row < 8:
            if board[front_row][self.posy] == 0:
                valid_moves.append((front_row, self.posy))
                
                # 2. Double step forward (only if first step is clear AND it's on starting row)
                starting_row = 6 if self.color == "White" else 1
                if self.posx == starting_row:
                    double_row = self.posx + (move_direction * 2)
                    if board[double_row][self.posy] == 0:
                        valid_moves.append((double_row, self.posy))
        
        # 3. Diagonal Captures
        capture_cols = [self.posy - 1, self.posy + 1]
        for col in capture_cols:
            if 0 <= front_row < 8 and 0 <= col < 8:
                target_square = board[front_row][col]
                # Can only move diagonally IF there is an enemy piece there
                if target_square != 0 and target_square.color != self.color:
                    valid_moves.append((front_row, col))
                    
        return valid_moves

