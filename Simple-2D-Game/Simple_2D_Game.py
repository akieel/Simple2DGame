
import pygame
from pygame.locals import *
import random
import sys



pygame.init()

window_width = 1000
window_height = 800
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Enhanced 2D Game")


BLACK = (0, 0, 0)
clock = pygame.time.Clock()

# Game states
GAME_MENU = 0
GAME_RUNNING = 1
game_state = GAME_MENU


# High score management
def save_high_score(high_score):
    try:
        with open("high_score.txt", "w") as f:
            f.write(str(high_score))
    except IOError:
        print("Unable to save the high score.")

def load_high_score():
    try:
        with open("high_score.txt", "r") as f:
            return int(f.read())
    except (IOError, ValueError):
        print("No high score found, starting at zero.")
        return 0

def save_game():
    print("Game state saved")

def main_menu():
    global game_state
    game_state = GAME_MENU
    show_menu()

def get_powerup_icon(powerup):
    color = item_types[powerup]['color']
    icon = pygame.Surface((20, 20))
    icon.fill(color)
    return icon

high_score = load_high_score()

# Item types with updated effects and properties
item_types = {
    'normal': {'color': (255, 255, 255), 'shape': 'rect', 'score': 1},
    'multiplier': {'color': (0, 255, 255), 'shape': 'circle', 'effect': 'multiplier', 'duration': 5000},
    'extra_life': {'color': (255, 105, 180), 'shape': 'circle', 'effect': 'extra_life'},
    'speed_boost': {'color': (0, 191, 255), 'shape': 'triangle', 'effect': 'speed_boost', 'duration': 5000},
    'power_up': {'color': (148, 0, 211), 'shape': 'rect', 'effect': 'increase_score', 'duration': 10000, 'score': 5},
    'penalty': {'color': (255, 69, 0), 'shape': 'circle', 'effect': 'decrease_speed', 'duration': 5000, 'score': -2},
    'shrink': {'color': (75, 0, 130), 'shape': 'triangle', 'effect': 'shrink_player', 'duration': 5000},
    'invincibility': {'color': (255, 223, 0), 'shape': 'circle', 'effect': 'invincibility', 'duration': 5000},
}

