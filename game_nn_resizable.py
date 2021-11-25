import pygame, sys, random
import numpy as np
import pickle

# for the birds - quantity, the brain, etc.
nplayer = 100
n1 = 16
n2 = 16
reload = True
shift = 5
frame_rate = 120
W,H = 576,1024 # the resolution that our birds are trained on

# display ratio
w = 288
h = w*H//W

# displaying shadow in fonts
dxy = [(-3*w/W,3*w/W),(3*w/W,3*w/W),(3*w/W,-3*w/W),(-3*w/W,-3*w/W),(5*w/W,5*w/W)]

def draw_floor():
    screen.blit(floor_surface, (floor_x_pos,900*w/W))
    screen.blit(floor_surface, (floor_x_pos + 576*w/W,900*w/W))

def create_pipe():
    random_pipe_pos = random.randint(350,800)
    bottom_pipe = pipe_surface.get_rect(midtop = (700*w/W,random_pipe_pos*w/W))
    top_pipe = pipe_surface.get_rect(midbottom = (700*w/W,(random_pipe_pos-250)*w/W))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 2*w/W
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

    if bird_rects[i].top <= -100*w/W or bird_rects[i].bottom >= 900*w/W:
        return False

    return True

def rotate_bird(bird, i):
    new_bird = pygame.transform.rotozoom(bird, -bird_movements[i]*3*W/w, 1)
    return new_bird

def bird_animation():
    new_bird_rects = [bird_surface.get_rect(center = (100*w/W,bird_rect.centery)) for bird_rect in bird_rects]
    return new_bird_rects

def info_display():
    nbirds = game_actives.count(True)
    # generation number
    gen_surface = game_font.render(f'Gen: {gen}', True, (0,0,0))
    # number of birds
    num_surface = game_font.render(f'{nbirds} bird' + ('s' if nbirds > 1 else ''), True, (0,0,0))
    # current distance
    fit_surface = game_font.render(f'{fitness//100}m', True, (0,0,0))
    # score
    score_surface = game_font.render(str(score), True, (0,0,0))
    # high score
    high_score_surface = game_font.render(f'High score: {high_score}', True, (0,0,0))
    # speed
    speed_surface = game_font.render(f'{frame_rate/120}x', True, (0,0,0))
    for dx,dy in dxy:
        gen_rect = gen_surface.get_rect(midright = ((550+dx)*w/W,(100+dy)*w/W))
        screen.blit(gen_surface, gen_rect)

        num_rect = num_surface.get_rect(midright = ((550+dx)*w/W,(150+dy)*w/W))
        screen.blit(num_surface, num_rect)

        fit_rect = fit_surface.get_rect(midright = ((550+dx)*w/W,(200+dy)*w/W))
        screen.blit(fit_surface, fit_rect)

        score_rect = score_surface.get_rect(center = ((288+dx)*w/W,(100+dy)*w/W))
        screen.blit(score_surface, score_rect)
        
        high_score_rect = high_score_surface.get_rect(center = ((288+dx)*w/W,(985+dy)*w/W))
        screen.blit(high_score_surface, high_score_rect)

        speed_rect = speed_surface.get_rect(midright = ((550+dx)*w/W,(250+dy)*w/W))
        screen.blit(speed_surface, speed_rect)
        
    gen_surface = game_font.render(f'Gen: {gen}', True, (255,255,255))
    gen_rect = gen_surface.get_rect(midright = (550*w/W,100*w/W))
    screen.blit(gen_surface, gen_rect)

    num_surface = game_font.render(f'{nbirds} bird' + ('s' if nbirds > 1 else ''), True, (255,255,255))
    num_rect = num_surface.get_rect(midright = (550*w/W,150*w/W))
    screen.blit(num_surface, num_rect)

    fit_surface = game_font.render(f'{fitness//100}m', True, (255,255,255))
    fit_rect = fit_surface.get_rect(midright = (550*w/W,200*w/W))
    screen.blit(fit_surface, fit_rect)

    score_surface = game_font.render(str(score), True, (255,255,255))
    score_rect = score_surface.get_rect(center = (288*w/W,100*w/W))
    screen.blit(score_surface, score_rect)

    high_score_surface = game_font.render(f'High score: {high_score}', True, (255,255,255))
    high_score_rect = high_score_surface.get_rect(center = (288*w/W,985*w/W))
    screen.blit(high_score_surface, high_score_rect)

    speed_surface = game_font.render(f'{frame_rate/120}x', True, (255,255,255))
    speed_rect = speed_surface.get_rect(midright = (550*w/W,250*w/W))
    screen.blit(speed_surface, speed_rect)

