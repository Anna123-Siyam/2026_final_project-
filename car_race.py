import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Racing Game")
clock = pygame.time.Clock()

# Game state
game_state = "menu"
transition_start_time = 0
transition_duration = 2000  # 2 seconds

level = 1

# Colors
GREEN = (34,177,76)
DARK_GREEN = (20,120,20)
GRAY = (120,120,120)
WHITE = (255,255,255)
BLUE = (0,100,255)
BLACK = (20,20,20)
BROWN = (120,80,20)
RAIN = (150,150,255)
RED = (255,0,0)

road_x = 200
road_width = 400

font = pygame.font.SysFont(None,40)
big_font = pygame.font.SysFont(None,70)

start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)

obstacle_width = 40
obstacle_height = 40

# --- MENU / CHECKERED BACKGROUND ---
def draw_checkered_background(surface, square_size=40):
    cols = WIDTH // square_size + 1
    rows = HEIGHT // square_size + 1
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * square_size, y * square_size, square_size, square_size)
            if (x + y) % 2 == 0:
                pygame.draw.rect(surface, BLACK, rect)
            else:
                pygame.draw.rect(surface, WHITE, rect)

def draw_menu():
    draw_checkered_background(screen)
    smaller_big_font = pygame.font.SysFont(None, 45)

    title_text = "Welcome to Anna's Car Racing Game"
    subtitle_text = "Click Start to begin the game"

    title = smaller_big_font.render(title_text, True, RED)
    subtitle = font.render(subtitle_text, True, RED)

    title_x = WIDTH//2 - title.get_width()//2
    subtitle_x = WIDTH//2 - subtitle.get_width()//2

    banner_top = HEIGHT//2 - 120
    banner_left = min(title_x, subtitle_x) - 20
    banner_right = max(title_x + title.get_width(),
                       subtitle_x + subtitle.get_width()) + 20
    banner_bottom = HEIGHT//2 + 10

    pygame.draw.rect(screen, WHITE,
        (banner_left, banner_top, banner_right - banner_left, banner_bottom - banner_top),
        border_radius=10)

    pygame.draw.rect(screen, BLACK,
        (banner_left, banner_top, banner_right - banner_left, banner_bottom - banner_top),
        3, border_radius=10)

    screen.blit(title, (title_x, HEIGHT//2 - 100))
    screen.blit(subtitle, (subtitle_x, HEIGHT//2 - 50))

    pygame.draw.rect(screen, (200, 0, 0), start_button, border_radius=10)
    button_text = font.render("START", True, WHITE)
    screen.blit(button_text,
        (start_button.x + start_button.width//2 - button_text.get_width()//2,
         start_button.y + start_button.height//2 - button_text.get_height()//2))

# --- TRANSITION SCREEN (FIXED) ---
def draw_transition():
    draw_checkered_background(screen)

    text = big_font.render("Moving on to Level 2", True, RED)

    text_x = WIDTH//2 - text.get_width()//2
    text_y = HEIGHT//2 - text.get_height()//2

    padding = 20

    # ONLY white rectangle behind text
    pygame.draw.rect(
        screen,
        WHITE,
        (text_x - padding,
         text_y - padding,
         text.get_width() + padding * 2,
         text.get_height() + padding * 2),
        border_radius=10
    )

    screen.blit(text, (text_x, text_y))

# --- GAME FUNCTIONS ---
def create_explosion(surface,x,y,max_radius=50,delay=15):
    colors=[(255,100,0),(255,150,0),(255,200,0)]
    for radius in range(0,max_radius,3):
        for color in colors:
            pygame.draw.circle(surface,color,(int(x),int(y)),radius)
        pygame.display.update()
        pygame.time.delay(delay)

def draw_car(color):
    car_surface = pygame.Surface((40,70), pygame.SRCALPHA)
    pygame.draw.rect(car_surface,color,(5,10,30,50),border_radius=8)
    pygame.draw.rect(car_surface,(200,220,255),(10,15,20,15),border_radius=4)
    pygame.draw.rect(car_surface,(200,220,255),(10,40,20,15),border_radius=4)
    pygame.draw.rect(car_surface,BLACK,(0,15,5,15))
    pygame.draw.rect(car_surface,BLACK,(35,15,5,15))
    pygame.draw.rect(car_surface,BLACK,(0,40,5,15))
    pygame.draw.rect(car_surface,BLACK,(35,40,5,15))
    return car_surface

def draw_tree(surface,x,y):
    if level == 1:
        pygame.draw.rect(surface,(139,69,19),(x-5,y,10,20))
        pygame.draw.circle(surface,(0,155,0),(x,y),15)
    else:
        pygame.draw.rect(surface,(120,70,30),(x-6,y,12,25))
        pygame.draw.circle(surface,(0,200,0),(x,y),18)
        pygame.draw.circle(surface,(0,170,0),(x-10,y+5),15)
        pygame.draw.circle(surface,(0,170,0),(x+10,y+5),15)

def reset_game(new_level=1):
    global player_x,player_y,player_speed,player_angle,player_progress
    global obstacles,snakes,rain
    global trees,game_over,winner
    global race_started,countdown_start_ticks,countdown_time
    global level

    level = new_level
    player_x = WIDTH//2
    player_y = 450
    player_speed = 0
    player_angle = 180
    player_progress = 0

    obstacles = []
    snakes = []

    rain = []
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

player_acceleration = 0.25
player_max_speed = 9
player_friction = 0.05
turn_speed = 3
grip = 0.92
race_distance = 6000
reset_game()

running=True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    reset_game(1)
                    game_state = "game"

    if game_state == "menu":
        draw_menu()
        pygame.display.update()
        continue

    # --- TRANSITION STATE ---
    if game_state == "transition":
        draw_checkered_background(screen)
        draw_transition()
        pygame.display.update()

        if pygame.time.get_ticks() - transition_start_time > transition_duration:
            reset_game(2)
            game_state = "game"

        continue

    # --- GAME ---
    if level == 1:
        screen.fill(DARK_GREEN)
        grass = GREEN
    else:
        screen.fill((10,80,10))
        grass = (0,120,0)

    pygame.draw.rect(screen,grass,(0,0,road_x,HEIGHT))
    pygame.draw.rect(screen,grass,(road_x+road_width,0,WIDTH-road_x-road_width,HEIGHT))
    pygame.draw.rect(screen,GRAY,(road_x,0,road_width,HEIGHT))

    keys = pygame.key.get_pressed()

    if level == 2:
        for drop in rain:
            pygame.draw.line(screen,RAIN,(drop[0],drop[1]),(drop[0],drop[1]+8),1)
            drop[1]+=10
            if drop[1] > HEIGHT:
                drop[1]=0
                drop[0]=random.randint(0,WIDTH)

    if not race_started:
        elapsed=(pygame.time.get_ticks()-countdown_start_ticks)/1000
        seconds_left=countdown_time-int(elapsed)
        if seconds_left>0:
            text="READY" if seconds_left==3 else "SET" if seconds_left==2 else "GO!"
            countdown_text=big_font.render(text,True,(200,0,0))
            screen.blit(countdown_text,(WIDTH//2-80,HEIGHT//2))
        else:
            race_started=True
    else:
        if not game_over:
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

            spawn_rate = 60 if level == 1 else 40
            if random.randint(1, spawn_rate) == 1:
                obstacles.append([random.randint(road_x, road_x+road_width-40), -50])

            for o in obstacles:
                speed = 5 if level == 1 else 7
                o[1] += speed

            player_rect=pygame.Rect(player_x-20,player_y-35,40,70)

            for o in obstacles:
                if player_rect.colliderect(pygame.Rect(o[0],o[1],40,40)):
                    create_explosion(screen,player_x,player_y)
                    game_over=True
                    winner="YOU CRASHED!"

            if level == 2 and random.randint(1,160)==1:
                snakes.append([random.randint(road_x, road_x+road_width), -50, 50])

            for s in snakes:
                x, y, length = s
                for i in range(0, length, 5):
                    pygame.draw.circle(screen, (0,100,0),
                        (x + int(5*math.sin(i/5)), y+i), 3)
                s[1] += 3

            for s in snakes:
                if player_rect.colliderect(pygame.Rect(s[0],s[1],5,s[2])):
                    create_explosion(screen,player_x,player_y)
                    game_over=True
                    winner="YOU HIT A SNAKE!"

            if player_progress >= race_distance:
                if level == 1:
                    game_state = "transition"
                    transition_start_time = pygame.time.get_ticks()
                else:
                    game_over=True
                    winner="YOU WON THE GAME!"

    for tree in trees:
        draw_tree(screen,tree[0],tree[1])

    for i in range(0, HEIGHT, 40):
        pygame.draw.line(screen,WHITE,
            (WIDTH//2, i + int(player_progress) % 40),
            (WIDTH//2, i + 20 + int(player_progress) % 40),5)

    rotated_player=pygame.transform.rotate(draw_car(BLUE),player_angle)
    screen.blit(rotated_player,
        rotated_player.get_rect(center=(player_x,player_y)).topleft)

    for o in obstacles:
        pygame.draw.rect(screen,BROWN,(o[0],o[1],40,40))

    distance_left=max(0,int(race_distance-player_progress))
    screen.blit(font.render(f"Distance Left: {distance_left}",True,BLACK),(20,20))
    screen.blit(font.render(f"Level: {level}",True,BLACK),(20,60))

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