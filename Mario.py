from argparse import Action
from ast import alias
import json
from os import supports_bytes_environ
import pipes
from random import randint
import json
from re import T
from sys import flags
from time import sleep
import pygame
pygame.init()
 
w = 1000
h = 600
sc = pygame.display.set_mode((w,h), pygame.RESIZABLE)

f1 = pygame.font.Font(None, 25)
f2 = pygame.font.Font(None, 18)
text1 = f1.render(' SCORE:', True,(180, 0, 0))
text2 = f2.render('GAME OVER', True,(180, 0, 0))


w_world = 8000
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
picture = block_surprise  = pygame.image.load('mario_block-surprise.png')
ground = pygame.image.load('fon_mario.jpg')
picture = pygame.transform.scale(picture, (60, 60))
ground = pygame.transform.scale(ground, (w_world, 60))
heart = pygame.image.load('heart.png')
heart = pygame.transform.scale(heart, (30, 25))
cool_face = pygame.image.load('cool_face.jpeg')
cool_face = pygame.transform.scale(cool_face, (26, 25))
timer_photo = pygame.image.load('timer_photo.webp')
timer_photo = pygame.transform.scale(timer_photo, (25, 25))
timer_photo.set_colorkey((255, 255, 255))

rect = picture.get_rect()

#block = pygame.transform.scale(block,(60,60))
all_mario = pygame.image.load('mario.png')
all_goomba = pygame.image.load('goomba.png')
all_money = pygame.image.load('mario_money.png')
#all_mario = pygame.transform.scale(all_mario,(600,500))

clock = pygame.time.Clock()

WHITE = 255, 255, 255
GREEN = 0, 255, 0
BLACK = 0, 0, 0
YELLOW = 255, 255, 0
RED = 255,0,0
BROWN = 153, 51, 0

class PIPE(pygame.Rect):
    def __init__(self, x, y):
        super(PIPE,self).__init__(x, y, 110,  h_bottom + 30)

    def set_W(self):
        self.w = h - self.y - (h - h_bottom)
    
    def draw(self, sc, wx):
        pygame.draw.rect(sc, GREEN,(self.x - wx, self.y , self.w, self.h ))
        pygame.draw.rect(sc, BLACK,(self.x - wx, self.y , self.w, self.h ), 3)
        pygame.draw.rect(sc, GREEN,(self.x - wx - 7, self.y  , self.w + 14, 25 ))
        pygame.draw.rect(sc, BLACK,(self.x - wx - 10, self.y , self.w + 19, 25), 3, 3)


