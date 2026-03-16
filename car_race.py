import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Racing Game")
clock = pygame.time.Clock()

level = 1

# Colors
GREEN = (34,177,76)
DARK_GREEN = (20,120,20)
GRAY = (120,120,120)
WHITE = (255,255,255)
BLUE = (0,100,255)
RED = (200,0,0)
BLACK = (20,20,20)
BROWN = (120,80,20)
YELLOW = (255,255,0)
RAIN = (150,150,255)

road_x = 200
road_width = 400

font = pygame.font.SysFont(None,40)
big_font = pygame.font.SysFont(None,70)

obstacle_width = 40
obstacle_height = 40

# ------------------
# Explosion
# ------------------
def create_explosion(surface,x,y,max_radius=50,delay=15):
    colors=[(255,100,0),(255,150,0),(255,200,0)]
    for radius in range(0,max_radius,3):
        for color in colors:
            pygame.draw.circle(surface,color,(int(x),int(y)),radius)
        pygame.display.update()
        pygame.time.delay(delay)

# ------------------
# Draw Car (RESTORED ORIGINAL)
# ------------------
def draw_car(color):
    car_surface = pygame.Surface((40,70), pygame.SRCALPHA)
    pygame.draw.rect(car_surface,color,(5,10,30,50),border_radius=8)
    # front window
    pygame.draw.rect(car_surface,(200,220,255),(10,15,20,15),border_radius=4)
    # back window
    pygame.draw.rect(car_surface,(200,220,255),(10,40,20,15),border_radius=4)
    # wheels
    pygame.draw.rect(car_surface,BLACK,(0,15,5,15))
    pygame.draw.rect(car_surface,BLACK,(35,15,5,15))
    pygame.draw.rect(car_surface,BLACK,(0,40,5,15))
    pygame.draw.rect(car_surface,BLACK,(35,40,5,15))
    return car_surface

# ------------------
# Draw Trees
# ------------------
def draw_tree(surface,x,y):
    if level == 1:
        pygame.draw.rect(surface,(139,69,19),(x-5,y,10,20))
        pygame.draw.circle(surface,(0,155,0),(x,y),15)
    else:
        pygame.draw.rect(surface,(120,70,30),(x-6,y,12,25))
        pygame.draw.circle(surface,(0,200,0),(x,y),18)
        pygame.draw.circle(surface,(0,170,0),(x-10,y+5),15)
        pygame.draw.circle(surface,(0,170,0),(x+10,y+5),15)

# ------------------
# Reset Game
# ------------------
def reset_game(new_level=1):
    global player_x,player_y,player_speed,player_angle,player_progress
    global ai_x,ai_y,ai_progress
    global obstacles,monkeys,snakes,rain
    global trees,game_over,winner
    global race_started,countdown_start_ticks,countdown_time
    global level

    level = new_level

    player_x = WIDTH//2
    player_y = 450
    player_speed = 0
    player_angle = 180
    player_progress = 0

    ai_x = WIDTH//2 + 80
    ai_y = 300
    ai_progress = 0

    obstacles = []
    monkeys = []
    snakes = []

    rain=[]
    for i in range(120):
        rain.append([random.randint(0,WIDTH),random.randint(0,HEIGHT)])

    game_over=False
    winner=""

    race_started=False
    countdown_start_ticks=pygame.time.get_ticks()
    countdown_time=3

    trees=[]
    for i in range(50):
        side=random.choice(["left","right"])
        x=random.randint(50,road_x-30) if side=="left" else random.randint(road_x+road_width+30,WIDTH-50)
        y=random.randint(-6000,HEIGHT)
        trees.append([x,y])

reset_game()

player_acceleration = 0.25
player_max_speed = 9
player_friction = 0.05
turn_speed = 3
grip = 0.92

ai_speed = 3
race_distance = 6000

running=True

