from socket import if_indextoname
import pygame as pg  # imports pyagme library with the shorthand name of pg
import os  # imports os, a python native libarary which deals with files and paths
import numpy as np # imports numpy, a python library with math, arrays, and a lot of stuff. For this, mostly arrays


main_dir = os.path.split(os.path.abspath(__file__))[0] # establishes the defualt absolute path to the directory where this is run/located on a computer
data_dir = os.path.join(main_dir, "data") # absolute path to the data folder

# a dictionary that correlates the box on the chess board to the 
# coordinate where a piece should be placed to be centered in that box
piece_spaces = {
    0 : 12.5,
    1 : 87.5,
    2 : 162.5, 
    3 : 237.5,
    4 : 312.5,
    5 : 387.5,
    6 : 462.5,
    7 : 537.5
}

# a dictionary that connects boxes on the board to x/y coordinate where movement dot would be placed
dot_spaces = {
    0 : 22.5,
    1 : 97.5,
    2 : 172.5, 
    3 : 247.5,
    4 : 322.5,
    5 : 397.5,
    6 : 472.5,
    7 : 547.5
}

naming_nums = {
    (-1, -1) : 11,
    (-1, 0) : 12,
    (-1, 1) : 13,
    (0, -1) : 14,
    (0, 0) : 15,
    (0, 1) : 16,
    (1, -1) : 17,
    (1, 0) : 18,
    (1, 1) : 19,
}



# ranges that connect a position from the mouse to a box on the board
cursor_range = [(0,73), (73, 148), (148, 223), (223, 298), (298, 373), (373,448), (448, 523), (523, 598)]

# Boards: an ndarray (numpy array with (n) dimensions) with two dimensions representing
# the board with a 3 digit number representing a particular piece, key below

# Digit 1 : Which instance of that piece it is
# Digit 2 : 1 = Pawn, 2 = Rook, 3 = Knight, 4 = Bishop, 5 = King, 6 = Queen, 9 = Dot
# Digit 3 : 1 = White, 2 = Black
# Makes the board - white at the top, black at the bottom of the matrix
boards = np.array([
    [120, 130, 140, 150, 168, 141, 131, 121],
    [110, 111, 112, 113, 114, 115, 116, 117]
])
boards = np.append(boards, np.zeros((4, 8)), 0)
boards = np.append(boards, np.array([[210, 211, 212, 213, 214, 215, 216, 217],[220, 230, 240, 250, 268, 241, 231, 221]]), 0)
boards = boards.astype(int)

turn_dict = {
    '1' : '2',
    '2' : '1'
}

dtos = np.array(np.zeros((8,8)))
dtos.astype(int)
print(boards)
 



