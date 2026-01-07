import pygame
import random
import json
import os
import math

# Constants
GRID_SIZE = 30
CELL_SIZE = 20
WIDTH = GRID_SIZE * CELL_SIZE  # 600
HEIGHT = GRID_SIZE * CELL_SIZE  # 600
FPS = 30
MOVE_DELAY = 100  # milliseconds between moves (10 moves/second)

# Colors (R, G, B)
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 20)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

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
        self.glow_pulse = 0
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


def draw_glow(screen, center_x, center_y, pulse_value, base_radius=60):
    """Draw a pulsing radial glow effect centered on position"""
    # Pulse between 0.8 and 1.2 of base radius
    current_radius = int(base_radius * (1.0 + 0.1 * math.sin(pulse_value)))
    
    # Create transparent surface for glow
    glow_surface = pygame.Surface((current_radius*2, current_radius*2), pygame.SRCALPHA)
    
    # Draw concentric circles with decreasing alpha for smooth gradient
    for radius in range(current_radius, 0, -3):
        # Quadratic falloff for more natural light distribution
        # Alpha fades from ~60 at center to 0 at edge
        alpha = int(60 * ((radius / current_radius) ** 2))
        pygame.draw.circle(glow_surface, (255, 255, 255, alpha), 
                          (current_radius, current_radius), radius)
    
    # Blit with normal alpha blending (not additive)
    screen.blit(glow_surface, 
                (center_x - current_radius, center_y - current_radius))


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
    
    # Game state
    score = 0
    game_over = False
    running = True
    last_move_time = pygame.time.get_ticks()
    particles = []
    
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
                        score = 0
                        game_over = False
                        last_move_time = pygame.time.get_ticks()
                        particles = []
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
        
        if not game_over:
            # Move snake based on timer, not frame rate
            current_time = pygame.time.get_ticks()
            time_since_move = current_time - last_move_time
            
            # Update interpolation for smooth rendering
            snake.update_interpolation(time_since_move / MOVE_DELAY)
            
            if time_since_move >= MOVE_DELAY:
                if not snake.move():
                    game_over = True
                    score_manager.update(score)
                else:
                    # Check food collision
                    if snake.body[0] == food.get_position():
                        # Spawn particle effect at food position
                        food_pixel_x = food.position[0] * CELL_SIZE + CELL_SIZE // 2
                        food_pixel_y = food.position[1] * CELL_SIZE + CELL_SIZE // 2
                        for i in range(12):
                            angle = (i / 12) * 2 * math.pi
                            speed = 2
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            particles.append(Particle(food_pixel_x, food_pixel_y, vx, vy, RED))
                        
                        snake.grow()
                        score += 10
                        food.spawn(snake.body)
                
                # Reset interpolation after move
                snake.interpolation = 0.0
                last_move_time = current_time
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw background grid
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, DARK_GRAY, (0, y), (WIDTH, y))
        
        # Update and draw particles
        particles = [p for p in particles if p.is_alive()]
        for particle in particles:
            particle.update()
            particle.draw(screen)
        
        if not game_over:
            # Update glow pulse animation
            snake.glow_pulse += 0.05
            
            # Draw glow effect from snake head
            head_x, head_y = snake.body[0]
            head_pixel_x = head_x * CELL_SIZE + CELL_SIZE // 2
            head_pixel_y = head_y * CELL_SIZE + CELL_SIZE // 2
            draw_glow(screen, head_pixel_x, head_pixel_y, snake.glow_pulse)
            
            # Draw game elements
            food.draw(screen)
            snake.draw(screen)
            
            # Draw score
            score_text = font.render(f'Score: {score}', True, WHITE)
            screen.blit(score_text, (10, 10))
            
            # Draw high score
            high_score_text = font.render(f'High Score: {score_manager.get_high_score()}', True, WHITE)
            screen.blit(high_score_text, (10, 50))
        else:
            # Game over screen
            game_over_text = font.render('Game Over!', True, WHITE)
            score_text = font.render(f'Score: {score}', True, WHITE)
            high_score_text = font.render(f'High Score: {score_manager.get_high_score()}', True, WHITE)
            restart_text = font.render('Press SPACE to restart', True, WHITE)
            
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 20))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == '__main__':
    main()
