import pygame
import random
import time
import os
from settings import *
from utils import load_stats, save_stats

# -------------------- Game Setup --------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WordRush - Typing Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

# Load sound effects
correct_sound = pygame.mixer.Sound("assets/correct.mp3")
wrong_sound = pygame.mixer.Sound("assets/wrong.mp3")

# Load background music and play on loop
pygame.mixer.music.load("assets/background.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Load words from file
with open("data/words.txt", "r") as file:
    word_list = [line.strip() for line in file.readlines()]

# Load saved statistics
stats = load_stats()

# -------------------- Game State Variables --------------------
game_state = "start"
falling_words = []
input_text = ""
score = 0
mistakes = 0
max_mistakes = 3
start_time = time.time()
game_duration = 60  # seconds
stats_saved = False
level = None

word_spawn_timer = 0
word_spawn_interval = 2
base_speed = 1.5
speed_increase_step = 0.2
speed_increase_every = 2  # Increase speed after every 2 correct words

# -------------------- Utility Functions --------------------
def new_word():
    """Generate a new falling word with randomized position and speed."""
    word = random.choice(word_list)
    word_surface = font.render(word, True, WORD_COLOR)
    word_width = word_surface.get_width()
    x = random.randint(20, WIDTH - word_width - 20)
    x = max(0, min(x, WIDTH - word_width))
    y = 0
    speed = random.uniform(base_speed, base_speed + 1.5)
    return {"word": word, "x": x, "y": y, "speed": speed}

def draw_text(text, size, color, x, y, center=True):
    """Render and display text on the screen."""
    font_obj = pygame.font.SysFont(FONT_NAME, size)
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

# -------------------- Main Game Loop --------------------
running = True
while running:
    screen.fill(BACKGROUND_COLOR)
    elapsed_time = time.time() - start_time
    remaining_time = max(0, game_duration - elapsed_time)
    dt = clock.get_time() / 1000  # Delta time for consistent timing

    # -------------------- Event Handling --------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Quit on ESC
            if event.key == pygame.K_ESCAPE:
                running = False

            # Toggle music on/off with M
            if event.key == pygame.K_m:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()

            # Start game from start screen
            if game_state == "start":
                if event.key == pygame.K_RETURN:
                    game_state = "level_select"

            # Level selection logic
            elif game_state == "level_select":
                if event.key == pygame.K_1:
                    level = "Easy"
                    base_speed = 1.5
                    word_spawn_interval = 2
                    game_state = "playing"
                    start_time = time.time()
                elif event.key == pygame.K_2:
                    level = "Medium"
                    base_speed = 2.5
                    word_spawn_interval = 1.5
                    game_state = "playing"
                    start_time = time.time()
                elif event.key == pygame.K_3:
                    level = "Hard"
                    base_speed = 3.5
                    word_spawn_interval = 1
                    game_state = "playing"
                    start_time = time.time()

            # Typing input handling during gameplay
            elif game_state == "playing":
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if falling_words and input_text.strip() == falling_words[0]["word"]:
                        score += 1
                        falling_words.pop(0)
                        if score % speed_increase_every == 0:
                            base_speed += speed_increase_step
                        correct_sound.play()
                    else:
                        mistakes += 1
                        if mistakes >= max_mistakes:
                            game_state = "game_over"
                        wrong_sound.play()
                    input_text = ""
                else:
                    input_text += event.unicode

            # Restart or exit on game over screen
            elif game_state == "game_over":
                if event.key == pygame.K_r:
                    # Reset game state
                    falling_words.clear()
                    input_text = ""
                    score = 0
                    mistakes = 0
                    start_time = time.time()
                    word_spawn_timer = 0
                    base_speed = 1.5
                    stats_saved = False
                    level = None
                    game_state = "level_select"
                elif event.key == pygame.K_ESCAPE:
                    running = False

    # -------------------- Game State Rendering --------------------
    if game_state == "start":
        draw_text("WordRush", 64, (25, 25, 112), WIDTH // 2, HEIGHT // 2 - 100)
        if int(time.time() * 2) % 2 == 0:
            draw_text("Press ENTER to Start", 30, (100, 100, 100), WIDTH // 2, HEIGHT // 2 + 20)
        draw_text("Press ESC to Quit", 20, (150, 150, 150), WIDTH // 2, HEIGHT // 2 + 80)

    elif game_state == "level_select":
        draw_text("Select Level", 50, (25, 25, 112), WIDTH // 2, HEIGHT // 2 - 120)
        draw_text("1. Easy 🐢", 36, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 40)
        draw_text("2. Medium 🚗", 36, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 20)
        draw_text("3. Hard 🚀", 36, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 80)
        draw_text("Press ESC to Cancel", 20, (150, 150, 150), WIDTH // 2, HEIGHT - 50)

    elif game_state == "playing":
        # Spawn new words at intervals
        word_spawn_timer += dt
        if word_spawn_timer >= word_spawn_interval:
            falling_words.append(new_word())
            word_spawn_timer = 0

        # Move and render falling words
        for word in falling_words[:]:
            word["y"] += word["speed"]
            if word["y"] > HEIGHT:
                falling_words.remove(word)
                mistakes += 1
                if mistakes >= max_mistakes:
                    game_state = "game_over"
            else:
                draw_text(word["word"], FONT_SIZE, WORD_COLOR, word["x"], word["y"])

        # Render input box
        pygame.draw.rect(screen, (220, 220, 220), (WIDTH // 2 - 150, HEIGHT - 80, 300, 50), border_radius=10)
        draw_text(input_text, FONT_SIZE - 4, INPUT_COLOR, WIDTH // 2, HEIGHT - 55)

        # Display game stats
        draw_text(f"⌨️ Score: {score}", 28, (34, 139, 34), 20, 20, center=False)
        draw_text(f"❌ Mistakes: {mistakes}/{max_mistakes}", 28, (178, 34, 34), 20, 60, center=False)
        draw_text(f"⏳ Time: {int(remaining_time)}s", 28, TEXT_COLOR, WIDTH - 180, 20, center=False)
        draw_text(f"Level: {level}", 28, TEXT_COLOR, WIDTH - 180, 60, center=False)

        # Display saved best stats
        pygame.draw.line(screen, (200, 200, 200), (0, 100), (WIDTH, 100), 2)
        draw_text(f"🏆 High Score: {stats.get('high_score', 0)}", 22, (0, 0, 0), 20, 110, center=False)
        draw_text(f"🎯 Best Accuracy: {stats.get('high_accuracy', 0)}%", 22, (0, 0, 0), 20, 140, center=False)
        draw_text(f"🚀 Best WPM: {stats.get('high_wpm', 0)}", 22, (0, 0, 0), 20, 170, center=False)

        # Transition to game over if time runs out
        if remaining_time <= 0:
            game_state = "game_over"

    elif game_state == "game_over":
        if not stats_saved:
            total_typed = score + mistakes
            accuracy = (score / total_typed) * 100 if total_typed > 0 else 0
            wpm = (score / (game_duration / 60))
            stats["high_wpm"] = max(stats["high_wpm"], int(wpm))
            stats["high_accuracy"] = max(stats["high_accuracy"], int(accuracy))
            stats["high_score"] = max(stats.get("high_score", 0), score)
            stats["total_words"] += total_typed
            save_stats(stats)
            stats_saved = True

        draw_text("🔥 GAME OVER 🔥", 60, (178, 34, 34), WIDTH // 2, HEIGHT // 2 - 120)
        pygame.draw.line(screen, (200, 200, 200), (WIDTH // 2 - 150, HEIGHT // 2 - 80), (WIDTH // 2 + 150, HEIGHT // 2 - 80), 2)
        draw_text(f"⌨️ Your Score: {score}", 36, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 30)
        draw_text(f"❌ Mistakes: {mistakes}/{max_mistakes}", 30, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 10)
        draw_text(f"🚀 WPM: {int(wpm)} | 🎯 Accuracy: {int(accuracy)}%", 30, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 50)
        draw_text("Press R to Restart or ESC to Exit", 24, (100, 100, 100), WIDTH // 2, HEIGHT // 2 + 120)

    # Refresh display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up and exit
pygame.quit()
