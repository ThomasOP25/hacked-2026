class Rook:
    def __init__(self, posx_, posy_, color_):
        self.posx = posx_
        self.posy = posy_
        self.color = color_
        
    def __str__(self):
        print(f"This is a rook with pos {self.posx}, {self.posy}")
            

class Bishop:
    def __init__(self, posx_, posy_, color_):
        self.posx = posx_
        self.posy = posy_
        self.color = color_
        
    def __str__(self):
        print(f"This is a bishop with pos {self.posx}, {self.posy}")
            
    

class Pawn:
    def __init__(self, posx_, posy_, color_):
        self.posx = posx_
        self.posy = posy_
        self.color = color_
        
    def __str__(self):
        print(f"This is a pawn with pos {self.posx}, {self.posy}")
            
   

class Knight:
    def __init__(self, posx_, posy_, color_):
        self.posx = posx_
        self.posy = posy_
        self.color = color_
        
    def __str__(self):
        print(f"This is a knight with pos {self.posx}, {self.posy}")  

class King:
    def __init__(self, posx_, posy_, color_):
        self.posx = posx_
        self.posy = posy_
        self.color = color_
        
    def __str__(self):
        print(f"This is a king with pos {self.posx}, {self.posy}")    

class Queen:
    def __init__(self, posx_, posy_, color_):
        self.posx = posx_
        self.posy = posy_
        self.color = color_
        
    def __str__(self):
        print(f"This is a queen with pos {self.posx}, {self.posy}")

