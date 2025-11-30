# -*- coding: utf-8 -*-
"""
Created on Sat Nov 29 15:17:25 2025

@author: Rachel
"""

import random
import numpy as np

class GreedyConfiguration:
    def __init__(self):
        self.repositionWhenIdle = True
        self.randomWalkIdle = True
        
class GreedyPolicy:
    def __init__(self, cfg, seed=None):
        self.cfg = cfg
        self.rng = random.Random(seed)
        
    def selectAction(self, state):
        taxis = asTaxiItems(state) #write
        requests = activeRequests(state)
        
        jointAction = {}
        
        idleTaxis = []
        i = 0
        while i < len(taxis):
            taxiId, v = taxis[i]
            if taxiStatus(v) == "idle":
                idleTaxis.append((taxiId, v))
            i = i + 1
            
        n = len(requests)
        a = 0
        while a < n:
            b = 0
            while b < n-1:
                w1 = requestWaitTime(requests[b]) #write
                w2 = requestWaitTime(requests[b + 1])
                if w1 < w2:
                    temp = requests[b]
                    requests[b] = requests[b + 1]
                    requests[b + 1] = temp
                b = b + 1
            a = a + 1
            
        rIndex = 0
        while rIndex < len(requests):
            r = requests[rIndex]
            if len(idleTaxis) == 0:
                break
            ride = getRequestId(r) #write
            origin = requestOrigin(r) #write
            if origin is None:
                rIndex = rIndex + 1
            
            bestIndex = 0
            bestDistance = np.inf
            
            i = 0
            while i < len(idleTaxis):
                taxiId, v = idleTaxis[i]
                distance = manhattan(taxiLocation(v), origin) #write
                if distance < bestDistance:
                    bestDistance = distance
                    bestIndex = i
                i = i + 1
            
            bestTaxiId, bestV = idleTaxis.pop(bestIndex)
            jointAction[bestTaxiId] = {"type": "assign", "request_id": ride}
            rIndex = rIndex + 1
            
        i = 0
        while i < len(idleTaxis):
            taxiId, v = idleTaxis[i]
            if self.cfg.repositionWhenIdle and self.cfg.randomWalkIdle:
                direction = self.rng.choice(["N", "S", "E", "W"])
                jointAction[taxiId] = {"type": "move", "direction": direction}
            else:
                jointAction[taxiId] = {"type": "stay"}
            
        i = 0
        while i < len(taxis):
            taxiId, v = taxis[i]
            if taxiId not in jointAction:
                jointAction[taxiId] = {"type": "stay"}
            i = i + 1
       
        return jointAction
            
def asTaxiItems(state):
    taxis = {}
    taxis = state.taxiStatus
    items = []
    i = 0
    while i < len(taxis):
        items.append((i, taxis[i]))
        i = i + 1
    return items
    
def taxiLocation(v):
    return v.location

def taxiStatus(v):
    return v.status

def activeRequests(state):
    requests = []
    requests = state.requests
    
    requestsList = []
    for r in requests:
        requestsList.append(r)
        
    active = []
    i = 0
    while i < len(requestsList):
        r = requestsList[i]
        cancelled = False
        completed = False
        cancelled = (r.cancelled == True)
        completed = (r.completed == True)
        if (not cancelled) and (not completed):
            active.append(r)
        i = i + 1
    return active
    
def requestOrigin(r):
    return r.origin

def requestWaitTime(r):
    return r.timeWaiting

def getRequestId(r):
    return r.id

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])