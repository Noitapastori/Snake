gi# Snake Survivor - Game Design Document

## Overview

A classic Snake game implemented in Python using Pygame, enhanced with modern features like power-ups, obstacles, and visual effects. The player controls a snake that grows longer as it consumes food, with the objective of achieving the highest score possible without colliding with walls, obstacles, or itself.

## Core Gameplay

### Objective
- Control the snake to eat food and grow longer
- Achieve the highest score possible
- Avoid colliding with walls or the snake's own body

### Controls
- **Arrow Keys**: Change snake direction (Up, Down, Left, Right)
  - *Note: Rapid inputs are queued - press multiple directions in quick succession to chain direction changes*
- **Space Bar**: Restart game after game over
- **Powerup Selection** (every 3 apples):
  - Left/Right Arrow Keys: Navigate powerup options
  - Enter or Space: Select powerup

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
- **Window Size**: 800x600 pixels (600x600 grid + 200px side panel)
- **Coordinate System**: (0,0) at top-left, (29,29) at bottom-right

### Snake Mechanics
- **Initial Length**: 3 segments
- **Starting Position**: Center of grid (15, 15)
- **Starting Direction**: Right
- **Movement Speed**: 10 cells per second (100ms per move)
- **Rendering**: 30 FPS for smooth animations
- **Movement Logic**: Timer-based (decoupled from frame rate)
- **Growth**: Snake grows by 1 segment when food is consumed
- **Direction Changes**: 
  - 180-degree turns are blocked to prevent instant self-collision
  - **Input Queue System**: Rapid arrow key presses are buffered (max 1 input queued)
  - Intermediate direction changes are executed sequentially, solving the "fast input collision" bug
  - Prevents input loss when player taps arrows faster than move speed

### Food System
- **Appearance**: Red rounded square (20x20 pixels) with pulsing animation
- **Animation**: Continuous size pulse using sine wave (±3 pixels)
- **Spawn Logic**: Random position on grid, avoiding snake body and obstacles
- **Collision**: Triggers when snake head occupies same cell as food
- **Effect**: +10 points, snake grows by 1 segment, food respawns, triggers **HYPE EFFECTS**:
  - Enhanced particle burst (28 particles: red + yellow mix)
  - Screen shake (8 pixels, 300ms decay)
  - Screen flash (white, 150ms fade)
  - Score zoom animation (1.5x to 1.0x scale with yellow highlight)

### Obstacle System
- **Generation**: 15 obstacles are randomly generated at the start of each game.
- **Appearance**: Rendered as gray, multi-cell blocks with a 3D effect.
- **Placement**: Obstacles are placed randomly, avoiding the edges and the snake's initial path to ensure a fair start.
- **Collision**: Colliding with an obstacle ends the game, unless the Shield power-up is active.

### Collision Detection
- **Wall Collision**: Snake head moves outside grid bounds (x < 0, x >= 30, y < 0, y >= 30)
- **Self Collision**: Snake head occupies same cell as any body segment
- **Food Collision**: Snake head coordinates match food coordinates

### Scoring System
- **Points Per Food**: 10 points (20 with Double Points powerup)
- **High Score**: Persistent across game sessions, stored in JSON file
- **Display**: Current score and high score shown during gameplay
- **Powerup Trigger**: Every 3 apples collected unlocks a powerup selection

### Powerup System

**Trigger Mechanism:**
- Every 3 apples collected pauses the game
- Player presented with 3 random powerup options
- Game remains paused until selection is made
- Selected powerup activates immediately

**Available Powerups:**

1. **Feedback: Screen shake (15 pixels, 300ms) + "SHIELD USED!" text floats upward with cyan color and fade-out (1 second)
   - Effect: Survive one collision (wall, obstacle, or self)
   - Duration: One-time use
   - Visual: Cyan particle explosion when shield breaks
   - Activation: Creates intense screen shake on break

2. **Double Points** (Yellow)
   - Effect: Next 5 apples worth 20 points instead of 10
   - Duration: 5 apples
   - Visual: All-yellow particle burst on collection
   - Counter: Shows remaining apples in indicator

3. **Ghost Mode** (Purple)
   - Effect: Pass through own tail without dying
   - Duration: 10 seconds
   - Visual: Purple-tinted powerup indicator
   - Gameplay: Only wall and obstacle collisions are fatal

4. **Speed Boost** (Orange)
   - Effect: 50% faster movement speed
   - Duration: 15 seconds
   - Visual: Orange powerup indicator with countdown
   - Gameplay: Move delay reduced from 100ms to 50ms

**Selection UI:**
- Semi-transparent dark overlay (180 alpha)
- 3 animated cards with powerup information
- Selected card pulses with white border
- Each card shows:
  - Powerup icon (emoji or text symbol)
  - Powerup name
  - Brief description
  - Color-coded background
