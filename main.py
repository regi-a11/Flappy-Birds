import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
screen_width = 288
screen_height = 512
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Load custom font images for score display
digit_images = [pygame.image.load(f"{i}.png").convert_alpha() for i in range(10)]

# Load game assets
background_day = pygame.image.load("background-day.png").convert()
background_night = pygame.image.load("background-night.png").convert()
bird_images = [
    pygame.image.load("yellowbird-upflap.png").convert_alpha(),
    pygame.image.load("yellowbird-midflap.png").convert_alpha(),
    pygame.image.load("yellowbird-downflap.png").convert_alpha(),
]
pipe_image = pygame.image.load("pipe-green.png").convert_alpha()
base_image = pygame.image.load("base.png").convert_alpha()
gameover_image = pygame.image.load("gameover.png").convert_alpha()
message_image = pygame.image.load("message.png").convert_alpha()
ok_button_image = pygame.image.load("ok_button.png").convert_alpha()  # Make sure you have this image

# Load audio files
flap_sound = pygame.mixer.Sound("wing.ogg")
hit_sound = pygame.mixer.Sound("hit.ogg")
point_sound = pygame.mixer.Sound("point.ogg")
die_sound = pygame.mixer.Sound("die.ogg")
swoosh_sound = pygame.mixer.Sound("swoosh.ogg")

# Game variables
gravity = 0.2
bird_movement = 0
game_active = True
score = 0
high_score = 0
pipe_passed = []
hit_flash = False  # Variable to control the hit flash effect
hit_flash_duration = 8  # Frames for the flash effect
hit_flash_counter = 0

# Create bird rectangle
bird_rect = bird_images[0].get_rect(center=(50, 256))

# Create pipes
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)
pipe_height = [200, 300, 400]

# Create base
base_x_pos = 0

# Create OK button
ok_button_image = pygame.transform.scale(ok_button_image, (100, 35))
ok_button_rect = ok_button_image.get_rect(center=(screen_width // 2, screen_height // 2 + 50))


def rotate_bird(bird_images):
    new_bird = pygame.transform.rotozoom(bird_images[0], -bird_movement * 3, 1)
    return new_bird


def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_image.get_rect(midtop=(screen_width + 50, random_pipe_pos))
    top_pipe = pipe_image.get_rect(midbottom=(screen_width + 50, random_pipe_pos - 150))
    return bottom_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 2
    return [pipe for pipe in pipes if pipe.right > -50]


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= screen_height:
            screen.blit(pipe_image, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_image, False, True)
            screen.blit(flip_pipe, pipe)


def check_collision(pipes):
    global hit_flash, hit_flash_counter
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            hit_flash = True
            hit_flash_counter = 0
            return False

    if bird_rect.top <= -50 or bird_rect.bottom >= 450:
        die_sound.play()
        hit_flash = True
        hit_flash_counter = 0
        return False

    return True


def draw_base():
    screen.blit(base_image, (base_x_pos, screen_height - 100))
    screen.blit(base_image, (base_x_pos + 288, screen_height - 100))


def score_display(score, y_pos):
    score_str = str(int(score))
    total_width = sum(digit_images[int(digit)].get_width() for digit in score_str)
    offset_x = (screen_width - total_width) // 2

    for digit in score_str:
        digit_image = digit_images[int(digit)]
        screen.blit(digit_image, (offset_x, y_pos))
        offset_x += digit_image.get_width()


def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score


def show_game_over_screen():
    screen.blit(gameover_image, (50, 200))
    score_display(score, 150)
    score_display(high_score, 250)
    screen.blit(ok_button_image, ok_button_rect)


def reset_game():
    global bird_rect, bird_movement, pipe_list, score, pipe_passed, game_active
    bird_rect.center = (50, 256)
    bird_movement = 0
    pipe_list.clear()
    score = 0
    pipe_passed = []
    game_active = True


def draw_hit_flash():
    if hit_flash:
        flash_surface = pygame.Surface((screen_width, screen_height))
        flash_surface.set_alpha(128)  # Set transparency level
        flash_surface.fill((255, 255, 255))  # White color
        screen.blit(flash_surface, (0, 0))


# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 6
                flap_sound.play()
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                reset_game()
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())
        if event.type == pygame.MOUSEBUTTONDOWN and not game_active:
            if ok_button_rect.collidepoint(event.pos):
                reset_game()

    screen.blit(background_day, (0, 0))

    if game_active:
        # Bird movement
        bird_movement += gravity
        bird_rect.centery += bird_movement
        screen.blit(rotate_bird(bird_images), bird_rect)
        game_active = check_collision(pipe_list)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Check for pipe pass and update score
        for pipe in pipe_list:
            if pipe.centerx < bird_rect.centerx and pipe not in pipe_passed:
                pipe_passed.append(pipe)
                score += 1
                point_sound.play()

        score_display(score, 50)
    else:
        show_game_over_screen()
        high_score = update_score(score, high_score)

    # Base
    base_x_pos -= 1
    draw_base()
    if base_x_pos <= -288:
        base_x_pos = 0

    # Draw hit flash if active
    if hit_flash:
        draw_hit_flash()
        hit_flash_counter += 1
        if hit_flash_counter >= hit_flash_duration:
            hit_flash = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