while running:
    clock.tick(60)

    # BACKGROUND
    if level == 1:
        screen.fill(DARK_GREEN)
        grass = GREEN
    else:
        screen.fill((10,80,10))
        grass = (0,120,0)

    pygame.draw.rect(screen,grass,(0,0,road_x,HEIGHT))
    pygame.draw.rect(screen,grass,(road_x+road_width,0,WIDTH-road_x-road_width,HEIGHT))
    pygame.draw.rect(screen,GRAY,(road_x,0,road_width,HEIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False

    keys = pygame.key.get_pressed()

    # RAIN LEVEL 2
    if level == 2:
        for drop in rain:
            pygame.draw.line(screen,RAIN,(drop[0],drop[1]),(drop[0],drop[1]+8),1)
            drop[1]+=10
            if drop[1] > HEIGHT:
                drop[1]=0
                drop[0]=random.randint(0,WIDTH)

    # COUNTDOWN
    if not race_started:
        elapsed=(pygame.time.get_ticks()-countdown_start_ticks)/1000
        seconds_left=countdown_time-int(elapsed)

        if seconds_left>0:
            text="READY" if seconds_left==3 else "SET" if seconds_left==2 else "GO!"
            countdown_text=big_font.render(text,True,RED)
            screen.blit(countdown_text,(WIDTH//2-80,HEIGHT//2))
        else:
            race_started=True

    else:
        if not game_over:
            # PLAYER MOVEMENT
            if keys[pygame.K_UP]:
                player_speed += player_acceleration
            if keys[pygame.K_DOWN]:
                player_speed -= player_acceleration

            player_speed=max(-player_max_speed/2,min(player_speed,player_max_speed))

            if player_speed!=0:
                if keys[pygame.K_LEFT]:
                    player_angle+=turn_speed
                if keys[pygame.K_RIGHT]:
                    player_angle-=turn_speed

            player_speed *= (1-player_friction)
            player_x += player_speed * math.sin(math.radians(player_angle)) * grip
            player_x=max(road_x,min(player_x,road_x+road_width))
            player_progress+=player_speed

            # AI PROGRESS
            ai_progress += ai_speed + random.uniform(-0.2,0.2)

            # LEVEL 1 OBSTACLES
            if level == 1 and random.randint(1,60)==1:
                obstacles.append([random.randint(road_x,road_x+road_width-obstacle_width),-50])
            for o in obstacles:
                o[1]+=5

            player_rect=pygame.Rect(player_x-20,player_y-35,40,70)
            for o in obstacles:
                rect=pygame.Rect(o[0],o[1],obstacle_width,obstacle_height)
                if player_rect.colliderect(rect):
                    create_explosion(screen,player_x,player_y)
                    game_over=True
                    winner="YOU CRASHED!"

            # LEVEL 2 MONKEYS & SNAKES
            if level == 2 and random.randint(1,180)==1:
                monkeys.append([road_x-40, random.randint(100,500), 4])
            if level == 2 and random.randint(1,160)==1:
                snakes.append([random.randint(road_x, road_x+road_width), -50, 50])

            # Draw monkeys with ears
            for m in monkeys:
                x, y, speed = m
                # body
                pygame.draw.rect(screen, (139,69,19), (x, y, 20, 15))
                # head
                pygame.draw.circle(screen, (160,82,45), (x+10, y-5), 7)
                # ears
                pygame.draw.circle(screen, (160,82,45), (x+4, y-5), 3)
                pygame.draw.circle(screen, (160,82,45), (x+16, y-5), 3)
                # tail
                pygame.draw.line(screen, (139,69,19), (x+20, y+7), (x+30, y+5), 3)
                # move
                m[0] += speed

            # Draw snakes
            for s in snakes:
                x, y, length = s
                for i in range(0, length, 5):
                    pygame.draw.circle(screen, (0,150,0), (x + int(5*math.sin(i/5)), y+i), 3)
                s[1] += 3

            # Collisions monkeys
            for m in monkeys:
                if player_rect.colliderect(pygame.Rect(m[0],m[1],20,15)):
                    create_explosion(screen,player_x,player_y)
                    game_over=True
                    winner="YOU HIT A MONKEY!"
            # Collisions snakes
            for s in snakes:
                if player_rect.colliderect(pygame.Rect(s[0],s[1],5, s[2])):
                    create_explosion(screen,player_x,player_y)
                    game_over=True
                    winner="YOU HIT A SNAKE!"

            # WIN CONDITIONS
            if player_progress >= race_distance:
                if level == 1:
                    reset_game(2)
                else:
                    game_over=True
                    winner="YOU WON THE GAME!"
            elif ai_progress >= race_distance:
                game_over=True
                winner="AI WON!"

    # Draw trees
    for tree in trees:
        draw_tree(screen,tree[0],tree[1])

    # ROAD LINES
    for i in range(0, HEIGHT, 40):
        pygame.draw.line(
            screen,
            WHITE,
            (WIDTH//2, i + int(player_progress) % 40),
            (WIDTH//2, i + 20 + int(player_progress) % 40),
            5
        )

    # DRAW CARS
    rotated_player=pygame.transform.rotate(draw_car(BLUE),player_angle)
    screen.blit(rotated_player,rotated_player.get_rect(center=(player_x,player_y)).topleft)
    rotated_ai=pygame.transform.rotate(draw_car(RED),0)
    screen.blit(rotated_ai,rotated_ai.get_rect(center=(ai_x,ai_y)).topleft)

    # DRAW LEVEL 1 OBSTACLES
    for o in obstacles:
        pygame.draw.rect(screen,BROWN,(o[0],o[1],obstacle_width,obstacle_height))

    # UI
    distance_left=max(0,int(race_distance-player_progress))
    screen.blit(font.render(f"Distance Left: {distance_left}",True,BLACK),(20,20))
    screen.blit(font.render(f"Level: {level}",True,BLACK),(20,60))

    # Game over
    if game_over:
        win_text=big_font.render(winner,True,BLACK)
        screen.blit(win_text,(WIDTH//2-200,HEIGHT//2))
        restart_text=font.render("Press SPACE to restart",True,BLACK)
        screen.blit(restart_text,(WIDTH//2-150,HEIGHT//2+80))
        if keys[pygame.K_SPACE]:
            reset_game(1)

    pygame.display.update()

pygame.quit()
sys.exit()