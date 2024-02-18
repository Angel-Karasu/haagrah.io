import math, pygame 
from pygame.locals import *
from random import randint

pygame.init()
pygame.display.set_caption('Haagrah.io')
pygame.display.set_icon(pygame.image.load('src/icon.png'))
pygame.mixer.music.load('src/haagrah_song.mp3')
pygame.mixer.music.play()

WIN_SIZE = (1000, 750)
WINDOW = pygame.display.set_mode(WIN_SIZE)

NB_NPCS = 5
NB_PARTICLES = 250

class Background:
    def __init__(self):
        img = pygame.image.load('src/background.png')
        self.original_img = img
        self.zoom = 8
        self.modify_img()

    def modify_img(self):
        self.size = self.original_img.get_rect()[3]*self.zoom
        self.img = pygame.transform.scale(self.original_img, (self.size, self.size))

    def unzoom(self, player, npcs, particles):
        self.zoom //= 2
        self.modify_img()
        self.show()

        player.size //= 3
        player.pos = [player.pos[0]//2, player.pos[1]//2]
        player.show()

        for npc in npcs:
            npc.size //= 3
            npc.pos = (npc.pos[0]//2, npc.pos[1]//2)
            npc.show()

        particles.extend(Particle() for _ in range(250))
        for prtcl in particles:
            prtcl.size //= 3
            prtcl.show()

        npcs.extend(Npc() for _ in range(5))

    def show(self): WINDOW.blit(self.img, (0,-125))

class Player:
    def __init__(self):
        img = pygame.image.load('src/JP_Zadi.png')
        self.img = img
        self.size = 100
        self.pos = [10, 10]
        self.change_img_size()

    def change_img_size(self): self.img_size = pygame.transform.scale(self.img, (self.size, self.size))

    def create_hitbox(self):
        self.hitbox_size = (self.size//2)*(math.cos(math.pi/4))*2 
        self.hitbox_pos = tuple(pos + (self.size - self.hitbox_size)//2 for pos in self.pos)

    def move(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]: self.pos[0] -= 1
        elif key[pygame.K_RIGHT]: self.pos[0] += 1

        if key[pygame.K_UP]: self.pos[1] -= 1
        elif key[pygame.K_DOWN]: self.pos[1] += 1
        self.create_hitbox()

    def eat(self, foods):
        for food in foods:
            if (self.hitbox_pos[0] <= food.pos[0] <= self.hitbox_pos[0] + self.hitbox_size and
                self.hitbox_pos[1] <= food.pos[1] <= self.hitbox_pos[1] + self.hitbox_size and
                self.size/2 > food.size ):

                self.size += food.size
                self.pos = [pos-food.size//2 for pos in self.pos]
                if type(food) == Npc: pygame.mixer.music.play()
                foods.remove(food)
                self.change_img_size()

            else: food.show()

    def show(self):
        self.change_img_size()
        self.create_hitbox()
        WINDOW.blit(self.img_size, tuple(self.pos))

class Particle:
    def __init__(self):
        self.pos = (randint(0, WIN_SIZE[0]), randint(0, WIN_SIZE[1]))
        self.color = (255, 0, 0)
        self.size = randint(2,10)
        self.show()

    def show(self): pygame.draw.circle(WINDOW, self.color, self.pos, self.size)

class Npc:
    def __init__(self):
        self.pos = (randint(20, WIN_SIZE[0]-20), randint(20, WIN_SIZE[0]-20))
        self.size = 50
        self.color = (randint(0,255), randint(0,255), randint(0,255))
        self.target = None
        self.show()

    def create_hitbox(self):
        self.hitbox_size = (self.size)*(math.cos(math.pi/4))*2
        self.hitbox_pos = tuple(pos - self.hitbox_size//2 for pos in self.pos)

    def move(self):
        if self.target not in particles: self.target = particles[randint(0, len(particles)-1)]
        self.target.color = self.color
        coord = (self.pos[0]-self.target.pos[0], self.pos[1]-self.target.pos[1])

        x = coord[0]//abs(coord[0]) if coord[0] != 0 else 0
        y = coord[1]//abs(coord[1]) if coord[1] != 0 else 0
        self.pos = (self.pos[0] - x, self.pos[1] - y)
        self.create_hitbox()

    def eat(self, foods):
        for food in foods:
            if (self.hitbox_pos[0] <= food.pos[0] <= self.hitbox_pos[0] + self.hitbox_size and
                self.hitbox_pos[1] <= food.pos[1] <= self.hitbox_pos[1] + self.hitbox_size and
                self.size > food.size and self != food ):

                self.size += food.size//2
                if type(food) == Npc: pygame.mixer.music.play()
                foods.remove(food)
                self.show()

            else: food.show()

    def eat_player(self, joueur):
        if (self.hitbox_pos[0] <= joueur.pos[0]+joueur.size//2 <= self.hitbox_pos[0]+self.hitbox_size and
            self.hitbox_pos[1] <= joueur.pos[1]+joueur.size//2 <= self.hitbox_pos[1]+self.hitbox_size and
            self.size > joueur.size//2):

            self.size += joueur.size//2
            joueur.size = 0
            pygame.mixer.music.play()
            joueur.changerTailleImg()

        else: joueur.show()

    def show(self):
        self.create_hitbox()
        pygame.draw.circle(WINDOW, self.color, self.pos, self.size)


background = Background()
player = Player()
particles = [Particle() for _ in range(NB_PARTICLES)]
npcs = [Npc() for _ in range(NB_NPCS)]

is_running = True
while is_running:
    background.show()
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP: pygame.mixer.music.play()
        elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            is_running = False

    player.move()
    player.eat(particles)
    player.eat(npcs)
    player.show()

    if len(particles) <= len(npcs): particles.extend(Particle() for _ in range(len(npcs)))

    sizes = [player.size//2]
    for npc in npcs:
        npc.move()
        npc.show()
        npc.eat(particles)
        npc.eat(npcs)
        npc.eat_player(player)
        
        sizes.append(npc.size)

    if max(sizes) > WIN_SIZE[1]/4 and background.zoom > 1: background.unzoom(player, npcs, particles)

    pygame.time.delay(7)
    pygame.display.flip()