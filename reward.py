# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 18:04:16 2025

@author: Rachel
"""

# Basic idea, but depending on env, tweak this

class RewardConfiguration:
    # CHANGE THESE!!
    def __init__(self):
        self.profitPerRide = 10.0
        self.travelCostPerStep = 0.1
        self.waitPenaltyPerStep = 2.0
        self.idlePenaltyPerStep = 0.02
        self.cancelPenalty = 5.0
        
def computeStepReward(state, action, nextState, info, config):
    if info is None:
        info = {}
    reward = 0.0
        
    completed = info.get("completed_rides", [])
    countCompleted = 0
    i = 0
    while i < len(completed):
        countCompleted = countCompleted + 1
        i = i + 1
    reward += config.profitPerRide * countCompleted
        
    moving = info.get("moving_taxis", [])
    countMoving = 0
    while i < len(moving):
        countMoving = countMoving + 1
        i = i + 1     
    reward -= config.travelCostPerStep * countMoving
        
    numberWaiting = len(nextState.requests)
    reward -= config.waitPenaltyPerStep * countMoving

    cancelled = info.get("cancelled_requests", [])
    countCancelled = 0
    i = 0
    while i < len(cancelled):
        countCancelled = countCancelled + 1
        i = i + 1
        
    idle = info.get("idle_taxis", [])
    countIdle = 0
    while i < len(idle):
        countIdle = countIdle + 1
        i = i + 1     
    reward -= config.idlePenaltyPerStop * countIdle     
    
    return reward