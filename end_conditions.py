def king_check(king, board, pieces_arr):
    for piece in pieces_arr:
        if piece.alive and piece.color != king.color:
            #Generate moves for all enemy pieces, king is checked if it shares cords with enemy valid move pieces
            moves = piece.get_valid_moves(board, pieces_arr)
            if (king.row, king.col) in moves:
                #King in check
                return True
    return False
    
def end_condition(turn, board, pieces_arr):
    king = None
    
    #Find the current king piece we are looking at
    for piece in pieces_arr:
        if piece.color == turn and piece.__class__.__name__ == "King":
            king = piece
        
    end = False
    if king_check(king, board, pieces_arr):
        
        #get all valid moves for king piece
        unsafe = 0    
        king_moves = king.get_valid_moves(board, pieces_arr)
        max_unsafe = len(king_moves)
        
        #Cycle through all king piece moves, and see if thery match any enemy piece move
        for kmove in king_moves:
            for piece in pieces_arr:
                if piece.color != king.color:
                    for move in piece.get_valid_moves(board, pieces_arr):
                        if move == kmove:
                            unsafe += 1
                
                else:
                    for move in piece.get_valid_moves(board, pieces_arr):
                        if move == kmove:
                            unsafe -= 1
        
        #checkmate                    
        if unsafe == max_unsafe:
            end = True
        
    return end
