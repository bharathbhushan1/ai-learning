"""
A very simple Q-learning example.

Environment: a 1D line of 6 cells [0, 1, 2, 3, 4, 5].
The agent starts at cell 0 and must reach the goal at cell 5.
Actions: move left (0) or right (1).
Reward: +1 for reaching the goal, 0 otherwise.

Q-learning learns a table Q[state][action] estimating how good each
action is in each state, using the update rule:

    Q(s, a) <- Q(s, a) + alpha * (reward + gamma * max_a' Q(s', a') - Q(s, a))
"""

import random

N_STATES = 6          # cells 0..5
GOAL = N_STATES - 1   # cell 5 is the goal (integer index, no trailing dot)

LEFT = 0
RIGHT = 1
ACTIONS = [LEFT, RIGHT]

EPSILON = 0.1         # exploration rate (chance of a random action)
ALPHA = 0.1           # learning rate
GAMMA = 0.9           # discount factor

EPISODES = 200        # how many times the agent plays the game


def behaviour_policy(Q, state) -> int:
    """Epsilon-greedy action selection: how the agent actually moves.

    With probability EPSILON it explores (random action); otherwise it
    exploits the current best estimate. Ties fall through to RIGHT, which
    happens to point toward the goal.
    """
    if random.random() < EPSILON:
        return random.choice(ACTIONS)
    return LEFT if Q[state][LEFT] > Q[state][RIGHT] else RIGHT

def env_step(state, action):
    """Apply an action to the environment.

    Returns (next_state, reward, done). Movement is clamped to the line:
    you cannot step left of cell 0 or right of the goal. Reaching the goal
    yields +1 and ends the episode; every other step yields 0.
    """
    if action == LEFT:
        next_state = max(state-1, 0)
    else:
        next_state = min(state+1, GOAL)

    if next_state == GOAL:
        return next_state, 1.0, True
    return next_state, 0.0, False

def target_policy(Q, next_state) -> float:
    """Greedy target value used to bootstrap the update.

    Returns the *value* of the best action in next_state (max over actions),
    not an action. This max is what makes the algorithm off-policy Q-learning:
    we learn about the greedy policy while behaving epsilon-greedily.
    """
    return max(Q[next_state])

def main():
    # one row per state. one column per action.
    Q = [[0.0, 0.0] for _ in range(N_STATES)]

    for _ in range(EPISODES):
        state = 0          # every episode starts at the far-left cell
        done = False
        while not done:
            action = behaviour_policy(Q, state)
            next_state, reward, done = env_step(state, action)
            best_next_Q = target_policy(Q, next_state)
            # TD update: nudge Q(s,a) toward the observed target.
            # reward + GAMMA * best_next_Q  is the target; subtracting the
            # old estimate gives the TD error, scaled by the learning rate.
            Q[state][action] += ALPHA * (
                reward + GAMMA * best_next_Q - Q[state][action]
            )
            state = next_state

    print("\nLearned Q-table:")
    for i in range(N_STATES):
        print(f' .. [{i}] L={Q[i][LEFT]:.2f} R={Q[i][RIGHT]:.2f}')
    print("\nBest action per state:")
    for i in range(N_STATES):
        if i == GOAL:
            print(f'  state {i}: GOAL')
        else:
            best = 'right' if Q[i][RIGHT] >= Q[i][LEFT] else 'left'
            print(f'  state {i}: {best}')


if __name__ == '__main__':
    main()
