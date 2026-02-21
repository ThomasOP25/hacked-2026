def check_diags(board, cords):
    '''
    Pass in board object and cords list with cords in format [x, y]
    '''
    safe = True
    diagFU, diagRU, diagFD, diagRD = cords #Forwards Up, Reverse Up, Forwards Down, Reverse Down diagonals
    king = board[cords[0]][cords[1]] #might be reversed when testing
    
    #pieces found by the diagonal beams
    pieces_found = []
    
    #proximal_piece indicates whether a pawn or king is within singular diag kill range. For example, if the king at pos [1,1] is under attack by a pawn at pos [2,2], then proximal_pieceFD = 1.
    proximal_pieceFU, proximal_pieceRU, proximal_pieceFD, proximal_pieceRD = 0
    
    #Stores pieces found by diagonal beams, 0 if nothing found.
    #Forward Up diag.
    while board[diagFU[0]][diagFU[1]] == king or board[diagFU[0]][diagFU[1]] == "0" or diagRU[0] < 8 or diagRU[1] > 0:
        diagFU[0] += 1
        diagFU[1] -= 1
        proximal_pieceFU += 1
        
                    
    if board[diagFU[0]][diagFU[1]] != "0":
        pieces_found.append(board[diagFU[0]][diagFU[1]])
    else:
        pieces_found.append(0)
    
                        
    #Reverse Up diag.
    while board[diagRU[0]][diagRU[1]] == king or board[diagRU[0]][diagRU[1]] == "0" or diagRU[0] > 0 or diagRU[1] > 0:
        diagRU[0] -= 1
        diagRU[1] -= 1
        proximal_pieceRU += 1
                    
    if board[diagRU[0]][diagRU[1]] != "0":
        pieces_found.append(board[diagRU[0]][diagRU[1]])                
    else:
        pieces_found.append(0)
        
    #Forward Down diag.
    while board[diagFD[0]][diagFD[1]] == king or board[diagFD[0]][diagFD[1]] == "0" or diagFD[0] < 8 or diagFD[1] < 8:
        diagFD[0] += 1
        diagFD[1] += 1
        proximal_pieceFD += 1
                
    if board[diagFD[0]][diagFD[1]] != "0":
        pieces_found.append(board[diagFD[0]][diagFD[1]])                
    else:
        pieces_found.append(0)
        
    #Reverse Down diag.
    while board[diagRD[0]][diagRD[1]] == king or board[diagRD[0]][diagRD[1]] == "0" or diagRD[0] > 0 or diagRD[1] < 8:
        diagRD[0] -= 1
        diagRD[1] += 1
        proximal_pieceRD += 1
                
    if board[diagRD[0]][diagRD[1]] != "0":
        pieces_found.append(board[diagRD[0]][diagRD[1]])                 
    else:
        pieces_found.append(0)
        
    '''
    [FU, RU, FD, RD] is in pieces_found, where each piece is an object or 0.  
    1. FU and RU can be attack points for a black king or pawn within proximal range; RD and FD can be attack points for a white king or pawn within proximal range.
    2. The opposite two diagonal points will always not be proximal for pawns of the same color, but proximal for kings of the same color.
    3. Bishops and Queens can attack as long as they are the proximal piece to the king.
    
    **Refer to the separated_diag_condition.txt file on the end_condition branch for better visual**
    '''
    if ((proximal_pieceFU == 1 and pieces_found[0] == "king" and king.color == "Black" and piece.color != king.color) or (proximal_pieceFU == 1 and pieces_found[0] == "pawn" or pieces_found[0] == "king" and king.color == "White" and piece.color != king.color) or (proximal_pieceRU == 1 and pieces_found[1] == "king" and king.color == "Black" and piece.color != king.color) or (proximal_pieceRU == 1 and pieces_found[1] == "pawn" or pieces_found[1] == "king" and king.color == "White" and piece.color != king.color)) or ((proximal_pieceFD == 1 and pieces_found[2] == "king" and king.color == "White" and piece.color != king.color) or (proximal_pieceFD == 1 and pieces_found[2] == "pawn" or pieces_found[2] == "king" and king.color == "Black" and piece.color != king.color) or (proximal_pieceRD == 1 and pieces_found[3] == "king" and king.color == "White" and piece.color != king.color) or (proximal_pieceRD == 1 and pieces_found[3] == "pawn" or pieces_found[3] == "king" and king.color == "Black" and piece.color != king.color)) or (piece == "bishop" and piece.color != king.color) or (piece == "queen" and piece.color != king.color):
        safe = False
    
    #Check after searching possible diags.
    return safe

