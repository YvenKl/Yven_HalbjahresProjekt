import pygame
from pygame.constants import (QUIT, K_KP_PLUS, K_KP_MINUS, K_ESCAPE, KEYDOWN, K_SPACE, K_1, K_LEFT, K_RIGHT, K_2, K_3)
import os
import pygame
from random import randint
import sys
from pygame.locals import *


class Settings(object):
    window_width = 1920
    window_height = 1080
    fps = 60
    title = "DefendTheTower"
    path = {}
    path['file'] = os.path.dirname(os.path.abspath(__file__))
    path['image'] = os.path.join(path['file'], "images")
    path_file = os.path.dirname(os.path.abspath(__file__))
    path_image = os.path.join(path_file, "images")
    directions = {'stop':(0, 0), 'down':(0,  1), 'up':(0, -1), 'left':(-1, 0), 'right':(1, 0)}
    player_vel = 5
    player_jumpvel_standart = 10
    attack_cooldown = 100
    overallcooldown = 0
    animation_indicator = 1
    constantwalk_indicator = 0
    idle = True
    left = False
    right = False
    jump = False
    isjump = False
    jumpdown = 0
    jumpvel_up = 10
    jumpvel_down = 10
    jump_deny = 1
    jump_decay = 0
    jump_indicator = 1
    idle_in = 30
    left_in = 20
    right_in = 20
    jump_in = 60
    hp = 100
    points = 0
    goblin_cooldown = 0
    nof_goblins = 3
    goblinminspeed = 3
    goblinmaxspeed = 5
    gwalk_in = 25
    tower_in = 35

    @staticmethod
    def dim():
        return (Settings.window_width, Settings.window_height)

    @staticmethod
    def filepath(name):
        return os.path.join(Settings.path['file'], name)

    @staticmethod
    def imagepath(name):
        return os.path.join(Settings.path['image'], name)


class Timer(object):
    def __init__(self, duration, with_start = True):
        self.duration = duration
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duration

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duration
            return True
        return False

    def change_duration(self, delta=10):
        self.duration += delta
        if self.duration < 0:
            self.duration = 0


class Animation(object):
    def __init__(self, namelist, endless, animationtime, colorkey=None):
        self.images = []
        self.endless = endless
        self.timer = Timer(animationtime)
        for filename in namelist:
            if colorkey == None:
                bitmap = pygame.image.load(Settings.imagepath(filename)).convert_alpha()
            else:
                bitmap = pygame.image.load(Settings.imagepath(filename)).convert()
                bitmap.set_colorkey(colorkey)           # Transparenz herstellen §\label{srcAnimation0101}§
            self.images.append(bitmap)
        self.imageindex = -1

    def next(self):
        if self.timer.is_next_stop_reached():
            self.imageindex += 1
            if self.imageindex >= len(self.images):
                if self.endless:
                    self.imageindex = 0
                else:
                    self.imageindex = len(self.images) - 1
        return self.images[self.imageindex]

    def is_ended(self):
        if self.endless:
            return False
        elif self.imageindex >= len(self.images) - 1:
            return True
        else:
            return False

class Background(object):
    def __init__(self, filename="background.jpg") -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))

    def draw(self, screen):
        screen.blit(self.image, (0, 0))
        main_font = pygame.font.SysFont("comicsans", 50) #Schriftart von der Font
        towerhp_label = main_font.render(f"Tower HP: {Settings.hp}", False, (255, 0, 0)) #Farben der Fonts
        point_label = main_font.render(f"Points: {Settings.points}", False, (255, 0, 0))
        #level_label = main_font.render(f"Difficulty: {Settings.level_indicator}", 1, (255, 0, 0))
        #screen.blit(level_label, (10, Settings.window_height - point_label.get_height() - 10)) #Koordinaten der Fonts
        screen.blit(towerhp_label, (10, 10))
        screen.blit(point_label, (Settings.window_width - point_label.get_width() - 10, 10))


