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
        
def computeStepReward(state, action, nextState, info, config):
    if info is None:
        info = {}
    reward = 0.0
        
    completed = info.get("completed_rides")
        
    if completed is None:
        completed = inferCompletedRequests(state, nextState)
            
    countCompleted = 0
    for ride in completed:
        countCompleted += 1
        
    reward += config.profitPerRide * countCompleted
        
    if "travel_distance" in info:
        travelDistance = info["travel_distance"]
        totalDistance = 0.0
        
        for taxiID in travelDistance:
            totalDistance += travelDistance[taxiID]
            
        reward -= config.travelCostPerStep * totalDistance
        
    else:
        for taxiID in action:
            a = action[taxiID]
            if actionIsMotion(a):
                reward -= config.travelCostPerStep
                    
    activeRequests = getActiveRequests(nextState)
        
    for r in activeRequests:
        waiting = r.timeWaiting
        if waiting > 0:
            reward = reward - config.waitPenaltyPerStep
                
    cancelled = info.get("cancelled_requests")
        
    if cancelled is None:
        cancelled = inferCancelledRequests(state, nextState)
    countCancelled = 0
    for ride in cancelled:
        countCancelled = countCancelled + 1
    reward = reward - config.cancelPenalty * countCancelled
        
    idleTaxis = info.get("idle_taxis")
    if idleTaxis is None:
        idleTaxis = inferIdleTaxis(nextState)
    countIdle = 0
    for idle in idleTaxis:
        countIdle = countIdle + 1
    reward = reward - cfg.idlePenaltyPerStep * countIdle

def getActiveRequests(state):
    requests = []
    requests = state.requests
    requestsList = []
    for r in requests:
        requestsList.append(r)
    active = []
    for r in requestsList:
        cancelledFlag = False
        completedFlag = False
        cancelledFlag = (r.cancelled == True)
        completedFlag = (r.completed == True)
        if (not cancelledFlag) and (not completedFlag):
            active.append(r)
        
    return active

def inferCompletedRequests(state, nextState):
    beforeActive = getActiveRequests(state)
    afterActive = getActiveRequests(nextState)
    
    beforeIDs = []
    i = 0
    while i < len(beforeActive):
        r = beforeActive[i]
        beforeIDs.append(r.id)
        i = i + 1
    
    afterIDs = []
    j = 0
    while j < len(afterActive):
        r = afterActive[i]
        afterIDs.append(r.id)
        j = j + 1
    
    completed = []
    k = 0
    while k < len(beforeIDs):
        ride = beforeIDs[k]
        if ride not in afterIDs:
            completed.append(ride)
        k = k + 1
    
    return completed

def inferCancelledRequests(state, nextState):
    beforeRequests = []
    afterRequests = []
    beforeRequests = state.requests
    afterRequessts = nextState.requests
    
    beforeList = []
    for r in beforeRequests:
        beforeList.append(r)
    
    afterList = []
    for r in afterRequests:
        afterList.append(r)
        
    beforeDict = {}
    i = 0
    while i < len(beforeList):
        r = beforeList[i]
        ride = i
        ride = r.id
        beforeDict[ride] = r
        i = i + 1
        
    afterDict = {}
    j = 0
    while j < len(afterList):
        r = afterList[j]
        ride = j
        ride = r.id
        afterDict[ride] = r
        j = j + 1
    
    cancelled = []
    for ride in afterDict:
        rAfter = afterDict[ride]
        afterCancelled = False
        afterCancelled = (rAfter.cancelled == True)
        
        if afterCancelled:
            rBefore = None
            if ride in beforeDict:
                rBefore = beforeDict[ride]
            beforeCancelled = False
            if rBefore is not None:
                beforeCancelled = (rBefore.cancelled == True)
            if not beforeCancelled:
                cancelled.append(ride)
    return cancelled

def inferIdleTaxis(state):
    taxis = {}
    taxis = state.taxis
    taxiList = []
    index = 0
    while index < len(taxis):
        taxiList.append((index, taxis[index]))
        index = index + 1
    
    idle = []
    i = 0
    while i < len(taxiList):
        taxiId, v = taxiList[i]
        status = "idle"
        status = v.status
        if status == "idle":
            idle.append(taxiId)
        i = i + 1
    return idle


def actionIsMotion(a):
    if a is None:
        return False
    if a == "stay":
        return False
    return True