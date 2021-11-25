import pygame, sys, random
import numpy as np
import pickle

# for the birds - quantity, the brain, etc.
nplayer = 100
n1 = 16
n2 = 16
reload = True

def draw_floor():
    screen.blit(floor_surface, (floor_x_pos,900))
    screen.blit(floor_surface, (floor_x_pos + 576,900))

def create_pipe():
    random_pipe_pos = random.randint(350,800)
    bottom_pipe = pipe_surface.get_rect(midtop = (700,random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (700,random_pipe_pos-250))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 2
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes

def draw_pipes(pipes):
    bottom = True
    for pipe in pipes:
        if bottom:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)
        bottom = not bottom

def check_collision(pipes, i):
    for pipe in pipes:
        if bird_rects[i].colliderect(pipe):
            return False

    if bird_rects[i].top <= -100 or bird_rects[i].bottom >= 900:
        return False

    return True

def rotate_bird(bird, i):
    new_bird = pygame.transform.rotozoom(bird, -bird_movements[i]*3, 1)
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rects = [new_bird.get_rect(center = (100,bird_rect.centery)) for bird_rect in bird_rects]
    return new_bird, new_bird_rects

def score_display():
    score_surface = game_font.render(str(score), True, (255,255,255))
    score_rect = score_surface.get_rect(center = (288,100))
    screen.blit(score_surface, score_rect)

    high_score_surface = game_font.render(f'High score: {high_score}', True, (255,255,255))
    high_score_rect = high_score_surface.get_rect(center = (288,985))
    screen.blit(high_score_surface, high_score_rect)

def gen_display():
    gen_surface = game_font.render(f'Gen: {gen}', True, (255,255,255))
    gen_rect = gen_surface.get_rect(midright = (550,100))
    screen.blit(gen_surface, gen_rect)

    num_surface = game_font.render(f'{game_actives.count(True)} birds', True, (255,255,255))
    num_rect = num_surface.get_rect(midright = (550,150))
    screen.blit(num_surface, num_rect)

    fit_surface = game_font.render(f'{fitness//100}m', True, (255,255,255))
    fit_rect = fit_surface.get_rect(midright = (550,200))
    screen.blit(fit_surface, fit_rect)

def pipe_score_check():
    global score
    for i in range(0, len(pipe_list), 2):
        if 98 < pipe_list[i].centerx < 102:
            score += 1

def sigmoid(x, deriv=False):
    sigmoid_ = np.reciprocal(1 + np.exp(-x))
    if deriv:
        return sigmoid_ * (1 - sigmoid_)
    return sigmoid_

def tanh(x, deriv=False):
    if deriv:
        return np.reciprocal(2 * np.cosh(x)**2)
    return (np.tanh(x)+1) / 2

# each player can know: birdy, bird_movement, pipex, pipey, npipex, npipey
class Player:
    def __init__(self, n1, n2, firstGen=True, w1=None, b1=None, w2=None, b2=None, w3=None, b3=None):
        if firstGen:
            self.w1 = np.random.randn(n1, 6)
            self.b1 = np.random.randn(n1, 1)
            self.w2 = np.random.randn(n2, n1)
            self.b2 = np.random.randn(n2, 1)
            self.w3 = np.random.randn(1, n2)
            self.b3 = np.random.randn(1, 1)
        else:
            self.w1, self.b1, self.w2, self.b2, self.w3, self.b3 = w1, b1, w2, b2, w3, b3

    def flap(self, birdy, bird_movement, pipex, pipey, npipex, npipey):
        a0 = np.array([birdy, bird_movement, pipex, pipey, npipex, npipey]).reshape(6,1)
        a1 = tanh(self.w1 @ a0 + self.b1)
        a2 = tanh(self.w2 @ a1 + self.b2)
        a3 = sigmoid(self.w3 @ a2 + self.b3)
        return round(a3.item())

    def bear(self):
        dw1, db1, dw2, db2, dw3, db3 = [np.random.randn(x.shape[0], x.shape[1])*0.1 for x in [self.w1, self.b1, self.w2, self.b2, self.w3, self.b3]]
        return Player(n1, n2, False, self.w1+dw1, self.b1+db1, self.w2+dw2, self.b2+db2, self.w3+dw3, self.b3+db3)

