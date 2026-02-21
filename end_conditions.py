def check_diags(board, cords):
    #Pass in board object and cords list
    safe = True
    diagFU, diagRU, diagFD, diagRD = [x,y]
    pieces_found = []
    king = board[x][y]
    for diag in range(4):
        for x in range(8):
            for y in range(8):
                #Forward Up diag.
                while board[diagFU[0]][diagFU[1]] != king or board[diagFU[0]][diagFU[1]] != "0":
                    diagFU[0] += 1
                    diagFU[1] -= 1
                        
                #Reverse Up diag.
                while board[diagFU[0]][diagFU[1]] != king or board[diagRU[0]][diagRU[1]] != "0" or diagRU[0] <= 8 or diagRU[1] <= 8:
                    diagRU[0] -= 1
                    diagRU[1] -= 1
                    
                #Forward Down diag.
                while board[diagFU[0]][diagFU[1]] != king or board[diagFD[0]][diagFD[1]] != "0" or diagFD[0] <= 8 or diagFD[1] <= 8:
                    diagFD[0] += 1
                    diagFD[1] += 1
                    
                #Reverse Down diag.
                while board[diagFU[0]][diagFU[1]] != king or board[diagRD[0]][diagRD[1]] != "0" or diagRD[0] <= 8 or diagRD[1] <= 8:
                    diagRD[0] -= 1
                    diagRD[1] += 1
                    
    #Check each searched diag.
    return safe

def check_straights(cord):
    pass
def check_slants(cord):
    pass
def game_condition(king):
    #Pass in king object.
    status = 1
    #Check if king is in check (status = 0)
    #Check if king is in checkmate (status = -1)
