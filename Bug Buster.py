"""
Copyright (c) 2024 Aaron James R. Mission

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 600
PLAYER_SIZE = 50
ENEMY_SIZE = 30
BULLET_SIZE = 5
FPS = 60
score = 0
hidden_score = 0
highscore_file = "player.data"
encryption_key = 0xAB
mutable_sounds = True

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Sounds
enemy_killed_sound = pygame.mixer.Sound(os.path.join("sfx", "splat.mp3"))
player_fire_sound = pygame.mixer.Sound(os.path.join("sfx", "fire.mp3"))
player_hurt_sound = pygame.mixer.Sound(os.path.join("sfx", "ouch.mp3"))

# Floor
floor_texture = pygame.image.load(os.path.join("img", "floor.png"))

# Player
player = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT - PLAYER_SIZE - 10, PLAYER_SIZE, PLAYER_SIZE)
player_speed = 5
player_lives = 3

# Bullets
bullets = []

# Load player texture
player_texture = pygame.image.load(os.path.join("img", "player.png"))

# Load enemy textures
enemy_textures = [
    pygame.image.load(os.path.join("img", "enemy_1.png")),
    pygame.image.load(os.path.join("img", "enemy_2.png")),
    pygame.image.load(os.path.join("img", "enemy_3.png"))
]

# Enemies
enemy_spawn_timer = 0
min_spawn_amount = 1
max_spawn_amount = 3

def create_enemy(amount):
    enemy_list = []
    for _ in range(amount):
        random_texture = random.choice(enemy_textures)
        enemy_list.append({
            'rect': pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), 0, ENEMY_SIZE, ENEMY_SIZE),
            'texture': random_texture
        })
    return enemy_list

enemies = []
enemy_speed = 2

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug Buster")
clock = pygame.time.Clock()

icon = pygame.image.load(os.path.join("img", "enemy_1.png"))
pygame.display.set_icon(icon)


title_font = os.path.join("font", "Robus-BWqOd.otf")
main_font = os.path.join("font", "SpaceMission-rgyw9.otf")
font = pygame.font.Font(main_font, 36)
font2 = pygame.font.Font(main_font, 26)
font3 = pygame.font.Font(None, 16)

def encrypt(data):
    return bytes([byte ^ encryption_key for byte in data])

def decrypt(data):
    return bytes([byte ^ encryption_key for byte in data])

def load_highscore():
    if os.path.exists(highscore_file):
        with open(highscore_file, 'rb') as file:
            encrypted_data = file.read()
            decrypted_data = decrypt(encrypted_data)
            return int(decrypted_data.decode())
    else:
        return 0

def save_highscore(new_highscore):
    encrypted_data = encrypt(str(new_highscore).encode())
    with open(highscore_file, 'wb') as file:
        file.write(encrypted_data)

def draw_window():
    screen.blit(floor_texture, (0, 0))
    # Render player with texture
    screen.blit(player_texture, player.topleft)

    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, bullet)

    for enemy in enemies:
        # Render enemy with texture
        screen.blit(enemy['texture'], enemy['rect'].topleft)

    # Display lives
    lives_text = font3.render(f"Lives: {player_lives}", True, WHITE)
    screen.blit(lives_text, (10, HEIGHT - lives_text.get_height() - 10))
    
    # Display score
    score_text = font.render(f"Score: {score}", True, RED)
    score_x = (WIDTH - score_text.get_width()) // 2
    screen.blit(score_text, (score_x, 10))

    # Display highscore 
    highscore_text = font2.render(f"Highscore: {load_highscore()}", True, RED)
    highscore_x = (WIDTH - highscore_text.get_width()) // 2
    screen.blit(highscore_text, (highscore_x, 40))
    
    pygame.display.update()

def move_player(keys):
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.x - player_speed > 0:
        player.x -= player_speed
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + player_speed < WIDTH - PLAYER_SIZE:
        player.x += player_speed

def move_bullets():
    bullets_to_remove = []

    for bullet in bullets:
        bullet.y -= 5
        if bullet.y < 0:
            bullets_to_remove.append(bullet)

    for bullet in bullets_to_remove:
        bullets.remove(bullet)

def move_enemies(enemy_spawn_interval):
    global enemy_spawn_timer

    enemy_spawn_timer += 1

    if enemy_spawn_timer >= enemy_spawn_interval:
        enemies.extend(create_enemy(random.randint(min_spawn_amount, max_spawn_amount)))
        enemy_spawn_timer = 0
        enemy_spawn_interval = random.randint(50, 200)

    for enemy in list(enemies): 
        enemy['rect'].y += enemy_speed
        if enemy['rect'].y > HEIGHT:
            enemies.remove(enemy)

def check_collisions():
    global player_lives, score, hidden_score
    try:
        for bullet in bullets:
            for enemy in list(enemies):
                if bullet.colliderect(enemy['rect']):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    play_sound(enemy_killed_sound)
                    # Update score based on the type of enemy killed
                    if enemy['texture'] == enemy_textures[0]:
                        score += 1
                        hidden_score += 1
                    elif enemy['texture'] == enemy_textures[1]:
                        score += 5
                        hidden_score += 5
                    elif enemy['texture'] == enemy_textures[2]:
                        score += 10
                        hidden_score += 5

        for enemy in list(enemies):
            if player.colliderect(enemy['rect']):
                player_lives -= 1
                enemies.remove(enemy)
                enemies.extend(create_enemy(random.randint(min_spawn_amount, max_spawn_amount)))
                play_sound(player_hurt_sound)
        if hidden_score > 0 and hidden_score >= 100:
            player_lives += 1
            hidden_score = 0
    except ValueError:
        pass  # Ignore since it is still working


def clear_all_enemies():
    enemies.clear()

def play_sound(sound):
    sound.play()

def main_menu():
    global score
    menu_font = pygame.font.Font(title_font, 50)
    small_font = pygame.font.Font(None, 25)

    menu_text = menu_font.render("Bug Buster", True, WHITE)
    instructions_text = small_font.render("Press AD or arrow keys to move", True, RED)
    instructions_text_2 = small_font.render("and space to shoot", True, RED)
    start_text = small_font.render("Press any key to start", True, RED)

    # Load logo image
    logo_image = pygame.image.load(os.path.join("img", "logo.png"))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if score > load_highscore():
                    save_highscore(score)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_d,
                                 pygame.K_LEFT, pygame.K_RIGHT,
                                 pygame.K_SPACE]:
                    return

        screen.blit(floor_texture, (0, 0))

        # Display logo at the top
        screen.blit(logo_image, (WIDTH // 2 - logo_image.get_width() // 2, 50))

        # Display Bug Buster text
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, 150))
        
        # Display instructions
        screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT - 85))
        screen.blit(instructions_text_2, (WIDTH // 2 - instructions_text_2.get_width() // 2, HEIGHT - 70))

        # Toggle visibility every 1000 milliseconds (1 second) for start_text
        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 50))

        pygame.display.update()
        clock.tick(FPS)

def main():
    global player_lives, score, mutable_sounds, hidden_score
    elapsed_time = 0
    enemy_spawn_interval = random.randint(50, 200)

    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join("sfx", "music.mp3"))
    pygame.mixer.music.play(-1)

    while True:
        main_menu()
        player_lives = 3

        while player_lives > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if score > load_highscore():
                        save_highscore(score)
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullets.append(pygame.Rect(player.x + PLAYER_SIZE // 2 - BULLET_SIZE // 2, player.y, BULLET_SIZE, BULLET_SIZE))
                        play_sound(player_fire_sound)

                    # Toggle mutability state on 'M' key press
                    if event.key == pygame.K_m:
                        mutable_sounds = not mutable_sounds
                        print(f'Sounds are now {"mutable" if mutable_sounds else "immutable"}')

            keys = pygame.key.get_pressed()
            move_player(keys)
            move_bullets()

            # Gradually decrease the spawning interval over time
            elapsed_time += 1
            if elapsed_time % 500 == 0:
                if enemy_spawn_interval > 20:
                    enemy_spawn_interval -= 10

            move_enemies(enemy_spawn_interval)
            check_collisions()

            # Adjust the sound volume based on mutability state
            if mutable_sounds:
                pygame.mixer.music.set_volume(0.5)  # Example volume, adjust as needed
            else:
                pygame.mixer.music.set_volume(0.0)

            draw_window()

            clock.tick(FPS)

        # Game over
        game_over_text = font.render("Game Over", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))

        # Update highscore if needed
        if score > load_highscore():
            save_highscore(score)

        pygame.display.update()
        pygame.time.delay(2000)
        clear_all_enemies()
        score = 0
        hidden_score = 0
        main_menu()

if __name__ == "__main__":
    main()
