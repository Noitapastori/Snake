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
- **Window Size**: 1024x600 pixels (600x600 grid + 424px side panel)
- **Coordinate System**: (0,0) at top-left, (29,29) at bottom-right
- **FPS**: 30 frames per second for smooth animations
- **Move Speed**: 10 cells per second (100ms between moves)

### Snake Mechanics
- **Initial Length**: 3 segments
- **Starting Position**: Center of grid (15, 15)
- **Starting Direction**: Up
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
- **Appearance**: Red apple sprite (20x20 pixels) with pulsing animation fallback to red rounded square
- **Sprite Asset**: `assets/sprites/apple.png` - scales to cell size with transparency support
- **Animation**: Continuous size pulse using sine wave (±3 pixels) for visual emphasis
- **Spawn Logic**: Random position on grid, avoiding snake body and obstacles
- **Collision**: Triggers when snake head occupies same cell as food
- **Effect**: +10 points (+20 with Double Points), snake grows by 1 segment, food respawns, triggers **DRAMATIC HYPE EFFECTS**:
  - Multi-layered particle burst (20+ particles with red/yellow/burst colors)
  - Expanding shockwave rings (50px radius, 600ms duration)
  - Screen shake (8 pixels, 300ms decay)
  - Screen flash (white, 150ms fade)
  - Border pulse effect (colored borders matching powerup state)
  - Score zoom animation with color highlights
  - Snake trail effects for enhanced motion visualization

### Obstacle System
- **Generation**: 15 obstacles are randomly generated at the start of each game
- **Appearance**: Rendered as gray, multi-cell blocks with 3D effect and dark borders
- **Placement**: Random positions avoiding grid edges and snake's starting area (16-20, 13-17)
- **Collision**: Fatal collision unless Shield powerup is active
- **Visual**: Gray blocks with black outlines, clearly distinguishable from other elements
- **Shield Interaction**: Shield can protect against obstacle collisions (but not self-collision in current build)

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

1. **Shield** (Cyan)
   - Effect: Survive one collision (wall, obstacle, or self)
   - Duration: One-time use
   - Visual: Cyan particle explosion when shield breaks
   - Feedback: Screen shake (15 pixels, 300ms) + "SHIELD USED!" text floats upward with cyan color and fade-out (1 second)

2. **Double Points** (Yellow)
   - Effect: Next 5 apples worth 20 points instead of 10
   - Duration: 5 apples
   - Visual: All-yellow particle burst on collection
   - Counter: Shows remaining apples in indicator

3. **Ghost Mode** (Purple)
   - Effect: Pass through own tail without dying (self-collision immunity)
   - Duration: 10 seconds
   - Visual: Purple-tinted powerup indicator with countdown timer
   - Sprite: `assets/sprites/ghost-mode.png` (60x60, scales to 32x32 for indicators)
   - Gameplay: Only wall and obstacle collisions are fatal during active period

4. **Speed Boost** (Orange)
   - Effect: 50% faster movement speed (100ms → 50ms move delay)
   - Duration: 15 seconds
   - Visual: Orange powerup indicator with countdown timer
   - Sprite: `assets/sprites/speed-boost.png` (60x60, scales to 32x32 for indicators)
   - Gameplay: Increased challenge due to faster movement, requires quicker reactions

**Selection UI:**
- Semi-transparent dark overlay (180 alpha) covering entire screen
- 3 animated cards (200x120px each) with powerup information
- Selected card pulses with white border and glow effect
- Each card shows:
  - Powerup icon (60x60 sprite, fallback to text icon)
  - Powerup name in large text
  - Brief description
  - Color-coded background matching powerup theme
- "Choose your powerup" header with instructions
- Arrow keys for navigation, Enter/Space to confirm
- Game pause during selection for strategic decision-making

**Active Powerup Indicators:**
- Display below high score in side panel
- Color-coded bars (240x60px) matching powerup type
- Show powerup icon (32x32 sprite) and name
- Timer for duration-based powerups or counter for use-based powerups
- Auto-cleanup when expired with smooth fade-out
- Multiple powerups can be active simultaneously
- Vertical stacking for multiple active effects

