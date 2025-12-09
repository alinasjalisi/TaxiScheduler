# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 19:04:52 2025

@author: Rachel
"""

GRID_SIZE = 10
NUM_TAXIS = 5
REQUEST_RATE = 2.0
CANCELLATION_PROB = 0.2

EPISODES = 20      # number of episodes to run
HORIZON = 50        # steps per episode
MCTS_ITERATIONS = 200

PROFIT_PER_RIDE = 10.0
TRAVEL_COST_PER_STEP = 0.1
WAIT_PENALTY_PER_STEP = 2.0
IDLE_PENALTY_PER_STEP = 0.02
CANCEL_PENALTY = 5.0