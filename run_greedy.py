# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 21:08:58 2025

@author: Rachel
"""
from environment import Environment
from greedy_policy import GreedyPolicy, GreedyConfiguration
from experiments import runMany
from settings import GRID_SIZE, NUM_TAXIS, REQUEST_RATE, CANCELLATION_PROB, EPISODES, HORIZON


def buildEnv():
    return Environment(grid_size=GRID_SIZE, num_taxis=NUM_TAXIS, request_rate=REQUEST_RATE, cancellation_prob=CANCELLATION_PROB)

def buildPolicy(env):
    cfg = GreedyConfiguration()
    return GreedyPolicy(cfg, env)

episodes = EPISODES
maxSteps = HORIZON

results = runMany(buildEnv, buildPolicy, episodes, maxSteps)
print("Greedy policy results over " + str(episodes) + " episodes:")
i = 0
while i < len(results):
    print("Episode " + str(i + 1) + " " + str(results[i]))
    i = i + 1