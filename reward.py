# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 18:04:16 2025

@author: Rachel
"""

from settings import (
    PROFIT_PER_RIDE,
    TRAVEL_COST_PER_STEP,
    WAIT_PENALTY_PER_STEP,
    IDLE_PENALTY_PER_STEP,
    CANCEL_PENALTY,
)


class RewardConfiguration:
    # CHANGE THESE!!
    def __init__(self):
        self.profitPerRide = PROFIT_PER_RIDE
        self.travelCostPerStep = TRAVEL_COST_PER_STEP
        self.waitPenaltyPerStep = WAIT_PENALTY_PER_STEP
        self.idlePenaltyPerStep = IDLE_PENALTY_PER_STEP
        self.cancelPenalty = CANCEL_PENALTY
        
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
    reward = reward + config.profitPerRide * countCompleted
        
    moving = info.get("moving_taxis", [])
    countMoving = 0
    i = 0
    while i < len(moving):
        countMoving = countMoving + 1
        i = i + 1     
    reward = reward - config.travelCostPerStep * countMoving
        
    numberWaiting = len(nextState.requests)
    reward = reward - config.waitPenaltyPerStep * numberWaiting

    cancelled = info.get("cancelled_requests", [])
    countCancelled = 0
    i = 0
    while i < len(cancelled):
        countCancelled = countCancelled + 1
        i = i + 1
    reward = reward - config.cancelPenalty * countCancelled
        
    idle = info.get("idle_taxis", [])
    countIdle = 0
    i = 0
    while i < len(idle):
        countIdle = countIdle + 1
        i = i + 1     
    reward = reward - config.idlePenaltyPerStep * countIdle     
    
    return reward