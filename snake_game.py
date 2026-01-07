import pygame
import random
import json
import os
import math

# Constants
GRID_SIZE = 30
CELL_SIZE = 20
GRID_WIDTH = GRID_SIZE * CELL_SIZE  # 600
PANEL_WIDTH = 200
WIDTH = GRID_WIDTH + PANEL_WIDTH  # 800 (600 grid + 200 panel)
HEIGHT = GRID_SIZE * CELL_SIZE  # 600
FPS = 30
MOVE_DELAY = 100  # milliseconds between moves (10 moves/second)

# Colors (R, G, B)
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

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        # Start at center (15, 15) with 3 segments moving right
        self.body = [(15, 15), (14, 15), (13, 15)]
        self.direction = RIGHT
        self.grow_pending = False
        self.interpolation = 0.0  # 0.0 to 1.0 for smooth movement between cells
    
    def move(self):
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
        opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        if new_direction != opposite[self.direction]:
            self.direction = new_direction
    
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
    
    def spawn(self, snake_body):
        # Keep generating random positions until we find one not on the snake
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            position = (x, y)
            if position not in snake_body:
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
        alpha = int(255 * (1 - progress))
        radius = int(5 * (1 - progress * 0.5))  # Shrink to 50% of original size
        
        if radius > 0:
            # Draw circle with fade effect using per-pixel alpha
            surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, alpha), (radius, radius), radius)
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
            # Snake starts at (15,15) moving right, so avoid x: 16-20, y: 13-17
            valid = True
            for pos in shape_positions:
                px, py = pos
                # Check general proximity and path in front of snake
                in_start_path = (16 <= px <= 20 and 13 <= py <= 17)
                too_close = abs(px - 15) + abs(py - 15) <= 3
                
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


