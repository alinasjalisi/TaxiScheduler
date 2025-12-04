# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 21:08:58 2025

@author: Rachel
"""
from environment import Environment
from greedy_policy import GreedyPolicy, GreedyConfig
from experiments import run_many

def buildEnv():
    return Environment(gridSize = 10, numTaxis = 3, requestRate = 0.5)

def buildPolicy(env):
    cfg = GreedyConfig()
    return GreedyPolicy(cfg, env)

episodes = 5
maxSteps = 50

results = run_many(buildEnv, buildPolicy, episodes, maxSteps)
print("Greedy policy results over " + str(episodes) + " episodes:")
i = 0
while i < len(results):
    print("Episode " + str(i) + " " + str(results[i]))
    i = i + 1