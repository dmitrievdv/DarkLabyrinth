import numpy,math
import sys,pygame
import random
from pygame.locals import *

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)

BUTTON_N = 0
BUTTON_PRESSED = pygame.USEREVENT+1
WIN = pygame.USEREVENT+2
MOVE_GHOSTS = pygame.USEREVENT+3
LOSE = pygame.USEREVENT+4

LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3

#pygame init
# if True: 
#     pygame.init()
#     size = width, height = 600, 600
#     screen = pygame.display.set_mode(size)

def translate_to_screen_coords(coords):
    screen_coords = (coords[0]*Main.width, coords[1]*Main.height)
    return screen_coords

def align_rect_coords(coords, rectsize, align):
    if align == "center":
        align_coords = (coords[0]-rectsize[0]//2, coords[1]-rectsize[1]//2)
        return align_coords
    if align == "left":
        align_coords = (coords[0], coords[1]-rectsize[1]//2)
        return align_coords
    if align == "right":
        align_coords = (coords[0]+rectsize[0], coords[1]-rectsize[1]//2)
        return align_coords
    
def get_indexes_in_direction(direction,i,j):
    indexes = [0,0]
    if direction == LEFT:
        indexes = [i-1,j]
    if direction == RIGHT:
        indexes = [i+1,j]
    if direction == UP:
        indexes = [i,j-1]
    if direction == DOWN:
        indexes = [i,j+1]
    return indexes

def inverse_direction(direction):
    if direction == LEFT:
        return RIGHT
    if direction == RIGHT:
        return LEFT
    if direction == UP:
        return DOWN
    if direction == DOWN:
        return UP

def off_edges(i,j,n):
    if i < 0 or i > n-1 or j < 0 or j > n-1:
        return True
    return False

def distance(coords1, coords2):
    return abs(coords1[0]-coords2[0])+abs(coords1[1]-coords2[1])

def generate_lab_border_alg(lab):
    n = lab.size
    border_cells = [[random.randint(0,Main.LABSIZE-1),\
                            random.randint(0,Main.LABSIZE-1)]]
    bn = len(border_cells)
    new_border_cells = []

    # build all walls that possible
    for i in range(n):
        for j in range(n): lab.cells[i][j].add_walls([LEFT, RIGHT, UP, DOWN])

    while bn > 0:
        # add new cells to the lab
        for i in range(bn):
            direction = random.randint(0,3)
            indexes = get_indexes_in_direction(direction, *border_cells[i])
            current = lab.cells[border_cells[i][0]][border_cells[i][1]]
            if not off_edges(*indexes, n=n): 
                new = lab.cells[indexes[0]][indexes[1]]
                if sum(new.walls) == 4:
                    current.del_walls([direction])
                    new.del_walls([inverse_direction(direction)])
                    border_cells.append(indexes)

        bn = len(border_cells)
        new_border_cells = []

        # get new borders of the lab
        for i in range(bn):
            delete = True
            # loop through all directions
            for direction in range(4):
                indexes = get_indexes_in_direction(direction, *border_cells[i])
                if off_edges(*indexes, n=n): continue
                new = lab.cells[indexes[0]][indexes[1]]
                # if there is a direction leading outside of the lab, this cell is lab's border
                if sum(new.walls) == 4: 
                    delete = False
            if not delete:
                new_border_cells.append(border_cells[i])

        border_cells = new_border_cells
        bn = len(border_cells)

    # if something wrong with lab border it will fix it
    lab.cells[0][0].walls[0] = 1
    lab.cells[0][0].walls[2] = 1

def generate_lab_path_alg(lab):
    # pygame.quit()
    # pygame.init()
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    path = []
    appendix = []
    n = lab.size
    n_path = len(path)
    directions = [LEFT, RIGHT, UP, DOWN]
    all_directions_bad = True

    for line in lab.cells:
        for current in line: current.add_walls([LEFT, RIGHT, UP, DOWN])

    for i in range(n):
        for j in range(n):
            current = lab.cells[i][j]
            current_indexes = [i, j]
            cap = 20 
            path = []
            appendix = []
            while not current.alg_bool:
                all_directions_bad = True
                for direction in directions:
                    indexes = get_indexes_in_direction(direction, *current_indexes)
                    if off_edges(*indexes, n=n): 
                        continue
                    new = lab.cells[indexes[0]][indexes[1]]
                    if sum(new.walls) == 4 or new.alg_bool:
                        all_directions_bad = False
                if not all_directions_bad and len(path)+1 < cap:
                    direction = random.randint(0,3)
                    indexes = get_indexes_in_direction(direction, *current_indexes)
                    if off_edges(*indexes, n=n): continue
                    new = lab.cells[indexes[0]][indexes[1]]
                    if sum(new.walls) == 4 or new.alg_bool:
                        current.del_walls([direction])
                        new.del_walls([inverse_direction(direction)])
                        path.append(current_indexes)
                        current_indexes = indexes
                        current = new
                        # lab.draw(screen, [n//2,n//2])
                        # pygame.time.wait(10)
                        # pygame.display.flip()
                        # screen.fill(black)
                elif i==0 and j==0 and len(path)+1==cap:
                    current.alg_bool = True
                else:
                    appendix.append(current_indexes)
                    current_indexes = path[-1]
                    current = lab.cells[current_indexes[0]][current_indexes[1]]
                    del path[-1]

            for indexes in path:
                current = lab.cells[indexes[0]][indexes[1]]
                current.alg_bool = True

            for indexes in appendix:
                current = lab.cells[indexes[0]][indexes[1]]
                current.alg_bool = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    quit()

            # lab.draw(screen, [n//2,n//2])
            # pygame.time.wait(200)
            # pygame.display.flip()
            # screen.fill(black)

def empty_lab(lab):
    n = lab.size
    for i in range(n):
        for j in range(n):
            lab.cells[i][j].walls = [0,0,0,0]


    i = 0
    for j in range(n): 
        lab.cells[i][j].walls[LEFT] = 1
        lab.cells[j][i].walls[UP] = 1
    i = n-1
    for j in range(n): 
        lab.cells[j][i].walls[DOWN] = 1
        lab.cells[i][j].walls[RIGHT] = 1

class GameState:
    def event_handler(self, event):
        if event.type == pygame.QUIT: 
            pygame.quit()
            quit()
        return self

    def draw(self):
        self.surface = screen
        fontTest = pygame.font.SysFont("monospace", 20)
        text = fontTest.render("Default GameState", True, (255,255,255))
        self.surface.blit(text,(0,100))
    
    def show(self):
        Main.screen.blit(self.surface, (0,0))

class TextBox:
    def __init__(self, text, coords, color, fonts = [("monospace", 20)], align = "center"):
        self.text = text
        self.coords = coords
        self.color = color
        self.fonts = fonts
        self.align = align

    def draw(self, surface):
        textsize = textwidth, textheight = (0, 0)
        screen_coords = translate_to_screen_coords(self.coords)
        for i in range(len(self.text)):
            if i < len(self.fonts):
                font = pygame.font.SysFont(*self.fonts[i])
            string = font.render(self.text[i], True, self.color)
            textsize = textwidth, textheight = font.size(self.text[i])
            screen_coords_i = (screen_coords[0], screen_coords[1] + textheight)
            screen_coords = screen_coords_i
            surface.blit(string,align_rect_coords(screen_coords_i, textsize, self.align))

class Button(TextBox):
    def __init__(self, text, coords, color, fonts = [("monospace", 20)], align = "center"):
        self.text = text
        self.align = align
        global BUTTON_N
        self.id = BUTTON_N
        BUTTON_N = BUTTON_N + 1
        self.coords = coords
        self.color = color
        self.noactivecolor = color
        self.activecolor = (abs(color[0]-255),\
                            abs(color[1]-255),\
                            abs(color[2]-255))
        self.fonts = fonts
        self.active = False
        self.event = pygame.event.Event(BUTTON_PRESSED, {"button" : self.id})

    def activate(self):
        if(not self.active):
            self.active = True
            self.color = self.activecolor
    
    def deactivate(self):
        if(self.active):
            self.active = False
            self.color = self.noactivecolor

    def press(self, inc = 0):
        if inc == 0:
            pygame.event.post(self.event)
        #pygame.time.set_timer(self.event, 100)

class Option(Button):
    def __init__(self, text, option_range, \
                coords, color, fonts = [("monospace", 20)], align = "center"):
        Button.__init__(self, text, coords, color,\
                     fonts, align)
        self.range = option_range
        self.option_index = 0

    def draw(self, surface):
        string = self.text[0]
        self.text[0] = string + ': ' + str(self.range[self.option_index])
        Button.draw(self, surface)
        self.text[0] = string

    def press(self, inc = 0):
        self.option_index += inc
        if self.option_index < 0: self.option_index = len(self.range) - 1
        if self.option_index > len(self.range) - 1: self.option_index = 0
        pygame.event.post(self.event)

class MainMenu(GameState):
    def __init__(self, title, *buttons):
        self.title = title
        self.buttons_n = len(buttons)
        self.buttons = buttons
        self.activebutton = -1

    def draw(self):
        self.surface = Main.screen
        self.title.draw(self.surface)
        for i in range(self.buttons_n):
            self.buttons[i-1].draw(self.surface)

    def button_press_handle(self):
        print(self.buttons[self.activebutton].text[0])
        if self.buttons[self.activebutton].text[0] == "OPTIONS":
            return options
        if self.buttons[self.activebutton].text[0] == "START GAME":
            ingame = InGame()
            gamestate = ingame
            return ingame
        if self.buttons[self.activebutton].text[0] == "CREDITS":
            return credits
        if self.buttons[self.activebutton].text[0] == "HELP":
            return help_menu
        if self.buttons[self.activebutton].text[0] == "QUIT":
            pygame.quit()
            quit()

    def event_handler(self, event):
        if event.type == pygame.QUIT: 
            pygame.quit()
            quit()
        if event.type == KEYDOWN:
            if event.key == K_w:
                if(self.activebutton == -1):
                    self.activebutton = 0
                    self.buttons[self.activebutton].activate()
                if(self.activebutton == 0):
                    self.buttons[self.activebutton].deactivate()
                    self.activebutton = self.buttons_n-1
                    self.buttons[self.activebutton].activate()
                else:
                    self.buttons[self.activebutton].deactivate()
                    self.activebutton = self.activebutton-1
                    self.buttons[self.activebutton].activate()
            if event.key == K_s:
                if(self.activebutton == -1):
                    self.activebutton = 0
                    self.buttons[self.activebutton].activate()
                if(self.activebutton == self.buttons_n-1):
                    self.buttons[self.activebutton].deactivate()
                    self.activebutton = 0
                    self.buttons[self.activebutton].activate()
                else:
                    self.buttons[self.activebutton].deactivate()
                    self.activebutton = self.activebutton+1
                    self.buttons[self.activebutton].activate()
            if event.key == K_SPACE:
                self.buttons[self.activebutton].press()
            if event.key == K_a:
                self.buttons[self.activebutton].press(-1)
            if event.key == K_d:
                self.buttons[self.activebutton].press(1)          
        if event.type == BUTTON_PRESSED:
            newstate = self.button_press_handle()
            # self.buttons[self.activebutton].deactivate()
            return newstate

        return self

class CreditsMenu(MainMenu):
    def __init__(self, text, *buttons, scroll_range = (0,0)):
        self.title = text
        self.buttons_n = len(buttons)
        self.buttons = buttons
        self.activebutton = -1
        self.minscroll, self.maxscroll = scroll_range
        if self.minscroll == self.maxscroll:
            self.minscroll = text.coords[1]
            self.maxscroll = text.coords[1]

    def button_press_handle(self):
        print(self.buttons[self.activebutton].text)
        if self.buttons[self.activebutton].text[0] == "BACK":
            # global gamestate 
            # gamestate = menu
            return menu

    def event_handler(self, event):
        if event.type == KEYDOWN:
            if event.key == K_UP:
                x,y = self.title.coords
                if y > self.minscroll:
                    self.title.coords = x, y-0.05
                    self.draw()
            if event.key == K_DOWN:
                x,y = self.title.coords
                if y < self.maxscroll:
                    self.title.coords = x, y+0.05
                    self.draw()  
        return super().event_handler(event)           


class OptionsMenu(MainMenu):
    def button_press_handle(self):
        button = self.buttons[self.activebutton]
        print(button.text[0])
        if button.text[0] == "BACK":
            return menu
        if button.text[0] == "RESOLUTION":
            return resolution
        if button.text[0] == "DIFFICULTY":
            return difficulty
        if button.text[0] == "LABSIZE":
            Main.LABSIZE = button.range[button.option_index]
            return self
        if button.text[0] == "ALGORITHM":
            Main.ALG = button.range[button.option_index]
            return self
        if button.text[0] == "CELL SIZE":
            Main.CELLSIZE = button.range[button.option_index]
            return self
        if button.text[0] == "TORCH PROBABILITY":
            Main.TORCH_PROP = button.range[button.option_index]
            return self
        if button.text[0] == "VISIBLE GHOSTS":
            Main.VISIBLE_GHOSTS = button.range[button.option_index]
            return self
        if button.text[0] == "GHOSTS' SPEED":
            Main.GHOSTS_SPEED = button.range[button.option_index]
            return self
        if button.text[0] == "GHOSTS NUMBER":
            Main.GHOSTS_NUM = button.range[button.option_index]
            return self

class WinMenu(MainMenu):
    def button_press_handle(self):
        print(self.buttons[self.activebutton].text[0])
        if self.buttons[self.activebutton].text[0] == "YES":
            # global gamestate 
            ingame = InGame()
            return ingame
        if self.buttons[self.activebutton].text[0] == "NO":
            # global gamestate
            # gamestate = menu
            return menu

class ResolutionMenu(MainMenu):
    def __init__(self, *buttons):
        self.buttons_n = len(buttons)
        self.buttons = buttons
        self.activebutton = -1

    def draw(self):
        self.surface = Main.screen
        for i in range(self.buttons_n):
            self.buttons[i-1].draw(self.surface)

    def button_press_handle(self):
        print(self.buttons[self.activebutton].text[0])
        if self.buttons[self.activebutton].text[0] == "BACK":
            return options
        if self.buttons[self.activebutton].text[0] == "300x300":
            Main.size = Main.width, Main.height = 300, 300
            Main.screen = pygame.display.set_mode(size)
            return options
        if self.buttons[self.activebutton].text[0] == "480x480":
            Main.size = Main.width, Main.height = 480, 480
            Main.screen = pygame.display.set_mode(Main.size)
            return options
        if self.buttons[self.activebutton].text[0] == "600x600":
            Main.size = Main.width, Main.height = 600, 600
            Main.screen = pygame.display.set_mode(Main.size)
            return options

class DifficultyMenu(ResolutionMenu):
    def button_press_handle(self):
        print(self.buttons[self.activebutton].text[0])
        if self.buttons[self.activebutton].text[0] == "BACK":
            # global gamestate 
            return options
        if self.buttons[self.activebutton].text[0] == "EASY":
            # global LABSIZE
            Main.LABSIZE = 30
            # global gamestate 
            return options
        if self.buttons[self.activebutton].text[0] == "NORMAL":
            # global LABSIZE
            Main.LABSIZE = 50
            # global gamestate 
            return options
        if self.buttons[self.activebutton].text[0] == "HARD":
            # global LABSIZE
            Main.LABSIZE = 70
            # global gamestate 
            return options

class Player:
    def __init__(self):
        self.torches = 0
        self.light_radius = 3
        i = random.randint(0, Main.LABSIZE-1)
        j = random.randint(0, Main.LABSIZE-1)
        self.coords = [i,j]

    def draw(self, surface):
        screen_center = (Main.width//2, Main.height//2)
        playersize = (Main.CELLSIZE//2 - 1)//2
        pygame.draw.line(surface, red, (screen_center[0]+playersize, \
                                           screen_center[1]+playersize), \
                                          (screen_center[0]-playersize, \
                                           screen_center[1]-playersize), 2)
        pygame.draw.line(surface, red, (screen_center[0]-playersize, \
                                           screen_center[1]+playersize), \
                                          (screen_center[0]+playersize, \
                                           screen_center[1]-playersize),2)

    def move(self, direction):
        global LEFT, RIGHT, UP, DOWN
        if direction == LEFT:
            self.coords[0] = self.coords[0] - 1
        if direction == RIGHT:
            self.coords[0] = self.coords[0] + 1
        if direction == UP:
            self.coords[1] = self.coords[1] - 1
        if direction == DOWN:
            self.coords[1] = self.coords[1] + 1

class Cell:
    def __init__(self):
        self.walls = []
        self.known = False
        self.walls = [0,0,0,0]
        #self.walls_visibility = [True,True,True,True]
        self.alg_bool = False
        self.known = False

    def __del__(self):
        del self.walls

    def draw(self, surface, cell_center, light):
        cellcize = Main.CELLSIZE//2
        cornerLU = (cell_center[0]-cellcize, cell_center[1]-cellcize)
        cornerLD = (cell_center[0]-cellcize, cell_center[1]+cellcize)
        cornerRU = (cell_center[0]+cellcize, cell_center[1]-cellcize)
        cornerRD = (cell_center[0]+cellcize, cell_center[1]+cellcize)
        
        color = (0,20*sum(light)//4,0)
        if 20*sum(light)//4 > 120: 
            color = (0, 120, 0)
        pygame.draw.polygon(surface, color, \
                    [cornerLU, cornerRU, cornerRD, cornerLD])

        # if self.known:
        #     color = (255*sum(light)//4,255*sum(light)//4,0)
        #     if 255*sum(light)//4 > 255: 
        #         color = (255, 255, 0)
        #     pygame.draw.circle(surface, color, cell_center, 2)

        
        color = [(0,0,0), (0,0,0), (0,0,0), (0,0,0)]
        for direction in [LEFT, RIGHT, UP, DOWN]:
            gr = 150*light[direction]
            if gr > 255: gr = 255
            color[direction] = (0,gr,0)


        if self.walls[LEFT] == 1:
            pygame.draw.line(surface, color[LEFT], cornerLD, cornerLU, 1)
        if self.walls[RIGHT] == 1:
            pygame.draw.line(surface, color[RIGHT], cornerRD, cornerRU, 1)
        if self.walls[UP] == 1:
            pygame.draw.line(surface, color[UP], cornerRU, cornerLU, 1)
        if self.walls[DOWN] == 1:
            pygame.draw.line(surface, color[DOWN], cornerLD, cornerRD, 1)



    def add_walls(self, directions):
        n = len(directions)
        for i in range(n):
            self.walls[directions[i]] = 1

    def del_walls(self, directions):
        n = len(directions)
        for i in range(n):
            self.walls[directions[i]] = 0

class Finish:
    def __init__(self):
        i = random.randint(0, Main.LABSIZE-1)
        j = random.randint(0, Main.LABSIZE-1)
        self.coords = [i,j]

    def draw(self, surface, player_coords):
        center = [0,0]
        player = [Main.width//2,Main.height//2]
        center[0] = (self.coords[0]-player_coords[0])*Main.CELLSIZE
        center[1] = (self.coords[1]-player_coords[1])*Main.CELLSIZE
        size = (Main.CELLSIZE//2 - 1)//2
        
        if abs(center[0]) > Main.width//2 or abs(center[1]) > Main.height//2:
            tx = (self.coords[0]-player_coords[0])*Main.CELLSIZE
            ty = (self.coords[1]-player_coords[1])*Main.CELLSIZE
            t = math.sqrt(pow(tx,2) + pow(ty,2))
            tx = tx/t; ty = ty/t
            pygame.draw.line(surface, yellow, (2*tx*Main.CELLSIZE + player[0],\
                                               2*ty*Main.CELLSIZE + player[1]),\
                                               (3*tx*Main.CELLSIZE + player[0],\
                                               3*ty*Main.CELLSIZE + player[1]))
        center[0] += Main.width//2
        center[1] += Main.height//2

        pygame.draw.line(surface, yellow, (center[0]+size, \
                                           center[1]+size), \
                                          (center[0]-size, \
                                           center[1]-size),2)
        pygame.draw.line(surface, yellow, (center[0]-size, \
                                           center[1]+size), \
                                          (center[0]+size, \
                                           center[1]-size),2)

class Labyrinth:
    def __init__(self, size):
        self.size = size
        self.cells = [[Cell() for i in range(self.size)]\
                                     for j in range(self.size)]

        self.visibility_mask = [[[False,False,False,False] for i in range(self.size)]\
                                        for j in range(self.size)]

        self.light = [[[False,False,False,False] for i in range(self.size)]\
                                        for j in range(self.size)]

        self.darkness = [[0 for i in range(self.size)]\
                                        for j in range(self.size)]

        if Main.ALG == "BORDER":
            generate_lab_border_alg(self)
        if Main.ALG == "PATHS":
            generate_lab_path_alg(self)
        if Main.ALG == "EMPTY": empty_lab(self)

    def __del__(self):
        del self.cells
        del self.visibility_mask
        del self.light
        del self.darkness

    def unrender_light(self, coords, rad):
        ic = coords[0]; jc = coords[1]
        for i in range(ic-rad, ic+rad+1):
            for j in range(jc-rad, jc+rad+1):
                if not off_edges(i, j, n=self.size):
                    self.light[i][j] = [0,0,0,0]

    def render_light(self, coords, rad):
        ic = coords[0]; jc = coords[1]
        darkness = 1.0 - self.darkness[ic][jc]
        l = 1
        if rad == 0: l = 0.01
        for d in [LEFT, RIGHT, UP, DOWN]:
            self.light[ic][jc][d] += l*darkness
        self.visibility_mask[ic][jc] = [True, True, True, True]
        for direction in [LEFT, RIGHT, UP, DOWN]:
            darkness = 1.0 - self.darkness[ic][jc]
            if direction == LEFT or direction == RIGHT:
                check_directions = [UP, DOWN]
            if direction == UP or direction == DOWN:
                check_directions = [RIGHT, LEFT]
            i = ic; j = jc
            for r in range(1,rad+1):
                indexes = get_indexes_in_direction(direction, i, j)
                if self.cells[i][j].walls[direction] == 0:
                    i = indexes[0]; j = indexes[1]
                    darkness *= 1.0 - self.darkness[i][j]
                    #self.light[i][j] = [1.0//pow(3,r), 1.0//pow(3,r), 1.0//pow(3,r), 1.0//pow(3,r)]
                    for d in [LEFT, RIGHT, UP, DOWN]:
                        self.light[i][j][d] += 1.0/pow(2,r)*darkness
                    self.visibility_mask[i][j] = [True, True, True, True]
                    front_darkness = darkness
                    for check_direction in check_directions:
                        if self.cells[i][j].walls[check_direction] == 0 and\
                                        r < rad:
                            indexes = get_indexes_in_direction(check_direction, i, j)
                            ich = indexes[0]; jch = indexes[1]
                            darkness *= 1.0 - self.darkness[ich][jch]
                            self.light[ich][jch][direction] += 1.0/pow(2,r+1)*darkness
                            self.light[ich][jch]\
                                [inverse_direction(check_direction)] += 1.0/pow(2,r+1)*darkness
                            self.visibility_mask[ich][jch][direction] = True
                            self.visibility_mask[ich][jch]\
                                 [inverse_direction(check_direction)] = True
                            if r+2 <= rad:
                                if self.cells[ich][jch].walls[direction] == 0:
                                    indexes = get_indexes_in_direction(direction, ich, jch)
                                    ich2 = indexes[0]; jch2 = indexes[1]
                                    darkness *= 1.0 - self.darkness[ich2][jch2]
                                    self.light[ich2][jch2][check_direction] += 1.0/pow(2,r+2)*darkness
                                    self.light[ich2][jch2]\
                                             [inverse_direction(direction)] += 1.0/pow(2,r+2)*darkness
                                    self.visibility_mask[ich2][jch2][check_direction] = True
                                    self.visibility_mask[ich][jch]\
                                                       [inverse_direction(direction)] = True
                    darkness = front_darkness

    def render_darkness(self, coords, rad):
        ic = coords[0]; jc = coords[1]
        draw = (sum(self.light[ic][jc]) > 0)
        self.darkness[ic][jc] = 1
        for direction in [LEFT, RIGHT, UP, DOWN]:
            if direction == LEFT or direction == RIGHT:
                check_directions = [UP, DOWN]
            if direction == UP or direction == DOWN:
                check_directions = [RIGHT, LEFT]
            i = ic; j = jc
            for r in range(1,rad+1):
                indexes = get_indexes_in_direction(direction, i, j)
                if self.cells[i][j].walls[direction] == 0:
                    i = indexes[0]; j = indexes[1]
                    #self.light[i][j] = [1.0//pow(3,r), 1.0//pow(3,r), 1.0//pow(3,r), 1.0//pow(3,r)]
                    self.darkness[i][j] += 1.0/pow(2,r) 
                    if self.darkness[i][j] > 1.0:
                        self.darkness[i][j] = 1.0
                    for check_direction in check_directions:
                        indexes = get_indexes_in_direction(check_direction, i, j)
                        ich = indexes[0]; jch = indexes[1]
                        if self.cells[i][j].walls[check_direction] == 0 and\
                                  r < rad:
                            self.darkness[ich][jch] += 1.0/pow(2,r+2)
                            if self.darkness[ich][jch] > 1.0:
                                self.darkness[ich][jch] = 1.0
                            if r+2 <= rad:
                                indexes = get_indexes_in_direction(direction, ich, jch)
                                ich2 = indexes[0]; jch2 = indexes[1]
                                if self.cells[ich][jch].walls[direction] == 0:
                                    self.darkness[ich2][jch2] += 1.0/pow(2,r+3)
                                    if self.darkness[ich2][jch2] > 1.0:
                                        self.darkness[ich2][jch2] = 1.0
                else: break
        return draw

    def unrender_darkness(self, coords, rad):
        ic = coords[0]; jc = coords[1]
        for i in range(ic-rad, ic+rad+1):
            for j in range(jc-rad, jc+rad+1):
                if not off_edges(i, j, n=self.size):
                    self.darkness[i][j] = 0

    def draw_local(self, surface, player_coords, center_coords = [-1,-1], rad = 2):
        cell_center = [0,0]
        ic = player_coords[0]; jc = player_coords[1]
        if center_coords[0] >= 0: ic = center_coords[0]; jc = center_coords[1]

        # print(self.light[ic][jc])

        for i in range(ic-rad, ic+rad+1):
            for j in range(jc-rad, jc+rad+1):
                if not off_edges(i, j, Main.LABSIZE):
                    cell_center[0] = (i-player_coords[0])*Main.CELLSIZE \
                                                    + Main.width//2
                    cell_center[1] = (j-player_coords[1])*Main.CELLSIZE \
                                                    + Main.height//2
                    self.cells[i][j].draw(surface, cell_center, self.light[i][j])

    def draw(self, surface, player_coords):
        cell_center = [0,0]
        #print(self.visibility_mask[player_coords[0]][player_coords[1]])
        for i in range(self.size):
            for j in range(self.size):
                visibility = self.visibility_mask[i][j]
                cell_center[0] = (i-player_coords[0])*Main.CELLSIZE + Main.width//2
                cell_center[1] = (j-player_coords[1])*Main.CELLSIZE + Main.height//2
                self.cells[i][j].draw(surface, cell_center, visibility)
                #print(cell_center)

class Torch:
    def __init__(self, coords, ignited):
        self.coords = coords
        self.ignited = ignited
        self.armed = False

    def arm_disarm(self):
        self.armed = not self.armed

    def draw(self, surface, player_coords, light = [1,1,1,1]):
        rd = 130
        gr = 82
        l = sum(light)//4
        if not self.ignited:
            rd = rd*l 
            gr = gr*l

        if rd > 130: rd = 130
        if gr > 82: gr = 82

        color = (rd, gr, 0) 
        # armed_color = (rd, 0, 0)

        # if(self.armed):
        #     color = armed_color

        center = [0,0]
        center[0] = (self.coords[0]-player_coords[0])*Main.CELLSIZE + Main.width//2
        center[1] = (self.coords[1]-player_coords[1])*Main.CELLSIZE + Main.width//2

        pygame.draw.line(surface, color, (center[0]+Main.CELLSIZE//4, center[1]+Main.CELLSIZE//3),\
                                          (center[0]+Main.CELLSIZE//4, center[1]-Main.CELLSIZE//3))
        if self.ignited:
            if self.armed:
                pygame.draw.circle(surface, red, (center[0]+Main.CELLSIZE//4, center[1]-Main.CELLSIZE//3+1), 3)
            else:
                pygame.draw.circle(surface, yellow, (center[0]+Main.CELLSIZE//4, center[1]-Main.CELLSIZE//3+1), 3)
        else:
            rgb = 50
            rgb = rgb*l
            if rgb > 50: rgb = 50
            pygame.draw.circle(surface, (rgb,rgb,rgb), (center[0]+Main.CELLSIZE//4, center[1]-Main.CELLSIZE//3+1), 3)

    def ignite_torch(self):
        self.ignited = True

    def extinguish_torch(self):
        self.ignited = False

class Ghost:
    def __init__(self, coords):
        self.coords = coords
        self.visible = False
        self.back_direction = -1

    def move(self, direction):
        self.coords = get_indexes_in_direction(direction, *self.coords)

    def draw(self, surface, player_coords):
        center = [0,0]
        center[0] = (self.coords[0]-player_coords[0])*Main.CELLSIZE + Main.width//2
        center[1] = (self.coords[1]-player_coords[1])*Main.CELLSIZE + Main.height//2
        size = (Main.CELLSIZE//2 - 1)//2

        if Main.VISIBLE_GHOSTS:
            pygame.draw.line(surface, (20,20,20), (center[0]+size, \
                                               center[1]+size), \
                                              (center[0]-size, \
                                               center[1]-size),2)
            pygame.draw.line(surface, (20,20,20), (center[0]-size, \
                                               center[1]+size), \
                                              (center[0]+size, \
                                               center[1]-size),2)

class InGame(GameState):
    def __init__(self):
        self.torches = [] 
        self.ghosts = []
        pygame.time.set_timer(MOVE_GHOSTS, 1000//Main.GHOSTS_SPEED)
        # self.ghosts.append(Ghost([15,15]))
        self.player = Player()
        self.steps = 0
        self.known_cells = 0
        self.lab = Labyrinth(Main.LABSIZE)
        for k in range(Main.GHOSTS_NUM):
            i = random.randint(0, Main.LABSIZE-1)
            j = random.randint(0, Main.LABSIZE-1)
            while (distance(self.player.coords, [i,j]) < 10 or sum(self.lab.cells[i][j].walls) > 2):
                i = random.randint(0, Main.LABSIZE-1)
                j = random.randint(0, Main.LABSIZE-1)
            self.ghosts.append(Ghost([i,j]))
        self.place_random_torches()
        self.lab.render_light(self.player.coords, 3)
        self.event = pygame.event.Event(WIN)
        self.event_lose = pygame.event.Event(LOSE)
        self.finish = Finish()
        self.torches.append(Torch(self.finish.coords, True))
        self.lab.render_light(self.finish.coords, 3)
        self.set_walls_visibility()
        self.infos=[]
        self.infos.append("PLAYER COORDS: "+str(self.player.coords))
        self.infos.append("EXIT COORDS: "+str(self.finish.coords))
        self.infos.append("STEPS: " + str(self.steps))
        self.infos.append("VISITED CELLS: " + str(self.known_cells)\
                    + " (" + str((100*self.known_cells)//Main.LABSIZE//Main.LABSIZE) + "%)")
        self.infos.append("TORCHES REMAIN: " + str(self.player.torches))

        self.update_info()
    
    def __del__(self):
        print("Deleting InGame")
        del self.torches
        del self.ghosts
        del self.player
        del self.lab
        del self.event
        del self.event_lose
        del self.finish
        del self.infos

    def place_random_torches(self):
        for i in range(self.lab.size):
            for j in range(self.lab.size):
                if random.random() < Main.TORCH_PROP:
                    ign = random.randint(0,1)
                    self.torches.append(Torch([i,j], ign))

    def set_walls_visibility(self):
        # print(self.player.coords)
        self.lab.unrender_light(self.player.coords, self.player.light_radius)
        # self.lab.unrender_light(self.finish.coords, 3)
        for torch in self.torches:
            if torch.ignited:
                self.lab.unrender_light(torch.coords, 3)
        # self.lab.render_light(self.finish.coords, 3)
        self.lab.render_light(self.player.coords, self.player.light_radius)
        for torch in self.torches:
            if torch.ignited:
                self.lab.render_light(torch.coords, 3)
        # for ghost in self.ghosts:
        #     ghost.visible = self.lab.unrender_darkness(ghost.coords, 1)
        # for ghost in self.ghosts:
        #     ghost.visible = self.lab.render_darkness(ghost.coords, 1)
        #self.lab.set_walls_visibility(self.player.coords)
    
    def change_player_light_radius(self, rad):
        self.lab.unrender_light(self.player.coords, self.player.light_radius)
        self.player.light_radius = rad
        self.set_walls_visibility()

    def move_player(self, direction):
        i = self.player.coords[0]
        j = self.player.coords[1]
        if not self.lab.cells[i][j].known: self.known_cells += 1
        self.lab.cells[i][j].known = True
        self.lab.unrender_light(self.player.coords, 3)
        self.player.move(direction)
        self.steps = self.steps+1
        self.set_walls_visibility()
        # print(self.lab.darkness[self.player.coords[0]][self.player.coords[1]])
        self.update_info()
        for ghost in self.ghosts:
            if self.player.coords == ghost.coords:
                pygame.event.post(self.event_lose)

    def update_info(self):
        i = self.player.coords[0]
        j = self.player.coords[1]
        
        self.infos[0] = ("PLAYER COORDS: "+str(self.player.coords))
        self.infos[1] = ("EXIT COORDS: "+str(self.finish.coords))
        self.infos[2] = ("STEPS: " + str(self.steps))
        self.infos[3] = ("VISITED CELLS: " + str(self.known_cells)\
            + " (" + str((100*self.known_cells)//Main.LABSIZE//Main.LABSIZE) + "%)")
        self.infos[4] = ("TORCHES REMAIN: " + str(self.player.torches))
        
    def draw(self):
        self.surface = Main.screen
        self.lab.draw_local(self.surface, self.player.coords, rad = 3)
        self.lab.draw_local(self.surface, self.player.coords, self.finish.coords, 3)
        for torch in self.torches:
            self.lab.draw_local(self.surface, self.player.coords, torch.coords, 3)
        for torch in self.torches:
            torch.draw(self.surface, self.player.coords,\
                         light = self.lab.light[torch.coords[0]][torch.coords[1]])
        for ghost in self.ghosts:
            ghost.draw(self.surface, self.player.coords)
        self.player.draw(self.surface)
        self.finish.draw(self.surface,self.player.coords)

    def pick_up_torch(self, pickuper):
        for torch in self.torches:
            if torch.coords == pickuper.coords:
                self.torches.remove(torch)
                pickuper.torches += 1
                # self.lab.unrender_light(torch.coords, 3)
                self.set_walls_visibility()
                self.update_info()

    def place_ignite_extinguish_torch(self, placer):
        torch_already_exist = False
        coords = [placer.coords[0], placer.coords[1]]
        for torch in self.torches:
            if torch.coords == coords:
                torch_already_exist = True 
                if torch.ignited:
                    torch.extinguish_torch()
                else: torch.ignite_torch()
                self.set_walls_visibility()
        if not torch_already_exist and placer.torches > 0:
            torch = Torch(coords, True)
            self.torches += [torch]
            # self.lab.render_light(torch.coords, 3)
            self.set_walls_visibility()
            placer.torches -= 1

    def move_ghosts(self, rad = 1):
        rad_cap = rad+1 
        for ghost in self.ghosts:
            self.lab.unrender_darkness(ghost.coords, rad)
        self.set_walls_visibility()
        for ghost in self.ghosts:
            ic = ghost.coords[0]; jc = ghost.coords[1]
            lmax = 0
            maxdir = [0]
            for direction in [LEFT, RIGHT, UP, DOWN]:
                if direction == LEFT or direction == RIGHT:
                    check_directions = [UP, DOWN]
                if direction == UP or direction == DOWN:
                    check_directions = [RIGHT, LEFT]
                i = ic; j = jc
                for r in range(rad_cap):
                    if self.lab.cells[i][j].walls[direction] == 0:
                        indexes = get_indexes_in_direction(direction, i, j)
                        i = indexes[0]; j = indexes[1]
                        l = sum(self.lab.light[i][j])
                        if l > lmax:
                            maxdir = [direction]
                            lmax = l
                        elif l == lmax:
                            maxdir.append(direction)
                        if lmax > 0:
                            rad_cap = r+1 
                            break
                        for check_direction in check_directions:
                            indexes = get_indexes_in_direction(check_direction, i, j)
                            ich = indexes[0]; jch = indexes[1]
                            if self.lab.cells[i][j].walls[check_direction] == 0 and\
                                    r < rad:
                                l = sum(self.lab.light[ich][jch])
                                if l > lmax:
                                    maxdir = [direction]
                                    lmax = l
                                elif l == lmax:
                                    maxdir.append(direction)
                                if lmax > 0:
                                    rad_cap = r+2 
                                    break
                                if r+2 <= rad:
                                    indexes = get_indexes_in_direction(direction, ich, jch)
                                    ich2 = indexes[0]; jch2 = indexes[1]
                                    if self.lab.cells[ich][jch].walls[direction] == 0:
                                        l = sum(self.lab.light[ich2][jch2])
                                        if l > lmax:
                                            maxdir = [direction]
                                            lmax = l
                                        elif l == lmax:
                                            maxdir.append(direction)
                                        if lmax > 0:
                                            rad_cap = r+3
                                            break


            direction = maxdir[random.randint(0, len(maxdir)-1)]
            if self.lab.cells[ic][jc].walls[direction] == 0: 
                ghost.move(direction)
                ghost.back_direction = inverse_direction(direction)
                # print("Ghost move", direction, ghost.back_direction)
            elif sum(self.lab.cells[ic][jc].walls) == 3: 
                # print("Ghost: dead end", ghost.back_direction)
                ghost.move(ghost.back_direction)
                ghost.back_direction = inverse_direction(ghost.back_direction)
        for ghost in self.ghosts:
            for torch in self.torches:
                if ghost.coords == torch.coords:
                    self.lab.unrender_light(torch.coords, 3)
                    torch.extinguish_torch()
                    if(torch.armed):
                        self.ghosts.remove(ghost)
                        self.torches.remove(torch)
            if ghost.coords == self.player.coords:
                pygame.event.post(self.event_lose)
        for ghost in self.ghosts:
            self.lab.render_darkness(ghost.coords, rad)
        self.set_walls_visibility()

    def arm_disarm_torch(self, coords):
        for torch in self.torches:
            if torch.coords == coords:
                print("(Dis)armed")
                torch.arm_disarm()

    def event_handler(self, event):
        i = self.player.coords[0]
        j = self.player.coords[1]
        if event.type == KEYDOWN:
            if event.key == K_m:
                return Map(self, [i,j])
            if event.key == K_TAB:
                return Info(self, *self.infos)
            if event.key == K_ESCAPE:
                return menu
                print("&")
            if event.key == K_w:
                if self.lab.cells[i][j].walls[UP] == 0:
                    self.move_player(UP)
            if event.key == K_s:
                if self.lab.cells[i][j].walls[DOWN] == 0:
                    self.move_player(DOWN)
            if event.key == K_a:
                if self.lab.cells[i][j].walls[LEFT] == 0:
                    self.move_player(LEFT)
            if event.key == K_d:
                if self.lab.cells[i][j].walls[RIGHT] == 0:
                    self.move_player(RIGHT)
            if event.key == K_e:
                self.pick_up_torch(self.player)
            if event.key == K_l:
                if self.player.light_radius > 0:
                    self.change_player_light_radius(0)
                else: self.change_player_light_radius(3)
            if event.key == K_g:
                coords = [self.player.coords[0],self.player.coords[1]]
                ghost = Ghost(coords)
                # ghost.visible = self.lab.render_darkness(ghost.coords, 3)
                self.ghosts.append(Ghost(coords))
            if event.key == K_z:
                self.arm_disarm_torch(self.player.coords)
            if event.key == K_SPACE:
                self.place_ignite_extinguish_torch(self.player)
            if self.player.coords == self.finish.coords:
                pygame.event.post(self.event)
        if event.type == QUIT:
            pygame.quit()
            print("&")
            quit()
        if event.type == WIN:
            del self
            return win
        if event.type == LOSE:
            del self
            print("DEAD :(")
            return lose
        if event.type == MOVE_GHOSTS:
            self.move_ghosts(rad = 3)
        return self

class Map(GameState):
    def __init__(self, state, coords):
        self.state = state
        self.coords = coords

    def draw(self):
        self.surface = Main.screen
        self.state.lab.draw(self.surface, self.coords)
        self.state.finish.draw(self.surface, self.coords)
        for torch in self.state.torches:
            i = torch.coords[0]
            j = torch.coords[1]
            torch.draw(self.surface, self.coords, self.state.lab.visibility_mask[i][j])

    def event_handler(self, event):
        if event.type == QUIT:
            pygame.quit()
            quit()
        if event.type == KEYDOWN:
            if event.key == K_TAB:
                return Info(self.state, *self.state.infos)
            if event.key == K_m:
                return self.state
            if event.key == K_w:
                self.coords[1] -= 1
            if event.key == K_s:
                self.coords[1] += 1
            if event.key == K_a:
                self.coords[0] -= 1
            if event.key == K_d:
                self.coords[0] += 1
        return self

class Info(GameState):
    def __init__(self, state, *infos):
        self.state = state
        self.texts = []
        for i in range(len(infos)):
            textbox = TextBox([infos[i]], (0.1,0.3+0.05*i), white, align="left")
            self.texts.append(textbox)

    def draw(self):
        self.surface = Main.screen
        for text in self.texts:
            text.draw(self.surface)

    def event_handler(self, event):
        if event.type == QUIT:
            pygame.quit()
            quit()
        if event.type == KEYDOWN:
            if event.key == K_m:
                return Map(self.state,self.state.player.coords)
            if event.key == K_TAB:
                return self.state
        return self

class Main:

    LABSIZE = 30
    VISIBLE_GHOSTS = False
    GHOSTS_NUM = 10
    CELLSIZE = 25 # must be odd
    EMPTY_LAB = False
    GHOSTS_SPEED = 1
    TORCH_PROP = 0.01
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    ALG = "PATHS"
    

    def __init__(self):
        gamestate = GameState()
        pygame.init() 

    def fill(self, state):
        self.gamestate = state

    def event_handler(self, event):
        state = self.gamestate.event_handler(event)
        self.fill(state)

    def main(self):
        while True:
            for event in pygame.event.get():
                self.event_handler(event)
            

            self.gamestate.draw()
            self.gamestate.show()
            pygame.display.flip()
            self.screen.fill(black)


#state of the game. menu, pause, ingame...
gamestate = GameState() 

gamestart_button = Button(["START GAME"], (0.5,0.4), yellow)
options_button = Button(["OPTIONS"], (0.5,0.45), yellow)
credits_button = Button(["CREDITS"], (0.5,0.5), yellow)
help_button = Button(["HELP"], (0.5,0.55), yellow)
quit_button = Button(["QUIT"], (0.5,0.6), yellow)
mainmenu_text = TextBox(["MAIN MENU"], (0.5,0.3), white, [("monospace",30)])
menu = MainMenu(mainmenu_text, gamestart_button, options_button \
                , credits_button, help_button, quit_button)

credits_text = TextBox(["CREDITS:", "me", '', '', '' ,'' ,'' ,'' ,'' ,'', '', '',
'','','','','','','','','','', 
'  /|  |\            /|  |\   ',
'  /|  |\            /|  |\   ',
' / |  | \          / |  | \  ',
' | |  | |          | |  | |  ',
' \  \/  /  __  __  \  \/  /  ',
'  \    /  / /  \ \  \    /   ',
'   \  /   \ \__/ /   \  /    ',
'   \  /   /      \   \  /    ',
'  _ \ \__/ O    O \__/ / _   ',
'  \\\\ \___          ___/ //   ',
'_  \\\\___/  ______  \___//  _ ',
'\\\\  ----(          )----  // ',
' \\\\_____( ________ )_____//  ',
'  ~-----(          )-----~ _ ',
'   _____( ________ )_____  \\\\',
'  /,----(          )----  _//',
' //     (  ______  )     /  \\',
' ~       \        /      \  /',
'          \  __  /       / / ',
'           \    /       / /  ',
'            \   \      / /   ',
'             \   ~----~ /    ',
'              \________/     ',
'   Watch out for the BUGS!!! '
                        ], (0.55,0.4), white)
back_button = Button(["BACK"], (0.1,0.05), yellow)
credits = CreditsMenu(credits_text, back_button, scroll_range = (-0.85,0.4))

help_text = TextBox([
 'This is a simple labyrinth game.',
  'Your goal is to find the exit.',
  'The exit is marked by yellow "x", or, if not',
  'visible, the direction to it is shown with yellow line.',
  'The labyrinth is completly dark,',
  'use torches and your light to brightened your path.',
  'To enable/disable your light press "L".',
  'You can pickup torches by pressing "E".',
  'To place/ignite/extinguish torch press SPACE.',
  'But you are not alone. There are also ghosts.',
  'They roam across the darkness in search for light. ',
  'If they see any they will try to eat the source.',
  'The only way to see them is to notice the',
  'disapperence of light around them.',
  'You can hide your presence from them by pressing "L"',
  'But if the ghost is close enough it will still see you.',
  'You can kill ghosts by luring them into traps.',
  'To set the trap stand on the torch and press "Z".',
  'If a ghost eats this torch it will kill it.',
  'The trap-torch will disappear after this.',
  'For easier navigation you can press "M" to view',
  'the map of visited parts of the labyrinth.',
  'You can also press TAB to view the amount of torches',
  'left for placing and some stats.'
  ''], (0.5,0.1), white, [("monospace",17)])
help_menu = CreditsMenu(help_text, back_button)


options_text = TextBox(["OPTIONS"], (0.5,0.3), white, [("monospace",30)])
resolution_button = Button(["RESOLUTION"], (0.5,0.4), yellow)
difficulty_button = Button(["DIFFICULTY"],(0.5, 0.45), yellow)
labsize_option = Option(["LABSIZE"], list(range(30,110,10))+list(range(0,30,10)), (0.5, 0.45), yellow)
empty_option = Option(["EMPTY LAB"], [False, True], (0.5,0.5), yellow)
alg_option = Option(["ALGORITHM"], ["PATHS", "BORDER", "EMPTY"], (0.5,0.5), yellow)
cellsize_option = Option(["CELL SIZE"], list(range(25,37,2))+list(range(15,21,2)), (0.5,0.55), yellow)
torchprop_option = Option(["TORCH PROBABILITY"], [0.01, 0.02, 0.05, 0.0025, 0.005], (0.5,0.6), yellow)
ghosts_speed_option = Option(["GHOSTS' SPEED", "in cells per second"], list(range(1,11)),\
     (0.5, 0.65), yellow, [("monospace",20), ("monospace",10)])
ghosts_visible_option = Option(["VISIBLE GHOSTS"], [False, True], (0.5, 0.7), yellow)
ghosts_num_option = Option(["GHOSTS NUMBER"], list(range(10,16)) + list(range(0,10)), (0.5, 0.75), yellow)

options = OptionsMenu(options_text, back_button, resolution_button,
                         labsize_option, alg_option, cellsize_option, torchprop_option, 
                         ghosts_speed_option, ghosts_visible_option, ghosts_num_option)

small_resolution_button = Button(["300x300"], (0.5,0.4), yellow)
med_resolution_button = Button(["480x480"], (0.5,0.45), yellow)
big_resolution_button = Button(["600x600"], (0.5,0.5), yellow)
resolution = ResolutionMenu(back_button, small_resolution_button, med_resolution_button, \
                    big_resolution_button)

win_text = TextBox(["YOU WIN! RESTART?"], (0.5,0.3), white, [("monospace",30)])
yes_button = Button(["YES"], (0.5,0.4), yellow)
no_button = Button(["NO"], (0.5,0.45), yellow)
win = WinMenu(win_text, yes_button, no_button)

lose_text = TextBox(["YOU'VE BEEN EATEN! RESTART?"], 
                (0.5,0.3), white, [("monospace",30)])
lose = WinMenu(lose_text, yes_button, no_button)

easy_difficulty_button = Button(["EASY"], (0.5,0.4), yellow)
norm_difficulty_button = Button(["NORMAL"], (0.5,0.45), yellow)
hard_difficulty_button = Button(["HARD"], (0.5,0.5), yellow)
difficulty = DifficultyMenu(back_button, easy_difficulty_button, norm_difficulty_button, \
                    hard_difficulty_button)


main = Main()
main.fill(menu)

main.main()

