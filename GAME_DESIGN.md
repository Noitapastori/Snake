gi# Snake Game - Game Design Document

## Overview

A classic Snake game implemented in Python using Pygame. The player controls a snake that grows longer as it consumes food, with the objective of achieving the highest score possible without colliding with walls or itself.

## Core Gameplay

### Objective
- Control the snake to eat food and grow longer
- Achieve the highest score possible
- Avoid colliding with walls or the snake's own body

### Controls
- **Arrow Keys**: Change snake direction (Up, Down, Left, Right)
- **Space Bar**: Restart game after game over

### Game Loop
1. Snake moves continuously in its current direction
2. Player inputs direction changes via arrow keys
3. Snake attempts to move one cell in the current direction each frame
4. Collision detection checks for food, walls, and self-collision
5. Score updates and food respawns when consumed
6. Game ends on collision, displaying game over screen

## Technical Specifications

### Grid System
- **Grid Size**: 30x30 cells
- **Cell Size**: 20x20 pixels
- **Window Size**: 600x600 pixels
- **Coordinate System**: (0,0) at top-left, (29,29) at bottom-right

### Snake Mechanics
- **Initial Length**: 3 segments
- **Starting Position**: Center of grid (15, 15)
- **Starting Direction**: Right
- **Movement Speed**: 10 cells per second (100ms per move)
- **Rendering**: 30 FPS for smooth animations
- **Movement Logic**: Timer-based (decoupled from frame rate)
- **Growth**: Snake grows by 1 segment when food is consumed
- **Direction Changes**: 180-degree turns are blocked to prevent instant self-collision

### Food System
- **Appearance**: Red rounded square (20x20 pixels) with pulsing animation
- **Animation**: Continuous size pulse using sine wave (±3 pixels)
- **Spawn Logic**: Random position on grid, avoiding snake body
- **Collision**: Triggers when snake head occupies same cell as food
- **Effect**: +10 points, snake grows by 1 segment, food respawns, particle burst spawns

### Collision Detection
- **Wall Collision**: Snake head moves outside grid bounds (x < 0, x >= 30, y < 0, y >= 30)
- **Self Collision**: Snake head occupies same cell as any body segment
- **Food Collision**: Snake head coordinates match food coordinates

### Scoring System
- **Points Per Food**: 10 points
- **High Score**: Persistent across game sessions, stored in JSON file
- **Display**: Current score and high score shown during gameplay

## Visual Design

### Color Palette
- **Background**: Black (0, 0, 0)
- **Background Grid**: Dark Gray (20, 20, 20)
- **Snake Body**: Green gradient (0, 255-100, 0) - fades from head to tail
- **Snake Outline**: Dark Green (0, 180, 0)
- **Food**: Red (255, 0, 0)
- **Particles**: Red (255, 0, 0) with alpha fade
- **Text**: White (255, 255, 255)

### Graphics Style
- **Snake**: Gradient effect from bright green head to darker tail, 4px rounded corners, dark green outline
- **Food**: Pulsing animation, 4px rounded corners
- **Background**: Subtle grid lines for spatial awareness
- **Particles**: Fading circles with alpha transparency

### UI Elements
- **Score Display**: Top-left corner, shows "Score: X"
- **High Score Display**: Below score, shows "High Score: X"
- **Font**: Default system font, 36pt
- **Game Over Screen**: Centered display showing:
  - "Game Over!" message
  - Final score
  - High score
  - "Press SPACE to restart" instruction

## Game States

### Playing State
- Snake moves automatically
- Player can change direction
- Score increments when food is eaten
- Transitions to Game Over state on collision

### Game Over State
- All movement stops
- Displays end game information
- High score is saved if current score exceeds it
- Player can restart by pressing Space

## Performance & Rendering

### Frame Rate Architecture
- **Display FPS**: 30 frames per second for smooth visual updates
- **Game Logic**: Timer-based movement (100ms intervals)
- **Benefit**: Consistent gameplay speed with smoother animations and particle effects
- **Implementation**: `pygame.time.get_ticks()` for timing, `clock.tick(30)` for frame limiting

