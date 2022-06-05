from argparse import Action
import json
from random import randint
import json
import pygame
pygame.init()
 
w = 1000
h = 600


w_world = 8000
h_bottom = 540

sc = pygame.display.set_mode((w,h), pygame.RESIZABLE)
WHITE = 255, 255, 255
GREEN = 0, 255, 0
BLACK = 0, 0, 0
YELLOW = 255, 255, 0
RED = 255, 0, 0

class WALL:
    def __init__(self,x,y,w,h) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
    def draw(self, sc, wx):
        pygame.draw.rect(sc, GREEN, (self.x - wx, self.y , self.w , self.h))


class WORLD:
    x_world = 0
    cell_size = 30
    tool_size = 60
    level_n = 0
    block_size = 60
    walls = []
    active_tool = 0

    tools = [
        (1,1),
        (1,2),
        (2,1),
        (2,2),
        (2,4),
        (4,2)
    ]

    def __init__(self):
        self.font = pygame.font.Font(None, 14)
        self._update_level_()

    def save_level(self):
        
        with open(self.level, 'w') as outfile:
            data = {'blocks':[]}
            for w in self.walls:
                block = {
                    'x':w.x,
                    'y':w.y,
                    'w':w.w,
                    'h':w.h
                }
                data['blocks'].append(block)
            json_string = json.dumps(data, indent=4)
            outfile.write(json_string)

    def load_level(self):
        self.clean_level()
        with open(self.level) as json_file:
            data = json.load(json_file)
            for block in data['blocks']:
                self.walls.append(WALL(block['x'], block['y'], block['w'], block['h']))
    

    def clean_level(self):
        self.walls.clear()

    def _update_level_(self):
        self.level = "level{}.json".format(self.level_n)
        self.level_info = self.font.render(self.level, True, WHITE)

    def level_up(self):
        self.level_n += 1
        self._update_level_()

    def level_down(self):
        if self.level_n > 0:
            self.level_n -= 1
            self._update_level_()

    def left(self):
        if self.x_world > 0:
            self.x_world -= self.block_size

    def right(self):
        if self.x_world<w_world-w:
            self.x_world += self.block_size

    def add_block(self, pos):
        x = pos[0] - pos[0]%(self.block_size/2) + self.x_world
        y = pos[1] - pos[1]%(self.block_size/2)
        if self.active_tool < len(self.tools):
            w = self.cell_size* self.tools[self.active_tool][0]
            h = self.cell_size* self.tools[self.active_tool][1]
            self.walls.append(WALL(x,y, w, h))
    
    def undo(self):
        self.walls.pop()

    def use_tool(self,x):
        self.active_tool = int(x/self.tool_size)
 
    def draw(self, sc):
        x,y=0,0
        for wall in self.walls:
            wall.draw(sc, self.x_world)
        while x<w:
            pygame.draw.line(sc,WHITE,(x,0),(x,h_bottom))
            x += self.block_size/2
        while y<h_bottom:
            pygame.draw.line(sc,WHITE,(0,y),(w,y))
            y += self.block_size/2
        sc.blit(self.level_info,(10,10))
        # small block
        for i in range(0,10):
            if i == self.active_tool:
                pygame.draw.rect(sc,RED,(i*self.tool_size,h_bottom, self.tool_size, self.tool_size),1,5)   
            else:
                pygame.draw.rect(sc,YELLOW,(i*self.tool_size,h_bottom, self.tool_size, self.tool_size),1,5)        
            if i < len(self.tools):
                WALL(i*self.tool_size + 10, h_bottom + 10,  10 * self.tools[i][0], 10 * self.tools[i][1]).draw(sc, 0)


                 
world = WORLD()

while 1:
    sc.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                world.save_level()
            if event.key == pygame.K_l:
                world.load_level()
            if event.key == pygame.K_n:
                world.clean_level()
            if event.key == pygame.K_u:
                world.undo()
            if event.key == pygame.K_LEFT:
                world.left()
            if event.key == pygame.K_RIGHT:
                world.right()
            if event.key == pygame.K_UP:
                world.level_up()
            if event.key == pygame.K_DOWN:
                world.level_down()
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if pos[1] < h_bottom:
                world.add_block(pos)
            else:
                world.use_tool(pos[0])    
    sc.fill(BLACK)
    world.draw(sc)
    pygame.display.flip()

