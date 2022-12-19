import pygame as pg
import os 
import numpy as np

if not pg.font:
    print("Warning, fonts disabled")
if not pg.mixer:
    print("Warning, sound disabled")


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

spaces = {
    0 : 12.5,
    1 : 87.5,
    2 : 162.5, 
    3 : 237.5,
    4 : 312.5,
    5 : 387.5,
    6 : 462.5,
    7 : 537.5
}

# Digit 1 : Which instance of that piece it is
# Digit 2 : 1 = Pawn, 2 = Rook, 3 = Knight, 4 = Bishop, 5 = King, 6 = Queen
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
                screen.blit(square.image, (spaces[spot],spaces[column]))

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
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = pg.transform.scale(pg.image.load('data/fishie.png'), (50,50)), (50,50)

class Groundhog(pg.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = pg.transform.scale(pg.image.load('data/groundhog.png'), (50,50)), (50,50)






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
    pg.mouse.set_visible(False)

    # Create The Background
    board = pg.transform.scale(pg.image.load('data/BlueBoard.png'), screen.get_size())
    
    
    # Put Text On The Background, Centered

    # Display The Background
    screen.blit(board, (0, 0))
    pg.display.flip()

    fishie = Fishie('new')
    groundhog = Groundhog('anew')
    allsprites = pg.sprite.RenderPlain([fishie, groundhog])
    clock = pg.time.Clock()

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

        allsprites.update()

        # Draw Everything
        screen.blit(board, (0, 0))
        blit_board(pieces, screen)
        pg.display.flip()

    pg.quit()


# Game Over


# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    main()