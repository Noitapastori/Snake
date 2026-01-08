# Snake Survivor

A modern, feature-rich take on the classic Snake game, built with Python and Pygame. This isn't just your standard snake game; it's a battle for survival with power-ups, obstacles, and dazzling visual effects.

## Features

- **Dynamic Gameplay**: Navigate a 30x30 grid, avoiding not only yourself but also randomly placed obstacles.
- **Stunning Visuals**:
  - Smooth, interpolated snake movement for a fluid experience.
  - A vibrant 800x600 window, including a 200px side panel for all your stats.
  - "Hype Effects": Eating food triggers particle bursts, screen shake, screen flashes, and score animations.
  - Animated food and power-up indicators.
- **Power-Up System**: Collect 3 apples to pause the game and choose one of three randomly offered power-ups:
  - **🛡️ Shield**: Survive one fatal collision (wall, obstacle, or self).
  - **2X Double Points**: The next 5 apples are worth double points.
  - **👻 Ghost Mode**: Pass through your own tail for 10 seconds.
  - **⚡ Speed Boost**: Move 50% faster for 15 seconds.
- **UI & Experience**:
  - An interactive title screen and a "Game Over" screen that tells you how you met your end.
  - An animated "3, 2, 1, GO!" countdown to start the action.
  - A dedicated side panel that displays your score, high score, game timer, and currently active power-ups.
- **Persistent High Scores**: Your high score is saved in `high_score.json` to challenge you across sessions.

## Requirements

- Python 3.7+
- `pygame-ce`

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd python-game-test
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Install dependencies from `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Play

You can run the game in two ways:

### From the Executable (Windows)
If you have the `dist` folder, you can run the game directly without any installation.
1.  Navigate into the `dist/snake_game` directory.
2.  Double-click `snake_game.exe` to start the game.

### From Source
After following the installation steps, run the game from the project's root directory:
```bash
python snake_game.py
```

### Controls
- **Arrow Keys**: Change the snake's direction.
- **Space Bar**: Restart the game after a "Game Over".
- **Power-up Selection**:
  - **Left/Right Arrow Keys**: Navigate the power-up choices.
  - **Enter or Space**: Select the highlighted power-up.

### Objective
- Eat the red food to grow your snake and increase your score.
- Every 3 food items, choose a strategic power-up to enhance your survival.
- Avoid colliding with the walls, your own tail (unless in Ghost Mode), and the gray obstacles.
- Survive as long as you can and set a new high score!

## License

This project is licensed under the MIT License.