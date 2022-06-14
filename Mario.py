from argparse import Action
from ast import alias
import json
from os import supports_bytes_environ
from random import randint
import json
from re import T
from sys import flags
from time import sleep
import pygame
pygame.init()
 
w = 1000
h = 600

f1 = pygame.font.Font(None, 18)
text1 = f1.render(' SCORE:', True,
                  (180, 0, 0))

w_world = 5000
h_bottom = 540

FPS = 30
pygame.mixer.music.load("super-mario-saundtrek.mp3")
pygame.mixer.music.play(-1)

song1 = pygame.mixer.Sound("money.mp3")
song2 = pygame.mixer.Sound("mario_jump.mp3")
song3 = pygame.mixer.Sound("mario-dead.mp3")
song4 = pygame.mixer.Sound("goomba-dead.mp3")
song5 = pygame.mixer.Sound("mario_level.end.mp3")




sky = pygame.image.load('sky2.jpg')
sky_rect = sky.get_rect(bottomright=(1700, 820 ))
block = pygame.image.load('block.jpg')
#block = pygame.transform.scale(block,(60,60))
all_mario = pygame.image.load('mario.png')
all_goomba = pygame.image.load('goomba.png')
all_money = pygame.image.load('mario_money.png')
#all_mario = pygame.transform.scale(all_mario,(600,500))

clock = pygame.time.Clock()

sc = pygame.display.set_mode((w,h), pygame.RESIZABLE)
WHITE = 255, 255, 255
GREEN = 0, 255, 0
BLACK = 0, 0, 0
YELLOW = 255, 255, 0
RED = 255,0,0

class FLAG(pygame.Rect):
    def __init__(self) -> None:
        super(FLAG,self).__init__(150 - 50 ,20, 10, h_bottom-20)
        self.f_h = self.y
        self.move_down = False
        self.flag_down = False

    def draw(self, sc, wx):
        pygame.draw.rect(sc, BLACK, (self.x - wx, self.y , self.w , self.h))
        pygame.draw.polygon(sc, RED, points=[(self.x- wx, self.f_h), (self.x - 50- wx, self.f_h + 20), (self.x-wx, self.f_h+40)])
        if self.move_down:
            self.f_h += 2
        if self.f_h > self.h - 25:
            self.flag_down = True
            self.move_down = False

    def reset(self):
        self.f_h = self.y
        self.move_down = False
        self.flag_down = False

    def set_down(self):
        if not self.flag_down:
            self.move_down = True


class COIN(pygame.Rect):
    def __init__(self,x,y) -> None:
        super(COIN,self).__init__(x,y,20,20)

    def draw(self, sc, wx):
        sc.blit(all_money, (self.x - wx, self.y))
            

class WALL(pygame.Rect):
    def __init__(self,x,y,w,h,c=0) -> None:
        super(WALL,self).__init__(x,y,w,h)
        self.dy = 0
        self.has_coin = c
        

    def draw(self, sc, wx):
        if self.x - wx < w and self.x + self.w - wx > 0:
            if self.y < h_bottom:  
                sc.blit(block, (self.x - wx, self.y + self.dy ) , (0, 0, self.w , self.h))
            else:
                if self.w > w:
                    pygame.draw.rect(sc, GREEN, (self.x - wx, self.y , self.w , self.h))
                else:
                    pygame.draw.rect(sc, BLACK, (self.x - wx, self.y , self.w , self.h))

        if self.dy != 0:
            self.dy += 1

    def hit(self):
        if self.has_coin:
            self.dy = -10
            self.has_coin = False
            # TODO - FIXME !!!
            world.coins.append(COIN(self.x+int(self.w/2)-10, self.y - 23))
            

class WORLD:
    x_world = 0
    block_size = 60
    lives = 4
    botton_block = WALL(0, h_bottom, w_world, h - h_bottom)
    current_level = 0

    goombas = []
    walls = []  
    stones = []
    coins = []


    def __init__(self, mario) -> None:
        self.font = pygame.font.Font(None, 18)
        self.mario = mario
        self.flag = FLAG()
        self.score = 0
        self.load_level(0)

    def load_level(self, n):
        level = "level{}.json".format(n)
        self.current_level = n
        self.clean_level()
        with open(level) as json_file:
            data = json.load(json_file)
            self.walls.append(self.botton_block)
            for block in data['blocks']:
                self.walls.append(WALL(block['x'], block['y'], block['w'], block['h'],block.get('c',0)))
            for g in data.get('goombas',[]):
                self.goombas.append(GOOMBA(g['x'],g['y']))


    def clean_level(self):
        self.mario.restart()
        self.walls.clear()
        self.score = 0
        self.goombas.clear()
        self.coins.clear()
        self.x_world = 0
        self.flag.reset()

    def move(self):
        dx = self.mario.vx
        if not ( dx > 0 and self.mario.x < w_world - self.mario.w or dx < 0 and self.mario.x > 0 ):
            self.mario.vx = 0
        self.mario.move(self.walls)
        i = self.mario.collidelist(self.coins)
        if i >= 0 and self.mario.alive:
            self.score += 1
            self.coins.pop(i)
            song1.play()
            mario.hit_coin()

        if dx > 0 and self.mario.x - self.x_world > w*3/4 and self.x_world < w_world - w :
            self.x_world += dx
        if dx < 0 and self.mario.x - self.x_world < w*1/4 and self.x_world > 0 :
            self.x_world += dx
        for g in self.goombas:
            if g.top > h:
                self.goombas.remove(g)
            g.move(self.walls)
        
        if self.mario.alive:
            self.hit_goombas()
            if not self.flag.move_down and self.mario.colliderect(self.flag) and mario.vy != 0 and not self.flag.flag_down :
                pygame.mixer.music.pause()
                song5.play()
                mario.mario_on_flag = True
                self.flag.set_down()

        if self.flag.flag_down:
            self.current_level = (self.current_level + 1) % 3
            self.load_level(self.current_level)


        if self.mario.top > h*2.7:
            self.load_level(self.current_level)
            self.lives -= 1


    def draw(self, sc):
        sc.blit(sky, sky_rect)
        for wall in self.walls:
            wall.draw(sc, self.x_world)
        for g in self.goombas:
            g.draw(sc,self.x_world)
        for c in self.coins:
            c.draw(sc, self.x_world)
        self.flag.draw(sc, self.x_world)
        self.mario.draw(sc, self.x_world)
        score_text = self.font.render('score:{}  lives:{}'.format(self.score, self.lives), True, (180, 0, 0))
        sc.blit(score_text,(10,10))
    
    def hit_goombas(self):
        i = self.mario.collidelist(self.goombas)
        if i >= 0:
            if self.mario.vy > 0:
                self.goombas[i].kill()
            elif self.goombas[i].alive:
                self.mario.kill()
                pygame.mixer.music.pause()
                song3.play()