- Instructions displayed at bottom
- Arrow keys for navigation, Enter/Space to confirm

**Active Powerup Indicators:**
- Display below high score (top-left area)
- Color-coded bars matching powerup type
- Show powerup icon and name
- Timer or counter for remaining duration/uses
- Auto-cleanup when expired
- Multiple powerups can be active simultaneously

## Visual Design

### Color Palette
- **Background**: Black (0, 0, 0)
- **Background Grid**: Dark Gray (20, 20, 20)
- **Snake Body**: Green gradient (0, 255-100, 0) - fades from head to tail
- **Snake Outline**: Dark Green (0, 180, 0)
- **Food**: Red (255, 0, 0)
- **Particles**: Red and Yellow (255, 0, 0) / (255, 255, 0) with alpha fade
- **Text**: White (255, 255, 255) / Yellow (255, 255, 0) for score flash
- **Countdown**: White for numbers, Green for "GO!"
- **Powerups**: 
  - Shield: Cyan (0, 255, 255)
  - Double Points: Yellow (255, 255, 0)
  - Ghost Mode: Purple (128, 0, 255)
  - Speed Boost: Orange (255, 165, 0)

### Graphics Style
- **Snake**: Gradient effect from bright green head to darker tail, 4px rounded corners, dark green outline
- **Food**: Pulsing animation, 4px rounded corners
- **Background**: Subtle grid lines for spatial awareness
- **Particles**: Fading circles with alpha transparency

### UI Elements
- **Score Display**: Top-left corner, shows "Score: X"
  - Animates with zoom effect (yellow, 1.5x scale) when collecting food
- **High Score Display**: Below score, shows "High Score: X"
- **Powerup Indicators**: Below high score, shows active powerups with timers/counters
- **Font**: Default system font, 36pt (24pt for powerup indicators)
- **Game Over Screen**: Centered display showing:
  - "Game Over!" message
  - Final score
  - High score
  - "Press SPACE to restart" instruction
- **Powerup Selection Screen**: Full-screen overlay with 3 animated cards

## Game Feel & Juice

### Countdown System
- **Duration**: 3 seconds (3, 2, 1) + 0.5 seconds (GO!)
- **Numbers (3, 2, 1)**:
  - Zoom in from 150% to 100% scale over 0.3 seconds
  - Bounce effect (±10% scale) for 0.1 seconds
  - Rotation wobble (±5°) during zoom phase
  - White text with glow effect
- **"GO!" Text**:
  - Explosive zoom from 50% to 130% then settle to 120%
  - Half rotation spin (180°) during animation
  - Green color with enhanced glow
  - Creates anticipation and excitement before gameplay

### Food Collection Effects (HYPE!)
When the player collects food, multiple simultaneous effects create a satisfying, juicy experience:

1. **Enhanced Particle Burst** (28 particles total)
   - 20 particles in circular pattern with variable speeds (2±1 pixels/frame)
   - 8 fast particles (4-6 pixels/frame) for extra emphasis
   - Red and yellow color mix (2:1 ratio)
   - Particles fade out over 600ms, shrink to 50% size

2. **Screen Shake**
   - 8 pixel intensity at peak
   - Smooth decay over 300ms
   - Random directional offset each frame
   - Affects all visual elements (grid, particles, game objects)

3. **Screen Flash**
   - White overlay flash
   - 80 alpha at peak
   - Fades to transparent over 150ms
   - Creates visual pop on collection

4. **Score Zoom Animation**
   - Score text scales from 1.5x to 1.0x over 300ms
   - Color changes to yellow during animation
   - Returns to white after animation completes
   - Draws player attention to score increase

**Design Philosophy**: These effects combine to create a powerful moment of feedback that makes every food collection feel impactful and rewarding, encouraging continued play and creating satisfying game feel.

## Game States

### Playing State
- Snake moves automatically
- Player can change direction
- Score increments when food is eaten
- Transitions to Game Over state on collision

### Game Over State
- **Death Animation** (2.5 seconds):
  - **Phase 1 (0-500ms)**: Collision moment frozen with dramatic particle burst
    - 40 fast particles in ring pattern (red, orange, yellow, white colors)
    - 20 slow red particles for depth effect
    - Massive screen shake (15 pixel intensity) creates impact
  - **Phase 2 (500-2000ms)**: Smooth zoom from 1x to 3x scale (ease-in curve)
    - Camera centers on snake head collision point
    - All game elements (snake, obstacles, food, particles) scale and pan smoothly
    - Creates cinematic "slow-motion replay" of collision
  - **Phase 3 (2000-2500ms)**: Hold at 3x zoom + fade to black
    - Black overlay gradually covers screen (500ms fade)
    - Builds tension before showing game over screen
