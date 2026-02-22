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
    
    #Get king piece for correct color
    for piece in pieces_arr:
        if piece.color == turn and piece.__class__.__name__ == "King":
            king = piece
            break

    end = False

    #Only check if king is in check
    if king_check(king, board, pieces_arr):

        anti_check = False

        for piece in pieces_arr:
            if piece.color == turn and piece.alive:

                valid_moves = piece.get_valid_moves(board, pieces_arr)

                for move in valid_moves:
                    orig_row = piece.row
                    orig_col = piece.col

                    piece.row = move[0]
                    piece.col = move[1]
                    
                    #Ant-check possible
                    if not king_check(king, board, pieces_arr):
                        anti_check = True

                    piece.row = orig_row
                    piece.col = orig_col

                    if anti_check:
                        break
            if anti_check:
                break

        #Nothing prevents check
        if not anti_check:
            end = True

    return end
