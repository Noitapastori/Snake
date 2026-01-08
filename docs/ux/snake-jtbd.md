# Snake (Arcade) — Jobs-to-be-Done (JTBD)

## Target Users
- **Who**: Arcade-oriented players chasing score, flow, and mastery
- **Platform**: Desktop, keyboard-only
- **Skill**: Comfortable with fast reaction games; expects tight, consistent rules
- **Primary motivation**: Beat personal bests and chase clean runs

## Job Statement
When I have a few minutes and want a fast, satisfying challenge, I want to jump into a run immediately and get clear, high-energy feedback on every success/fail moment, so I can chase higher scores without friction.

## Success Criteria (User-Perceived)
- **Time-to-fun**: From launch/restart to meaningful play in < 5 seconds.
- **Control trust**: No unexpected turns, pauses, or “input got eaten.”
- **Clarity under speed**: I always know why I died and what powerups are active.
- **Feedback payoff**: Eating food feels impactful; shield saves feel heroic.
- **Fairness**: Death feels deserved (no "cheap" early collisions).

## Current Experience (from the build)
- Countdown and restart flow exist.
- Powerup selection interrupts play every 3 apples.
- Strong “juice” exists: particles, shake, flash, score zoom.
- Right panel + playfield layout differs from the README’s 600x600 note.

## Key Pain Points to Prevent (Arcade audience)
- **Input mode ambiguity**: Arrow keys used both for steering and powerup selection can cause unexpected direction state when play resumes.
- **Cognitive interruption**: Powerup selection can feel like an unwanted pause if cards aren’t instantly scannable.
- **Unclear death cause**: With obstacles + effects, players must still understand the exact reason for game over.

## Design Principles (Arcade + Juicy)
1. **Instant restart loop**: Minimize downtime between runs.
2. **Mode-specific controls**: When a modal/pause UI is up, it fully captures input.
3. **Readable at speed**: Powerup state is always visible, minimal, and stable.
4. **Juice with purpose**: Effects amplify events but never hide critical state.
5. **Teach through play**: Learn powerups via on-screen cues, not external docs.