# Player, Enemy, and Item classes with updated logic for handling power-ups and other effects
class Player:
    def __init__(self, speed=5):
        self.position = [window_width // 2, window_height // 2]  # Set initial position to center
        self.speed = speed
        self.boosted_speed = 8
        self.rect = pygame.Rect(self.position[0], self.position[1], 20, 20)
        self.speed_boost_active = False
        self.speed_boost_end_time = 0
        self.multiplier = 1
        self.lives = 3
        self.invulnerable = False
        self.invulnerability_end_time = 0
        self.active_powerups = {}

    def move(self, keys):
        if self.invulnerable and pygame.time.get_ticks() > self.invulnerability_end_time:
            self.invulnerable = False

        current_speed = self.boosted_speed if self.speed_boost_active else self.speed
        diagonal_speed = current_speed / 1.414

        if keys[K_LEFT] and keys[K_UP]:
            self.position[0] -= diagonal_speed
            self.position[1] -= diagonal_speed
        elif keys[K_LEFT] and keys[K_DOWN]:
            self.position[0] -= diagonal_speed
            self.position[1] += diagonal_speed
        elif keys[K_RIGHT] and keys[K_UP]:
            self.position[0] += diagonal_speed
            self.position[1] -= diagonal_speed
        elif keys[K_RIGHT] and keys[K_DOWN]:
            self.position[0] += diagonal_speed
            self.position[1] += diagonal_speed
        else:
            if keys[K_LEFT]:
                self.position[0] -= current_speed
            if keys[K_RIGHT]:
                self.position[0] += current_speed
            if keys[K_UP]:
                self.position[1] -= current_speed
            if keys[K_DOWN]:
                self.position[1] += current_speed

        self.position[0] = max(0, min(self.position[0], window_width - 20))
        self.position[1] = max(0, min(self.position[1], window_height - 20))

        self.rect.update(self.position[0], self.position[1], 20, 20)

    def check_boost(self):
        if self.speed_boost_active and pygame.time.get_ticks() > self.speed_boost_end_time:
            self.speed_boost_active = False
            self.speed = 5

    def add_powerup(self, powerup, duration):
        self.active_powerups[powerup] = duration

    def update_powerups(self):
        for powerup in list(self.active_powerups):
            self.active_powerups[powerup] -= 1
            if self.active_powerups[powerup] <= 0:
                del self.active_powerups[powerup]

def draw_powerups(window, active_powerups):
    start_x = 10  # Starting X position for the first power-up icon
    y = 10  # Y position is constant since they will be in a row
    for powerup, duration in active_powerups.items():
        # Assuming you have a function to get the icon based on powerup name
        icon = get_powerup_icon(powerup)
        window.blit(icon, (start_x, y))
        # Display the duration next to the icon
        font = pygame.font.Font(None, 24)
        duration_surf = font.render(str(duration // 1000), True, (255, 255, 255))  # Convert ms to seconds
        window.blit(duration_surf, (start_x + icon.get_width() + 5, y))
        start_x += icon.get_width() + 60  # Move to the next position for the next power-up

def game_loop():
    player = Player()
    paused = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_game()
        if paused:
            display_pause_menu()
        else:
            player.update_powerups()
            draw_powerups(window, player)

def display_pause_menu():
    resume_button = Button("Resume", 350, 300, 300, 50)
    save_button = Button("Save Game", 350, 400, 300, 50)
    main_menu_button = Button("Main Menu", 350, 500, 300, 50)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.rect.collidepoint(pygame.mouse.get_pos()):
                    return
                elif save_button.rect.collidepoint(pygame.mouse.get_pos()):
                    save_game()
                elif main_menu_button.rect.collidepoint(pygame.mouse.get_pos()):
                    main_menu()


class Enemy:
    def __init__(self):
        self.position = [random.randint(0, window_width), random.randint(0, window_height)]
        self.speed = [random.randint(-3, 3), random.randint(-3, 3)]
        self.rect = pygame.Rect(self.position[0], self.position[1], 20, 20)

    def move(self):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]

        if self.position[0] < 0 or self.position[0] > window_width - 20:
            self.speed[0] *= -1
        if self.position[1] < 0 or self.position[1] > window_height - 20:
            self.speed[1] *= -1

        self.rect.update(self.position[0], self.position[1], 20, 20)


class Item:
    def __init__(self):
        self.type = random.choice(list(item_types.keys()))
        self.position = [random.randint(0, window_width), random.randint(0, window_height)]
        self.rect = pygame.Rect(self.position[0], self.position[1], 20, 20)
        self.properties = item_types[self.type]

# Game initialization and main loop logic, including menu display, game state management, and event handling
def reset_game():
    global player, items, enemies, score, level
    player = Player()  # No longer need to pass x and y
    items = [Item() for _ in range(2)]
    enemies = [Enemy()]
    score = 0
    level = 1

def spawn_new_item():
    items.append(Item())

def level_up():
    global level, score
    new_level = score // 10 + 1
    if new_level > level:
        level = new_level
        enemies.append(Enemy())
        

class NotificationManager:
    def __init__(self):
        self.notifications = []  # Holds tuples of (message, expiration_time)
        self.font = pygame.font.Font(None, 48)  # Adjust size as needed for visibility

    def add_notification(self, message, duration=2000):  # Duration in milliseconds
        expiration_time = pygame.time.get_ticks() + duration
        self.notifications.append((message, expiration_time))

    def draw_notifications(self, window):
        for message, expiration_time in self.notifications[:]:  # Iterate through a copy for safe removal
            if pygame.time.get_ticks() > expiration_time:
                self.notifications.remove((message, expiration_time))
                continue  # Skip drawing this notification

            # Render the message
            text_surface = self.font.render(message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(window_width / 2, window_height / 2))

            # Ensure text_rect is defined before this point
            # Create a semi-transparent surface for the background
            background_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10))
            background_surface.set_alpha(128)  # Adjust alpha for desired transparency
            background_surface.fill((0, 0, 0))  # Black background

            # Make sure the blit order places the background behind the text
            window.blit(background_surface, (text_rect.x - 10, text_rect.y - 5))  # Adjust positioning as needed
            window.blit(text_surface, text_rect)

notification_manager = NotificationManager()

            



class Button:
    def __init__(self, text, x, y, width, height, color=(100, 100, 100), text_color=(255, 255, 255), font_size=36):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, window):
        # Draw the button rectangle
        pygame.draw.rect(window, self.color, self.rect)
        # Draw the button text
        font = pygame.font.Font(None, self.font_size)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        window.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def pause_game():
    paused = True
    resume_button = Button("Resume", 350, 300, 300, 50)
    save_button = Button("Save Game", 350, 400, 300, 50)
    main_menu_button = Button("Main Menu", 350, 500, 300, 50)

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.is_clicked(event):
                    paused = False
                elif save_button.is_clicked(event):
                    print("Game saved!")  # Placeholder for actual save logic
                elif main_menu_button.is_clicked(event):
                    main_menu()  # Ensure this function correctly transitions to the main menu
                    return  # Exit the pause menu

        window.fill((0, 0, 0, 128))  # Optional: create a translucent overlay
        resume_button.draw(window)
        save_button.draw(window)
        main_menu_button.draw(window)

        pygame.display.flip()
        clock.tick(60)