def check_straights(board, cords):
    safe = True
    #Four possible straight beams from king.
    Ubeam, Dbeam, Lbeam, Rbeam = cords
    
    selected_piece = board[cords[0]][cords[1]]
    
    #Pieces found in straight beams (0 if none)
    pieces_found = []
    
    #Search in one beam's direction until a piece is found or until reaching a border. Store piece or 0 in list.
    #Up beam
    while board[Ubeam[0]][Ubeam[1]] == selected_piece or board[Ubeam[0]][Ubeam[1]] == "0" or Ubeam[0] > 0:
        Ubeam[0] -= 1
    
    if board[Ubeam[0]][Ubeam[1]] != "0":
        pieces_found.append(board[Ubeam[0]][Ubeam[1]])                 
    else:
        pieces_found.append(0)    
    
    #Down Beam
    while board[Dbeam[0]][Dbeam[1]] == selected_piece or board[Dbeam[0]][Dbeam[1]] == "0" or Dbeam[0] < 8:
        Dbeam[0] += 1
        
    if board[Dbeam[0]][Dbeam[1]] != "0":
        pieces_found.append(board[Dbeam[0]][Dbeam[1]])                 
    else:
        pieces_found.append(0) 
    
    #Left Beam
    while board[Lbeam[0]][Lbeam[1]] == selected_piece or board[Lbeam[0]][Lbeam[1]] == "0" or Lbeam[0] > 0:
        Lbeam[1] -= 1    
    
    if board[Lbeam[0]][Lbeam[1]] != "0":
        pieces_found.append(board[Lbeam[0]][Lbeam[1]])                 
    else:
        pieces_found.append(0) 
    
    #Right Beam
    while board[Rbeam[0]][Rbeam[1]] == selected_piece or board[Rbeam[0]][Rbeam[1]] == "0" or Rbeam[0] < 8:
        Rbeam[1] += 1    
        
    if board[Rbeam[0]][Rbeam[1]] != "0":
        pieces_found.append(board[Rbeam[0]][Rbeam[1]])                 
    else:
        pieces_found.append(0)   
    
    #The only pieces that can take out the king in a straight line is the king, the queen, or the rook.
    for piece in pieces_found:
        if piece == "Rook" or piece == "Queen" or piece == "King" and selected_piece.color != piece.color:
            safe = False
    
    return safe
    
    
def check_slants(board, cords):
    safe = True
    
    #Left 4 Possible Knight pos
    if cords[0] - 2 >= 0 and cords[1] - 1 >= 0:
        if board[cords[0] - 2][cords[1] - 1] == "Knight":
            safe = False
    
    if cords[0] - 2 >= 0 and cords[1] + 1 < 8:
        if board[cords[0] - 2][cords[1] + 1] == "Knight":
            safe = False    
    
    if cords[0] - 1 >= 0 and cords[1] + 2 < 8:
        if board[cords[0] - 1][cords[1] + 2] == "Knight":
            safe = False    
    
    if cords[0] - 1 >= 0 and cords[1] - 2 < 8:
        if board[cords[0] - 1][cords[1] - 2] == "Knight":
            safe = False    
    
    
    #Right 4 possible knight pos       
    if cords[0] + 2 >= 0 and cords[1] - 1 >= 0:
        if board[cords[0] + 2][cords[1] - 1] == "Knight":
            safe = False
    
    
    if cords[0] + 2 >= 0 and cords[1] + 1 < 8:
        if board[cords[0] + 2][cords[1] + 1] == "Knight":
            safe = False  
    
    if cords[0] + 1 >= 0 and cords[1] - 2 >= 0:
        if board[cords[0] + 1][cords[1] - 2] == "Knight":
            safe = False
                    
    if cords[0] + 1 >= 0 and cords[1] + 2 < 8:
        if board[cords[0] + 1][cords[1] + 2] == "Knight":
            safe = False 
    
    return safe
    
    
def game_condition():
    #Pass in king object.
    diag_safe = check_diags(board, cords)
    straight_safe = check_straights(board, cords)
    slant_safe = check_slants(board, cords)
    
    #Safe king default.
    status = 1
    legal_moves = legal_moves(king, board)
    
    #Check if king is in check (status = 0)
    if not diag_safe or not straight_safe or not slant_safe:
        status = 0
        
    #Check if king is in checkmate (status = -1)
    if not diag_safe or not straight_safe or not slant_safe and len(legal_moves) == 0:
        status = -1
    
    #Checkmated king (status = -1)
    return status