### Asset Specifications

**Required Sprites:**
- **Apple**: `assets/sprites/apple.png` (recommended 20x20px, auto-scales)
- **Shield Powerup**: `assets/sprites/shield.png` (60x60px base, scales to 32x32 for indicators)
- **Double Points Powerup**: `assets/sprites/double-points.png` (60x60px base, scales to 32x32)
- **Ghost Mode Powerup**: `assets/sprites/ghost-mode.png` (60x60px base, scales to 32x32)
- **Speed Boost Powerup**: `assets/sprites/speed-boost.png` (60x60px base, scales to 32x32)

**Sprite Requirements:**
- Format: PNG with alpha transparency support
- Base size: 60x60px for powerups (will be scaled for different uses)
- Error handling: Automatic fallback to text icons if sprites fail to load
- Validation: Size and format checking during load
- Caching: All sprites cached on first load for performance

## Visual Effects System

### Particle Effects
- **Food Collection**: Multi-layered particle bursts with red/yellow colors
- **Shield Break**: Cyan lightning particles with sparkle effects
- **Collision**: Dramatic particle explosions (40+ particles) with screen effects
- **Particle Types**: Circle, star (4-pointed), and lightning bolt shapes
- **Lifetime**: Variable duration (700-1200ms) with fade-out
- **Physics**: Realistic velocity and gravity simulation

### Screen Effects
- **Screen Shake**: Intensity-based camera shake (8-15 pixels) with natural decay
- **Screen Flash**: White flash overlay (150ms duration, alpha fade)
- **Border Pulse**: Colored screen border effects matching game events
- **Shockwave Rings**: Expanding rings from impact points (80px max radius)
- **Snake Trail**: Motion trail segments following snake movement

### Animation Systems
- **Food Pulse**: Continuous sine wave size animation (±3 pixels)
- **Card Selection**: Pulsing powerup cards with border effects
- **Death Animation**: Zoom and fade sequence (2.5 seconds total)
- **Shield Text**: "SHIELD USED!" floats upward with fade (1 second)
- **Score Highlights**: Zoom and color effects on score changes

### UI Animations
- **Countdown**: "3, 2, 1, GO!" sequence with scaling text
- **Powerup Cards**: Smooth pulsing selection indicators
- **Active Powerup Bars**: Color-coded progress bars with smooth updates
- **Game Over**: Dramatic zoom-to-black with fade transitions

## Visual Design

### Color Palette
- **Background**: Black (0, 0, 0)
- **Background Grid**: Dark Gray (20, 20, 20)
- **Snake Head**: Directional sprite graphic (base orientation: facing left)
- **Snake Body**: Green gradient (0, 255-100, 0) - fades from head to tail
- **Snake Outline**: Dark Green (0, 180, 0)
- **Food**: Apple sprite graphic with red color scheme fallback (255, 0, 0)
- **Particles**: Red and Yellow (255, 0, 0) / (255, 255, 0) with alpha fade
- **Text**: White (255, 255, 255) / Yellow (255, 255, 0) for score flash
- **Countdown**: White for numbers, Green for "GO!"
- **Powerups**: 
  - Shield: Cyan (0, 255, 255)
  - Double Points: Yellow (255, 255, 0)
  - Ghost Mode: Purple (128, 0, 255)
  - Speed Boost: Orange (255, 165, 0)

### Graphics Style
- **Snake Head**: Directional sprite graphic (20x20 pixels) from `assets/sprites/snake-head.png`
  - Rotates based on movement direction (LEFT=0°, DOWN=90°, RIGHT=180°, UP=270°)
  - Fallback to bright green rectangle with dark green outline if sprite unavailable
  - Smooth rotation caching for performance optimization
- **Snake Body**: Green gradient rectangles (255→100 brightness) with 4px rounded corners
  - Body segments maintain procedural rendering for visual consistency
  - Dark green outline (0, 180, 0) for definition
