# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 21:08:58 2025

@author: Rachel
"""
from environment import Environment
from greedy_policy import GreedyPolicy, GreedyConfiguration
from experiments import runMany

def buildEnv():
    return Environment(grid_size = 10, num_taxis = 3, request_rate = 0.5)

def buildPolicy(env):
    cfg = GreedyConfiguration()
    return GreedyPolicy(cfg, env)

episodes = 5
maxSteps = 50

results = runMany(buildEnv, buildPolicy, episodes, maxSteps)
print("Greedy policy results over " + str(episodes) + " episodes:")
i = 0
while i < len(results):
    print("Episode " + str(i) + " " + str(results[i]))
    i = i + 1