- **Game Over Screen** (displays after animation):
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
- **Alpha Blending**: Per-pixel alpha for smooth particle fade and screen flash
- **Screen Shake**: Dynamic offset applied to all visual elements
- **Animation Updates**: Food pulse, particles, score zoom, and shake update every frame
- **Draw Order**: Grid (shaken) → Particles (shaken) → Obstacles → Food → Snake → UI → Flash Overlay
- **Hype System**: Coordinated timing of multiple effects for maximum impact

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
- 28 particles spawn in enhanced burst when food is eaten (20 standard + 8 fast)
- Standard particles: 2±1 pixels/frame with red/yellow color mix
- Fast particles: 4-6 pixels/frame in yellow
- Particles fade out over 600ms
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

### Powerup Class
**Responsibilities:**
- Define powerup types and metadata
- Track powerup activation state
- Manage duration/use counters
- Check expiration conditions

**Key Methods:**
- `activate(current_time)`: Activates the powerup and starts timer
- `is_expired(current_time)`: Returns True if powerup has expired
- `get_remaining_time(current_time)`: Returns remaining seconds for duration-based powerups

**Powerup Types:**
- `SHIELD`: One-time collision protection
- `DOUBLE_POINTS`: 2x score for 5 apples
- `GHOST_MODE`: Pass through self for 10 seconds
- `SPEED_BOOST`: 50% faster movement for 15 seconds

**Metadata:**
- Each powerup has name, description, color, duration, and icon
- Stored in INFO dictionary for easy access
- Used for rendering selection cards and active indicators

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
- **Leaderboard* - Recent Updates
- **Fixed rapid input bug**: Implemented direction input queue system
  - Prevents input loss when player taps arrow keys faster than game move speed
  - Buffers up to 1 queued direction change for responsive classic snake feel
  - Solves the "tapping arrows too fast causes false collisions" issue
  
- **Added shield usage feedback**: Visual indicator when shield is consumed
  - Floating "SHIELD USED!" text in cyan color
  - Floats upward from center of game grid with smooth fade-out (1 second duration)
  - Combined with existing cyan particle burst and screen shake for dramatic effect
  
- **Implemented death camera animation**: Cinematic slow-motion zoom on collision
  - 2.5 second total animation sequence
  - Phase 1 (0-500ms): Dramatic particle explosion (40 fast + 20 slow particles in red/orange/yellow/white)
  - Phase 2 (500-2000ms): Smooth 3x zoom centered on collision point with ease-in easing
  - Phase 3 (2000-2500ms): Hold zoom + fade to black for dramatic effect
  - Shows exact point of collision before transitioning to game over screen
  - Massive screen shake (15 pixels) at collision moment for impact

### January 2026 - Previous Updates*: Top 10 scores instead of single high score
- **Statistics**: Games played, average score, total food eaten
- **Customization**: User-selectable colors and themes
- **Multiplayer**: Two-player mode with separate snakes

### Technical Improvements
- **Settings Menu**: Configure speed, colors, controls
- **Replay System**: Save and watch previous games
- **Mobile Controls**: Touch/swipe support for mobile devices
- **Achievements**: Unlock badges for milestones

## Change Log

### January 2026
- **Removed radial light effect**: Removed the pulsing white glow that appeared around the snake's head for a cleaner visual aesthetic
- **Added dynamic countdown system**: Implemented animated countdown (3, 2, 1, GO!) with zoom, rotation, and bounce effects to build anticipation
- **Enhanced food collection feedback**: Added comprehensive "juice" system with:
  - Screen shake (8px, 300ms decay)
  - Enhanced particle burst (28 particles with red/yellow mix)
  - Screen flash effect (white overlay, 150ms fade)
  - Score zoom animation (1.5x scale with yellow highlight)
- **Improved game feel**: All effects work together to create satisfying, impactful moments that reward player actions and increase engagement
- **Implemented powerup system**: Added strategic depth with 4 unique powerups:
  - Shield: One-time collision protection with dramatic break effect
  - Double Points: 2x score for next 5 apples with all-yellow particles
  - Ghost Mode: Pass through own tail for 10 seconds
  - Speed Boost: 50% faster movement for 15 seconds
- **Added powerup selection UI**: Every 3 apples triggers animated selection screen with:
  - 3 random powerup cards with pulsing animations
  - Arrow key navigation and Enter/Space selection
  - Color-coded cards with icons, names, and descriptions
  - Game pause during selection for strategic decision-making
- **Active powerup indicators**: Visual feedback system showing:
  - Color-coded bars with powerup information
  - Countdown timers for duration-based powerups
  - Use counters for consumable powerups
  - Multiple simultaneous powerup support
