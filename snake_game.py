import pygame
import random
import json
import os
import math

# ===== DISPLAY CONSTANTS =====
GRID_SIZE = 30
CELL_SIZE = 20
GRID_WIDTH = GRID_SIZE * CELL_SIZE  # 600
PANEL_WIDTH = 200
WIDTH = GRID_WIDTH + PANEL_WIDTH  # 800 (600 grid + 200 panel)
HEIGHT = GRID_SIZE * CELL_SIZE  # 600
FPS = 30

# ===== GAME TIMING CONSTANTS =====
MOVE_DELAY = 100  # milliseconds between moves (10 moves/second)
COUNTDOWN_DURATION = 3500  # 3 seconds (3, 2, 1) + 0.5 seconds (GO!) = 3.5 seconds total
GO_DURATION = 500  # "GO!" shows for 0.5 seconds
DEATH_ANIMATION_DURATION = 2500  # 2.5 seconds
SHIELD_BREAK_DURATION = 300  # milliseconds
SCORE_FLASH_DURATION = 300  # milliseconds
SCREEN_FLASH_DURATION = 150  # milliseconds
SHIELD_TEXT_DURATION = 1000  # milliseconds

# ===== ANIMATION CONSTANTS =====
DEATH_ZOOM_START = 500  # ms before zoom starts
DEATH_ZOOM_DURATION = 1500  # ms for zoom animation
DEATH_ZOOM_MAX = 3.0  # maximum zoom scale
DEATH_FADE_START = 2000  # ms before fade starts
SHIELD_BREAK_PARTICLE_COUNT = 16
COLLISION_PARTICLE_COUNT = 40
COLLISION_SLOW_PARTICLES = 20
FOOD_BURST_PARTICLES = 20
FOOD_FAST_PARTICLES = 8
SCREEN_SHAKE_DECAY = 8
SCREEN_SHAKE_DURATION = 300

# ===== SNAKE CONSTANTS =====
SNAKE_START_X = 15
SNAKE_START_Y = 15
SNAKE_START_LENGTH = 3
OBSTACLE_START_AREA_MIN_X = 16
OBSTACLE_START_AREA_MAX_X = 20
OBSTACLE_START_AREA_MIN_Y = 13
OBSTACLE_START_AREA_MAX_Y = 17

# ===== POWERUP CONSTANTS =====
POWERUP_SELECTION_INTERVAL = 3  # every N apples
POWERUP_SELECTION_COUNT = 3  # 3 choices per selection

# ===== COLORS (R, G, B) =====
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 20)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 255)
OBSTACLE_LIGHT = (100, 100, 100)
OBSTACLE_MID = (70, 70, 70)
OBSTACLE_DARK = (40, 40, 40)
GRID_LINE_COLOR = (30, 30, 30)

# ===== BUTTON COLORS =====
BUTTON_NORMAL = (0, 100, 0)  # Dark Green
BUTTON_HOVER = (0, 150, 0)   # Brighter Green
BUTTON_TEXT = (255, 255, 255)
TITLE_COLOR = (0, 255, 0)

# ===== DIRECTIONS =====
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# ===== DIRECTION UTILITIES =====
OPPOSITE_DIRECTIONS = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


class Snake:
    def __init__(self):
        # Start at center with 3 segments moving right
        self.body = [(SNAKE_START_X, SNAKE_START_Y), (SNAKE_START_X - 1, SNAKE_START_Y), (SNAKE_START_X - 2, SNAKE_START_Y)]
        self.direction = RIGHT
        self.grow_pending = False
        self.interpolation = 0.0  # 0.0 to 1.0 for smooth movement between cells
        self.direction_queue = []  # Queue for buffering rapid input changes
    
    def move(self):
        # Consume next direction from queue if available
        if self.direction_queue:
            self.direction = self.direction_queue.pop(0)
        
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or
            new_head[1] < 0 or new_head[1] >= GRID_SIZE):
            return False  # Collision with wall
        
        # Check self collision
        if new_head in self.body:
            return False  # Collision with self
        
        # Move snake
        self.body.insert(0, new_head)
        if not self.grow_pending:
            self.body.pop()  # Remove tail
        else:
            self.grow_pending = False
        
        return True  # No collision
    
    def grow(self):
        self.grow_pending = True
    
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        # Determine what direction to compare against
        compare_direction = self.direction_queue[-1] if self.direction_queue else self.direction
        
        # Validate: prevent 180-degree reversal and duplicate consecutive directions
        if new_direction != OPPOSITE_DIRECTIONS[compare_direction] and new_direction != compare_direction:
            # Limit queue size to 1 buffered input for responsive classic snake feel
            if len(self.direction_queue) < 1:
                self.direction_queue.append(new_direction)
    
    def check_self_collision(self):
        return self.body[0] in self.body[1:]
    
    def update_interpolation(self, progress):
        """Update interpolation based on time since last move"""
        self.interpolation = min(1.0, progress)
    
    def get_display_position(self, segment_index):
        """Get interpolated pixel position for smooth rendering"""
        current_pos = self.body[segment_index]
        
        # Interpolate from previous position to current position
        if segment_index < len(self.body) - 1 and self.interpolation < 1.0:
            next_pos = self.body[segment_index + 1]
            # Lerp from previous (next in list) to current position
            x = next_pos[0] + (current_pos[0] - next_pos[0]) * self.interpolation
            y = next_pos[1] + (current_pos[1] - next_pos[1]) * self.interpolation
        else:
            # No interpolation for last segment or when interpolation is complete
            x, y = current_pos
        
        return (x * CELL_SIZE, y * CELL_SIZE)
    
    def draw(self, screen):
        for i, segment in enumerate(self.body):
            # Use interpolated position for smooth movement
            x, y = self.get_display_position(i)
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            # Gradient effect - brighter at head, darker toward tail
            brightness = max(100, 255 - (i * 5))
            color = (0, brightness, 0)
            # Draw with rounded corners
            pygame.draw.rect(screen, color, rect, border_radius=4)
            # Add darker outline
            pygame.draw.rect(screen, DARK_GREEN, rect, 2, border_radius=4)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.pulse = 0
    
    def spawn(self, snake_body_and_obstacles):
        # Keep generating random positions until we find one not on the snake or obstacles
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            position = (x, y)
            if position not in snake_body_and_obstacles:
                self.position = position
                break
    
    def get_position(self):
        return self.position
    
    def draw(self, screen):
        x, y = self.position
        # Pulse animation
        self.pulse += 0.1
        size_offset = int(math.sin(self.pulse) * 3)
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        adjusted_rect = rect.inflate(size_offset, size_offset)
        pygame.draw.rect(screen, RED, adjusted_rect, border_radius=4)


