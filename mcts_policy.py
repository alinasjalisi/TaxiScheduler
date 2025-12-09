# mcts_policy.py

import math
import random
from copy import deepcopy
from environment import Action

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action  # joint action
        self.children = []
        self.visits = 0
        self.value = 0.0

def ucb_score(parent, child, c=2.0):
    if child.visits == 0:
        return float('inf')
    exploit = child.value / child.visits
    explore = c * math.sqrt(math.log(parent.visits) / child.visits)
    return exploit + explore


def get_legal_actions(state, max_distance=5):
    actions = []

    idle_all = [Action(taxi.id, "idle") for taxi in state.taxis]
    actions.append(idle_all)

    idle_taxis = [t for t in state.taxis if t.status == "idle"]

    for taxi in idle_taxis:
        for req in state.requests:
            # unpack positions
            taxi_x, taxi_y = taxi.position
            pickup_x, pickup_y = req.origin  
            
            # manhattan distance
            distance = abs(taxi_x - pickup_x) + abs(taxi_y - pickup_y)
            
            # only create action if taxi is close enough
            if distance <= max_distance:
                joint = [Action(t.id, "idle") for t in state.taxis]
                joint[taxi.id] = Action(taxi.id, "assign", target=req)
                actions.append(joint)

    return actions


def select(node):

    while node.children:
        node = max(node.children, key=lambda c: ucb_score(node, c))
    return node


def expand(node, env):
    if not hasattr(node, 'untried_actions'):
        node.untried_actions = get_legal_actions(node.state, max_distance=5)

    if not node.untried_actions:
        return None
    
    # expand one action at a time
    action = node.untried_actions.pop()
    next_state = env.step(node.state, action)
    child = MCTSNode(next_state, parent=node, action=action)
    node.children.append(child)
    
    return [child] 


def rollout(state, env, depth=15):
  
    total_reward = 0.0
    current_state = state

    for _ in range(depth):
        actions = get_legal_actions(current_state, max_distance=5)
        if not actions:
            break
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
        # selection: find leaf node
        node = select(root)

        if node.visits > 0:
            children = expand(node, env)
            if children:
                    node = children[0] 
        #simulation: rollout from current node
        reward = rollout(node.state, env, depth=15)
        
        # update ancestors
        backpropagate(node, reward)

    # select best action
    if not root.children:
        return [Action(taxi.id, "idle") for taxi in state.taxis]
    
    best = max(root.children, key=lambda c: c.value / c.visits if c.visits > 0 else  0)
    return best.action

class MCTSPolicy:
    def __init__(self, env, iterations=100):
        self.env = env
        self.iterations = iterations
    
    def selectAction(self, state):
        return mcts_policy(state, self.env, self.iterations)