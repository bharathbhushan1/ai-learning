# q-learning

A minimal [Q-learning](https://en.wikipedia.org/wiki/Q-learning) example in
Python, managed with [uv](https://docs.astral.sh/uv/). It learns the optimal
policy for a tiny 1D gridworld from scratch — no dependencies, just the
standard library.

## The problem

The environment is a 1D line of 6 cells `[0, 1, 2, 3, 4, 5]`. The agent starts
at cell 0 and must reach the goal at cell 5. At each step it can move **left**
(`0`) or **right** (`1`); movement is clamped at the ends. Reaching the goal
gives a reward of `+1` and ends the episode, every other step gives `0`.

Q-learning is **off-policy**: the agent *behaves* with an epsilon-greedy policy
(mostly greedy, occasionally random to keep exploring) while *learning* about
the greedy policy via the `max` over next-state actions. The table
`Q[state][action]` is updated with the temporal-difference rule:

```
Q(s, a) <- Q(s, a) + alpha * (reward + gamma * max_a' Q(s', a') - Q(s, a))
```

After training, the best action in every non-goal state is `right`, with the
learned values discounted back from the goal by `gamma`.

## Setup

```sh
cd q-learning
uv sync
```

## Run

```sh
uv run q_learning_simple.py
```

It trains for `EPISODES` episodes and then prints the learned Q-table and the
best action per state. The `main.py` stub is the default uv entry point and is
not used by the example.

## Files

- `q_learning_simple.py` — the full example. Module-level constants define the
  environment (`N_STATES`, `GOAL`, `LEFT`/`RIGHT`/`ACTIONS`) and the
  hyperparameters (`EPSILON` exploration rate, `ALPHA` learning rate, `GAMMA`
  discount, `EPISODES`). Three small functions split the algorithm:
  - `behaviour_policy(Q, state)` — epsilon-greedy action selection (how the
    agent actually moves); ties fall through to `RIGHT`.
  - `env_step(state, action)` — applies an action and returns
    `(next_state, reward, done)`, clamping movement to the line.
  - `target_policy(Q, next_state)` — returns the greedy target *value*
    (`max` over actions) that bootstraps the update; this `max` is what makes
    the algorithm off-policy.

  `main()` initialises the Q-table to zeros, runs the episode/step loop applying
  the TD update, and prints the learned table and per-state best action.
- `main.py` — default uv-generated `Hello from q-learning!` stub; unused by the
  example.
- `pyproject.toml` / `uv.lock` / `.python-version` — uv project metadata
  (Python ≥ 3.12, no third-party dependencies).

## Changelog

- `2026-06-29` — Initial Q-learning example (`q_learning_simple.py`): a 1D
  6-cell gridworld solved with tabular off-policy Q-learning, plus this README.
