import pygame
import sys
import random
import math

pygame.init()

# ------------------
# Window
# ------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Racing Game")
clock = pygame.time.Clock()

# ------------------
# Colors
# ------------------
GREEN = (34,177,76)
DARK_GREEN = (20,120,20)
GRAY = (120,120,120)
WHITE = (255,255,255)
BLUE = (0,100,255)
RED = (200,0,0)
BLACK = (20,20,20)
BROWN = (120,80,20)
YELLOW = (255,255,0)

# ------------------
# Track
# ------------------
road_x = 200
road_width = 400

# ------------------
# Fonts
# ------------------
font = pygame.font.SysFont(None,40)
big_font = pygame.font.SysFont(None,70)

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
# Draw Car
# ------------------
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

# ------------------
# Draw Tree
# ------------------
def draw_tree(surface,x,y):
    pygame.draw.rect(surface,(139,69,19),(x-5,y,10,20))
    pygame.draw.circle(surface,(0,155,0),(x,y),15)

# ------------------
# Reset Game
# ------------------
def reset_game():

    global player_x,player_y,player_speed,player_angle,player_progress
    global ai_x,ai_y,ai_progress,ai_crashed
    global obstacles,boosts,boost_timer
    global trees,game_over,winner
    global countdown_time,race_started,countdown_start_ticks

    player_x = WIDTH//2
    player_y = 450
    player_speed = 0
    player_angle = 180
    player_progress = 0

    ai_x = WIDTH//2 + 80
    ai_y = 300
    ai_progress = 0
    ai_crashed = False

    obstacles = []
    boosts = []
    boost_timer = 0

    game_over = False
    winner = ""

    race_started = False
    countdown_start_ticks = pygame.time.get_ticks()
    countdown_time = 3

    trees=[]
    for i in range(50):
        side=random.choice(["left","right"])
        x=random.randint(50,road_x-30) if side=="left" else random.randint(road_x+road_width+30,WIDTH-50)
        y=random.randint(-6000,HEIGHT)
        trees.append([x,y])

# ------------------
# Initialize
# ------------------
reset_game()

player_acceleration = 0.25
player_max_speed = 9
player_friction = 0.05
turn_speed = 3
grip = 0.92

ai_speed = 3
race_distance = 6000

obstacle_width = 40
obstacle_height = 40
obstacle_speed = 4

boost_width = 30
boost_height = 30
boost_speed = 6

# ------------------
# Game Loop
# ------------------
running=True