def pause_display():
    # darken the screen
    img = pygame.Surface((w,h))
    img.set_alpha(100)
    screen.blit(img, (0,0))
    
    pause_surface = game_font.render('||', True, (0,0,0))
    for dx,dy in dxy:
        pause_rect = pause_surface.get_rect(center = ((288+dx)*w/W,(512+dy)*w/W))
        screen.blit(pause_surface, pause_rect)
    
    pause_surface = game_font.render('||', True, (255,255,255))
    pause_rect = pause_surface.get_rect(center = (288*w/W,512*w/W))
    screen.blit(pause_surface, pause_rect)

def pipe_score_check():
    global score
    for i in range(0, len(pipe_list), 2):
        if 98*w/W < pipe_list[i].centerx < 102*w/W:
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
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf', 40*w//W)

# game variables
gravity = 0.25*w/W
bird_movements = [0 for _ in range(nplayer)]
game_actives = [True for _ in range(nplayer)]
fitnesses = [0 for _ in range(nplayer)] # distance traveled
fitness = 0
score = 0
high_score = 0

bg_surface = pygame.image.load('assets/background-night.png').convert() # easier for pygame to work with
bg_surface = pygame.transform.scale(bg_surface, (w,h))

floor_surface = pygame.image.load('assets/base.png').convert()
floor_surface = pygame.transform.scale(floor_surface, (2*floor_surface.get_size()[0]*w//W,2*floor_surface.get_size()[1]*w//W))
floor_x_pos = 0

bluebird_downflap = pygame.image.load('assets/bluebird-downflap.png').convert_alpha()
bluebird_downflap = pygame.transform.scale(bluebird_downflap, (2*bluebird_downflap.get_size()[0]*w//W,2*bluebird_downflap.get_size()[1]*w//W))
bluebird_midflap = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
bluebird_midflap = pygame.transform.scale(bluebird_midflap, (2*bluebird_midflap.get_size()[0]*w//W,2*bluebird_midflap.get_size()[1]*w//W))
bluebird_upflap = pygame.image.load('assets/bluebird-upflap.png').convert_alpha()
bluebird_upflap = pygame.transform.scale(bluebird_upflap, (2*bluebird_upflap.get_size()[0]*w//W,2*bluebird_upflap.get_size()[1]*w//W))

redbird_downflap = pygame.image.load('assets/redbird-downflap.png').convert_alpha()
redbird_downflap = pygame.transform.scale(redbird_downflap, (2*redbird_downflap.get_size()[0]*w//W,2*redbird_downflap.get_size()[1]*w//W))
redbird_midflap = pygame.image.load('assets/redbird-midflap.png').convert_alpha()
redbird_midflap = pygame.transform.scale(redbird_midflap, (2*redbird_midflap.get_size()[0]*w//W,2*redbird_midflap.get_size()[1]*w//W))
redbird_upflap = pygame.image.load('assets/redbird-upflap.png').convert_alpha()
redbird_upflap = pygame.transform.scale(redbird_upflap, (2*redbird_upflap.get_size()[0]*w//W,2*redbird_upflap.get_size()[1]*w//W))

yellowbird_downflap = pygame.image.load('assets/yellowbird-downflap.png').convert_alpha()
yellowbird_downflap = pygame.transform.scale(yellowbird_downflap, (2*yellowbird_downflap.get_size()[0]*w//W,2*yellowbird_downflap.get_size()[1]*w//W))
yellowbird_midflap = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
yellowbird_midflap = pygame.transform.scale(yellowbird_midflap, (2*yellowbird_midflap.get_size()[0]*w//W,2*yellowbird_midflap.get_size()[1]*w//W))
yellowbird_upflap = pygame.image.load('assets/bluebird-upflap.png').convert_alpha()
yellowbird_upflap = pygame.transform.scale(yellowbird_upflap, (2*yellowbird_upflap.get_size()[0]*w//W,2*yellowbird_upflap.get_size()[1]*w//W))

bird_frames = [[bluebird_downflap, redbird_downflap, yellowbird_downflap],
               [bluebird_midflap, redbird_midflap, yellowbird_midflap],
               [bluebird_upflap, redbird_upflap, yellowbird_upflap]]
flap_index = 1
color_indices = [0 for _ in range(nplayer)]
bird_surface = bird_frames[0][0]
bird_rects = [bird_frames[0][0].get_rect(center = (100*w/W,512*w/W)) for _ in range(nplayer)]

BIRDFLAP = 0

pipe_surface = pygame.image.load('assets/pipe-red.png').convert()
pipe_surface = pygame.transform.scale(pipe_surface, (2*pipe_surface.get_size()[0]*w//W,2*pipe_surface.get_size()[1]*w//W))
pipe_list = []
SPAWNPIPE = 169

# the automated birds army :))
if reload:
    with open(r'.\data\data', 'rb') as load_file:
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
        flap_index = (flap_index + 1) % 3
        bird_rects = bird_animation()
    
    SPAWNPIPE = (SPAWNPIPE + 1) % 170
    if SPAWNPIPE == 0:
        pipe_list.extend(create_pipe())
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # escape
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            # pause the process
            if event.key == pygame.K_SPACE:
                pause_display()
                pygame.display.update()
                cont = True
                while cont:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
                            if event.key == pygame.K_SPACE:
                                cont = False
                                break
            # change game speed
            if event.key == pygame.K_RIGHT:
                frame_rate = min(frame_rate << 1, 480)
            if event.key == pygame.K_LEFT:
                frame_rate = max(frame_rate >> 1, 30)

    screen.blit(bg_surface, (0,0))

    current_pipe = next(pipe for pipe in pipe_list if pipe.right > 60*w/W)
    next_pipe = next((pipe for pipe in pipe_list if pipe.right > current_pipe.right), current_pipe)
    for i in range(nplayer):
        if game_actives[i]:
            # bird
            if birds[i].flap(bird_rects[i].centery*W/w, bird_movements[i]*W/w, current_pipe.centerx*W/w, current_pipe.top*W/w-125, next_pipe.centerx*W/w, next_pipe.top*W/w-125):
                bird_movements[i] = -8.5*w/W
                color_indices[i] = (color_indices[i] + 1) % 3
                
            bird_movements[i] += gravity
            rotated_bird = rotate_bird(bird_frames[flap_index][color_indices[i]], i)
            bird_rects[i].centery += bird_movements[i]
            screen.blit(rotated_bird, bird_rects[i])
            if i == 0: # the best bird of the last generation - red circle
                pygame.draw.circle(screen, (255,0,0), bird_rects[i].center, 50*w//W, width=7*w//W)
            elif i == 1: # the hatchling of the best bird - yellow cirle
                pygame.draw.circle(screen, (255,255,0), bird_rects[i].center, 50*w//W, width=7*w//W)
            elif i == nplayer-2: # the worst bird of the last generation - black circle
                pygame.draw.circle(screen, (255,255,255), bird_rects[i].center, 50*w//W, width=7*w//W)
            elif i == nplayer-1: # the hatchling of the worst bird - white circle
                pygame.draw.circle(screen, (0,0,0), bird_rects[i].center, 50*w//W, width=7*w//W)
                
            game_actives[i] = check_collision(pipe_list, i)
            if not game_actives[i]:
                fitnesses[i] = fitness

    if any(game_actives):
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
            bird_rects[i].center = (100*w/W,512*w/W)
        bird_movements = [0 for _ in range(nplayer)]
        #print([f for f in fitnesses if f])
        fitnesses = [0 for _ in range(nplayer)]
        fitness = 0
        high_score = max(high_score, score)
        score = 0
        gen += 1

        # save the birds
        #with open(r'D:\personal\BKU\211\NCKH\flappy-bird\data', 'wb') as save_file:
        #    pickle.dump({'gen': gen, 'high_score': high_score, 'birds': birds}, save_file)

    # floor
    floor_x_pos -= 2*w/W
    draw_floor()
    if floor_x_pos <= -w:
        floor_x_pos = 0

    # useful information
    info_display()
    
    pygame.display.update()
    clock.tick(frame_rate)