def show_menu():
    global game_state, high_score

    # Define buttons
    start_button = Button("Start Game", window_width // 2 - 100, 250, 200, 50, color=(0, 255, 0),
                          text_color=(255, 255, 255))
    exit_button = Button("Exit", window_width // 2 - 100, 350, 200, 50, color=(255, 0, 0), text_color=(255, 255, 255))

    menu_font = pygame.font.Font(None, 74)
    while True:
        window.fill(BLACK)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if start_button.is_clicked(event):
                reset_game()
                game_state = GAME_RUNNING
                return  # Start the game
            if exit_button.is_clicked(event):
                pygame.quit()
                sys.exit()

        # Draw menu text and buttons
        menu_text = menu_font.render("Main Menu", True, (255, 255, 255))
        window.blit(menu_text, (window_width / 2 - menu_text.get_width() / 2, 150))
        start_button.draw(window)
        exit_button.draw(window)
        high_score_text = menu_font.render(f"High Score: {high_score}", True, (255, 255, 255))
        window.blit(high_score_text, (window_width / 2 - high_score_text.get_width() / 2, 450))

        pygame.display.flip()
        clock.tick(60)

reset_game()

# Main game loop
reset_game()
while True:
    if game_state == GAME_MENU:
        show_menu()
    elif game_state == GAME_RUNNING:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    game_state = GAME_MENU
            if event.type == USEREVENT + 2:  # Reset multiplier after duration
                player.multiplier = 1
                pygame.time.set_timer(USEREVENT + 2, 0)  # Stop the timer

        
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.check_boost()

        for enemy in enemies:
            enemy.move()

        for item in items[:]:  # Iterate over a copy of the list to allow modification
            if player.rect.colliderect(item.rect):
                if item.type == 'speed_boost':
                    player.speed_boost_active = True
                    player.speed_boost_end_time = pygame.time.get_ticks() + item.properties['duration']
                    player.speed = player.boosted_speed
                    notification_manager.add_notification("Speed Boost")
                elif item.type == 'multiplier':
                    player.multiplier += 1  # Increase the score multiplier
                    pygame.time.set_timer(USEREVENT + 2, item.properties['duration'])  # Reset multiplier after duration
                elif item.type == 'extra_life':
                    if player.lives < 3:
                        player.lives += 1  # Increase the player's lives
                        notification_manager.add_notification("+1 Life")
                elif item.type == 'power_up':
                    score += item.properties['score'] * player.multiplier  # Apply multiplier effect to power-up score
                elif item.type == 'penalty':
                    player.speed = max(2, player.speed - 1.6)
                    pygame.time.set_timer(USEREVENT + 1, item.properties['duration'])
                    notification_manager.add_notification("Penalty Speed")
                else:  # Handle normal item score increment with multiplier
                    score += item.properties.get('score', 0) * player.multiplier

                items.remove(item)  # Remove the collected item
                spawn_new_item()  # Spawn a new item to replace it

        if score > high_score:
            high_score = score
            save_high_score(high_score)

        level_up()  # Check if it's time to level up and spawn more enemies

        window.fill(BLACK)
        if player.invulnerable:  # Change player color to indicate invulnerability
            pygame.draw.rect(window, (255, 255, 0), player.rect)
        else:
            pygame.draw.rect(window, (0, 0, 255), player.rect)  # Player

        for item in items:
            if item.properties['shape'] == 'rect':
                pygame.draw.rect(window, item.properties['color'], item.rect)  # Items
            elif item.properties['shape'] == 'circle':
                pygame.draw.circle(window, item.properties['color'], item.rect.center, 10)  # Items
            elif item.properties['shape'] == 'triangle':
                pygame.draw.polygon(window, item.properties['color'], [(item.rect.centerx, item.rect.top),
                                                                       (item.rect.left, item.rect.bottom),
                                                                       (item.rect.right, item.rect.bottom)])  # Items

        for enemy in enemies:
            pygame.draw.rect(window, (255, 0, 0), enemy.rect)  # Enemies

        # Handle collision with enemies, considering invulnerability
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect) and not player.invulnerable:
                player.lives -= 1
                if player.lives <= 0:
                    game_state = GAME_MENU  # Game over, return to menu
                    break  # Exit the loop to avoid additional processing
                else:
                    player.invulnerable = True
                    player.invulnerability_end_time = pygame.time.get_ticks() + 3000  # 3 seconds of invincibility
                    
        notification_manager.draw_notifications(window)
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        level_text = font.render(f"Level: {level}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
        window.blit(score_text, (10, 10))
        window.blit(level_text, (10, 50))
        window.blit(lives_text, (10, 90))

        pygame.display.flip()
        clock.tick(60)
