# User Journey — Arcade Snake Run (Keyboard)

## Persona
- **Who**: Arcade score-chaser
- **Goal**: Beat personal best, learn powerups, maintain flow
- **Context**: Short sessions, repeated restarts, wants fast feedback
- **Success metric**: New high score, or “better than last run” in a few tries

## Journey Stages

### Stage 1: Start / Re-entry
- **User does**: Launches game or restarts after death
- **User thinks**: “Get me back in—this run I’ll go further.”
- **User feels**: Impatient, motivated
- **UX risks**:
  - Too much downtime (long countdown, unclear restart)
  - Unclear initial state (where hazards are, where food is)
- **Opportunities**:
  - Keep countdown short and consistent; make restart instruction always visible on game over
  - Ensure early play is fair (avoid spawn traps; avoid surprise obstacles in the first seconds)

### Stage 2: Early Run (Establish Flow)
- **User does**: Builds score, learns obstacle density, tests controls
- **User thinks**: “Controls feel tight—let’s ramp.”
- **User feels**: Focused, building confidence
- **UX risks**:
  - Visual effects obscure critical readability (snake head, obstacle edges)
  - Confusion about collision rules (obstacles vs self vs wall)
- **Opportunities**:
  - Maintain strong contrast and crisp edges, especially for the snake head
  - Provide clear, immediate death cause messaging on fail

### Stage 3: Mid Run (Powerup Choice Interrupt)
- **Trigger**: Powerup selection every 3 apples
- **User does**: Stops, scans 3 options, selects quickly
- **User thinks**: “Which choice maximizes score/survival right now?”
- **User feels**: Slightly interrupted; wants speed
- **UX risks**:
  - Input confusion: arrow keys accidentally change snake direction while choosing
  - Decision latency: text-heavy cards slow the flow
- **Opportunities**:
  - In selection mode, capture arrows exclusively for navigation
  - Make each card scannable in < 1 second: big name, 1-line effect, duration/counter
  - Reinforce selection: short confirmation + active indicator update

### Stage 4: High Intensity (Stacked Effects)
- **User does**: Plays faster with longer snake; relies on peripheral UI
- **User thinks**: “Don’t choke—manage space and speed.”
- **User feels**: Tense, excited
- **UX risks**:
  - Powerup info not glanceable (timers too small, moving layout)
  - Juice becomes noise (shake/flash hides collision boundary)
- **Opportunities**:
  - Stable UI positions; avoid layout shift when powerups appear/expire
  - Cap or shape effects so they don’t mask critical edges (e.g., flash fades quickly, shake decays)

### Stage 5: Fail Moment (Game Over)
- **User does**: Dies, evaluates cause, decides to restart
- **User thinks**: “That was on me—again.” (or “That was unfair.”)
- **User feels**: Frustrated but ready to retry
- **UX risks**:
  - Death feels ambiguous; player blames the game
  - Restart affordance not obvious or delayed
- **Opportunities**:
  - Display a single-line death reason (“Hit wall”, “Hit obstacle”, “Hit self”)
  - Keep restart action immediate and consistent (Space)

### Stage 6: Outcome (Retention Loop)
- **User does**: Plays “just one more run”
- **User thinks**: “I can beat that score.”
- **User feels**: Engaged, competitive
- **UX opportunities**:
  - Emphasize new high score moment with celebratory feedback
  - Keep friction low: predictable pacing, consistent controls, reliable persistence
