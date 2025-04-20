import pygame
import random
import time
import psycopg2

# ---------------- DB SETUP ----------------

DB_NAME = "snake_game"
DB_USER = "postgres"
DB_PASSWORD = "hello123"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def create_table():
    with connect() as conn:
        with conn.cursor() as cur:
            # cur.execute("DROP TABLE IF EXISTS user_score;")
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_score (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    score INTEGER
                );
            ''')
            conn.commit()


def save_score(username, score):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                    INSERT INTO user_score (username, score)
                    VALUES (%s, %s)
                    ON CONFLICT (username)
                    DO UPDATE SET score = GREATEST(user_score.score, EXCLUDED.score)
                """, (username, score))
            conn.commit()

def get_max_score(username):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT score FROM user_score WHERE username = %s ORDER BY score DESC LIMIT 1", (username,))
            result = cur.fetchone()
            if result:
                return result[0]  
            return 0


create_table()


# -----------------------------------------game

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
WHITE, GREEN, RED, BLUE = (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255)
YELLOW = (255,255,0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Verdana", 20)
font_large = pygame.font.SysFont("Verdana", 40)

create_table()

# -------- USERNAME INPUT SCREEN ----------
def get_username():
    username = ''
    input_active = True
    while input_active:
        screen.fill(WHITE)
        text = font_large.render("Enter your name: " + username, True, (0,0,0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip() != '':
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 15:
                    username += event.unicode
    return username.strip()

username = get_username()
max_score = get_max_score(username)


# Game variables
score = 0
level = 1
snake = [(100, 100)]
SPEED = 10
direction = (CELL_SIZE, 0)
pause = False
new_speed = 0 

food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
        random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
food_weight = random.randint(1, 3)
food_time = time.time()

running = True
while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_score(username, score)
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p :
                pause = not pause
            if (event.key == pygame.K_UP or event.key == pygame.K_w) and direction != (0, CELL_SIZE):
                direction = (0, -CELL_SIZE)
            elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and direction != (0, -CELL_SIZE):
                direction = (0, CELL_SIZE)
            elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and direction != (CELL_SIZE, 0):
                direction = (-CELL_SIZE, 0)
            elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and direction != (-CELL_SIZE, 0):
                direction = (CELL_SIZE, 0)


    # Пауза
    if pause:
        pause_text = font_large.render("PAUSED", True, (128, 0, 128))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.display.flip()

        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_score(username, score)
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    paused = False
            clock.tick(5)  # 5 FPS в режиме паузы
        continue

    # Update snake
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    if new_head in snake or not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
        save_score(username, score)
        running = False
    else:
        snake.insert(0, new_head)

        if new_head == food:
            score += food_weight
            food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                    random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            food_weight = random.randint(1, 3)
            food_time = time.time()

            if score % 5 == 0:
                level += 1
                SPEED += 2
                new_speed = SPEED
        else:
            snake.pop()

    if time.time() - food_time > 5:
        food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
        food_weight = random.randint(1, 3)
        food_time = time.time()

    # Draw snake and food
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))
    food_color = RED if food_weight == 1 else BLUE if food_weight == 2 else YELLOW
    pygame.draw.rect(screen, food_color, (*food, CELL_SIZE, CELL_SIZE))

    # Score display
    screen.blit(font_small.render(f"User: {username}", True, (0,0,0)), (10, 10))
    screen.blit(font_small.render(f"Points: {score}", True, (0,0,0)), (10, 30))
    screen.blit(font_small.render(f"Level: {level}", True, (0,0,0)), (10, 50))
    screen.blit(font_small.render(f"Your max: {max_score}", True, (0,0,0)), (10, 70))

    # if pause:
    #     SPEED = 0
    # else: 
    #     SPEED = new_speed

    pygame.display.flip()
    clock.tick(SPEED)

pygame.quit()
