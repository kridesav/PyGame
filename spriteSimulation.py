import pygame
import math, random, sys, os, time
import numpy as np
import neat

# Constants
WIDTH = 1600
HEIGHT = 900
FPS = 120
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GREY = (128, 128, 128)
LIGHTGREY = (192, 192, 192)
DARKGREY = (64, 64, 64)
BROWN = (165, 42, 42)
DARKGREEN = (0, 100, 0)
LIGHTGREEN = (144, 238, 144)
LIGHTBLUE = (173, 216, 230)
LIGHTYELLOW = (255, 255, 224)
LIGHTORANGE = (255, 218, 185)
LIGHTPURPLE = (221, 160, 221)
LIGHTCYAN = (224, 255, 255)
LIGHTBROWN = (210, 180, 140)
LIGHTRED = (255, 192, 203)

# Classes
class Hunter:
    def __init__(self, x, y):
        self.surface = pygame.image.load('hunter.png').convert_alpha()
        self.surface = pygame.transform.scale(self.surface, (20, 20))
        self.rotateSurface = self.surface
        self.pos = [x, y]
        self.angle = 0
        self.vel = 1
        self.speed = 1
        self.center = [self.pos[0] + 10, self.pos[1] + 10]
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.action = ''
        self.health = 100
        self.score = 0
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 20, 20)

    def move(self):
        if self.action == 'left':
            self.angle -= 5
        if self.action == 'right':
            self.angle += 5
        if self.action == 'up':
            self.speed += self.vel
            if self.speed > 6:
                self.speed = 6
            if self.speed > 1:
                self.speed -= 0.5
            if self.speed < 1:
                self.speed = 1

    def draw(self, map):
        map.blit(self.rotateSurface, self.pos)
        # for r in self.radars:
        #     pygame.draw.line(map, RED, self.center, r[0], 1)
        
    
    def update(self, preys):
        self.health -= 0.25
        if self.health <= 0:
            self.is_alive = False
        self.move()

        self.pos[0] += math.cos(math.radians(self.angle)) * self.speed
        self.pos[1] -= math.sin(math.radians(self.angle)) * self.speed

        new_pos = [self.pos[0], self.pos[1]]

        edge = 800
        edge2 = 0
        penalty = 5

        # Check if the new position is outside the map area
        if new_pos[0] < edge2:
            new_pos[0] = edge2
            self.health -= penalty
        elif new_pos[0] + 20  > edge:
            new_pos[0] = edge - 20
            self.health -= penalty
        if new_pos[1] < edge2:
            new_pos[1] = edge2
            self.health -= penalty
        elif new_pos[1] + 20 > edge:
            new_pos[1] = edge - 20
            self.health -= penalty

        self.pos = new_pos

        self.rotateSurface = self.rot_center(self.surface, self.angle)
        self.center = [self.pos[0] + 10, self.pos[1] + 10]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 20, 20)
        self.radars.clear()
        self.radar(preys, 800, 800)
        self.attack(preys)
        
    def attack(self, preys):
        if not self.is_alive:
            return
        for prey in preys:
            if self.rect.colliderect(prey.rect):
                if prey.is_alive:
                    prey.health -= 100
                    self.health += 10
                    self.score += 10
                    
    
    def radar(self, preys, map_width, map_height):
        for angle in range(-35, 36, 10):  # Adjust the range and step as needed
            length = 0
            x = int(self.center[0] + math.cos(math.radians(360 - (angle))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (angle))) * length)
            hit = 0  # 0 = nothing in radar
            while length < 300:  # Reduce the maximum length to 200
                if x < 0 or y < 0 or x > map_width or y > map_height:  # Check if the radar line has hit a wall
                    hit = 2  # 2 = wall
                    break
                for prey in preys:
                    if prey.rect.collidepoint((x, y)):
                        if prey.is_alive:
                            hit = 1  # 1 = prey
                            break
                if hit:
                    break
                length += 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + angle))) * length)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + angle))) * length)
            self.radars.append(hit)

    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
    
    def get_alive(self):
        return self.is_alive
    
    def get_health(self):
        return self.health
    
    def get_data(self):
        radars = self.radars
        ret = [0,0,0,0,0,0,0,0]
        for i, r in enumerate(radars):
            ret[i] = r
        return ret

    
