import pygame as pg
import os 
import numpy as np
from sympy import Range

if not pg.font:
    print("Warning, fonts disabled")
if not pg.mixer:
    print("Warning, sound disabled")


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

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

cursor_range = [(0,73), (73, 148), (148, 223), (223, 298), (298, 373), (373,448), (448, 523), (523, 598)]


# Digit 1 : Which instance of that piece it is
# Digit 2 : 1 = Pawn, 2 = Rook, 3 = Knight, 4 = Bishop, 5 = King, 6 = Queen, 9 = Dot
# Digit 3 : 1 = White, 2 = Black
boards = np.array([
    [120, 130, 140, 150, 160, 141, 131, 121],
    [110, 111, 112, 113, 114, 115, 116, 117]
])
boards = np.append(boards, np.zeros((4, 8)), 0)
boards = np.append(boards, np.array([[210, 211, 212, 213, 214, 215, 216, 217],[220, 230, 240, 250, 260, 241, 231, 221]]), 0)
print(boards)




#boards[1][3] = 12
#x,y = np.where(boards == 12)
#x = int(x); y = int(y)


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

def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()

    fullname = os.path.join(data_dir, name)
    sound = pg.mixer.Sound(fullname)

    return sound

def make_board(orig):
    bong = []
    for i, line in enumerate(orig):
        for j, piece in enumerate(line):
            if str(piece)[1] == str(1):
                bong.append(Fishie(piece))
            elif str(piece)[1] == str(2):
                bong.append(Groundhog(piece))
            elif str(piece)[1] == str(3):
                #bong.append(Knight)
                bong.append(3)
            elif str(piece)[1] == str(4):
                #bong.append(Bishop)
                bong.append(4)
            elif str(piece)[1] == str(5):
                #bong.append(King)
                bong.append(5)
            elif str(piece)[1] == str(6):
                #bong.append(Queen)
                bong.append(6)
            else:
                bong.append(0)
                print(str(piece)[1])
    
    return np.reshape(bong, (8,8))

def blit_board(board, screen):
    #screen.blit(img, (x,y))

    for column, file in enumerate(board):
        for spot, square in enumerate(file):
            if type(square) != int:
                screen.blit(square.image, (piece_spaces[spot],piece_spaces[column]))

def check_range(num):
    for ind,rng in enumerate(cursor_range):
        if num in range(rng[0],rng[1]):
            return ind

class Fist(pg.sprite.Sprite):
    """moves a clenched fist on the screen, following the mouse"""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image("fist.bmp", -1)
        self.fist_offset = (-235, -80)
        self.punching = False

    def update(self):
        """move the fist based on the mouse position"""
        pos = pg.mouse.get_pos()
        self.rect.topleft = pos
        self.rect.move_ip(self.fist_offset)
        if self.punching:
            self.rect.move_ip(15, 25)

    def punch(self, target):
        """returns true if the fist collides with the target"""
        if not self.punching:
            self.punching = True
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        """called to pull the fist back"""
        self.punching = False


class Chimp(pg.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
    monkey when it is punched."""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image("chimp.bmp", -1, 4)
        screen = pg.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 90
        self.move = 18
        self.dizzy = False

    def update(self):
        """walk or spin, depending on the monkeys state"""
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        """move the monkey across the screen, and turn at the ends"""
        newpos = self.rect.move((self.move, 0))
        if not self.area.contains(newpos):
            if self.rect.left < self.area.left or self.rect.right > self.area.right:
                self.move = -self.move
                newpos = self.rect.move((self.move, 0))
                self.image = pg.transform.flip(self.image, True, False)
        self.rect = newpos

    def _spin(self):
        """spin the monkey image"""
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = False
            self.image = self.original
        else:
            rotate = pg.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        """this will cause the monkey to start spinning"""
        if not self.dizzy:
            self.dizzy = True
            self.original = self.image

class Fishie(pg.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        self.box = np.where(boards == int(name))
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = pg.transform.scale(pg.image.load('data/fishie.png'), (50,50)), (50,50)

    def create_moves(self):
        if str(self.name)[0] == '1':
            boards[self.box[0],self.box[1] - 1] = int(str(self.name) + '0')
            if self.box[0] == 2 or self.box[0] == 7:
                boards[self.box[0],self.box[1] - 2] = int(str(self.name) + '1')
        elif str(self.name)[0] == '2':
            boards[self.box[0],self.box[1] + 1] = int(str(self.name) + '0')
            if self.box[0] == 2 or self.box[0] == 7:
                boards[self.box[0],self.box[1] + 2] = int(str(self.name) + '1')

        if self.box[0] == 2 or self.box[0] == 7:
            boards[self.box[0],self.box[1] + 2] = int(str(self.name) + '1')

    def close_moves(self):
        boards[self.box[0],self.box[1] + 1] = 0

        if self.box[0] == 2 or self.box[0] == 7:
            boards[self.box[0],self.box[1] + 2] = 0

class Groundhog(pg.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = pg.transform.scale(pg.image.load('data/groundhog.png'), (50,50)), (50,50)

class Dot(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(pg.image.load('data/dote.png'), (30,30))
        self.image.set_alpha(175)
        self.rect = (30,30)  






def main():
    """this function is called when the program starts.
    it initializes everything it needs, then runs in
    a loop until the function returns."""
    pieces = make_board(boards)
    print(pieces)
    # Initialize Everything
    pg.init()
    screen = pg.display.set_mode((600, 600), pg.SCALED)
    pg.display.set_caption("Monkey Fever")
    pg.mouse.set_visible(True)

    # Create The Background
    board = pg.transform.scale(pg.image.load('data/BlueBoard.png'), screen.get_size())
    
    
    # Put Text On The Background, Centered

    # Display The Background
    screen.blit(board, (0, 0))
    pg.display.flip()

    fishie = Fishie('new')
    groundhog = Groundhog('anew')
    dote = Dot()
    allsprites = pg.sprite.RenderPlain([fishie, groundhog])
    clock = pg.time.Clock()
    prev_box = None
    # Main Loop
    going = True
    while going:
        clock.tick(60)

        # Handle Input Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
        
        if pg.mouse.get_pressed(3)[0] == True:
            mouse_pos = pg.mouse.get_pos()
            cur_box = check_range(mouse_pos[0]), check_range(mouse_pos[1])
            if str(pieces[cur_box[0]][cur_box[1]].name)[1] == '1':
                #open dots
                pieces[cur_box[0]][cur_box[1]].create_moves()
            
        
        if prev_box != cur_box:
            #close dots
            pieces[cur_box[0]][cur_box[1]].close_moves()

        else:
            cur_box = None
        
        allsprites.update()

        # Draw Everything
        screen.blit(board, (0, 0))
        blit_board(pieces, screen)
        screen.blit(dote.image, (dot_spaces[1], dot_spaces[1]))
        pg.display.flip()

        prev_box = cur_box
    pg.quit()


# Game Over


# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    main()