class FLAG(pygame.Rect):
    def __init__(self) -> None:
        super(FLAG,self).__init__(w_world- 100 ,20, 10, h_bottom-20)
        self.f_h = self.y
        self.move_down = False
        self.flag_down = False

    def draw(self, sc, wx):
        pygame.draw.rect(sc, GREEN, (self.x - wx, self.y , self.w -3, self.h))
        pygame.draw.polygon(sc, WHITE, points=[(self.x- wx, self.f_h +10), (self.x - 50- wx, self.f_h + 20 +10), (self.x-wx, self.f_h+40+10)])
        pygame.draw.rect(sc, BROWN, (self.x -wx -17, w - h_bottom+40, 40, 40))
        pygame.draw.rect(sc, BLACK, (self.x -wx -17 , w - h_bottom+40, 40, 40), 3)
        pygame.draw.circle(sc, GREEN, (self.x - wx + 4, self.y), 10)
        pygame.draw.circle(sc, BLACK, (self.x - wx + 4, self.y), 10, 2)

        if self.move_down:
            self.f_h += 2
        if self.f_h > self.h - 65 :
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
    def __init__(self,x,y,w,h,c=0,) -> None:
        super(WALL,self).__init__(x,y,w,h)
        self.dy = 0
        self.has_coin = c
        

    def draw(self, sc, wx):
        if self.x - wx < w and self.x + self.w - wx > 0:
            if self.y < h_bottom:  
                sc.blit(block, (self.x - wx, self.y + self.dy ) , (0, 0, self.w , self.h))
            else:
                if self.w > w:
                    pass
                    pygame.draw.rect(sc, GREEN, (self.x - wx, self.y , self.w , self.h))
                else:
                    pygame.draw.rect(sc, BLACK, (self.x - wx, self.y , self.w , self.h))
            if self.has_coin == True:
                sc.blit(picture,(self.x - wx, self.y))


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
    lives = 5
    botton_block = WALL(0, h_bottom, w_world, h - h_bottom)
    current_level = 0
    game_over = False
    all_score = 0
    time = 360
    timer = FPS
    goombas = []
    walls = []  
    stones = []
    coins = []
    pipes = []


    def __init__(self, mario) -> None:
        self.font = pygame.font.Font(None, 18)
        self.mario = mario
        self.flag = FLAG()
        self.score = 0
        self.load_level(0)

    def load_level(self, n):
        self.score = 0
        self.time = 360
        self.all_score = 0
        level = "level{}.json".format(n)
        self.current_level = n
        self.clean_level()
        #self.trubies.append(PIPE())
        with open(level) as json_file:
            data = json.load(json_file)
            self.walls.append(self.botton_block)
            for block in data['blocks']:
                self.walls.append(WALL(block['x'], block['y'], block['w'], block['h'],block.get('c',0)))
            for g in data.get('goombas',[]):
                self.goombas.append(GOOMBA(g['x'],g['y']))
            for p in data.get('pipes',[]):
                self.pipes.append(PIPE(p['x'], p['y']))
    
    def time_f(self):
        if self.time < 1:
            mario.kill()
            self.time = 4
        if self.timer < 1:
            self.time -= 1
            self.timer = FPS
        else:
            self.timer -= 1



    def clean_level(self):
        self.mario.restart()
        self.walls.clear()
        self.goombas.clear()
        self.coins.clear()
        self.pipes.clear()
        self.x_world = 0
        self.flag.reset()
    
    def GAME_OVER(self):
        self.score = 0
        self.current_level = 0
        self.lives = 5 
        self.all_score = 0  
        self.timer = 0     

    def move(self):
        dx = self.mario.vx
        if not ( dx > 0 and self.mario.x < w_world - self.mario.w or dx < 0 and self.mario.x > 0 ):
            self.mario.vx = 0
        self.mario.move(self.walls, self.pipes)
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
            g.move(self.walls, self.pipes)
        
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
            self.lives += 5


        if self.mario.top > h*2.7:
            self.load_level(self.current_level)
            self.lives -= 1
        if self.lives < 1:
            self.GAME_OVER()

        
            
    def draw(self, sc):
        sc.blit(sky, sky_rect)
        pygame.draw.rect(sc, BLACK,(0, 0, 1000, 30))
        pygame.draw.rect(sc, WHITE,(0, -2, 1002, 32), 2)
        pygame.draw.line(sc, WHITE,[65, -2], [65, 28], 2)
        pygame.draw.line(sc, WHITE,[125, -2], [125, 28], 2)
        pygame.draw.line(sc, WHITE,[230, -2], [230, 28], 2)
        pygame.draw.line(sc, WHITE,[310, -2], [310, 28], 2)
        sc.blit(ground, (0, h_bottom))
        for p in self.pipes:
            p.draw(sc, self.x_world)
        for wall in self.walls:
            wall.draw(sc, self.x_world)
        for g in self.goombas:
            g.draw(sc,self.x_world) 
        for c in self.coins:
            c.draw(sc, self.x_world)
        self.flag.draw(sc, self.x_world)
        self.mario.draw(sc, self.x_world)
        pygame.draw.circle(sc, YELLOW,( 28, 12), 9)
        sc.blit(timer_photo,(240, 0))
        sc.blit(cool_face,(135, 0))
        sc.blit(heart,(72, 0))
        score_text = f1.render('  {}  '.format(self.score), True, (WHITE))
        sc.blit(score_text,(32,5))
        lives_text = f1.render('  {}  '.format(self.lives), True, (WHITE))
        sc.blit(lives_text,(92, 5))
        score_text = f1.render('  {}  '.format(self.all_score), True, (WHITE))
        sc.blit(score_text,(155, 5))
        time_text = f1.render('  {}  '.format(self.time), True, (WHITE))
        sc.blit(time_text,(260, 5))



        #score_text = f1.render('|         {}      |         {}      |         {}       |          {}      
        # |'.format(self.score, self.lives, self.all_score, self.time), True, (WHITE))
        #sc.blit(score_text,(40,5))
        self.time_f()
    
    def hit_goombas(self):
        i = self.mario.collidelist(self.goombas)
        if i >= 0 and mario.alive:
            if self.mario.vy > 0:
                self.goombas[i].kill()
            elif self.goombas[i].alive:
                self.mario.kill()
                pygame.mixer.music.pause()
                song3.play()
            self.all_score += 200


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
        super(MARIO, self).__init__(50, 50 ,35,60)
        font = pygame.font.Font(None, 14)
        self.coin_up = font.render("+1", True, YELLOW)
        self.show_coin = 0

    def restart(self):
        self.alive = True
        self.vx = 0
        self.vy = 0
        self.x = 50
        self.y = 500
        pygame.mixer.music.unpause()
   
    def jump(self):
        if self.alive and self.can_jump:
            self.vy = -23
            self.can_jump = False
            song2.play()

    def kill(self):
        self.alive = False
        self.vy = -15
        pygame.mixer.music.pause()
        song3.play()

    def move(self, walls, pipes):
        if self.mario_on_flag and not world.game_over:
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
        i = self.collidelist(pipes)
        if i >= 0 and self.alive:
            pipe = pipes[i]
            if self.vy > 0:
                self.y = pipe.y - self.h 
                self.can_jump = True
        # x
        self.x += self.vx
        i = self.collidelist(walls)
        if i>=0 and self.alive:
            wall = walls[i]
            if self.vx > 0:
                self.x = wall.x - self.w
            else:
                self.x = wall.x + wall.w
        i = self.collidelist(pipes)
        if i>=0 and self.alive:
            pipe = pipes[i]
            if self.vx > 0:
                self.x = pipe.x - self.w 
            else:
                self.x = pipe.x + pipe.w

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
            world.all_score += 10
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

    def move(self,walls,pipes):
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
        i = self.collidelist(pipes)
        if i >= 0 and self.alive:
            pipe = pipes[i]
            if self.vy > 0:
                self.y = pipe.y - self.h
            else:
                self.y = pipe.y + pipe.h
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
        i = self.collidelist(pipes)
        if i>=0 and self.alive:
            pipe = pipes[i]
            if self.vx > 0:
                self.x = pipe.x - self.w 
            else:
                self.x = pipe.x + pipe.w
            self.vx = -self.vx

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
def main():
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
main()

