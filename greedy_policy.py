# -*- coding: utf-8 -*-
"""
Created on Sat Nov 29 15:17:25 2025

@author: Rachel
"""

import numpy as np
from environment import Action

class GreedyConfiguration:
    def __init__(self):
        self.repositionWhenIdle = True
        
class GreedyPolicy:
    def __init__(self, cfg, env, seed=None):
        self.cfg = cfg
        self.env = env
        
    def selectAction(self, state):
        actions = []
        i = 0
        while i < len(state.taxis):
            taxi = state.taxis[i]
            actions.append(Action(taxi.id, "idle"))
            i = i + 1
        
        idleTaxis = []
        i = 0
        while i < len(state.taxis):
            taxi = state.taxis[i]
            if taxi.status == "idle":
                idleTaxis.append(taxi)
            i = i + 1
            
        requests = []
        i = 0
        while i < len(state.requests):
            requests.append(state.requests[i])
            i = i + 1
            
        n = len(requests)
        a = 0
        while a < n:
            b = 0
            while b < n-1:
                if requests[b].waitingTime < requests[b + 1].waitingTime:                
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
            
            bestIndex = 0
            bestDistance = np.inf
            
            j = 0
            while j < len(idleTaxis):
                taxi = idleTaxis[j]
                distance = manhattan(taxi.position, r.origin)
                if distance < bestDistance:
                    bestDistance = distance
                    bestIndex = j
                j = j + 1
            
            bestTaxi = idleTaxis[bestIndex]
            actions[bestTaxi.id] = Action(bestTaxi.id, "assign", target = r)
            
            newIdle = []
            j = 0
            while j < len(idleTaxis):
                if j != bestIndex:
                    newIdle.append(idleTaxis[j])
                j  = j + 1
            
            idleTaxis = newIdle
            rIndex = rIndex + 1
                
        return actions
            


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])