while running:

    clock.tick(60)
    screen.fill(DARK_GREEN)

    pygame.draw.rect(screen,GREEN,(0,0,road_x,HEIGHT))
    pygame.draw.rect(screen,GREEN,(road_x+road_width,0,WIDTH-road_x-road_width,HEIGHT))
    pygame.draw.rect(screen,GRAY,(road_x,0,road_width,HEIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False

    keys = pygame.key.get_pressed()

    # ------------------
    # Countdown
    # ------------------
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

            # ------------------
            # Player Movement
            # ------------------
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

            if abs(player_speed)<0.05:
                player_speed=0

            if boost_timer>0:
                player_speed+=0.3
                boost_timer-=1

            player_x += player_speed * math.sin(math.radians(player_angle)) * grip
            player_x=max(road_x,min(player_x,road_x+road_width))
            player_progress+=player_speed

            # ------------------
            # SUPER SMART AI
            # ------------------
            if ai_progress < race_distance and not ai_crashed:

                ai_y = 300
                road_center = road_x + road_width//2

                ai_rect = pygame.Rect(ai_x-20, ai_y-35, 40,70)

                for obstacle in obstacles:

                    obs_rect = pygame.Rect(obstacle[0],obstacle[1],obstacle_width,obstacle_height)

                    # look very far ahead
                    if obs_rect.top > ai_y-60 and obs_rect.top < ai_y+250:

                        if ai_rect.colliderect(obs_rect):

                            if ai_x < road_center:
                                ai_x -= 5
                            else:
                                ai_x += 5

                if ai_x < road_x+30:
                    ai_x += 4
                if ai_x > road_x+road_width-30:
                    ai_x -= 4

                if ai_x < road_center:
                    ai_x += 0.3
                elif ai_x > road_center:
                    ai_x -= 0.3

                ai_progress += ai_speed + random.uniform(-0.2,0.2)

            # ------------------
            # Spawn Obstacles
            # ------------------
            if random.randint(1,60)==1:
                obstacle_x=random.randint(road_x,road_x+road_width-obstacle_width)
                obstacles.append([obstacle_x,-50])

            # ------------------
            # Spawn Boost
            # ------------------
            if random.randint(1,200)==1:
                boost_x=random.randint(road_x,road_x+road_width-boost_width)
                boosts.append([boost_x,-50])

            for obstacle in obstacles:
                obstacle[1]+=obstacle_speed

            obstacles=[o for o in obstacles if o[1]<HEIGHT+100]

            for boost in boosts:
                boost[1]+=boost_speed

            boosts=[b for b in boosts if b[1]<HEIGHT+100]

            # ------------------
            # Move Trees
            # ------------------
            for tree in trees:
                tree[1]+=-player_speed

            player_rect=pygame.Rect(player_x-20,player_y-35,40,70)
            ai_rect=pygame.Rect(ai_x-20,ai_y-35,40,70)

            # Player crash
            for obstacle in obstacles:

                obstacle_rect=pygame.Rect(obstacle[0],obstacle[1],obstacle_width,obstacle_height)

                if player_rect.colliderect(obstacle_rect):
                    create_explosion(screen,player_x,player_y)
                    game_over=True
                    winner="YOU CRASHED!"

            # Boost pickup
            for boost in boosts[:]:

                boost_rect=pygame.Rect(boost[0],boost[1],boost_width,boost_height)

                if player_rect.colliderect(boost_rect):
                    boost_timer=120
                    boosts.remove(boost)

            # Finish logic
            if player_progress>=race_distance:
                game_over=True
                winner="YOU WON!"

            elif ai_progress>=race_distance and not ai_crashed:
                game_over=True
                winner="AI WON!"

    # ------------------
    # Draw Trees
    # ------------------
    for tree in trees:
        draw_tree(screen,tree[0],tree[1])

    # ------------------
    # Road Lines
    # ------------------
    for i in range(0,HEIGHT,40):
        pygame.draw.line(screen,WHITE,
            (WIDTH//2,i+int(player_progress)%40),
            (WIDTH//2,i+20+int(player_progress)%40),5)

    # ------------------
    # Draw Cars
    # ------------------
    rotated_player=pygame.transform.rotate(draw_car(BLUE),player_angle)
    screen.blit(rotated_player,rotated_player.get_rect(center=(player_x,player_y)).topleft)

    rotated_ai=pygame.transform.rotate(draw_car(RED),0)
    screen.blit(rotated_ai,rotated_ai.get_rect(center=(ai_x,ai_y)).topleft)

    # Obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen,BROWN,(obstacle[0],obstacle[1],obstacle_width,obstacle_height))

    # Boosts
    for boost in boosts:
        pygame.draw.circle(screen,YELLOW,(boost[0]+15,boost[1]+15),15)

    # UI
    distance_left=max(0,int(race_distance-player_progress))
    screen.blit(font.render(f"Distance Left: {distance_left}",True,BLACK),(20,20))
    screen.blit(font.render(f"Speed: {int(abs(player_speed)*20)} km/h",True,BLACK),(20,60))

    if boost_timer>0:
        screen.blit(font.render("BOOST!",True,YELLOW),(20,100))

    # Game Over
    if game_over:

        win_text=big_font.render(winner,True,BLACK)
        screen.blit(win_text,(WIDTH//2-150,HEIGHT//2))

        restart_text=font.render("Press SPACE to restart",True,BLACK)
        screen.blit(restart_text,(WIDTH//2-150,HEIGHT//2+80))

        if keys[pygame.K_SPACE]:
            reset_game()

    pygame.display.update()

pygame.quit()
sys.exit()