pygame.init()
screen = pygame.display.set_mode((576,1024))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf', 40)

# game variables
gravity = 0.25
bird_movements = [0 for _ in range(nplayer)]
game_actives = [True for _ in range(nplayer)]
fitnesses = [0 for _ in range(nplayer)] # distance traveled
fitness = 0
score = 0
high_score = 0

bg_surface = pygame.image.load('assets/background-night.png').convert() # easier for pygame to work with
bg_surface = pygame.transform.scale(bg_surface, (576,1024))

floor_surface = pygame.image.load('assets/base.png').convert()
floor_surface = pygame.transform.scale2x(floor_surface)
floor_x_pos = 0

bird_downflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-downflap.png').convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-upflap.png').convert_alpha())
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 1
bird_surface = bird_frames[bird_index]
bird_rects = [bird_surface.get_rect(center = (100,512)) for _ in range(nplayer)]

BIRDFLAP = 0

pipe_surface = pygame.image.load('assets/pipe-red.png').convert()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
SPAWNPIPE = 169

# the automated birds army :))
if reload:
    with open(r'.\data\data_fast', 'rb') as load_file:
        data = pickle.load(load_file)
    gen = data['gen']
    high_score = data['high_score']
    birds = data['birds']
else:
    gen = 1
    birds = [Player(n1,n2) for _ in range(nplayer)]

while True:
    fitness += 1
    
    BIRDFLAP = (BIRDFLAP + 1) % 7
    if BIRDFLAP == 0:
        bird_index = (bird_index + 1) % 3
        bird_surface, bird_rects = bird_animation()
    
    SPAWNPIPE = (SPAWNPIPE + 1) % 170
    if SPAWNPIPE == 0:
        pipe_list.extend(create_pipe())
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(bg_surface, (0,0))

    current_pipe = next(pipe for pipe in pipe_list if pipe.right > 60)
    next_pipe = next((pipe for pipe in pipe_list if pipe.right > current_pipe.right), current_pipe)
    for i in range(nplayer):
        if game_actives[i]:
            # bird
            if birds[i].flap(bird_rects[i].centery, bird_movements[i], current_pipe.centerx, current_pipe.top-125, next_pipe.centerx, next_pipe.top-125):
                bird_movements[i] = -8.5
                
            bird_movements[i] += gravity
            rotated_bird = rotate_bird(bird_surface, i)
            bird_rects[i].centery += bird_movements[i]
            screen.blit(rotated_bird, bird_rects[i])
            game_actives[i] = check_collision(pipe_list, i)
            if not game_actives[i]:
                fitnesses[i] = fitness

    if game_actives.count(True) > 40:
        # pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
        
        pipe_score_check()
    else:
        # wipe out the worst half of the population, then reproduce, nplayer % 2 == 0
        indices = np.argsort(fitnesses)[::-1][:nplayer//2]
        hatchlings = []
        for i in indices:
            hatchlings.append(birds[i])
            hatchlings.append(birds[i].bear())
        birds = hatchlings

        # game logic
        game_actives = [True for _ in range(nplayer)]
        pipe_list.clear()
        SPAWNPIPE = 169
        for i in range(nplayer):
            bird_rects[i].center = (100,512)
        bird_movements = [0 for _ in range(nplayer)]
        #print([f for f in fitnesses if f])
        fitnesses = [0 for _ in range(nplayer)]
        fitness = 0
        high_score = max(high_score, score)
        score = 0
        gen += 1

        # save the birds
        with open(r'.\data\data_fast', 'wb') as save_file:
            pickle.dump({'gen': gen, 'high_score': high_score, 'birds': birds}, save_file)

    # floor
    floor_x_pos -= 2
    draw_floor()
    if floor_x_pos <= -576:
        floor_x_pos = 0

    # useful information
    score_display()
    gen_display()
    
    pygame.display.update()
    clock.tick(1000)
