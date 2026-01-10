# Snake Survivor

A modern, feature-rich take on the classic Snake game, built with Python and Pygame. This isn't just your standard snake game; it's an intense survival experience with strategic power-ups, challenging obstacles, and spectacular visual effects that create an engaging and addictive gameplay experience.

## Features

- **Dynamic Gameplay**: Navigate a 30x30 grid, avoiding not only yourself but also randomly placed obstacles.
- **Stunning Visuals**:
  - Smooth, interpolated snake movement with trail effects for fluid experience.
  - A vibrant 1024x600 window with a 424px side panel for comprehensive game stats.
  - "Hype Effects": Eating food triggers multi-layered particle bursts, expanding shockwave rings, screen shake, screen flashes, border pulse effects, and dramatic score animations.
  - Animated food with pulsing effects and professional sprite assets.
  - Snake trail effects that follow movement for enhanced visual feedback.
- **Power-Up System**: Collect 3 apples to pause the game and choose one of three randomly offered power-ups:
  - **🛡️ Shield**: Survive one fatal collision (wall, obstacle, or self) with dramatic shield break effects.
  - **2X Double Points**: The next 5 apples are worth double points with yellow particle effects.
  - **👻 Ghost Mode**: Pass through your own tail for 10 seconds (immune to self-collision).
  - **⚡ Speed Boost**: Move 50% faster for 15 seconds (100ms → 50ms move delay).
- **Enhanced Selection System**: 
  - Beautiful powerup cards with sprite icons and descriptions
  - Animated selection interface with pulsing effects
  - Strategic pause gameplay for tactical decision-making
  - Multiple simultaneous powerups supported
- **UI & Experience**:
  - Interactive title screen and detailed "Game Over" screen that identifies your cause of death.
  - Animated "3, 2, 1, GO!" countdown sequence to build anticipation.
  - Comprehensive side panel displaying score, high score, game timer, and active power-ups.
  - Active powerup indicators with countdown timers and use counters.
  - Dramatic visual effects including shockwave rings, screen shake, and border pulses.
  - Professional sprite assets with automatic fallbacks for missing files.
- **Persistent High Scores**: Your high score is saved in `high_score.json` to challenge you across sessions.

## Requirements

- Python 3.7+
- `pygame-ce`

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd snake-survivor
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows
    python -m venv .venv
    .venv\Scripts\activate
    
    # On macOS/Linux  
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies from `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Play

Run the game from the project's root directory:
```bash
python snake_game.py
```

## Building the Executable

You can create a standalone executable from the source code using PyInstaller.

1.  **Ensure PyInstaller is installed:**
    ```bash
    pip install pyinstaller
    ```

2.  **Build the executable:**
    Run PyInstaller from the project's root directory. You can use the provided `.spec` file for configuration:
    ```bash
    pyinstaller snake_game.spec
    ```
    Or, you can have PyInstaller generate a new spec file:
    ```bash
    pyinstaller snake_game.py --onefile --windowed
    ```

3.  **Run the executable:**
    The executable will be located in the `dist` directory.

### Controls
- **Arrow Keys**: Change the snake's direction with intelligent input queuing to prevent collision bugs.
- **Space Bar**: Restart the game after a "Game Over".
- **Power-up Selection** (every 3 apples):
  - **Left/Right Arrow Keys**: Navigate through the 3 powerup choices.
  - **Enter or Space**: Select the highlighted power-up and continue the game.

### Objective
- Eat the red food (apples) to grow your snake and increase your score.
- Every 3 food items, strategically choose a power-up to enhance your survival chances.
- Avoid colliding with the walls, your own tail (unless in Ghost Mode), and the gray obstacles.
- Survive as long as possible and set a new high score!
- Experience spectacular visual effects and smooth gameplay mechanics.

## License

This project is licensed under the MIT License.