class MARIO(pygame.Rect):
    vy = 0
    vx = 0
    draw_count = 0
    alive = True
    can_jump = True
    mario_on_flag = False
    action = "stay"
    texture = {
     "right": [(500, 200),(500,100), (500, 0), (500, 100)],
     "left": [(400, 600), (400,700), (400, 800), (400, 700)],
     "stay" : [(300, 400)],
     "jump_right": [(500, 400)],
     "jump_left": [(400, 400)]
    }

    def __init__(self):
        super(MARIO, self).__init__(50,50,35,60)
        font = pygame.font.Font(None, 14)
        self.coin_up = font.render("+1", True, YELLOW)
        self.show_coin = 0

    def restart(self):
        self.alive = True
        self.vx = 0
        self.vy = 0
        self.x = 50
        self.y = 50
        pygame.mixer.music.unpause()
   

    def jump(self):
        if self.alive and self.can_jump:
            self.vy = -20
            self.can_jump = False
            song2.play()

    def kill(self):
        self.alive = False
        self.vy = -15


    def move(self, walls):
        if self.mario_on_flag:
            self.vx = 0
            self.vy = 4

        if self.vy < 20:
            self.vy = self.vy + 1
        # y
        self.y += self.vy
        i = self.collidelist(walls)
        if i >= 0 and self.alive:
            wall = walls[i]
            if self.vy > 0:
                self.y = wall.y - self.h
                self.can_jump = True
            else:
                self.y = wall.y + wall.h
                wall.hit()
            self.vy = 0
        # x
        self.x += self.vx
        i = self.collidelist(walls)
        if i>=0 and self.alive:
            wall = walls[i]
            if self.vx > 0:
                self.x = wall.x - self.w
            else:
                self.x = wall.x + wall.w

        if self.mario_on_flag and self.bottom >= h_bottom:
            self.mario_on_flag = False
       
 
    def hit_coin(self):
        self.show_coin = FPS

    def set_vx(self, vx):
        if self.alive:
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
        if not self.alive or self.mario_on_flag:
            self.action = "jump_right"
            

        #pygame.draw.rect(sc, BLACK, (mario.x - wx, mario.y, self.w, self.h))
        num_frames = len(self.texture[self.action])
        frame = int(self.draw_count*10/FPS)%num_frames
        sc.blit(all_mario,(self.x - wx, self.y), self.texture[self.action][frame] + (self.w, self.h) )
        if self.show_coin:
            sc.blit(self.coin_up, (self.x - wx, self.y - 12))
            self.show_coin -= 1
        

#GOOMBA
class GOOMBA(pygame.Rect):
    vx = 3
    vy = 0
    draw_count = 0
    alive = True

    textures_walk = [(33, 11),(91,11)]
    textures_dead = (151, 11)

    def __init__(self, x, y):
        self.x0 = x
        super(GOOMBA,self).__init__(x,y, 46,46)
        
    def kill(self):
        self.alive = False
        self.vy = -15
        song4.play()

    def move(self,walls):
        # y
        self.y += self.vy
        i = self.collidelist(walls)
        if i >= 0 and self.alive:
            wall = walls[i]
            if self.vy > 0:
                self.y = wall.y - self.h
            else:
                self.y = wall.y + wall.h
            self.vy = 0
        # x
        self.x += self.vx
        i = self.collidelist(walls)
        if i>=0 and self.alive:
            wall = walls[i]
            if self.vx > 0:
                self.x = wall.x - self.w
            else:
                self.x = wall.x + wall.w
            self.vx = - self.vx
        if self.vy < 20:
            self.vy = self.vy + 1

        if self.alive and abs(self.x - self.x0) > 200:
            self.vx = - self.vx
        

    def draw(self,sc, wx):
        if self.alive:
            self.draw_count += 1
            num_frames = len(self.textures_walk)
            frame = int(self.draw_count*10/FPS)%num_frames
            sc.blit(all_goomba,(self.x - wx, self.y), self.textures_walk[frame] + (self.w, self.h) )
        else:
            self.show_coin = True
            sc.blit(all_goomba,(self.x - wx, self.y), self.textures_dead + (self.w, self.h) )



mario = MARIO()
world = WORLD(mario)

pygame.mixer.music.play(-1)
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