### Visual Effects Rendering
- **Particle System**: Dynamic list, auto-cleanup of expired particles
- **Alpha Blending**: Per-pixel alpha for smooth particle fade
- **Animation Updates**: Food pulse and particles update every frame
- **Draw Order**: Grid → Particles → Food → Snake → UI

## Data Persistence

### High Score Storage
- **File**: `high_score.json`
- **Location**: Same directory as game executable
- **Format**: JSON with single key-value pair `{"high_score": <integer>}`
- **Behavior**: 
  - Loads on game start (defaults to 0 if file missing)
  - Saves only when new high score is achieved
  - Persists across game sessions

## Classes and Architecture

### Snake Class
**Responsibilities:**
- Manage snake body (list of coordinate tuples)
- Handle movement and direction changes
- Detect collisions with walls and self
- Manage growth when food is consumed

**Key Methods:**
- `move()`: Updates position, returns False on collision
- `grow()`: Flags next move to add segment
- `change_direction()`: Updates direction with 180° prevention
- `draw()`: Renders snake to screen

### Food Class
**Responsibilities:**
- Generate random food positions
- Avoid spawning on snake body
- Render food on screen with pulse animation
- Provide position for collision detection

**Key Methods:**
- `spawn(snake_body)`: Creates new random position
- `get_position()`: Returns current coordinates
- `draw()`: Renders pulsing food to screen

### Particle Class
**Responsibilities:**
- Create visual feedback when food is eaten
- Manage particle lifetime and animation
- Render fading, shrinking particles

**Key Methods:**
- `update()`: Updates particle position based on velocity
- `is_alive()`: Returns True if particle hasn't exceeded lifetime
- `draw()`: Renders particle with alpha fade and size reduction

**Behavior:**
- 12 particles spawn radially when food is eaten
- Each particle moves outward at 2 pixels/frame
- Particles fade out over 500ms
- Particles shrink to 50% of original size (5px radius)
- Auto-cleanup when expired

### HighScoreManager Class
**Responsibilities:**
- Load high score from file
- Save high score to file
- Update high score when exceeded

**Key Methods:**
- `load()`: Reads from JSON file with error handling
- `save()`: Writes score to JSON file
- `update()`: Saves if current score is new high score
- `get_high_score()`: Returns current high score value

## Future Enhancement Ideas

### Gameplay Enhancements
- **Progressive Difficulty**: Increase speed as score increases
- **Power-ups**: Special food items with unique effects
- **Obstacles**: Static barriers to navigate around
- **Multiple Lives**: Allow limited number of collisions
- **Pause Functionality**: Press P to pause/resume game

### Visual Enhancements
- ✅ **Background Grid**: Visual grid lines for better spatial awareness (IMPLEMENTED)
- ✅ **Particle Effects**: Visual feedback for eating food (IMPLEMENTED)
- ✅ **Snake Gradient**: Brighter head fading to darker tail (IMPLEMENTED)
- ✅ **Rounded Corners**: Modern look for snake and food (IMPLEMENTED)
- ✅ **Food Animation**: Pulsing effect (IMPLEMENTED)
- **Snake Head Sprite**: Distinguish head from body with unique shape
- **Food Variations**: Different food types with different point values
- **Smooth Movement**: Interpolation between cells for fluid motion
- **Trail Effects**: Subtle motion blur or ghost trail

### Audio
- **Sound Effects**: Eating food, collision, game over
- **Background Music**: Looping ambient track

### Features
- **Multiple Difficulty Levels**: Easy/Medium/Hard with different speeds
- **Leaderboard**: Top 10 scores instead of single high score
- **Statistics**: Games played, average score, total food eaten
- **Customization**: User-selectable colors and themes
- **Multiplayer**: Two-player mode with separate snakes

### Technical Improvements
- **Settings Menu**: Configure speed, colors, controls
- **Replay System**: Save and watch previous games
- **Mobile Controls**: Touch/swipe support for mobile devices
- **Achievements**: Unlock badges for milestones
