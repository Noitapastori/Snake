import pygame
import random
import json
import os

# Constants
GRID_SIZE = 30
CELL_SIZE = 20
WIDTH = GRID_SIZE * CELL_SIZE  # 600
HEIGHT = GRID_SIZE * CELL_SIZE  # 600
FPS = 10

# Colors (R, G, B)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
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
    
    def draw(self, screen):
        for segment in self.body:
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GREEN, rect)


class Food:
    def __init__(self):
        self.position = (0, 0)
    
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
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, rect)


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
            # Move snake
            if not snake.move():
                game_over = True
                score_manager.update(score)
            else:
                # Check food collision
                if snake.body[0] == food.get_position():
                    snake.grow()
                    score += 10
                    food.spawn(snake.body)
        
        # Drawing
        screen.fill(BLACK)
        
        if not game_over:
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