- **Food**: Apple sprite graphic with pulsing animation
  - Fallback to red rounded rectangle (4px corners) if sprite unavailable
  - Sprite caching system for scaled versions during pulse effect
- **Asset Management**: 
  - Error handling with graceful fallbacks to procedural graphics
  - Debug logging for sprite loading and cache performance
  - Sprite cache optimization (99%+ hit rate achieved)
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

### Sprite System Implementation
- **Asset Directory**: `assets/sprites/` contains all sprite files
- **Supported Formats**: PNG with alpha transparency preferred
- **Loading Strategy**: Sprites loaded at class initialization with error handling
- **Scaling**: All sprites scaled to CELL_SIZE (20x20 pixels) at load time
- **Rotation**: pygame.transform.rotate() for directional sprites
- **Caching Strategy**:
  - Apple sprites: Cache scaled versions for pulse animation sizes
  - Snake head: Cache all 4 rotational orientations (0°, 90°, 180°, 270°)
  - Cache size limits: 10 entries with FIFO cleanup
- **Performance Optimization**:
  - convert_alpha() for optimal blitting performance  
  - Cache hit rates exceed 99% for smooth gameplay
  - Real-time scaling only on cache misses
- **Error Handling & Fallbacks**:
  - FileNotFoundError: Falls back to procedural graphics
  - pygame.error: Falls back with debug logging
  - Invalid dimensions: Validates sprite before scaling
  - Graceful degradation maintains full game functionality
- **Debug Logging**: Comprehensive console output for troubleshooting sprite issues

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
- Render food on screen with pulse animation and sprite graphics
- Provide position for collision detection
- Manage sprite loading and caching system

**Key Methods:**
- `spawn(snake_body)`: Creates new random position
- `get_position()`: Returns current coordinates
- `load_sprite()`: Loads apple.png with error handling and fallbacks
- `get_cached_sprite()`: Returns cached scaled sprites for pulse animation
- `draw()`: Renders sprite or fallback rectangle with pulsing effect

**Sprite System:**
- Asset path: `assets/sprites/apple.png`
- Caching: Scaled versions for pulse sizes (-3 to +3 pixels)
- Performance: 99%+ cache hit rate for optimal rendering
- Fallback: Red rounded rectangle if sprite loading fails

### Snake Class (Extended)
**Sprite System Additions:**
- `load_sprites()`: Loads snake-head.png with comprehensive error handling
- `get_direction_angle()`: Converts direction tuples to rotation angles
- `get_rotated_head_sprite()`: Returns cached rotated head sprites
- **Rotation Mapping** (base sprite faces LEFT):
  - LEFT: 0° (base orientation)  
  - DOWN: 90° clockwise
  - RIGHT: 180°
  - UP: 270° clockwise
- **Performance**: Sprite rotation caching with cache size limits
- **Fallback**: Green rectangles if sprite system unavailable

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
- **Multiple Lives**: Allow limited number of collisions before game over
- **Pause Functionality**: Press P to pause/resume game
- **Special Food Types**: Different food varieties with varying point values and effects
- **Achievement System**: Unlock badges for reaching specific milestones

### Visual Enhancements
- ✅ **Background Grid**: Visual grid lines for better spatial awareness (IMPLEMENTED)
- ✅ **Particle Effects**: Visual feedback for eating food (IMPLEMENTED)
- ✅ **Snake Gradient**: Brighter head fading to darker tail (IMPLEMENTED) 
- ✅ **Rounded Corners**: Modern look for snake and food (IMPLEMENTED)
- ✅ **Food Animation**: Pulsing effect (IMPLEMENTED)
- ✅ **Smooth Movement**: Interpolation between cells for fluid motion (IMPLEMENTED)
- ✅ **Trail Effects**: Snake motion trail with segment tracking (IMPLEMENTED)
- **Snake Head Sprite**: Distinguish head from body with unique directional sprite
- **Environment Themes**: Different visual themes (forest, neon, retro)
- **Background Patterns**: Subtle animated backgrounds

