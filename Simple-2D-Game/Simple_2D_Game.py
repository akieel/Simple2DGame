import pygame
from pygame.locals import *
import random
import sys
import json

pygame.init()

window_width = 1000
window_height = 800
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Enhanced 2D Game with Leveling and Scoring")

BLACK = (0, 0, 0)
clock = pygame.time.Clock()

# Game states
GAME_MENU = 0
GAME_RUNNING = 1
GAME_PAUSED = 2
GAME_OVER = 3

game_state = GAME_MENU
paused = False
player, items, enemies, boss, score, level, combo_timer, combo_multiplier = None, [], [], None, 0, 1, 0, 1

# Combo system
COMBO_DURATION = 3000  # Time in milliseconds for combo to reset

def save_high_score(high_score):
    try:
        with open("high_score.txt", "w") as f:
            f.write(str(high_score))
    except Exception as e:
        print(f"Unable to save the high score: {e}")

def load_high_score():
    try:
        with open("high_score.txt", "r") as f:
            return int(f.read())
    except Exception as e:
        print(f"No high score found, starting at zero: {e}")
        return 0

def main_menu():
    global game_state
    game_state = GAME_MENU

high_score = load_high_score()

item_types = {
    'normal': {'color': (255, 255, 255), 'shape': 'rect', 'score': 100},
    'multiplier': {'color': (0, 255, 255), 'shape': 'circle', 'effect': 'multiplier', 'duration': 5000, 'score': 200},
    'extra_life': {'color': (255, 105, 180), 'shape': 'circle', 'effect': 'extra_life', 'score': 300},
    'speed_boost': {'color': (0, 191, 255), 'shape': 'triangle', 'effect': 'speed_boost', 'duration': 5000, 'score': 150},
    'invincibility': {'color': (255, 223, 0), 'shape': 'circle', 'effect': 'invincibility', 'duration': 5000, 'score': 250},
}

class Player(pygame.sprite.Sprite):
    def __init__(self, speed=5):
        super().__init__()
        self.position = [window_width // 2, window_height // 2]
        self.speed = speed
        self.rect = pygame.Rect(self.position[0], self.position[1], 20, 20)
        self.lives = 3
        self.score = 0
        self.level = 1

    def move(self, keys):
        if keys[K_LEFT]:
            self.position[0] -= self.speed
        if keys[K_RIGHT]:
            self.position[0] += self.speed
        if keys[K_UP]:
            self.position[1] -= self.speed
        if keys[K_DOWN]:
            self.position[1] += self.speed

        self.position[0] = max(0, min(self.position[0], window_width - 20))
        self.position[1] = max(0, min(self.position[1], window_height - 20))

        self.rect.update(self.position[0], self.position[1], 20, 20)

    def update_score(self, points):
        global combo_timer, combo_multiplier
        now = pygame.time.get_ticks()
        if now - combo_timer < COMBO_DURATION:
            combo_multiplier += 0.5
        else:
            combo_multiplier = 1
        combo_timer = now
        self.score += points * combo_multiplier

def reset_game():
    global player, items, enemies, score, level, combo_timer, combo_multiplier
    player = Player()
    items = [Item() for _ in range(5)]
    enemies = [Enemy() for _ in range(3)]
    score = 0
    level = 1
    combo_timer = pygame.time.get_ticks()
    combo_multiplier = 1

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.position = [random.randint(0, window_width), random.randint(0, window_height)]
        self.speed = [random.randint(-2, 2), random.randint(-2, 2)]
        self.rect = pygame.Rect(self.position[0], self.position[1], 20, 20)

    def move(self):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]

        if self.position[0] < 0 or self.position[0] > window_width - 20:
            self.speed[0] *= -1
        if self.position[1] < 0 or self.position[1] > window_height - 20:
            self.speed[1] *= -1

        self.rect.update(self.position[0], self.position[1], 20, 20)

class Item(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(list(item_types.keys()))
        self.position = [random.randint(0, window_width), random.randint(0, window_height)]
        self.rect = pygame.Rect(self.position[0], self.position[1], 20, 20)
        self.properties = item_types[self.type]

def game_loop():
    global game_state, player, score, level
    while game_state == GAME_RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.move(keys)

        window.fill(BLACK)

        for item in items:
            pygame.draw.rect(window, item.properties['color'], item.rect)
            if player.rect.colliderect(item.rect):
                player.update_score(item.properties['score'])
                items.remove(item)
                items.append(Item())

        for enemy in enemies:
            enemy.move()
            pygame.draw.rect(window, (255, 0, 0), enemy.rect)
            if player.rect.colliderect(enemy.rect):
                game_state = GAME_OVER

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
        level_text = font.render(f"Level: {level}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
        window.blit(score_text, (10, 10))
        window.blit(level_text, (10, 50))
        window.blit(lives_text, (10, 90))

        pygame.display.flip()
        clock.tick(60)

reset_game()
game_loop()