class Particle:
    def __init__(self, x, y, velocity_x, velocity_y, color):
        self.x = x
        self.y = y
        self.vx = velocity_x
        self.vy = velocity_y
        self.lifetime = 600  # milliseconds
        self.created_time = pygame.time.get_ticks()
        self.color = color
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
    
    def is_alive(self):
        return pygame.time.get_ticks() - self.created_time < self.lifetime
    
    def draw(self, screen):
        age = pygame.time.get_ticks() - self.created_time
        progress = age / self.lifetime
        # Fade alpha and size as particle ages
        alpha = max(0, min(255, int(255 * (1 - progress))))  # Clamp to valid range
        radius = max(1, int(5 * (1 - progress * 0.5)))  # Ensure radius is at least 1
        
        if radius > 0 and alpha > 0:
            # Draw circle with fade effect using per-pixel alpha
            surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            # Handle both RGB and RGBA colors - ensure all values are integers
            color_rgb = (int(self.color[0]), int(self.color[1]), int(self.color[2]))
            color_with_alpha = (color_rgb[0], color_rgb[1], color_rgb[2], alpha)
            pygame.draw.circle(surface, color_with_alpha, (radius, radius), radius)
            screen.blit(surface, (self.x - radius, self.y - radius))


class Obstacle:
    def __init__(self):
        self.positions = []
        self.shapes = []  # List of (positions_list, width, height) tuples
    
    def generate(self, count, snake_body, food_position):
        """Generate random obstacles avoiding snake, food, and edges. Some span multiple cells."""
        self.positions = []
        self.shapes = []
        attempts = 0
        max_attempts = count * 20
        obstacles_created = 0
        
        while obstacles_created < count and attempts < max_attempts:
            # Randomly decide shape: 60% single cell, 20% 2x1, 10% 1x2, 10% 2x2
            rand = random.random()
            if rand < 0.6:
                width, height = 1, 1
            elif rand < 0.8:
                width, height = 2, 1
            elif rand < 0.9:
                width, height = 1, 2
            else:
                width, height = 2, 2
            
            # Avoid edges (2 cell margin plus shape size)
            x = random.randint(2, GRID_SIZE - 2 - width)
            y = random.randint(2, GRID_SIZE - 2 - height)
            
            # Generate all positions for this shape
            shape_positions = []
            for dx in range(width):
                for dy in range(height):
                    shape_positions.append((x + dx, y + dy))
            
            # Check if all positions are free and not too close to snake start
            valid = True
            for pos in shape_positions:
                px, py = pos
                # Check general proximity and path in front of snake
                in_start_path = (OBSTACLE_START_AREA_MIN_X <= px <= OBSTACLE_START_AREA_MAX_X and 
                                OBSTACLE_START_AREA_MIN_Y <= py <= OBSTACLE_START_AREA_MAX_Y)
                too_close = abs(px - SNAKE_START_X) + abs(py - SNAKE_START_Y) <= 3
                
                if (pos in snake_body or 
                    pos == food_position or 
                    pos in self.positions or
                    too_close or
                    in_start_path):  # Keep center and starting path clear
                    valid = False
                    break
            
            if valid:
                self.positions.extend(shape_positions)
                self.shapes.append((x, y, width, height))
                obstacles_created += 1
            
            attempts += 1
    
    def check_collision(self, position):
        """Check if position collides with obstacle"""
        return position in self.positions
    
    def draw(self, screen):
        """Draw obstacles with subtle 3D effect as connected multi-cell blocks"""
        for shape in self.shapes:
            x, y, width, height = shape
            base_x = x * CELL_SIZE
            base_y = y * CELL_SIZE
            shape_width = width * CELL_SIZE
            shape_height = height * CELL_SIZE
            
            # Main block (entire shape as one rectangle)
            main_rect = pygame.Rect(base_x, base_y, shape_width, shape_height)
            pygame.draw.rect(screen, OBSTACLE_MID, main_rect, border_radius=3)
            
            # Light highlight on top-left (3D effect)
            highlight_rect = pygame.Rect(base_x + 2, base_y + 2, 
                                        shape_width - 4, max(4, shape_height // 3))
            pygame.draw.rect(screen, OBSTACLE_LIGHT, highlight_rect, border_radius=2)
            
            # Shadow on bottom-right (3D effect)
            shadow_rect = pygame.Rect(base_x + 2, base_y + shape_height - max(4, shape_height // 3) - 2, 
                                     shape_width - 4, max(4, shape_height // 3))
            pygame.draw.rect(screen, OBSTACLE_DARK, shadow_rect, border_radius=2)
            
            # Outer border for definition
            pygame.draw.rect(screen, OBSTACLE_DARK, main_rect, 2, border_radius=3)
            
            # Draw internal grid lines for multi-cell obstacles
            if width > 1 or height > 1:
                for gx in range(1, width):
                    line_x = base_x + gx * CELL_SIZE
                    pygame.draw.line(screen, OBSTACLE_DARK, 
                                   (line_x, base_y), (line_x, base_y + shape_height), 1)
                for gy in range(1, height):
                    line_y = base_y + gy * CELL_SIZE
                    pygame.draw.line(screen, OBSTACLE_DARK, 
                                   (base_x, line_y), (base_x + shape_width, line_y), 1)



class HighScoreManager:
    def __init__(self, filename='high_score.json'):
        self.filename = filename
        self.high_score = self.load()
    
    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0
    
    def save(self, score):
        with open(self.filename, 'w') as f:
            json.dump({'high_score': score}, f)
    
    def update(self, current_score):
        if current_score > self.high_score:
            self.high_score = current_score
            self.save(current_score)
    
    def get_high_score(self):
        return self.high_score


class Powerup:
    """Powerup system with 4 types: Shield, Double Points, Ghost Mode, Speed Boost"""
    
    # Powerup types
    SHIELD = 'shield'
    DOUBLE_POINTS = 'double_points'
    GHOST_MODE = 'ghost_mode'
    SPEED_BOOST = 'speed_boost'
    
    # Powerup metadata
    INFO = {
        SHIELD: {
            'name': 'Shield',
            'description': 'Survive one collision',
            'color': CYAN,
            'duration': None,  # One-time use
            'icon': '🛡️'
        },
        DOUBLE_POINTS: {
            'name': 'Double Points',
            'description': 'Next 5 apples worth 20pts',
            'color': YELLOW,
            'duration': None,  # Lasts for 5 apples
            'icon': '2X'
        },
        GHOST_MODE: {
            'name': 'Ghost Mode',
            'description': 'Pass through yourself (10s)',
            'color': PURPLE,
            'duration': 10000,  # 10 seconds
            'icon': '👻'
        },
        SPEED_BOOST: {
            'name': 'Speed Boost',
            'description': '50% faster movement (15s)',
            'color': ORANGE,
            'duration': 15000,  # 15 seconds
            'icon': '⚡'
        }
    }
    
    def __init__(self, powerup_type):
        self.type = powerup_type
        self.active = False
        self.start_time = 0
        self.remaining_uses = 0  # For double points (counts apples)
        
    def activate(self, current_time):
        """Activate the powerup"""
        self.active = True
        self.start_time = current_time
        if self.type == Powerup.DOUBLE_POINTS:
            self.remaining_uses = 5
    
    def is_expired(self, current_time):
        """Check if powerup has expired"""
        if not self.active:
            return True
        
        duration = Powerup.INFO[self.type]['duration']
        if duration is not None:
            return current_time - self.start_time >= duration
        
        # For non-duration powerups (shield, double points)
        if self.type == Powerup.DOUBLE_POINTS:
            return self.remaining_uses <= 0
        
        return False
    
    def get_remaining_time(self, current_time):
        """Get remaining time in seconds"""
        if not self.active:
            return 0
        duration = Powerup.INFO[self.type]['duration']
        if duration is None:
            return 0
        remaining_ms = duration - (current_time - self.start_time)
        return max(0, remaining_ms / 1000)


class FontManager:
    """Manages cached font objects for performance"""
    def __init__(self):
        self.fonts = {}
    
    def get_font(self, size):
        """Get or create a font of the specified size"""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]


class GameState:
    """Encapsulates all game state variables"""
    def __init__(self):
        # Game flow states
        self.title_screen_active = True
        self.game_running = False
        self.game_over = False
        self.running = True
        
        # Game objects
        self.snake = Snake()
        self.food = Food()
        self.score_manager = HighScoreManager()
        self.obstacle = Obstacle()
        
        # Scoring and timing
        self.score = 0
        self.elapsed_time = 0
        self.start_time = 0
        self.last_move_time = 0
        
        # Input and UI
        self.selected_button = 0  # 0 for Start, 1 for Quit
        self.death_reason = ""
        
        # Game mechanics
        self.particles = []
        self.active_powerups = []
        self.apples_collected = 0
        
        # Animation states
        self.countdown_active = True
        self.countdown_start_time = 0
        self.powerup_selection_active = False
        self.powerup_choices = []
        self.selected_powerup_index = 0
        self.death_animation_active = False
        self.death_animation_start = 0
        self.death_focal_point = (0, 0)
        
        # Visual effects
        self.screen_shake_intensity = 0.0
        self.screen_shake_time = 0
        self.score_flash_time = 0
        self.screen_flash_time = 0
        self.shield_text_active = False
        self.shield_text_time = 0
    
    def reset_game(self, current_time):
        """Reset game state for a new game"""
        self.snake = Snake()
        self.obstacle.generate(15, self.snake.body, self.food.position)
        self.food.spawn(self.snake.body + self.obstacle.positions)
        self.score = 0
        self.elapsed_time = 0
        self.last_move_time = current_time
        self.countdown_active = True
        self.countdown_start_time = current_time
        self.particles = []
        self.screen_shake_intensity = 0
        self.screen_shake_time = 0
        self.score_flash_time = 0
        self.screen_flash_time = 0
        self.apples_collected = 0
        self.active_powerups = []
        self.powerup_selection_active = False
        self.powerup_choices = []
        self.selected_powerup_index = 0
        self.death_reason = ""
        self.death_animation_active = False
        self.shield_text_active = False


def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake Survivor')
    clock = pygame.time.Clock()
    
    # Initialize font manager for performance
    font_manager = FontManager()
    
    # Create game state
    state = GameState()
    state.start_time = pygame.time.get_ticks()
    state.last_move_time = state.start_time
    state.countdown_start_time = state.start_time
    
    # Title screen button setup
    start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    quit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
    
    while state.running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.running = False

            if state.title_screen_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        state.selected_button = (state.selected_button - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        state.selected_button = (state.selected_button + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if state.selected_button == 0:  # Start Game
                            state.title_screen_active = False
                            state.game_running = True
                            state.start_time = current_time
                            state.reset_game(current_time)
                        else:  # Quit Game
                            state.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_rect.collidepoint(mouse_pos):
                        state.title_screen_active = False
                        state.game_running = True
                        state.start_time = current_time
                        state.reset_game(current_time)
                    elif quit_button_rect.collidepoint(mouse_pos):
                        state.running = False
            
            elif state.game_running:
                if event.type == pygame.KEYDOWN:
                    if state.game_over:
                        if event.key == pygame.K_SPACE:
                            state.game_over = False
                            state.reset_game(current_time)
                    else:
                        # Mode-specific input capture:
                        if state.powerup_selection_active:
                            if event.key == pygame.K_LEFT:
                                state.selected_powerup_index = (state.selected_powerup_index - 1) % POWERUP_SELECTION_COUNT
                            elif event.key == pygame.K_RIGHT:
                                state.selected_powerup_index = (state.selected_powerup_index + 1) % POWERUP_SELECTION_COUNT
                            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                                chosen_type = state.powerup_choices[state.selected_powerup_index]
                                new_powerup = Powerup(chosen_type)
                                new_powerup.activate(current_time)
                                state.active_powerups.append(new_powerup)
                                state.powerup_selection_active = False
                                state.powerup_choices = []
                                state.selected_powerup_index = 0
                        else:
                            # Handle direction changes (playing/countdown)
                            if event.key == pygame.K_UP:
                                state.snake.change_direction(UP)
                            elif event.key == pygame.K_DOWN:
                                state.snake.change_direction(DOWN)
                            elif event.key == pygame.K_LEFT:
                                state.snake.change_direction(LEFT)
                            elif event.key == pygame.K_RIGHT:
                                state.snake.change_direction(RIGHT)
        
        # Drawing
        screen.fill(BLACK)

        if state.title_screen_active:
            # Draw title
            title_font = font_manager.get_font(90)
            button_font = font_manager.get_font(50)
            
            title_text = title_font.render('Snake Survivor', True, TITLE_COLOR)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            screen.blit(title_text, title_rect)

            # Draw buttons
            # Start Button
            start_color = BUTTON_HOVER if start_button_rect.collidepoint(mouse_pos) or state.selected_button == 0 else BUTTON_NORMAL
            pygame.draw.rect(screen, start_color, start_button_rect, border_radius=10)
            start_text = button_font.render('Start Game', True, BUTTON_TEXT)
            start_text_rect = start_text.get_rect(center=start_button_rect.center)
            screen.blit(start_text, start_text_rect)

            # Quit Button
            quit_color = BUTTON_HOVER if quit_button_rect.collidepoint(mouse_pos) or state.selected_button == 1 else BUTTON_NORMAL
            pygame.draw.rect(screen, quit_color, quit_button_rect, border_radius=10)
            quit_text = button_font.render('Quit Game', True, BUTTON_TEXT)
            quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
            screen.blit(quit_text, quit_text_rect)

        elif state.game_running:
            if not state.game_over:
                state.elapsed_time = (current_time - state.start_time) / 1000
            
            # Handle countdown timer
            if state.countdown_active:
                time_since_countdown = current_time - state.countdown_start_time
                if time_since_countdown >= COUNTDOWN_DURATION + GO_DURATION:
                    state.countdown_active = False
                    state.last_move_time = current_time  # Reset move timer after countdown
            
            # Move snake based on timer, not frame rate (only if countdown finished)
            time_since_move = current_time - state.last_move_time
            
            # Apply speed boost if active
            current_move_delay = MOVE_DELAY
            for powerup in state.active_powerups:
                if powerup.type == Powerup.SPEED_BOOST and powerup.active:
                    current_move_delay = int(MOVE_DELAY * 0.5)  # 50% faster
            
            if not state.countdown_active and not state.powerup_selection_active and not state.death_animation_active and time_since_move >= current_move_delay:
                # Check if ghost mode is active (allows passing through self)
                ghost_mode_active = any(p.type == Powerup.GHOST_MODE and p.active for p in state.active_powerups)
                
                # Predict next head position before moving
                head_x, head_y = state.snake.body[0]
                next_dir = state.snake.direction_queue[0] if state.snake.direction_queue else state.snake.direction
                next_head = (head_x + next_dir[0], head_y + next_dir[1])
                
                collision_detected = False
                collision_type = None  # 'wall', 'obstacle', or 'self'
                
                # Check for wall collision
                if next_head[0] < 0 or next_head[0] >= GRID_SIZE or next_head[1] < 0 or next_head[1] >= GRID_SIZE:
                    collision_detected = True
                    collision_type = 'wall'
                # Check for obstacle collision before moving
                elif state.obstacle.check_collision(next_head):
                    collision_detected = True
                    collision_type = 'obstacle'
                # Check for self-collision on the predicted next position BEFORE moving
                # Exclude tail since it will move away during the move
                elif not ghost_mode_active and next_head in state.snake.body[:-1]:
                    collision_detected = True
                    collision_type = 'self'
                
                # Check if shield is active BEFORE moving
                shield_active = False
                for powerup in state.active_powerups:
                    if powerup.type == Powerup.SHIELD and powerup.active:
                        shield_active = True
                        break
                
                # Only move if no collision detected, OR if shield will protect us from wall/obstacle
                if not collision_detected or (shield_active and collision_type in ['wall', 'obstacle']):
                    move_result = state.snake.move()
                
                if collision_detected:
                    if shield_active:
                        # Shield is active, break it and continue game
                        for powerup in state.active_powerups:
                            if powerup.type == Powerup.SHIELD and powerup.active:
                                powerup.active = False  # Shield breaks
                                # Create shield break effect
                                head_x, head_y = state.snake.body[0]
                                head_pixel_x = head_x * CELL_SIZE + CELL_SIZE // 2
                                head_pixel_y = head_y * CELL_SIZE + CELL_SIZE // 2
                                for i in range(16):
                                    angle = (i / 16) * 2 * math.pi
                                    speed = 3 + random.uniform(0, 2)
                                    vx = math.cos(angle) * speed
                                    vy = math.sin(angle) * speed
                                    state.particles.append(Particle(head_pixel_x, head_pixel_y, vx, vy, CYAN))
                                state.screen_shake_intensity = 10
                                state.screen_shake_time = current_time
                                # Trigger shield text effect
                                state.shield_text_active = True
                                state.shield_text_time = current_time
                                break
                        # Shield absorbed the collision, continue game normally
                        collision_detected = False
                    else:
                        # Trigger death animation instead of immediate game over
                        state.death_animation_active = True
                        state.death_animation_start = current_time
                        state.particles.clear()  # Clear any existing particles before creating new ones
                        
                        # Get snake head position for zoom focal point
                        head_x, head_y = state.snake.body[0]
                        head_pixel_x = head_x * CELL_SIZE + CELL_SIZE // 2
                        head_pixel_y = head_y * CELL_SIZE + CELL_SIZE // 2
                        state.death_focal_point = (head_pixel_x, head_pixel_y)
                        state.death_collision_type = collision_type
                        
                        # Create dramatic collision particle explosion
                        particle_count = 40  # More particles for drama
                        particle_colors = [RED, ORANGE, YELLOW, WHITE]
                        
                        # Ring of fast particles
                        for i in range(particle_count):
                            angle = (i / particle_count) * 2 * math.pi
                            speed = 4 + random.uniform(0, 3)
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            color = random.choice(particle_colors)
                            state.particles.append(Particle(head_pixel_x, head_pixel_y, vx, vy, color))
                        
                        # Extra burst of slow particles for depth
                        for i in range(20):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = 1 + random.uniform(0, 2)
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            state.particles.append(Particle(head_pixel_x, head_pixel_y, vx, vy, RED))
                        
                        # Massive screen shake
                        state.screen_shake_intensity = 15
                        state.screen_shake_time = current_time
                        
                        state.score_manager.update(state.score)
                        # Set death reason for Game Over screen
                        if collision_type == 'wall':
                            state.death_reason = "You hit the wall!"
                        elif collision_type == 'obstacle':
                            state.death_reason = "You crashed into an obstacle!"
                        elif collision_type == 'self':
                            state.death_reason = "You ran into yourself!"
                        else:
                            state.death_reason = "Game Over!"
                else:
                    # Check food collision
                    if state.snake.body[0] == state.food.get_position():
                        # Spawn enhanced particle effect at food position
                        food_pixel_x = state.food.position[0] * CELL_SIZE + CELL_SIZE // 2
                        food_pixel_y = state.food.position[1] * CELL_SIZE + CELL_SIZE // 2
                        
                        # Check if double points is active
                        points_to_add = 10
                        for powerup in state.active_powerups:
                            if powerup.type == Powerup.DOUBLE_POINTS and powerup.active:
                                points_to_add = 20
                                powerup.remaining_uses -= 1
                                if powerup.remaining_uses <= 0:
                                    powerup.active = False
                                break
                        
                        # Main burst - 20 particles in circle
                        for i in range(20):
                            angle = (i / 20) * 2 * math.pi
                            speed = 2 + random.uniform(-0.5, 1.5)  # Variable speed
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            # Mix of red and yellow particles (or all yellow if double points)
                            if points_to_add == 20:
                                color = YELLOW
                            else:
                                color = RED if i % 3 != 0 else YELLOW
                            state.particles.append(Particle(food_pixel_x, food_pixel_y, vx, vy, color))
                        
                        # Extra fast particles for emphasis
                        for i in range(8):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = 4 + random.uniform(0, 2)
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            state.particles.append(Particle(food_pixel_x, food_pixel_y, vx, vy, YELLOW))
                        
                        # Trigger screen shake
                        state.screen_shake_intensity = 8
                        state.screen_shake_time = current_time
                        
                        # Trigger score flash
                        state.score_flash_time = current_time
                        
                        # Trigger screen flash
                        state.screen_flash_time = current_time
                        
                        state.snake.grow()
                        state.score += points_to_add
                        state.food.spawn(state.snake.body + state.obstacle.positions)
                        state.apples_collected += 1
                        
                        # Trigger powerup selection every 3 apples
                        if state.apples_collected % 3 == 0 and not state.powerup_selection_active:
                            state.powerup_selection_active = True
                            # Generate 3 random powerup choices
                            all_types = [Powerup.SHIELD, Powerup.DOUBLE_POINTS, Powerup.GHOST_MODE, Powerup.SPEED_BOOST]
                            state.powerup_choices = random.sample(all_types, 3)
                            state.selected_powerup_index = 1  # Start with middle option selected
                
                # Reset interpolation after move
                state.snake.interpolation = 0.0
                state.last_move_time = current_time
            
            # Clean up expired powerups
            state.active_powerups = [p for p in state.active_powerups if not p.is_expired(current_time)]
            
            # Handle screen shake decay (runs during normal gameplay)
            if state.screen_shake_intensity > 0:
                time_since_shake = current_time - state.screen_shake_time
                if time_since_shake > 300:  # Shake lasts 300ms
                    state.screen_shake_intensity = 0
                else:
                    # Decay shake intensity
                    state.screen_shake_intensity = 8 * (1 - time_since_shake / 300)
            
            # Handle death animation
            if state.death_animation_active:
                death_time_elapsed = current_time - state.death_animation_start
                if death_time_elapsed >= 2500:  # 2.5 seconds
                    state.death_animation_active = False
                    state.game_over = True
                    state.particles.clear()  # Clear particles when game over, so they don't loop on the game over screen
        
            # Calculate screen shake offset
            shake_x = 0
            shake_y = 0
            if state.screen_shake_intensity > 0:
                shake_x = random.randint(-int(state.screen_shake_intensity), int(state.screen_shake_intensity))
                shake_y = random.randint(-int(state.screen_shake_intensity), int(state.screen_shake_intensity))
            
            # Drawing
            screen.fill(BLACK)
            
            # Handle death animation zoom effect
            if state.death_animation_active:
                death_time_elapsed = current_time - state.death_animation_start
                
                # Animation phases: 500ms freeze, 1500ms zoom (500-2000ms), 500ms hold+fade (2000-2500ms)
                if death_time_elapsed < 500:
                    zoom_scale = 1.0
                elif death_time_elapsed < 2000:
                    progress = (death_time_elapsed - 500) / 1500
                    # Ease-in zoom curve
                    zoom_scale = 1.0 + (progress ** 1.5) * 2.0  # 1.0x to 3.0x
                else:
                    zoom_scale = 3.0
                
                # Create zoom surface
                zoom_surface = pygame.Surface((GRID_WIDTH, HEIGHT))
                zoom_surface.fill(BLACK)
                
                # Calculate camera offset to center on death focal point
                focal_x, focal_y = state.death_focal_point
                camera_x = focal_x - GRID_WIDTH // 2
                camera_y = focal_y - HEIGHT // 2
                
                # Draw grid
                for x in range(0, GRID_WIDTH, CELL_SIZE):
                    pygame.draw.line(zoom_surface, (30, 30, 30), (x, 0), (x, HEIGHT))
                for y in range(0, HEIGHT, CELL_SIZE):
                    pygame.draw.line(zoom_surface, (30, 30, 30), (0, y), (GRID_WIDTH, y))
                
                # Draw particles
                for particle in state.particles:
                    particle.draw(zoom_surface)
                
                # Draw obstacles
                state.obstacle.draw(zoom_surface)
                
                # Draw food
                state.food.draw(zoom_surface)
                
                # Draw snake (frozen)
                state.snake.draw(zoom_surface)
                
                # Scale the surface
                scaled_width = int(GRID_WIDTH * zoom_scale)
                scaled_height = int(HEIGHT * zoom_scale)
                scaled_surface = pygame.transform.scale(zoom_surface, (scaled_width, scaled_height))
                
                # Calculate blit position to center zoom on focal point
                blit_x = -(camera_x * zoom_scale) + shake_x
                blit_y = -(camera_y * zoom_scale) + shake_y
                
                # Blit scaled surface to screen (grid area only)
                screen.blit(scaled_surface, (blit_x, blit_y))
                
                # Draw fade overlay in final phase
                if death_time_elapsed >= 2000:
                    fade_progress = (death_time_elapsed - 2000) / 500
                    fade_alpha = int(fade_progress * 255)
                    fade_surface = pygame.Surface((GRID_WIDTH, HEIGHT), pygame.SRCALPHA)
                    fade_surface.fill((0, 0, 0, fade_alpha))
                    screen.blit(fade_surface, (0, 0))
                
                # Draw panel normally
                panel_rect = pygame.Rect(GRID_WIDTH, 0, PANEL_WIDTH, HEIGHT)
                pygame.draw.rect(screen, DARK_GRAY, panel_rect)
                pygame.draw.line(screen, WHITE, (GRID_WIDTH, 0), (GRID_WIDTH, HEIGHT), 2)
            else:
                # Normal rendering
                # Draw panel background
                panel_rect = pygame.Rect(GRID_WIDTH, 0, PANEL_WIDTH, HEIGHT)
                pygame.draw.rect(screen, DARK_GRAY, panel_rect)
                
                # Draw separator line between grid and panel
                pygame.draw.line(screen, WHITE, (GRID_WIDTH, 0), (GRID_WIDTH, HEIGHT), 2)
                
                # Draw background grid (with shake offset, only on grid area)
                for x in range(0, GRID_WIDTH, CELL_SIZE):
                    pygame.draw.line(screen, (30, 30, 30), (x + shake_x, shake_y), (x + shake_x, HEIGHT + shake_y))
                for y in range(0, HEIGHT, CELL_SIZE):
                    pygame.draw.line(screen, (30, 30, 30), (shake_x, y + shake_y), (GRID_WIDTH + shake_x, y + shake_y))
                
                # Update and draw particles (with shake offset)
                state.particles = [p for p in state.particles if p.is_alive()]
                for particle in state.particles:
                    particle.update()
                    # Temporarily offset particle position for shake
                    original_x, original_y = particle.x, particle.y
                    particle.x += shake_x
                    particle.y += shake_y
                    particle.draw(screen)
                    particle.x, particle.y = original_x, original_y
                
                # Draw obstacles
                state.obstacle.draw(screen)
                
                # Initialize font for panel UI
                font = font_manager.get_font(36)
            
            # Update particles even during death animation
            if state.death_animation_active:
                state.particles = [p for p in state.particles if p.is_alive()]
                for particle in state.particles:
                    particle.update()
            
            if not state.game_over and not state.death_animation_active:
                # Draw game elements
                state.food.draw(screen)
                state.snake.draw(screen)
                
                # Draw score with zoom effect in panel
                if state.score_flash_time > 0:
                    time_since_flash = current_time - state.score_flash_time
                    if time_since_flash < 300:  # Flash lasts 300ms
                        # Scale from 1.5 to 1.0
                        scale = 1.5 - (time_since_flash / 300) * 0.5
                        score_font_size = int(36 * scale)
                        score_font = pygame.font.Font(None, score_font_size)
                        score_text = score_font.render(f'Score: {state.score}', True, YELLOW)
                        score_rect = score_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 30))
                        screen.blit(score_text, score_rect)
                    else:
                        score_text = font.render(f'Score: {state.score}', True, WHITE)
                        score_rect = score_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 30))
                        screen.blit(score_text, score_rect)
                else:
                    score_text = font.render(f'Score: {state.score}', True, WHITE)
                    score_rect = score_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 30))
                    screen.blit(score_text, score_rect)
                
                # Draw high score in panel
                high_score_text = font.render(f'High Score: {state.score_manager.get_high_score()}', True, WHITE)
                high_score_rect = high_score_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 70))
                screen.blit(high_score_text, high_score_rect)

                # Draw timer
                timer_text = font.render(f'Time: {int(state.elapsed_time)}', True, WHITE)
                timer_rect = timer_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 110))
                screen.blit(timer_text, timer_rect)
                
                # Draw active powerup indicators in panel
                if state.active_powerups:
                    indicator_y = 160
                    indicator_font = pygame.font.Font(None, 22)
                    title_font = pygame.font.Font(None, 28)
                    
                    # Draw "Active Powerups" title
                    title_text = title_font.render('Active Powerups', True, YELLOW)
                    title_rect = title_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 140))
                    screen.blit(title_text, title_rect)
                    
                    for powerup in state.active_powerups:
                        if powerup.active:
                            info = Powerup.INFO[powerup.type]
                            
                            # Background bar (centered in panel)
                            bar_width = 180
                            bar_height = 60
                            bar_x = GRID_WIDTH + (PANEL_WIDTH - bar_width) // 2
                            bar_rect = pygame.Rect(bar_x, indicator_y, bar_width, bar_height)
                            pygame.draw.rect(screen, info['color'], bar_rect, border_radius=8)
                            pygame.draw.rect(screen, WHITE, bar_rect, 2, border_radius=8)
                            
                            # Icon (larger)
                            icon_font = pygame.font.Font(None, 32)
                            icon_text = icon_font.render(info['icon'], True, BLACK)
                            icon_rect = icon_text.get_rect(center=(bar_x + 20, indicator_y + 20))
                            screen.blit(icon_text, icon_rect)
                            
                            # Name
                            name_text = indicator_font.render(info['name'], True, BLACK)
                            screen.blit(name_text, (bar_x + 40, indicator_y + 8))
                            
                            # Timer or uses remaining
                            if powerup.type == Powerup.DOUBLE_POINTS:
                                remaining_text = indicator_font.render(f'{powerup.remaining_uses} apples left', True, BLACK)
                                screen.blit(remaining_text, (bar_x + 40, indicator_y + 32))
                            elif info['duration'] is not None:
                                remaining_time = powerup.get_remaining_time(current_time)
                                time_text = indicator_font.render(f'{remaining_time:.1f}s remaining', True, BLACK)
                                screen.blit(time_text, (bar_x + 40, indicator_y + 32))
                        
                        indicator_y += 70
                
                # Screen flash effect when collecting food (only on grid area)
                if state.screen_flash_time > 0:
                    time_since_flash = current_time - state.screen_flash_time
                    if time_since_flash < 150:  # Flash lasts 150ms
                        flash_alpha = int(80 * (1 - time_since_flash / 150))
                        flash_surface = pygame.Surface((GRID_WIDTH, HEIGHT), pygame.SRCALPHA)
                        flash_surface.fill((255, 255, 255, flash_alpha))
                        screen.blit(flash_surface, (0, 0))
                
                # Draw shield used text (floating upward with fade)
                if state.shield_text_active:
                    time_since_shield = current_time - state.shield_text_time
                    shield_text_duration = 1000  # 1 second
                    if time_since_shield < shield_text_duration:
                        # Calculate alpha fade (255 to 0)
                        alpha = int(255 * (1 - time_since_shield / shield_text_duration))
                        # Calculate upward offset (0 to -100 pixels)
                        y_offset = -(time_since_shield / shield_text_duration) * 100
                        
                        # Create shield text with large font
                        shield_font = pygame.font.Font(None, 60)
                        shield_text = shield_font.render('SHIELD USED!', True, CYAN)
                        shield_text.set_alpha(alpha)
                        
                        # Center on game grid
                        shield_rect = shield_text.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2 + y_offset))
                        screen.blit(shield_text, shield_rect)
                    else:
                        state.shield_text_active = False
                
                # Draw powerup selection screen (centered on grid)
                if state.powerup_selection_active:
                    # Semi-transparent overlay over grid only
                    overlay = pygame.Surface((GRID_WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    screen.blit(overlay, (0, 0))
                    
                    # Title
                    title_font = pygame.font.Font(None, 48)
                    title_text = title_font.render('Choose a Powerup!', True, YELLOW)
                    title_rect = title_text.get_rect(center=(GRID_WIDTH // 2, 80))
                    screen.blit(title_text, title_rect)
                    
                    # Draw 3 powerup cards
                    card_width = 150
                    card_height = 200
                    card_spacing = 30
                    start_x = (GRID_WIDTH - (card_width * 3 + card_spacing * 2)) // 2
                    card_y = 180
                    
                    for i, powerup_type in enumerate(state.powerup_choices):
                        card_x = start_x + i * (card_width + card_spacing)
                        info = Powerup.INFO[powerup_type]
                        
                        # Card background with selection highlight
                        if i == state.selected_powerup_index:
                            # Animated scale for selected card
                            pulse = math.sin(current_time / 200) * 5
                            card_rect = pygame.Rect(card_x - pulse, card_y - pulse, 
                                                   card_width + pulse * 2, card_height + pulse * 2)
                            pygame.draw.rect(screen, info['color'], card_rect, border_radius=10)
                            pygame.draw.rect(screen, WHITE, card_rect, 4, border_radius=10)
                        else:
                            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                            pygame.draw.rect(screen, info['color'], card_rect, border_radius=10)
                            pygame.draw.rect(screen, DARK_GRAY, card_rect, 2, border_radius=10)
                        
                        # Icon
                        icon_font = pygame.font.Font(None, 60)
                        icon_text = icon_font.render(info['icon'], True, BLACK)
                        icon_rect = icon_text.get_rect(center=(card_x + card_width // 2, card_y + 50))
                        screen.blit(icon_text, icon_rect)
                        
                        # Name
                        name_font = pygame.font.Font(None, 32)
                        name_text = name_font.render(info['name'], True, BLACK)
                        name_rect = name_text.get_rect(center=(card_x + card_width // 2, card_y + 120))
                        screen.blit(name_text, name_rect)
                        
                        # Description (word wrap)
                        desc_font = pygame.font.Font(None, 20)
                        desc_lines = info['description'].split(' ')
                        line1 = ' '.join(desc_lines[:3])
                        line2 = ' '.join(desc_lines[3:]) if len(desc_lines) > 3 else ''
                        
                        desc_text1 = desc_font.render(line1, True, BLACK)
                        desc_rect1 = desc_text1.get_rect(center=(card_x + card_width // 2, card_y + 155))
                        screen.blit(desc_text1, desc_rect1)
                        
                        if line2:
                            desc_text2 = desc_font.render(line2, True, BLACK)
                            desc_rect2 = desc_text2.get_rect(center=(card_x + card_width // 2, card_y + 175))
                            screen.blit(desc_text2, desc_rect2)
                
                # Draw countdown if active
                if state.countdown_active:
                    time_since_countdown = current_time - state.countdown_start_time
                    
                    # Semi-transparent overlay
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 150))  # Black with 150 alpha
                    screen.blit(overlay, (0, 0))
                    
                    # Determine countdown number or "GO!"
                    if time_since_countdown < COUNTDOWN_DURATION:
                        countdown_value = 3 - int(time_since_countdown / 1000)
                        countdown_text = str(countdown_value)
                        color = WHITE
                        base_font_size = 120
                        
                        # Calculate progress within current second (0.0 to 1.0)
                        progress_in_second = (time_since_countdown % 1000) / 1000.0
                        
                        # Zoom in effect: Start at 150% scale, zoom to 100%, then slight bounce
                        if progress_in_second < 0.3:
                            # Zoom in phase (0.3 seconds)
                            scale = 1.5 - (progress_in_second / 0.3) * 0.5
                        elif progress_in_second < 0.4:
                            # Bounce phase (0.1 seconds)
                            bounce_progress = (progress_in_second - 0.3) / 0.1
                            scale = 1.0 - math.sin(bounce_progress * math.pi) * 0.1
                        else:
                            # Steady phase
                            scale = 1.0
                        
                        # Slight rotation wobble during zoom
                        if progress_in_second < 0.4:
                            rotation_angle = math.sin(progress_in_second * math.pi * 5) * 5  # ±5 degrees
                        else:
                            rotation_angle = 0
                        
                        font_size = int(base_font_size * scale)
                    else:
                        countdown_text = "GO!"
                        color = GREEN
                        base_font_size = 100
                        
                        # GO! explosion effect
                        go_progress = (time_since_countdown - COUNTDOWN_DURATION) / GO_DURATION
                        
                        # Explosive zoom from 50% to 130% then settle to 120%
                        if go_progress < 0.5:
                            scale = 0.5 + (go_progress / 0.5) * 0.8  # 0.5 to 1.3
                        else:
                            scale = 1.3 - ((go_progress - 0.5) / 0.5) * 0.1  # 1.3 to 1.2
                        
                        # Rotation spin on GO!
                        rotation_angle = go_progress * 360 * 0.5  # Half rotation
                        
                        font_size = int(base_font_size * scale)
                    
                    # Create large font for countdown
                    countdown_font = pygame.font.Font(None, font_size)
                    text_surface = countdown_font.render(countdown_text, True, color)
                    
                    # Apply rotation if needed
                    if abs(rotation_angle) > 0.1:
                        text_surface = pygame.transform.rotate(text_surface, -rotation_angle)
                    
                    text_rect = text_surface.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2))
                    
                    # Add pulsing glow effect to countdown text
                    glow_font = pygame.font.Font(None, int(font_size * 1.1))
                    for offset in range(5, 0, -1):
                        alpha = 50 - offset * 10
                        glow_surface = glow_font.render(countdown_text, True, (*color[:3],))
                        
                        # Apply same rotation to glow
                        if abs(rotation_angle) > 0.1:
                            glow_surface = pygame.transform.rotate(glow_surface, -rotation_angle)
                        
                        glow_surface.set_alpha(alpha)
                        glow_rect = glow_surface.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2))
                        screen.blit(glow_surface, glow_rect)
                    
                    screen.blit(text_surface, text_rect)
            else:
                # Game over screen - show frozen death scene with full fade overlay
                # Create the final frozen scene surface
                frozen_surface = pygame.Surface((GRID_WIDTH, HEIGHT))
                frozen_surface.fill(BLACK)
                
                # Draw grid
                for x in range(0, GRID_WIDTH, CELL_SIZE):
                    pygame.draw.line(frozen_surface, (30, 30, 30), (x, 0), (x, HEIGHT))
                for y in range(0, HEIGHT, CELL_SIZE):
                    pygame.draw.line(frozen_surface, (30, 30, 30), (0, y), (GRID_WIDTH, y))
                
                # Don't draw particles on game over screen - they should be cleared
                
                # Draw obstacles
                state.obstacle.draw(frozen_surface)
                
                # Draw food
                state.food.draw(frozen_surface)
                
                # Draw snake (frozen)
                state.snake.draw(frozen_surface)
                
                # Blit frozen scene to screen
                screen.blit(frozen_surface, (0, 0))
                
                # Dark fade overlay over the scene
                fade_overlay = pygame.Surface((GRID_WIDTH, HEIGHT), pygame.SRCALPHA)
                fade_overlay.fill((0, 0, 0, 200))  # Strong fade for readability
                screen.blit(fade_overlay, (0, 0))
                
                # Draw panel background
                panel_rect = pygame.Rect(GRID_WIDTH, 0, PANEL_WIDTH, HEIGHT)
                pygame.draw.rect(screen, DARK_GRAY, panel_rect)
                pygame.draw.line(screen, WHITE, (GRID_WIDTH, 0), (GRID_WIDTH, HEIGHT), 2)
                
                # Initialize font for game over screen
                game_over_font = font_manager.get_font(48)
                text_font = font_manager.get_font(36)
                
                game_over_text = game_over_font.render('Game Over!', True, RED)
                reason_text = text_font.render(state.death_reason, True, YELLOW)
                score_text = text_font.render(f'Final Score: {state.score}', True, WHITE)
                high_score_text = text_font.render(f'High Score: {state.score_manager.get_high_score()}', True, WHITE)
                restart_text = text_font.render('Press SPACE to restart', True, WHITE)
                
                screen.blit(game_over_text, (GRID_WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
                screen.blit(reason_text, (GRID_WIDTH // 2 - reason_text.get_width() // 2, HEIGHT // 2 - 40))
                screen.blit(score_text, (GRID_WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 0))
                screen.blit(high_score_text, (GRID_WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 40))
                screen.blit(restart_text, (GRID_WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == '__main__':
    main()
