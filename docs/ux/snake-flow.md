# Flow Spec (Figma-Ready) — Arcade Snake

## Primary UX Goal
Keep players in a fast restart loop with high-impact feedback, while preventing mode/controls confusion during powerup selection.

## Global UX Rules
- **Controls are mode-specific**: Selection overlays capture input; steering is disabled while selecting.
- **Feedback never hides state**: Effects amplify events but do not obscure snake head or collision boundaries.
- **UI stability**: Score/high score/powerups stay in fixed positions; no layout shifts.

## States & Screens

### 1) Countdown State
**Entry**: New game start or restart
- **On-screen**: Large countdown (3,2,1) then “GO”
- **Interaction**: No steering until “GO” completes (or allow steering but don’t move until start—pick one and be consistent)
- **Exit**: Transition to Playing

### 2) Playing State
**On-screen**:
- Playfield (grid, snake, food, obstacles)
- Right panel: Score, High Score, Active Powerups

**Interactions**:
- Arrow keys: change direction (no 180-degree reversal)

**System feedback**:
- Food eaten: particles + shake + flash + score pop (short-lived)
- Powerup active: persistent indicator with timer/counter

**Exit conditions**:
- Every 3 apples: enter Powerup Selection (pause movement)
- Collision without shield: enter Game Over

### 3) Powerup Selection (Pause Overlay)
**Entry**: Triggered at apples 3, 6, 9…

**On-screen**:
- Dimmed overlay + three cards
- Each card shows: name, 1-line effect, duration/counter, strong iconography (not color alone)
- Bottom helper text: Left/Right to choose, Enter/Space to confirm

**Interactions**:
- Left/Right: move selection
- Enter/Space: confirm

**UX requirements**:
- While overlay is visible, **do not change snake direction** (avoid “hidden” steering changes).
- Confirm action gives immediate acknowledgment (brief text and panel indicator updates).

**Exit**: Return to Playing

### 4) Game Over
**Entry**: Collision with wall/obstacle/self (when shield not active)

**On-screen**:
- Game over title
- Final score + high score
- One-line death reason
- Instruction: Press Space to restart

**Interaction**:
- Space: restart to Countdown

## Copy/Content Guidelines
- Keep card descriptions <= 1 short sentence.
- Prefer numbers over adjectives (“Next 5 apples score double” vs “Score more”).

## Accessibility & Comfort (Within Juicy Priority)
- Provide a “Reduced Effects” option or toggle (recommended) to reduce shake/flash intensity.
- Never rely on color alone for powerup differentiation; always show name + icon + timer/counter.
- Maintain legible text size/contrast in the right panel.