class Goblin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation = Animation([f"goblin_walk{i}.png" for i in range(5)], False, 1) # §\label{srcAnimation0102}§
        self.image = self.animation.next()
        self.rect = self.image.get_rect()
        self.rect.top = Settings.window_height - self.get_height()  # Spawnpoint des Players (Unten mittig)
        self.rect.left = Settings.window_width - self.rect.width / 2  # Spawnpoint des Players (Unten mittig)
        self.speed_h = randint(Settings.goblinminspeed, Settings.goblinmaxspeed)
        self.speed_v = 0

    def gwalk(self):
        if Settings.gwalk_in >= 25:
            Settings.gwalk_in = 0
            self.animation = Animation([f"goblin_walk{i}.png" for i in range(5)], False, 100)

    def gwalkcount(self):
        if Settings.gwalk_in <= 25:
                Settings.gwalk_in += 1

    def get_width(self):
        return self.rect.width

    def get_height(self):
        return self.rect.height

    def get_center(self):
        return self.rect.center

    def update(self):
        self.rect.move_ip((-self.speed_h, self.speed_v))
        self.gwalkcount()
        self.gwalk()
        self.image = self.animation.next()


class Tower(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.animation = Animation([f"tower{i}.png" for i in range(6)], False, 1)  # §\label{srcAnimation0102}§
        self.image = self.animation.next()
        self.rect = self.image.get_rect()
        self.rect.top = Settings.window_height - self.get_height()
        self.rect.bottom = Settings.window_height

    def tower(self):
        if Settings.tower_in >= 35:
            Settings.tower_in = 0
            self.animation = Animation([f"tower{i}.png" for i in range(5)], False, 100)

    def towercount(self):
        if Settings.tower_in <= 35:
                Settings.tower_in += 1

    def get_height(self):
        return self.rect.height

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.tower()
        self.towercount()
        self.image = self.animation.next()

class Shots(pygame.sprite.Sprite):
    def __init__(self, pos_player_x, pos_player_y, vel_x, vel_y) -> None:
        super().__init__()
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.pos_shots_x = pos_player_x
        self.pos_shots_y = pos_player_y
        self.image = pygame.image.load(os.path.join(Settings.path_image, "shots.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = self.pos_shots_x
        self.rect.centery = self.pos_shots_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect.move_ip((self.vel_x, self.vel_y))
        self.off_map()

    def off_map(self):
        if self.rect.top + self.vel_y > Settings.window_height:
            self.kill()
        if self.rect.bottom + self.vel_y < 0:
            self.kill()
        if self.rect.right + self.vel_x < 0:
            self.kill()
        if self.rect.left + self.vel_x > Settings.window_width:
            self.kill()

    def center(self, pos_player_x, pos_player_y):
        self.pos_shots_x = pos_player_x
        self.pos_shots_y = pos_player_y


class Fighter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation=Animation([f"player{i}_idle.png" for i in range(4)], False, 1) # §\label{srcAnimation0102}§
        self.image = self.animation.next()
        self.rect = self.image.get_rect()
        self.rect.top = Settings.window_height - self.get_height()  # Spawnpoint des Players (Unten mittig)
        self.rect.left = Settings.window_width / 2 - self.rect.width / 2  # Spawnpoint des Players (Unten mittig)

    def jump(self):
        if Settings.jump == True:
            self.rect.top -= Settings.jumpvel_up
            #Settings.jumpvel_up = Settings.jumpvel_up -
            Settings.jump_decay += 1
            if Settings.jump_decay >= 60:
                Settings.jumpvel_up = Settings.player_jumpvel_standart
                Settings.jump_indicator = 0
                Settings.jump_deny = 2
                Settings.jump = False

        if not self.rect.top == Settings.window_height - self.get_height() and Settings.jump_indicator == 0:
            Settings.jumpdown += 1
            self.rect.top += Settings.jumpvel_down

        if self.rect.top == Settings.window_height - self.get_height() and Settings.jump_deny == 2:
            Settings.jumpvel_down = Settings.player_jumpvel_standart
            Settings.jumpdown = 0
            Settings.jump_decay = 0
            Settings.jump_indicator = 1
            Settings.jump_deny = 1
            Settings.isjump = False

    def jump_logic(self):
        if Settings.jump_decay == 45:
            Settings.jumpvel_up = Settings.jumpvel_up / 2

        if Settings.jumpdown == 15:
            Settings.jumpvel_down = Settings.jumpvel_down * 1.5

    def idle(self):
        if Settings.idle == True and Settings.idle_in >= 30:
            Settings.idle_in = 0
            self.animation = Animation([f"player{i}_idle.png" for i in range(4)], False, 100)

    def left(self):
        if Settings.left == True and Settings.left_in >= 20:
            Settings.left_in = 0
            self.animation = Animation([f"player{i}_left.png" for i in range(4)], False, 100)


    def right(self):
        if Settings.right == True and Settings.right_in >= 20:
            Settings.right_in = 0
            self.animation = Animation([f"player{i}_right.png" for i in range(4)], False, 100)

    def idlecount(self):
        if Settings.idle == True:
            if Settings.idle_in <= 30:
                Settings.idle_in += 1
        else:
            Settings.idle_in = 30

    def leftcount(self):
        if Settings.left == True:
            if Settings.left_in <= 20:
                Settings.left_in += 1
        else:
            Settings.left_in = 20

    def rightcount(self):
        if Settings.right == True:
            if Settings.right_in <= 20:
                Settings.right_in += 1
        else:
            Settings.right_in = 20

    def jumpcount(self):
        if Settings.jump == True:
            pass

    def get_width(self):
        return self.rect.width

    def get_height(self):
        return self.rect.height

    def get_center(self):
        return self.rect.center

    def center_update(self):
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.center_update()
        self.idlecount()
        self.leftcount()
        self.rightcount()
        self.idle()
        self.left()
        self.right()
        self.jump()
        self.jump_logic()
        self.image = self.animation.next()
        self.movement()

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left - Settings.player_vel > 0:  # links movement
            self.rect.left -= Settings.player_vel
            Settings.idle = False
            Settings.right = False
            Settings.left = True
            #if self.rect.top == Settings.window_height - self.get_height():
        elif keys[pygame.K_RIGHT] and self.rect.left + Settings.player_vel + self.get_width() < Settings.window_width:  # rechts movement
            self.rect.left += Settings.player_vel
            Settings.idle = False
            Settings.left = False
            Settings.right = True
            #if self.rect.top == Settings.window_height - self.get_height():

        elif keys[pygame.K_SPACE] and self.rect.top - Settings.player_vel > 0 and Settings.jump_indicator == 1 and Settings.jump_deny == 1 and Settings.animation_indicator == 1:  # jump
            Settings.jump = True
            Settings.isjump = True
            Settings.jump_deny = 3

        else:
            Settings.right = False
            Settings.left = False
            Settings.idle = True


class Game(object):
    def __init__(self) -> None:
        super().__init__()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "10, 50"
        pygame.init()
        self.screen = pygame.display.set_mode(Settings.dim(), FULLSCREEN)
        pygame.display.set_caption(Settings.title)
        self.clock = pygame.time.Clock()
        self.fighter = pygame.sprite.GroupSingle(Fighter())
        self.goblin = pygame.sprite.Group(Goblin())
        self.tower = pygame.sprite.GroupSingle(Tower())
        self.shots = pygame.sprite.Group()
        self.shot = Shots(self.fighter.sprite.rect.centerx, self.fighter.sprite.rect.centery+200, 5, 0)
        self.running = False

    def run(self) -> None:
        self.start()
        self.running = True
        while self.running:
            self.clock.tick(Settings.fps)
            self.watch_for_events()
            self.update()
            self.draw()
        pygame.quit()

    def shoting_shots(self):
        if len(self.shots.sprites()) <= 10:
            self.shot.center(self.fighter.sprite.rect.centerx,self.fighter.sprite.rect.centery+200)
            self.shots.add(Shots(self.fighter.sprite.rect.centerx, self.fighter.sprite.rect.centery+200, 5, 0))


    def goblin_spawn(self):
        if Settings.goblin_cooldown >= 60:
            Settings.goblin_cooldown = 0
            if len(self.goblin.sprites()) < Settings.nof_goblins:
                self.goblin.add(Goblin())

    def goblin_cooldown(self):
        if Settings.goblin_cooldown <= 60:
            Settings.goblin_cooldown += 1


    def g_t_collide(self):
        pygame.sprite.groupcollide(self.goblin, self.tower, True, False,pygame.sprite.collide_rect)  # Standart rect collision

    def watch_for_events(self) -> None:
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_LEFT:
                    pass
                elif event.key == K_RIGHT:
                    pass
                elif event.key == K_DOWN:
                    self.shoting_shots()

    def update(self) -> None:
        self.fighter.update()
        self.goblin.update()
        self.tower.update()
        self.goblin_spawn()
        self.goblin_cooldown()
        self.g_t_collide()
        self.shots.update()

    def draw(self) -> None:
        self.background.draw(self.screen)
        self.fighter.draw(self.screen)
        self.goblin.draw(self.screen)
        self.tower.draw(self.screen)
        self.shots.draw(self.screen)
        pygame.display.flip()

    def start(self):
        self.background = Background()


if __name__ == '__main__':
    anim = Game()
    anim.run()
