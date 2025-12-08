# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 20:49:19 2025

@author: Rachel
"""

from metrics import EpisodeHistory, summarizedMetrics
from reward import computeStepReward, RewardConfiguration

def runEpisode(env, policy, maxSteps, rewardCfg):
    state = env.createInitialState()
    hist = EpisodeHistory()
    
    knownRequestIDs = {}
    
    stepIndex = 0
    while stepIndex < maxSteps:
        actions = policy.selectAction(state)
        nextState = env.step(state, actions)
        
        beforeIDs = []
        i = 0
        while i < len(state.requests):
            beforeIDs.append(state.requests[i].id)
            i = i + 1
            
        afterIDs = []
        i = 0
        while i < len(nextState.requests):
            afterIDs.append(nextState.requests[i].id)
            i = i + 1
        
        newRequests = []
        i = 0
        while i < len(nextState.requests):
            r = nextState.requests[i]
            if r.id not in knownRequestIDs:
                newRequests.append(r)
                knownRequestIDs[r.id] = True
            i = i + 1
            
        removedIDs = []
        while i < len(beforeIDs):
            rID = beforeIDs[i]
            if rID not in afterIDs:
                removedIDs.append(rID)
            i = i + 1        
                
        assignedIDsNext = []
        i = 0
        while i < len(nextState.taxis):
            taxi = nextState.taxis[i]
            if taxi.assignedRequest is not None:
                assignedIDsNext.append(taxi.assignedRequest.id)
            i = i + 1
     
        pickedUpIDs = []
        cancelledIDs = []
        i = 0
        while i < len(removedIDs):
            rID = removedIDs[i]
            if rID in assignedIDsNext:
                pickedUpIDs.append(rID)
            else:
                cancelledIDs.append(rID)
            i = i + 1
        
        completedIDs = []
        i = 0
        while i < len(state.taxis):
            oldTaxi = state.taxis[i]
            newTaxi = nextState.taxis[i]
            if oldTaxi.status == "occupued" and newTaxi.status == "idle":
                if oldTaxi.assignedRequest is not None:
                    completedIDs.append(oldTaxi.assignedRequest.id)
            i = i + 1
            
        idleTaxis = []
        i = 0
        while i < len(nextState.taxis):
            taxi = nextState.taxis[i]
            if taxi.status == "idle":
                idleTaxis.append(taxi.id)
            i = i + 1
            
        movingTaxis = []
        i = 0
        while i < len(state.taxis):
            oldTaxi = state.taxis[i]
            newTaxi = nextState.taxis[i]
            if oldTaxi.position != newTaxi.position:
                movingTaxis.append(oldTaxi.id)
            i = i + 1
            
        hist.note_new_requests(newRequests)
        hist.note_pickups(nextState.time, pickedUpIDs)
        hist.note_dropoffs(nextState.time, completedIDs)
        hist.note_cancellations(nextState.time, cancelledIDs)
        hist.note_idle_taxis(idleTaxis)
        
        info = {"completed_rides" : completedIDs, "cancelled_requests" : cancelledIDs, "idleTaxis" : idleTaxis, "movingTaxis" : movingTaxis}
        
        stepReward = computeStepReward(state, actions, nextState, info, rewardCfg)
        hist.total_revenue = hist.total_revenue + stepReward
        
        state = nextState
        stepIndex = stepIndex + 1
        
    return hist

def runMany(envBuilder, policyBuilder, episodes, maxSteps):
    results = []
    episode = 0
    while episode < episodes:
        env = envBuilder()
        policy = policyBuilder(env)
        hist = runEpisode(env, policy, maxSteps, RewardConfiguration())
        metrics = summarizedMetrics(hist)
        results.append(metrics)
        episode = episode + 1
        
    return results