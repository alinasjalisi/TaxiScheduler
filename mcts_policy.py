# mcts_policy.py

import math
import random
from copy import deepcopy
from environment import Action

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action  #joint action
        self.children = []
        self.visits = 0
        self.value = 0.0


#ucb score calculation
def ucb_score(parent, child, c=1.4):
    if child.visits == 0:
        return float('inf')
    exploit = child.value / child.visits
    explore = c * math.sqrt(math.log(parent.visits) / child.visits)
    return exploit + explore

#limited action set
def get_legal_actions(state):
    actions = []

    idle_all = [Action(taxi.id, "idle") for taxi in state.taxis]
    actions.append(idle_all)

    idle_taxis = [t for t in state.taxis if t.status == "idle"]

    for taxi in idle_taxis:
        for req in state.requests:
            joint = [Action(t.id, "idle") for t in state.taxis]
            joint[taxi.id] = Action(taxi.id, "assign", target=req)
            actions.append(joint)

    return actions


def select(node):
    while node.children:
        node = max(node.children, key=lambda c: ucb_score(node, c))
    return node

def expand(node, env):
    actions = get_legal_actions(node.state)

    for action in actions:
        next_state = env.step(node.state, action)
        child = MCTSNode(next_state, parent=node, action=action)
        node.children.append(child)

    return node.children

def rollout(state, env, depth=10):
    total_reward = 0.0
    current_state = state

    for _ in range(depth):
        actions = get_legal_actions(current_state)
        action = random.choice(actions)

        current_state = env.step(current_state, action)
        total_reward += env.get_reward(current_state)

    return total_reward

def backpropagate(node, reward):
    while node is not None:
        node.visits += 1
        node.value += reward
        node = node.parent

def mcts_policy(state, env, iterations=100):

    root = MCTSNode(state)

    for _ in range(iterations):
        leaf = select(root)

        if leaf.visits == 0:
            reward = rollout(leaf.state, env)
            backpropagate(leaf, reward)
            continue

        expand(leaf, env)
        child = random.choice(leaf.children)
        reward = rollout(child.state, env)
        backpropagate(child, reward)

    best = max(root.children, key=lambda c: c.visits)
    return best.action