class Prey:
    def __init__(self, x, y):
        self.surface = pygame.image.load('prey.png').convert_alpha()
        self.surface = pygame.transform.scale(self.surface, (20, 20))
        self.rotateSurface = self.surface
        self.pos = [x, y]
        self.angle = 0
        self.vel = 1
        self.speed = 1
        self.center = [self.pos[0] + 10, self.pos[1] + 10]
        self.action = ''
        self.health = 100
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 20, 20)
        self.is_alive = True

    def move(self):
        if self.action == 'left':
            self.angle -= 10
        if self.action == 'right':
            self.angle += 10
        if self.action == 'up':
            self.speed += self.vel
            if self.speed > 2:
                self.speed = 2
            if self.speed > 1:
                self.speed -= 0.5
            if self.speed < 1:
                self.speed = 1
    

    def draw(self, map):
        map.blit(self.rotateSurface, self.pos)

    def update(self):
        self.move()
        self.pos[0] += math.cos(math.radians(self.angle)) * self.speed
        self.pos[1] -= math.sin(math.radians(self.angle)) * self.speed

        new_pos = [self.pos[0], self.pos[1]]
        edge = 800
        edge2 = 0

        # Check if the new position is outside the map area
        if new_pos[0] < edge2:
            new_pos[0] = edge2
        elif new_pos[0] + 20  > edge:
            new_pos[0] = edge - 20
        if new_pos[1] < edge2:
            new_pos[1] = edge2
        elif new_pos[1] + 20 > edge:
            new_pos[1] = edge - 20

        self.pos = new_pos
        if self.health <= 0:
            self.is_alive = False
        
        self.rotateSurface = self.rot_center(self.surface, self.angle)
        self.center = [self.pos[0] + 10, self.pos[1] + 10]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 20, 20)
    
    def get_health(self):
        return self.health
    
    def get_alive(self):
        return self.is_alive
    
    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
    
# Map
def Map():
    map = pygame.image.load('map.png').convert_alpha()
    map = pygame.transform.scale(map, (800, 800))
    
    return map
# Functions



# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sprite Simulation")
map = Map()
background = pygame.Surface(map.get_size())


# Game loop
def run_sim(hunter_genomes, config):

    hunter_nets = []
    hunters = []
    preys = []
    for i in range(20):
        preys.append(Prey(random.randint(200,600), random.randint(200,600)))

    for genome_id, genome in hunter_genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        hunter_nets.append(net)
        hunters.append(Hunter(random.randint(0,800), random.randint(0,800)))

        # Initialize Pygame
    pygame.init()
    clock = pygame.time.Clock()
    start_time = time.time()

    running = True
    while running:
            background.fill(WHITE)
            background.blit(map, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            remaining_hunters = 0
            elapsed_time = time.time() - start_time

            for i, hunter in enumerate(hunters):
                if hunter.get_alive():
                    remaining_hunters += 1
                    hunter.draw(background)
                output = hunter_nets[i].activate(hunter.get_data())
                if output[0] > 0.5:
                    hunter.action = 'left'
                if output[1] > 0.5:
                    hunter.action = 'right'
                if output[2] > 0.5:
                    hunter.action = 'up'

                hunter.update(preys)
                hunter.action = ''
                hunter_genomes[i][1].fitness = hunter.score

            if remaining_hunters == 0:
                break

            for i, prey in enumerate(preys):
                if prey.get_alive():
                    prey.draw(background)
                random_action = random.randint(0, 2)
                if random_action == 0:
                    prey.action = 'left'
                if random_action == 1:
                    prey.action = 'right'
                if random_action == 2:
                    prey.action = 'up'

                prey.update()
                prey.action = ''
                if not prey.get_alive():
                    preys[i] = Prey(random.randint(200,600), random.randint(200,600))
            
            screen.blit(background, (50, 50))
            
            pygame.display.update()
            clock.tick(FPS)

if __name__ == '__main__':
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, 'config-feedforward.txt')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(run_sim, 50)

    print('\nBest genome:\n{!s}'.format(winner))