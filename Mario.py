from argparse import Action
import json
from random import randint
import json
import pygame
pygame.init()
 
w = 1000
h = 600

f1 = pygame.font.Font(None, 18)
text1 = f1.render(' SCORE:', True,
                  (180, 0, 0))

w_world = 8000
h_bottom = 550

FPS = 30

sky = pygame.image.load('sky2.jpg')
sky_rect = sky.get_rect(bottomright=(1450, 750 ))
block = pygame.image.load('block.jpg')
block = pygame.transform.scale(block,(60,60))
all_mario = pygame.image.load('mario.png')
#all_mario = pygame.transform.scale(all_mario,(600,500))

clock = pygame.time.Clock()

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
        self.dy = 0
        self.coin = False
        self.coin_up = False
        #self.coin_x = self.coin_y = 0
        

    def draw(self, sc, wx):
        if self.x - wx < w and self.x + self.w - wx > 0:
            if self.y < h_bottom:  
                sc.blit(block, (self.x - wx, self.y + self.dy , self.w , self.h))
            else:
                if self.w > w:
                    pygame.draw.rect(sc, GREEN, (self.x - wx, self.y , self.w , self.h))
                else:
                    pygame.draw.rect(sc, BLACK, (self.x - wx, self.y , self.w , self.h))
        if self.coin:
            pygame.draw.circle(sc, YELLOW, (self.x+int(self.w/2) - wx, self.y - 17), 12)
            
            
        if self.dy != 0:
            self.dy += 1

    def hit_coin(self, x,y,w,h):
        if self.coin:
            if x < self.x+int(self.w/2) < x+w and y < self.y-12  < y+h:
                self.coin = False
                self.coin_up = True
                return True
        return False

    def hit(self, x,y,w,h):

        if x+w<self.x or x > self.x+self.w or y > self.y+self.h or y+h<self.y:
            return False
        else:
            if y < self.y + self.h < y + h and mario.vy < 0:
                if not self.coin_up:
                    self.dy = -10
                    self.coin = True
                
        return True
        


class WORLD:
    x_world = 0
    block_size = 60
    botton_block = WALL(0, h_bottom, w_world, h - h_bottom)
    

    walls = []  
    stones = []  

    def __init__(self, mario) -> None:
        self.font = pygame.font.Font(None, 18)
        self.mario = mario
        self.mario.walls = self.walls
        self.mario.world = self
        self.score = 0
        self.load_level(0)

    def load_level(self, n):
        level = "level{}.json".format(n)
        self.clean_level()
        with open(level) as json_file:
            data = json.load(json_file)
            self.walls.append(self.botton_block)
            for block in data['blocks']:
                self.walls.append(WALL(block[0], block[1], self.block_size, self.block_size))

    def clean_level(self):
        self.walls.clear()
        self.score = 0

    def move(self):
        dx = self.mario.vx
        if not ( dx > 0 and self.mario.x < w_world - self.mario.sz_x or dx < 0 and self.mario.x > 0 ):
            self.mario.vx = 0
        self.mario.move()
        if self.mario.hit_coin():
            self.score += 1
        if dx > 0 and self.mario.x - self.x_world > w*3/4 and self.x_world < w_world - w :
            self.x_world += dx
        if dx < 0 and self.mario.x - self.x_world < w*1/4 and self.x_world > 0 :
            self.x_world += dx
 
    def draw(self, sc):
        sc.blit(sky, sky_rect)
        for wall in self.walls:
            wall.draw(sc, self.x_world)
        self.mario.draw(sc, self.x_world)
        score_text = self.font.render('score:{}'.format(self.score), True, (180, 0, 0))
        sc.blit(score_text,(10,10))

class MARIO:
    x = 330 
    y = 30
    vy = 0
    vx = 0
    sz_y = 60
    sz_x = 35
    draw_count = 0

    can_jump = True
    action = "stay"
    texture = {
     "right": [(500, 200),(500,100), (500, 0), (500, 100)],
     "left": [(400, 600), (400,700), (400, 800), (400, 700)],
     "stay" : [(300, 400)],
     "jump_right": [(500, 400)],
     "jump_left": [(400, 400)]
    }

    def __init__(self) -> None:
        font = pygame.font.Font(None, 14)
        self.coin_up = font.render("+1", True, YELLOW)
        self.show_coin = 0

    def jump(self):
        if self.can_jump:
            self.vy = -20
            self.can_jump = False

    def move(self):
        # y
        self.y += self.vy
        for w in self.walls:
            if w.hit(self.x, self.y, self.sz_x, self.sz_y):
                if self.vy > 0:
                    self.y = w.y - self.sz_y - 1
                else:
                    self.y = w.y + w.h + 1
                self.vy = 0
                self.can_jump = True
                break
        # x
        self.x += self.vx
        for w in self.walls:
            if w.y < h_bottom and w.hit(self.x, self.y, self.sz_x, self.sz_y):
                if self.vx > 0:
                    self.x = w.x - self.sz_x - 1
                else:
                    self.x = w.x + w.w + 1
                break

        if self.vy < 20:
            self.vy = self.vy + 1

    def hit_coin(self):
        for w in self.walls:
            if w.hit_coin(self.x, self.y, self.sz_x, self.sz_y):
                self.show_coin = FPS
                return True
        return False


    def set_vx(self, vx):
        self.vx = vx

    def draw(self,sc, wx):
        self.draw_count += 1
        if self.vx < 0:
            self.action = "left"
        elif self.vx > 0:
            self.action = "right"
        else:
            self.action = "stay"
        if not self.can_jump and self.vx > 0:
            self.action = "jump_right"
        if not self.can_jump and self.vx < 0:
            self.action = "jump_left"
        
        #pygame.draw.rect(sc, BLACK, (mario.x - wx, mario.y, self.sz_x, self.sz_y))
        #sc.blit(all_mario,(mario.x - wx, mario.y), (68, 15, self.sz, self.sz) )
        num_frames = len(self.texture[self.action])
        frame = int(self.draw_count*10/FPS)%num_frames
        sc.blit(all_mario,(mario.x - wx, mario.y), self.texture[self.action][frame] + (self.sz_x, self.sz_y) )
        if self.show_coin:
            sc.blit(self.coin_up, (mario.x - wx, mario.y - 12))
            self.show_coin -= 1
        


mario = MARIO()
world = WORLD(mario)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                mario.jump()
            if event.key == pygame.K_1:
                world.load_level(0)
            if event.key == pygame.K_2:
                world.load_level(1)
            if event.key == pygame.K_3:
                world.load_level(2)
    Keys = pygame.key.get_pressed()
    mario.set_vx(0)
    if Keys [pygame.K_LEFT]:
        mario.set_vx(-7)
    elif Keys [pygame.K_RIGHT]:
        mario.set_vx(7)
        
    world.move()
    world.draw(sc)
    pygame.display.flip()
    clock.tick(FPS)