# Default code which loads an image as a pygame image with the default path
def load_image(name, colorkey=None, scale=1):
    fullname = os.path.join(data_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()

# Default code which loads a sound as a pygame image with the default path
def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()

    fullname = os.path.join(data_dir, name)
    sound = pg.mixer.Sound(fullname)

    return sound

# Function which takes the boards matrix (matrix of pieces represented by integers)
# turns it into a matrix of object instances 
def make_board(orig):
    bong = []
    # Goes through the entire array piece by piece

    # First by the horizontal/ rank
    if orig[0][0] == 0:
            bong = [0]
            bong = bong * 63
            bong.append(Dot(0))
            return np.reshape(bong, (8,8))

    for i, line in enumerate(orig):

        
        # Then within rank, it goes by "file"
        for j, piece in enumerate(line):
            # If it's length is 1, it has to be a 0 and is a pawn
            if len(str(piece)) == 1:
                bong.append(0)
            # If it has a 1 for the second digit, it is a pawn
            elif str(piece)[1] == str(1):
                bong.append(Fishie(piece))
            # If it has a 2 for the second digit, it is a groundhog
            elif str(piece)[1] == str(2):
                bong.append(Groundhog(piece))
            # If it has a 3 for the second digit, it is a Birdie/knight
            elif str(piece)[1] == str(3):
                #bong.append(Knight)
                bong.append(Rat(piece))
            # If it has a 4 for the second digit, it is a bishop 
            elif str(piece)[1] == str(4):
                #bong.append(Bishop)
                bong.append(Snake(piece))
            # If it has a 5 for the second digit, it is a King
            elif str(piece)[1] == str(5):
                #bong.append(King)
                bong.append(King(piece))
            # If it has a 6 for the second digit, it is a Queen
            elif str(piece)[1] == str(6):
                #bong.append(Queen)
                bong.append(Queen(piece))
            else:
                bong.append(0)
    
    return np.reshape(bong, (8,8))

def blit_board(board, screen):
    # Goes through the matrix and blits (prints) the image of that piece to the screen
    # Does this through using the image variable within each instance of a piece
    for column, file in enumerate(board):
        for spot, square in enumerate(file):
            if type(square) is int or type(square) is float: continue

            elif int(square.name) >= 1000:
                screen.blit(square.image, (dot_spaces[spot],dot_spaces[column]))
            else:
                screen.blit(square.image, (piece_spaces[spot],piece_spaces[column]))

def check_range(num):
    # Goes through the cursor ranges and it finds which one the input number is in
    # Returns index/which number range it is in/which square it is in
    for ind,rng in enumerate(cursor_range):
        if num in range(rng[0],rng[1]):
            return ind

def nice(x : int, y : int, typee, ofset_x=0, ofset_y=0, inp=None):
    '''
    Parameters:
    ----------
    x : int
        X coordinate of the piece.
    y : int
        Y coordinate of the piece.
    typee : int
        Type of conversion/information request. 

        1: Return color of piece (not racist)
        2: Change dtos - Need inp then Change dotes
        4: Change boards - Need inp
        5: Change Piece
    ofset_x : int
        How far the piece that you want the information of is from the piece
        Optional, default is 0 - checking the piece specified in x,y
    ofset_y : int
        How far the piece that you want the information of is from the piece
        Optional, default is 0 - checking the piece specified in x,y

    Output:
    ------
    Type 1:
        Str : color of piece (1 or 2)
    Type 2: 
        Just changes variables
    
    '''
    if (x + ofset_x not in range(0,8)) or (y + ofset_y not in range(0,8)):
        return None
    

    if typee==1:
        return str(boards[x+ofset_x, y + ofset_y]).lstrip('[')[0]
    elif typee==2:
        dtos[x+ofset_x, y+ofset_y] = inp
        if int(dtos[x+ofset_x, y+ofset_y]) != 0:
            dotes[x+ofset_x, y+ofset_y] = Dot(dtos[x+ofset_x, y+ofset_y])
            return
        else:
            dotes[x+ofset_x, y+ofset_y] = 0
            return

    elif typee==3:
        return int(str(boards[x+ofset_x, y + ofset_y]).lstrip('[')[1])

        
        
    #elif typee==3:
    #    if dtos[x+ofset_x, y+ofset_y] != 0:
    #        dotes[x+ofset_x, y+ofset_y] = Dot(dtos[x+ofset_x, y+ofset_y])
    #    else:
    #        dotes[x+ofset_x, y+ofset_y] = 0
    #    return





#def check_square(x,y,opt):



# Example class

# Fishie class

class Dot(pg.sprite.Sprite):
    def __init__(self, name):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(pg.image.load('data/dote.png'), (30,30))
        self.image.set_alpha(175)
        self.rect = (30,30)  
        self.name = name


dotes = make_board(dtos)
pieces = []

class Fishie(pg.sprite.Sprite):
    # ttvtommyinit
    def __init__(self, name):
        self.name = name
        self.box = np.where(boards == int(self.name))
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        if nice(self.box[0],self.box[1],1) == '1':
            self.image = pg.transform.scale(pg.image.load('data/Goldfish_white.png'), (50,50))
        else: 
            self.image = pg.transform.scale(pg.image.load('data/Goldfish_black.png'), (50,50))
        self.rect = (50,50)

    # Creates the dots of possible moves for a pawn
    def create_moves(self):
        # determines which color it is (for top or bottom)
        if str(self.name)[0] == '1': #White
            if nice(self.box[0], self.box[1], 1, 1, 0) == '0':
                nice(self.box[0], self.box[1], 2, 1, 0, int(str(self.name) + '00'))
                if self.box[0] == 1:
                    nice(self.box[0], self.box[1], 2, 2, 0, int(str(self.name) + '01'))
            
            if nice(self.box[0], self.box[1], 1, 1, -1) == '2':
                nice(self.box[0], self.box[1], 2, 1, -1, int(str(self.name) + '02'))
            if nice(self.box[0], self.box[1], 1, 1, 1) == '2':
                nice(self.box[0], self.box[1], 2, 1, 1, int(str(self.name) + '03'))


        elif str(self.name)[0] == '2': # Black
            if nice(self.box[0], self.box[1], 1, -1, 0) == '0':
                nice(self.box[0], self.box[1], 2, -1, 0, int(str(self.name) + '00'))

            if self.box[0] == 6:
                nice(self.box[0], self.box[1], 2, -2, 0, int(str(self.name) + '01'))
            
            if nice(self.box[0], self.box[1], 1, -1, -1) == '1':
                nice(self.box[0], self.box[1], 2, -1, -1, int(str(self.name) + '02'))
            if nice(self.box[0], self.box[1], 1, -1, 1) == '1':
                nice(self.box[0], self.box[1], 2, -1, 1, int(str(self.name) + '03'))

          


        
        
    
    # Removes the moves created
    def close_moves(self):
        # determines which color it is (for top or bottom)
        if str(self.name)[0] == '1': #White
            # Takes the box that is one below the box of the piece and places a number
            # Which is 4 digits, and has the identifier appended to the end of the piece name
            if self.box[0] == 7:
                boards[self.box[self.box[0], self.box[1]]] = int('16' + str(self.name)[-1])
                pieces[self.box[self.box[0], self.box[1]]] = Queen(str(boards[self.box[self.box[0], self.box[1]]]))
            dtos[self.box[0] + 1,self.box[1]] = 0
            dotes[self.box[0] + 1, self.box[1]] = 0
            # If it is on the 2nd or 7th rank then it can move two spaces so it adds that box
            if (self.box[0] == 1):
                dtos[self.box[0] + 2,self.box[1]] = 0
                dotes[self.box[0] + 2, self.box[1]] = 0
            
            nice(self.box[0], self.box[1], 2, 1, -1, 0)
            #nice(self.box[0], self.box[1], 3, 1, -1)

            nice(self.box[0], self.box[1], 2, 1, 1, 0)
            #nice(self.box[0], self.box[1], 3, 1, 1)
            

        elif str(self.name)[0] == '2': # Black
            # Takes the box that is one above the box of the piece and places a number
            # Which is 4 digits, and has the identifier appended to the end of the piece name
            if self.box[0] == 0:
                boards[self.box[self.box[0], self.box[1]]] = int('26' + str(self.name)[-1])
                pieces[self.box[self.box[0], self.box[1]]] = Queen(str(boards[self.box[self.box[0], self.box[1]]]))
            
            dtos[self.box[0] - 1,self.box[1]] = 0
            dotes[self.box[0] - 1, self.box[1]] = 0
            # If it is on the 2 or 7th rank then it can move two spaces so it adds that box
            if (self.box[0] == 6):
                dtos[self.box[0] - 2,self.box[1]] = 0
                dotes[self.box[0] - 2, self.box[1]] = 0
            
            nice(self.box[0], self.box[1], 2, -1, -1, 0)
            #nice(self.box[0], self.box[1], 3, -1, -1)
            nice(self.box[0], self.box[1], 2, -1, 1, 0)
            #nice(self.box[0], self.box[1], 3, -1, 1)


class Groundhog(pg.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        self.box = np.where(boards == int(self.name))
        pg.sprite.Sprite.__init__(self)
        if nice(self.box[0],self.box[1],1) == '1':
            self.image = pg.transform.scale(pg.image.load('data/white_walrus.png'), (50,50))
        else: 
            self.image = pg.transform.scale(pg.image.load('data/black_walrus.png'), (50,50))
        self.rect = (50,50)

    def create_moves(self):
        clr = nice(self.box[0], self.box[1], 1)
        if (nice(self.box[0], self.box[1], 1, 1, 0) != clr) and (nice(self.box[0], self.box[1], 1, 2, 0) != clr):
            nice(self.box[0], self.box[1], 2, 2, 0, int(str(self.name) + '00'))
    
        if (nice(self.box[0], self.box[1], 1, -1, 0) != clr) and (nice(self.box[0], self.box[1], 1, -2, 0) != clr):
            nice(self.box[0], self.box[1], 2, -2, 0, int(str(self.name) + '01'))

        if (nice(self.box[0], self.box[1], 1, 0, 1) != clr) and (nice(self.box[0], self.box[1], 1, 0, 2) != clr):
            nice(self.box[0], self.box[1], 2, 0, 2, int(str(self.name) + '02'))

        if (nice(self.box[0], self.box[1], 1, 0, -1) != clr) and (nice(self.box[0], self.box[1], 1, 0, -2) != clr):
            nice(self.box[0], self.box[1], 2, 0, -2, int(str(self.name) + '03'))

        
        

        for i in range(-1, 2):
            for j in range(-1,2):
                if nice(self.box[0], self.box[1], 1, i, j) == '0':
                    nice(self.box[0], self.box[1], 2, i, j, int(str(self.name) + str(naming_nums[(i,j)])))



    # Removes the moves created
    def close_moves(self):
        nice(self.box[0], self.box[1], 2, 2, 0, 0)
        nice(self.box[0], self.box[1], 2, -2, 0, 0)
        nice(self.box[0], self.box[1], 2, 0, 2,0)
        nice(self.box[0], self.box[1], 2, 0, -2, 0)

        for i in range(-1, 2):
            for j in range(-1,2):
                nice(self.box[0], self.box[1], 2, i, j, 0)        

        
class Queen(pg.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        self.box = np.where(boards == int(self.name))
        pg.sprite.Sprite.__init__(self)
        if nice(self.box[0],self.box[1],1) == '1':
            self.image = pg.transform.scale(pg.image.load('data/white_queen.png'), (50,50))
        else: 
            self.image = pg.transform.scale(pg.image.load('data/black_queen.png'), (50,50))
        self.rect = (50,50)

    def create_moves(self):
        clr = nice(self.box[0], self.box[1], 1)

        stop = None
        

        for i in range(-1, 2):
            for j in range(-1,2):
                for k in range(1,8):
                    if nice(self.box[0], self.box[1], 1, i * k, j * k) != '0':
                        if nice(self.box[0], self.box[1], 1, i * k, j * k) != clr:
                            stop = k + 1
                        else:
                            stop = k
                        break
                for l in range(1, stop):
                    nice(self.box[0], self.box[1], 2, i * l, j * l, int(str(self.name) + str(naming_nums[(i,j)] - 10)  + str(l)))




    # Removes the moves created
    def close_moves(self):
        
        for i in range(-1, 2):
            for j in range(-1,2):
                for k in range(1,9):
                    nice(self.box[0], self.box[1], 2, i*k, j*k, 0)
        

class King(pg.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        self.box = np.where(boards == int(self.name))
        pg.sprite.Sprite.__init__(self)
        if nice(self.box[0],self.box[1],1) == '1':
            self.image = pg.transform.scale(pg.image.load('data/white_king.png'), (50,50))
        else: 
            self.image = pg.transform.scale(pg.image.load('data/black_king.png'), (50,50))
        self.rect = (50,50)

    def create_moves(self):
        clr = nice(self.box[0], self.box[1], 1)
        

        for i in range(-1, 2):
            for j in range(-1,2):
                if nice(self.box[0], self.box[1], 1, i, j) != clr:
                    nice(self.box[0], self.box[1], 2, i, j, int(str(self.name) + str(naming_nums[(i,j)])))






    # Removes the moves created
    def close_moves(self):
        
        for i in range(-1, 2):
            for j in range(-1,2):
                nice(self.box[0], self.box[1], 2, i, j, 0)
        

class Rat(pg.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        self.box = np.where(boards == int(self.name))
        pg.sprite.Sprite.__init__(self)
        if nice(self.box[0],self.box[1],1) == '1':
            self.image = pg.transform.scale(pg.image.load('data/white_rat.png'), (50,50))
        else: 
            self.image = pg.transform.scale(pg.image.load('data/black_rat.png'), (50,50))
        self.rect = (50,50)

    def create_moves(self):
        clr = nice(self.box[0], self.box[1], 1)
        
        for i in range(-1, 2):
            for j in range(-1,2):
                if (nice(self.box[0], self.box[1], 1, i, j) != '0') and (nice(self.box[0], self.box[1], 1, i * 2, j* 2) != clr):
                    nice(self.box[0], self.box[1], 2, i*2, j * 2, int(str(self.name) + str(naming_nums[(i,j)] - 10) + '0'))
        
        

        for i in range(-1, 2):
            for j in range(-1,2):
                if nice(self.box[0], self.box[1], 1, i, j) == '0':
                    nice(self.box[0], self.box[1], 2, i, j, int(str(self.name) + str(naming_nums[(i,j)])))



    # Removes the moves created
    def close_moves(self):
        for i in range(-1, 2):
            for j in range(-1,2):   
                nice(self.box[0], self.box[1], 2, i*2, j * 2, 0)
        
        

        for i in range(-1, 2):
            for j in range(-1,2):
                nice(self.box[0], self.box[1], 2, i, j, 0)    

class Snake(pg.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        self.box = np.where(boards == int(self.name))
        pg.sprite.Sprite.__init__(self)
        if nice(self.box[0],self.box[1],1) == '1':
            self.image = pg.transform.scale(pg.image.load('data/white_snake.png'), (50,50))
        else: 
            self.image = pg.transform.scale(pg.image.load('data/black_snake.png'), (50,50))
        self.rect = (50,50)

    def create_moves(self):
        clr = nice(self.box[0], self.box[1], 1)

        stop = None
        

        for i in range(-1, 2, 2):
            for j in range(-1,2, 2):
                for k in range(1,9):
                    if nice(self.box[0], self.box[1], 1, i * k, j * k) != '0':
                        if nice(self.box[0], self.box[1], 1, i * k, j * k) != clr:
                            stop = k + 1
                        else:
                            stop = k
                        break
                for l in range(1, stop):
                    nice(self.box[0], self.box[1], 2, i * l, j * l, int(str(self.name) + str(naming_nums[(i,j)] - 10) + str(l)))





    # Removes the moves created
    def close_moves(self):
        
        for i in range(-1, 2, 2):
            for j in range(-1,2, 2):
                for k in range(1,8):
                    nice(self.box[0], self.box[1], 2, i*k, j*k, 0)


pieces = make_board(boards) # Turns numbers into object instances


def main():
    """this function is called when the program starts.
    it initializes everything it needs, then runs in
    a loop until the function returns."""
    
    
    print(pieces)
    # Initialize Everything
    pg.init()
    screen = pg.display.set_mode((600, 600), pg.SCALED)
    pg.display.set_caption("CHESS 3 FTW")
    pg.mouse.set_visible(True)

    # Create The Background
    board = pg.transform.scale(pg.image.load('data/BlueBoard.png'), screen.get_size()) # Loads in board as pygame image
    
    
    # Put Text On The Background, Centered

    # Display The Background
    screen.blit(board, (0, 0)) # displays board to screen
    pg.display.flip()

    clock = pg.time.Clock()
    prev_box = None 
    cur_box = None
    dotes[7,7] = 0
    turn = '1'

    # Main Loop
    going = True
    while going:
        clock.tick(60)

        # Handle Input Events
        for event in pg.event.get(): # Quits the game
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
            if event.type == pg.KEYDOWN and event.key == pg.K_e:
                rt = True
                turn = turn_dict[turn]
        
        if (list(np.where(boards == 150)[0]) == []) or  (list(np.where(boards == 250)[0]) == []):
            going = False

        
        if pg.mouse.get_pressed(3)[0] == True: # If the main mouse button pressed
            mouse_pos = pg.mouse.get_pos() # Gets mouse coordinate
            cur_box = check_range(mouse_pos[1]), check_range(mouse_pos[0]) # Inputs the box which the mouse is in
            # Moves piece
            
            if (type(pieces[cur_box[0]][cur_box[1]]) != int) or (type(dotes[cur_box[0]][cur_box[1]]) != int): # If it is a 0, do nothing
                
                if (type(dotes[cur_box[0]][cur_box[1]]) != int) and (dotes[cur_box[0]][cur_box[1]].name >= 10000) and (prev_box != cur_box):
                    piece_move = str(int(dotes[cur_box[0]][cur_box[1]].name))[:-2]
                    ind1, ind2 = np.where(boards == int(piece_move))
                    ind1 = int(ind1); ind2 = int(ind2)
                    if str(pieces[ind1][ind2].name)[1] == '2': # Walrus
                        pieces[ind1][ind2].close_moves()
                        if abs(ind1-cur_box[0]) == 2:
                            spt = int(np.average([ind1,cur_box[0]]))
                            boards[spt][int(ind2)] = 0
                            pieces[spt][int(ind2)] = 0
                        elif abs(ind2-cur_box[1]) == 2:
                            spt = int(np.average([ind2,cur_box[1]]))
                            boards[int(ind1)][spt] = 0
                            pieces[int(ind1)][spt] = 0

                        boards[cur_box[0]][cur_box[1]] = int(piece_move)
                        pieces[cur_box[0]][cur_box[1]] = pieces[int(ind1),int(ind2)]
                        boards[int(ind1)][int(ind2)] = 0
                        pieces[int(ind1)][int(ind2)] = 0
                        pieces[cur_box[0],cur_box[1]].box = int(cur_box[0]),int(cur_box[1])
                        turn = turn_dict[turn]
                    elif str(pieces[ind1][ind2].name)[1] == '3':  # Rat
                        n = len(list(set(i for j in boards for i in j)))
                        pieces[ind1][ind2].close_moves()
                        boards[cur_box[0]][cur_box[1]] = int(piece_move)
                        pieces[cur_box[0]][cur_box[1]] = pieces[int(ind1),int(ind2)]
                        boards[int(ind1)][int(ind2)] = 0
                        pieces[int(ind1)][int(ind2)] = 0
                        pieces[cur_box[0],cur_box[1]].box = int(cur_box[0]),int(cur_box[1])
                        if rt == True:
                            turn = turn_dict[turn]
                        elif (abs(ind1-cur_box[0]) == 2) and (len(list(set(i for j in boards for i in j))) == n):
                            turn = turn
                        else: 
                            turn = turn_dict[turn]
                        
                    else:
                        pieces[ind1][ind2].close_moves()
                        boards[cur_box[0]][cur_box[1]] = int(piece_move)
                        pieces[cur_box[0]][cur_box[1]] = pieces[int(ind1),int(ind2)]
                        boards[int(ind1)][int(ind2)] = 0
                        pieces[int(ind1)][int(ind2)] = 0
                        pieces[cur_box[0],cur_box[1]].box = int(cur_box[0]),int(cur_box[1])
                        turn = turn_dict[turn]
                    print(boards)
                    print(np.where(boards == 150), np.where(boards == 260))
                # Creating moves
                elif str(pieces[cur_box[0]][cur_box[1]].name)[1] == '1' or '2': # If is a pawn, make the moves - later will be all pieces
                    #open dots
                    if (nice(cur_box[0], cur_box[1], 1) == turn):
                        if (prev_box != None) and (prev_box != cur_box) and (type(pieces[prev_box[0]][prev_box[1]]) != int): 
                            pieces[prev_box[0]][prev_box[1]].close_moves() # closes movement

                        pieces[cur_box[0]][cur_box[1]].create_moves() # Uses method to make moves
                    print(boards)

                    
            
                #if (prev_box != None) and (prev_box != cur_box) and (type(pieces[prev_box[0]][prev_box[1]]) != int): # if clicked (nested if) and the previous box has been set and the previous box and current box are different
                #    pieces[prev_box[0]][prev_box[1]].close_moves() # closes movement

            
            
          

        

        # Draw Everything
        screen.blit(board, (0, 0))
        blit_board(pieces, screen) # Custom function which prints the entire board to the screen
        blit_board(dotes, screen)
        pg.display.flip()

        prev_box = cur_box
        rt = False

    
    pg.quit()


# Game Over


# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    main()