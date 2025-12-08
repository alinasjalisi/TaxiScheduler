# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 20:21:02 2025

@author: Rachel
"""

class RequestEvent:
    def __init__(self, requestID, arrivalTime):
        self.requestID = requestID
        self.arrivalTime = arrivalTime
        self.pickupTime = None
        self.dropoffTime = None
        self.cancelledTime = None
        
class EpisodeHistory:
    def __init__(self):
        self.events = {}
        self.taxiIdleSteps = {}
        self.totalRevenue = 0.0
        self.completedRides = 0
    
    def noteNewRequests(self, newRequests):
        if newRequests is None:
            return
        i = 0
        while i < len(newRequests):
            r = newRequests[i]
            rID = r.id
            if rID not in self.events:
                self.events[rID] = RequestEvent(rID, r.arrival_time)
            i = i + 1
        
    def notePickups(self, t, pickedUpIDs):
        if pickedUpIDs is None:
            return
        i = 0
        while i < len(pickedUpIDs):
            rID = pickedUpIDs[i]
            if rID in self.events:
                event = self.events[rID]
                if event.pickupTime is None:
                    event.pickupTime = t
            i = i + 1
    
    def noteDropoffs(self, t, completedIDs):
        if completedIDs is None:
            return
        i = 0
        while i < len(completedIDs):
            rID = completedIDs[i]
            if rID in self.events:
                event = self.events[rID]
                if event.dropoffTime is None:
                    event.dropoffTime = t
            self.completedRides = self.completedRides + 1
            i = i + 1
            
    def noteCancellations(self, t, cancelledIDs):
        if cancelledIDs is None:
            return
        i = 0
        while i < len(cancelledIDs):
            rID = cancelledIDs[i]
            if rID in self.events:
                event = self.events[rID]
                if event.cancelledTime is None:
                    event.cancelledTime = t
            i = i + 1 

    def noteIdleTaxis(self, t, idleTaxiIDs):
        if idleTaxiIDs is None:
            return
        i = 0
        while i < len(idleTaxiIDs):
            tID = idleTaxiIDs[i]
            if tID not in self.taxiIdleSteps:
                self.taxiIdleSteps[tID] = 0
            self.taxiIdleSteps[tID] = self.taxiIdleSteps[tID] + 1
            i = i + 1 
            
def averageWaitTime(hist):
    waits = []
    for rID in hist.events:
        event = hist.events[rID]
        if event.pickupTime is not None:
            waits.append(event.pickupTime - event.arrivalTime)
        elif event.cancelledTime is not None:
            waits.append(event.cancelledTime - event.arrivalTime)
    
    if len(waits) == 0:
        return 0.0
    
    total = 0.0
    i = 0
    while i < len(waits):
        total = total + waits[i]
        i = i + 1
        
    return total / float(len(waits))

def averageIdleTime(hist):
    if len(hist.taxiIdleSteps) == 0:
        return 0.0
    
    totalIdle = 0.0
    countTaxis= 0
    for tID in hist.taxiIdleSteps:
        totalIdle = totalIdle + hist.taxiIdleSteps[tID]
        countTaxis = countTaxis + 1
        
    return totalIdle / float(countTaxis)

def totalCompletedRides(hist):
    return hist.completedRides

def totalRevenue(hist):
    return hist.totalRevenue

def summarizedMetrics(hist):
    return {"avg_wait_time" : averageWaitTime(hist), "avg_idle_time" : averageIdleTime(hist), "completed_rides" : float(totalCompletedRides(hist)), "total_revenue" : float(totalRevenue(hist))}
    