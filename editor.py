from argparse import Action
import json
from random import randint
import json
import pygame
pygame.init()
 
w = 1000
h = 600


w_world = 8000
h_bottom = 550

sc = pygame.display.set_mode((w,h), pygame.RESIZABLE)
WHITE = 255, 255, 255
GREEN = 0, 255, 0
BLACK = 0, 0, 0
YELLOW = 255, 255, 0

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
    block_size = 60

    walls = []  

    def save_level(self):
        with open('level.json', 'w') as outfile:
            data = {}
            data['blocks'] = [[w.x,w.y] for w in self.walls]
            json_string = json.dumps(data)
            outfile.write(json_string)

    def load_level(self):
        with open('level.json') as json_file:
            data = json.load(json_file)
            for block in data['blocks']:
                self.walls.append(WALL(block[0], block[1], self.block_size, self.block_size))

    def new_level(self):
        self.walls.clear()

    def left(self):
        if self.x_world > 0:
            self.x_world -= self.block_size

    def right(self):
        if self.x_world<w_world-w:
            self.x_world += self.block_size

    def add_block(self, pos):
        x = pos[0] - pos[0]%(self.block_size/2) + self.x_world
        y = pos[1] - pos[1]%(self.block_size/2)
        self.walls.append(WALL(x,y, self.block_size, self.block_size))
    
    def undo(self):
        self.walls.pop()

    def draw(self, sc):
        x,y=0,0
        while x<w:
            pygame.draw.line(sc,WHITE,(x,0),(x,h))
            x += self.block_size/2
        while y<h:
            pygame.draw.line(sc,WHITE,(0,y),(w,y))
            y += self.block_size/2
        for wall in self.walls:
            wall.draw(sc, self.x_world)

world = WORLD()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                world.save_level()
            if event.key == pygame.K_l:
                world.load_level()
            if event.key == pygame.K_n:
                world.new_level()
            if event.key == pygame.K_u:
                world.undo()
            if event.key == pygame.K_LEFT:
                world.left()
            if event.key == pygame.K_RIGHT:
                world.right()
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            world.add_block(pos)    
    sc.fill(BLACK)
    world.draw(sc)
    pygame.display.flip()

