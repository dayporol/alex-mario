from argparse import Action
import json
from random import randint
import json
from re import X
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

all_goomba = pygame.image.load('goomba.png')


class WALL:
    def __init__(self,x,y,w,h,c=False) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c
        
    def draw(self, sc, wx):
        pygame.draw.rect(sc, GREEN, (self.x - wx, self.y , self.w , self.h))
        if self.c:
            pygame.draw.circle(sc, YELLOW, (self.x - wx + self.w//2, self.y+self.h//2) , 5)
            pygame.draw.circle(sc, BLACK, (self.x - wx + self.w//2, self.y+self.h//2) , 6, 2)
    
class PIPE:

    def __init__(self, x, y, W=110, H=None):
        self.x = x
        self.y = y
        self.W = W
        self.H = H if H else h_bottom-y

    def draw(self, sc, wx):
        pygame.draw.rect(sc, GREEN,(self.x - wx, self.y , self.W, self.H ))
        pygame.draw.rect(sc, BLACK,(self.x - wx, self.y , self.W, self.H ), 3)
        pygame.draw.rect(sc, GREEN,(self.x - wx - 7, self.y  , self.W + 14, 25 ))
        pygame.draw.rect(sc, BLACK,(self.x - wx - 10, self.y , self.W + 19, 25), 3, 3)

#GOOMBA
class GOOMBA:
    sz_y = 46
    sz_x = 46

    texture = (33, 11)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def draw(self,sc, wx):
        sc.blit(all_goomba,(self.x - wx, self.y), self.texture + (self.sz_x, self.sz_y) )



class WORLD:
    x_world = 0
    cell_size = 30
    tool_size = 60
    level_n = 0
    block_size = 60
    walls = []
    goombas = []
    pipes = []
    active_tool = 0

        

    tools = [
        {'type': 'wall', 'size': (1,1) ,'has_coin':0},
        {'type': 'wall', 'size': (1,2) ,'has_coin':0},
        {'type': 'wall', 'size': (2,1) ,'has_coin':0},
        {'type': 'wall', 'size': (2,2) ,'has_coin':0},
        {'type': 'wall', 'size': (2,2) ,'has_coin':1},
        {'type': 'wall', 'size': (2,4) ,'has_coin':0},
        {'type': 'wall', 'size': (4,2) ,'has_coin':0},
        {'type': 'goomba'},
        {'type': 'pipe'},

    ]

    def __init__(self):
        self.font = pygame.font.Font(None, 14)
        self._update_level_()


    def save_level(self):
        
        with open(self.level, 'w') as outfile:
            data = {'blocks':[],'goombas':[], 'pipes':[]}
            for w in self.walls:
                block = {
                    'x':w.x,
                    'y':w.y,
                    'w':w.w,
                    'h':w.h,
                    'c':w.c
                }
                data['blocks'].append(block)
            for g in self.goombas:
                goomba = {
                    'x':g.x,
                    'y':g.y,
                }
                data['goombas'].append(goomba)

            for p in self.pipes:
                pipe = {
                    'x':p.x,
                    'y':p.y,
                }
                data['pipes'].append(pipe)

            json_string = json.dumps(data, indent=4)
            outfile.write(json_string)

    def load_level(self):
        self.clean_level()
        with open(self.level) as json_file:
            data = json.load(json_file)
            for block in data['blocks']:
                self.walls.append(WALL(block['x'], block['y'], block['w'], block['h'], block.get('c',0)))
            for g in data.get('goombas',[]):
                self.goombas.append(GOOMBA(g['x'], g['y']))
            for p in data.get('pipes',[]):
                self.pipes.append(PIPE(p['x'], p['y']))
    

    def clean_level(self):
        self.goombas.clear()
        self.walls.clear()
        self.pipes.clear()

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
            tool = self.tools[self.active_tool]
            if tool['type'] == 'wall':
                w = self.cell_size* tool['size'][0]
                h = self.cell_size* tool['size'][1]
                self.walls.append(WALL(x,y, w, h, tool['has_coin'] ))
            elif tool['type'] == 'goomba':
                self.goombas.append(GOOMBA(x,y))
            elif tool['type'] == 'pipe':
                self.pipes.append(PIPE(x,y))
    
    def undo(self):
        if self.active_tool < len(self.tools):
            tool = self.tools[self.active_tool]
            if tool['type'] == 'wall':
                if len(self.walls) != 0:
                    self.walls.pop()
            elif tool['type'] == 'goomba':
                self.goombas.pop()
            elif tool['type'] == 'pipe':
                self.pipes.pop()

    def use_tool(self,x):
        self.active_tool = int(x/self.tool_size)
 
    def draw(self, sc):
        x,y=0,0
        for wall in self.walls:
            wall.draw(sc, self.x_world)

        for g in self.goombas:
            g.draw(sc, self.x_world)
        
        for p in self.pipes:
            p.draw(sc, self.x_world)

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
                if self.tools[i]['type'] == 'wall':
                    size = self.tools[i]['size']
                    has_coin = self.tools[i]['has_coin']
                    WALL(i*self.tool_size + 10, h_bottom + 10,  10 * size[0], 10 * size[1], has_coin).draw(sc, 0)
                elif self.tools[i]['type'] == 'goomba':
                    GOOMBA(i*self.tool_size + 7, h_bottom + 5).draw(sc,0)
                elif self.tools[i]['type'] == 'pipe':
                    PIPE(i*self.tool_size + 10, h_bottom + 5, 40, 40).draw(sc,0)


                 
world = WORLD()
def main():
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
                if pos[1 ] < h_bottom:
                    world.add_block(pos)
                else:
                    world.use_tool(pos[0])    
        sc.fill(BLACK)
        world.draw(sc)
        pygame.display.flip()
main()