### Audio
- **Sound Effects**: Eating food, collision, shield break, powerup selection
- **Background Music**: Dynamic looping tracks that respond to game state
- **Audio Feedback**: Directional audio cues for enhanced immersion

### Advanced Features
- **Multiple Difficulty Levels**: Easy/Medium/Hard with different speeds and obstacle counts
- **Leaderboard System**: Top 10 scores with player names and timestamps
- **Statistics Dashboard**: Games played, average score, survival time analytics
- **Customization Options**: User-selectable snake colors and trail effects
- **Two-Player Mode**: Competitive split-screen gameplay
- **Settings Menu**: Configure controls, audio, visual effects intensity
- **Replay System**: Save and replay notable games
- **Online Features**: Global leaderboards and shared replays* - Recent Updates
- **Fixed rapid input bug**: Implemented direction input queue system
  - Prevents input loss when player taps arrow keys faster than game move speed
  - Buffers up to 1 queued direction change for responsive classic snake feel
  - Solves the "tapping arrows too fast causes false collisions" issue
  
- **Added shield usage feedback**: Visual indicator when shield is consumed
  - Floating "SHIELD USED!" text in cyan color
  - Floats upward from center of game grid with smooth fade-out (1 second duration)
  - Combined with existing cyan particle burst and screen shake for dramatic effect
  
- **Implemented cinematic death animation**: Professional game-over sequence
  - 2.5 second total animation with three distinct phases
  - Dramatic particle explosion (40+ particles) at collision point
  - Smooth 3x zoom centered on collision with professional easing
  - Fade to black transition leading to game over screen
  - Enhanced screen shake (15 pixels) for maximum impact

## Change Log

### January 10, 2026 - Complete Feature Implementation
- **Professional Visual Effects System**: 
  - Multi-layered particle system with circles, stars, and lightning shapes (20-40+ particles per event)
  - Expanding shockwave rings from impact points (80px max radius, 600ms duration)
  - Screen shake with natural decay and variable intensity (8-15 pixels)
  - Screen flash effects (white overlay, 150ms fade with alpha blending)
  - Border pulse effects with color-coded themes matching game events
  - Snake trail system with 8-segment trailing effect for enhanced motion visualization
  - Professional sprite management with error handling and fallbacks

- **Enhanced Snake Mechanics**:
  - Smooth interpolated movement between cells (30 FPS rendering, timer-based movement)
  - Intelligent input queue system preventing rapid-input collision bugs
  - Direction change buffering (max 1 queued input) for responsive controls
  - 180-degree turn blocking to prevent instant self-collision

- **Complete 4-Powerup System**:
  - **Shield**: One-time collision immunity with dramatic cyan break effects and floating "SHIELD USED!" text
  - **Double Points**: 5 apples worth 20 points each with yellow particle themes
  - **Ghost Mode**: 10-second self-collision immunity with purple visual theme
  - **Speed Boost**: 50% movement speed increase (100ms → 50ms) for 15 seconds with orange theme

- **Advanced Selection Interface**:
  - Animated powerup cards (200x120px) with professional styling
  - Sprite icons with automatic text fallbacks
  - Pulsing selection effects and smooth navigation
  - Strategic game pause for tactical decision-making

- **Comprehensive UI System**:
  - 1024x600 window with 424px information panel
  - Active powerup indicators with countdown timers and use counters
  - Multiple simultaneous powerups with vertical stacking
  - Professional typography and color schemes

- **Cinematic Death Animation**:
  - Death reason identification and display
  - 2.5-second zoom-and-fade sequence with particle explosions
  - Enhanced collision detection with shield interaction
  - Massive screen shake (15 pixels) for collision impact

- **Asset Management System**:
  - Complete sprite loading with validation and caching
  - Apple and all powerup sprites (60x60 base, auto-scaled)
  - Graceful degradation to text icons when files missing
  - Performance optimization with memory-efficient caching