def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Initialize game objects
    snake = Snake()
    food = Food()
    food.spawn(snake.body)
    score_manager = HighScoreManager()
    obstacle = Obstacle()
    obstacle.generate(15, snake.body, food.position)  # 15 obstacles for moderate difficulty
    
    # Game state
    score = 0
    game_over = False
    running = True
    last_move_time = pygame.time.get_ticks()
    particles = []
    
    # Hype effects
    screen_shake_intensity = 0
    screen_shake_time = 0
    score_flash_time = 0
    screen_flash_time = 0
    
    # Powerup system
    apples_collected = 0
    active_powerups = []  # List of active Powerup objects
    powerup_selection_active = False
    powerup_choices = []  # 3 random powerup types to choose from
    selected_powerup_index = 0  # For keyboard navigation
    
    # Countdown state
    countdown_active = True
    countdown_start_time = pygame.time.get_ticks()
    countdown_duration = 3000  # 3 seconds (3, 2, 1)
    go_duration = 500  # "GO!" shows for 0.5 seconds
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        # Restart game
                        snake = Snake()
                        food.spawn(snake.body)
                        obstacle.generate(15, snake.body, food.position)
                        score = 0
                        game_over = False
                        countdown_active = True
                        countdown_start_time = pygame.time.get_ticks()
                        last_move_time = pygame.time.get_ticks()
                        particles = []
                        screen_shake_intensity = 0
                        screen_shake_time = 0
                        score_flash_time = 0
                        screen_flash_time = 0
                        apples_collected = 0
                        active_powerups = []
                        powerup_selection_active = False
                        powerup_choices = []
                        selected_powerup_index = 0
                else:
                    # Handle direction changes
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
                    
                    # Handle powerup selection
                    if powerup_selection_active:
                        if event.key == pygame.K_LEFT:
                            selected_powerup_index = (selected_powerup_index - 1) % 3
                        elif event.key == pygame.K_RIGHT:
                            selected_powerup_index = (selected_powerup_index + 1) % 3
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            # Activate selected powerup
                            chosen_type = powerup_choices[selected_powerup_index]
                            new_powerup = Powerup(chosen_type)
                            new_powerup.activate(pygame.time.get_ticks())
                            active_powerups.append(new_powerup)
                            powerup_selection_active = False
                            powerup_choices = []
                            selected_powerup_index = 0
        
        if not game_over:
            current_time = pygame.time.get_ticks()
            
            # Handle countdown timer
            if countdown_active:
                time_since_countdown = current_time - countdown_start_time
                if time_since_countdown >= countdown_duration + go_duration:
                    countdown_active = False
                    last_move_time = current_time  # Reset move timer after countdown
            
            # Move snake based on timer, not frame rate (only if countdown finished)
            time_since_move = current_time - last_move_time
            
            # Apply speed boost if active
            current_move_delay = MOVE_DELAY
            for powerup in active_powerups:
                if powerup.type == Powerup.SPEED_BOOST and powerup.active:
                    current_move_delay = int(MOVE_DELAY * 0.5)  # 50% faster
            
            if not countdown_active and not powerup_selection_active and time_since_move >= current_move_delay:
                # Check if ghost mode is active (allows passing through self)
                ghost_mode_active = any(p.type == Powerup.GHOST_MODE and p.active for p in active_powerups)
                
                move_result = snake.move()
                collision_detected = False
                
                if not move_result:
                    collision_detected = True
                elif obstacle.check_collision(snake.body[0]):
                    collision_detected = True
                elif not ghost_mode_active and snake.check_self_collision():
                    collision_detected = True
                
                if collision_detected:
                    # Check if shield is active
                    shield_active = False
                    for powerup in active_powerups:
                        if powerup.type == Powerup.SHIELD and powerup.active:
                            shield_active = True
                            powerup.active = False  # Shield breaks
                            # Create shield break effect
                            head_x, head_y = snake.body[0]
                            head_pixel_x = head_x * CELL_SIZE + CELL_SIZE // 2
                            head_pixel_y = head_y * CELL_SIZE + CELL_SIZE // 2
                            for i in range(16):
                                angle = (i / 16) * 2 * math.pi
                                speed = 3 + random.uniform(0, 2)
                                vx = math.cos(angle) * speed
                                vy = math.sin(angle) * speed
                                particles.append(Particle(head_pixel_x, head_pixel_y, vx, vy, CYAN))
                            screen_shake_intensity = 10
                            screen_shake_time = current_time
                            break
                    
                    if not shield_active:
                        game_over = True
                        score_manager.update(score)
                else:
                    # Check food collision
                    if snake.body[0] == food.get_position():
                        # Spawn enhanced particle effect at food position
                        food_pixel_x = food.position[0] * CELL_SIZE + CELL_SIZE // 2
                        food_pixel_y = food.position[1] * CELL_SIZE + CELL_SIZE // 2
                        
                        # Check if double points is active
                        points_to_add = 10
                        for powerup in active_powerups:
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
                            particles.append(Particle(food_pixel_x, food_pixel_y, vx, vy, color))
                        
                        # Extra fast particles for emphasis
                        for i in range(8):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = 4 + random.uniform(0, 2)
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            particles.append(Particle(food_pixel_x, food_pixel_y, vx, vy, YELLOW))
                        
                        # Trigger screen shake
                        screen_shake_intensity = 8
                        screen_shake_time = current_time
                        
                        # Trigger score flash
                        score_flash_time = current_time
                        
                        # Trigger screen flash
                        screen_flash_time = current_time
                        
                        snake.grow()
                        score += points_to_add
                        food.spawn(snake.body + obstacle.positions)
                        apples_collected += 1
                        
                        # Trigger powerup selection every 3 apples
                        if apples_collected % 3 == 0 and not powerup_selection_active:
                            powerup_selection_active = True
                            # Generate 3 random powerup choices
                            all_types = [Powerup.SHIELD, Powerup.DOUBLE_POINTS, Powerup.GHOST_MODE, Powerup.SPEED_BOOST]
                            powerup_choices = random.sample(all_types, 3)
                            selected_powerup_index = 1  # Start with middle option selected
                
                # Reset interpolation after move
                snake.interpolation = 0.0
                last_move_time = current_time
            
            # Clean up expired powerups
            active_powerups = [p for p in active_powerups if not p.is_expired(current_time)]
            
            # Update screen shake
            if screen_shake_intensity > 0:
                time_since_shake = current_time - screen_shake_time
                if time_since_shake > 300:  # Shake lasts 300ms
                    screen_shake_intensity = 0
                else:
                    # Decay shake intensity
                    screen_shake_intensity = 8 * (1 - time_since_shake / 300)
        
        # Calculate screen shake offset
        shake_x = 0
        shake_y = 0
        if screen_shake_intensity > 0:
            shake_x = random.randint(-int(screen_shake_intensity), int(screen_shake_intensity))
            shake_y = random.randint(-int(screen_shake_intensity), int(screen_shake_intensity))
        
        # Drawing
        screen.fill(BLACK)
        
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
        particles = [p for p in particles if p.is_alive()]
        for particle in particles:
            particle.update()
            # Temporarily offset particle position for shake
            original_x, original_y = particle.x, particle.y
            particle.x += shake_x
            particle.y += shake_y
            particle.draw(screen)
            particle.x, particle.y = original_x, original_y
        
        # Draw obstacles
        obstacle.draw(screen)
        
        if not game_over:
            # Draw game elements
            food.draw(screen)
            snake.draw(screen)
            
            # Draw score with zoom effect in panel
            if score_flash_time > 0:
                time_since_flash = current_time - score_flash_time
                if time_since_flash < 300:  # Flash lasts 300ms
                    # Scale from 1.5 to 1.0
                    scale = 1.5 - (time_since_flash / 300) * 0.5
                    score_font_size = int(36 * scale)
                    score_font = pygame.font.Font(None, score_font_size)
                    score_text = score_font.render(f'Score: {score}', True, YELLOW)
                    score_rect = score_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 30))
                    screen.blit(score_text, score_rect)
                else:
                    score_text = font.render(f'Score: {score}', True, WHITE)
                    score_rect = score_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 30))
                    screen.blit(score_text, score_rect)
            else:
                score_text = font.render(f'Score: {score}', True, WHITE)
                score_rect = score_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 30))
                screen.blit(score_text, score_rect)
            
            # Draw high score in panel
            high_score_text = font.render(f'High Score: {score_manager.get_high_score()}', True, WHITE)
            high_score_rect = high_score_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 70))
            screen.blit(high_score_text, high_score_rect)
            
            # Draw active powerup indicators in panel
            if active_powerups:
                indicator_y = 120
                indicator_font = pygame.font.Font(None, 22)
                title_font = pygame.font.Font(None, 28)
                
                # Draw "Active Powerups" title
                title_text = title_font.render('Active Powerups', True, YELLOW)
                title_rect = title_text.get_rect(center=(GRID_WIDTH + PANEL_WIDTH // 2, 100))
                screen.blit(title_text, title_rect)
                
                for powerup in active_powerups:
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
            if screen_flash_time > 0:
                time_since_flash = current_time - screen_flash_time
                if time_since_flash < 150:  # Flash lasts 150ms
                    flash_alpha = int(80 * (1 - time_since_flash / 150))
                    flash_surface = pygame.Surface((GRID_WIDTH, HEIGHT), pygame.SRCALPHA)
                    flash_surface.fill((255, 255, 255, flash_alpha))
                    screen.blit(flash_surface, (0, 0))
            
            # Draw powerup selection screen (centered on grid)
            if powerup_selection_active:
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
                
                for i, powerup_type in enumerate(powerup_choices):
                    card_x = start_x + i * (card_width + card_spacing)
                    info = Powerup.INFO[powerup_type]
                    
                    # Card background with selection highlight
                    if i == selected_powerup_index:
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
                
                # Instructions
                instruction_font = pygame.font.Font(None, 28)
                instruction_text = instruction_font.render('Arrow Keys: Select  |  Enter/Space: Choose', True, WHITE)
                instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 60))
                screen.blit(instruction_text, instruction_rect)
            
            # Draw countdown if active
            if countdown_active:
                time_since_countdown = current_time - countdown_start_time
                
                # Semi-transparent overlay
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))  # Black with 150 alpha
                screen.blit(overlay, (0, 0))
                
                # Determine countdown number or "GO!"
                if time_since_countdown < countdown_duration:
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
                    go_progress = (time_since_countdown - countdown_duration) / go_duration
                    
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
            # Game over screen
            screen.fill(BLACK)
            
            # Draw panel background
            panel_rect = pygame.Rect(GRID_WIDTH, 0, PANEL_WIDTH, HEIGHT)
            pygame.draw.rect(screen, DARK_GRAY, panel_rect)
            pygame.draw.line(screen, WHITE, (GRID_WIDTH, 0), (GRID_WIDTH, HEIGHT), 2)
            
            game_over_text = font.render('Game Over!', True, RED)
            score_text = font.render(f'Final Score: {score}', True, WHITE)
            high_score_text = font.render(f'High Score: {score_manager.get_high_score()}', True, WHITE)
            restart_text = font.render('Press SPACE to restart', True, WHITE)
            
            screen.blit(game_over_text, (GRID_WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(score_text, (GRID_WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(high_score_text, (GRID_WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 20))
            screen.blit(restart_text, (GRID_WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == '__main__':
    main()
