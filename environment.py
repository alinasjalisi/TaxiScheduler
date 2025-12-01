# environment.py
import random
import copy
import numpy as np
from typing import List, Tuple, Optional

class Taxi:
    def __init__(self, taxi_id: int, position: Tuple[int, int]):
        self.id = taxi_id
        self.position = position  # (x, y) coordinates on grid
        self.status = "idle"  
        self.assigned_request = None  
        self.destination = None  
        self.remaining_travel_time = 0  
        
    def __repr__(self):
        return f"Taxi(id={self.id}, pos={self.position}, status={self.status})"

class Request:

    def __init__(self, request_id: int, origin: Tuple[int, int], 
                 destination: Tuple[int, int], arrival_time: int):
        self.id = request_id
        self.origin = origin  # pickup location (x, y)
        self.destination = destination  
        self.arrival_time = arrival_time
        self.waiting_time = 0 
        self.is_cancelled = False
        
    def __repr__(self):
        return f"Request(id={self.id}, from={self.origin}, to={self.destination})"

class State:
   
    def __init__(self, taxis: List[Taxi], requests: List[Request], 
                 time: int, traffic_level: float = 1.0):
        self.taxis = taxis 
        self.requests = requests  # active reqs*
        self.time = time  
        self.traffic_level = traffic_level  # 1.0 = normal, >1.0 = congested
        
    def __repr__(self):
        return f"State(time={self.time}, taxis={len(self.taxis)}, requests={len(self.requests)})"

class Action:
   
    def __init__(self, taxi_id: int, action_type: str, target=None):
        self.taxi_id = taxi_id
        self.action_type = action_type  
        self.target = target  
        
    def __repr__(self):
        return f"Action(taxi={self.taxi_id}, type={self.action_type})"

class Environment:
    # simulates autonomous taxi dispatch system
    def __init__(self, grid_size: int = 10, num_taxis: int = 3, 
                 request_rate: float = 0.3, cancellation_prob: float = 0.05):
       
        self.grid_size = grid_size
        self.num_taxis = num_taxis
        self.request_rate = request_rate
        self.cancellation_prob = cancellation_prob
        self.request_counter = 0  # to generate unique request IDs
        
    def create_initial_state(self) -> State:
       # initial state w random positions
        taxis = []
        for i in range(self.num_taxis):
            position = (random.randint(0, self.grid_size - 1),
                       random.randint(0, self.grid_size - 1))
            taxis.append(Taxi(taxi_id=i, position=position))
        
        return State(taxis=taxis, requests=[], time=0)
    
    def step(self, state: State, actions: List[Action]) -> State:
       # returns next state after applying stochastic transitions & actions

        new_state = self._copy_state(state)
        
        self._process_taxi_actions(new_state, actions)
        
        self._update_taxi_positions(new_state)

        self._generate_new_requests(new_state)

        self._update_requests(new_state)
        
        self._update_traffic(new_state)
        
        new_state.time += 1
        
        return new_state
    
    def _copy_state(self, state: State) -> State:
        
        new_taxis = []
        for taxi in state.taxis:
            new_taxi = Taxi(taxi.id, taxi.position)
            new_taxi.status = taxi.status
            new_taxi.assigned_request = taxi.assigned_request
            new_taxi.destination = taxi.destination
            new_taxi.remaining_travel_time = taxi.remaining_travel_time
            new_taxis.append(new_taxi)
        
        new_requests = []
        for req in state.requests:
            new_req = Request(req.id, req.origin, req.destination, req.arrival_time)
            new_req.waiting_time = req.waiting_time
            new_req.is_cancelled = req.is_cancelled
            new_requests.append(new_req)
        
        return State(new_taxis, new_requests, state.time, state.traffic_level)
    
    def _process_taxi_actions(self, state: State, actions: List[Action]):

        for action in actions:
            taxi = state.taxis[action.taxi_id]
            
            if action.action_type == "assign" and taxi.status == "idle":
                # assign taxi to req
                request = action.target
                if request and not request.is_cancelled:
                    taxi.status = "en_route_to_pickup"
                    taxi.assigned_request = request
                    taxi.destination = request.origin
                    taxi.remaining_travel_time = self._manhattan_distance(
                        taxi.position, request.origin
                    )
                    
            elif action.action_type == "move" and taxi.status == "idle":
                # repositioning
                target_pos = action.target
                if target_pos:
                    taxi.destination = target_pos
                    taxi.remaining_travel_time = self._manhattan_distance(
                        taxi.position, target_pos
                    )
                    
            elif action.action_type == "idle":
                pass
    
    def _update_taxi_positions(self, state: State):
    
        for taxi in state.taxis:
            if taxi.status == "idle":
                continue
            
            # check if taxi reached destination
            if taxi.remaining_travel_time <= 0:
                if taxi.status == "en_route_to_pickup":
                    taxi.position = taxi.assigned_request.origin
                    taxi.status = "occupied"
                    taxi.destination = taxi.assigned_request.destination
                    taxi.remaining_travel_time = self._manhattan_distance(
                        taxi.position, taxi.destination
                    )
                    state.requests = [r for r in state.requests 
                                     if r.id != taxi.assigned_request.id]
                    
                elif taxi.status == "occupied":
                    taxi.position = taxi.destination
                    taxi.status = "idle"
                    taxi.assigned_request = None
                    taxi.destination = None
                    taxi.remaining_travel_time = 0
            else:
                # move taxi one step to destination
                taxi.position = self._move_toward(taxi.position, taxi.destination)
                taxi.remaining_travel_time -= 1
                
                # stochastic traffic delay
                if random.random() < state.traffic_level * 0.1:
                    taxi.remaining_travel_time += 1  # Traffic delay
    
    def _generate_new_requests(self, state: State):

        num_new_requests = np.random.poisson(self.request_rate)

        for _ in range(num_new_requests):
            origin = (random.randint(0, self.grid_size - 1),
                     random.randint(0, self.grid_size - 1))
            destination = (random.randint(0, self.grid_size - 1),
                          random.randint(0, self.grid_size - 1))
            
            while origin == destination:
                destination = (random.randint(0, self.grid_size - 1),
                             random.randint(0, self.grid_size - 1))
            
            new_request = Request(
                request_id=self.request_counter,
                origin=origin,
                destination=destination,
                arrival_time=state.time
            )
            self.request_counter += 1
            state.requests.append(new_request)
    
    def _update_requests(self, state: State):
    
        for request in state.requests:
            request.waiting_time += 1
            
            # stochastic cancellation
            if random.random() < self.cancellation_prob:
                request.is_cancelled = True
        
        state.requests = [r for r in state.requests if not r.is_cancelled]
    
    def _update_traffic(self, state: State):

        # traffic evolves as random walk between 0.8 and 1.5
        change = random.uniform(-0.1, 0.1)
        state.traffic_level = max(0.8, min(1.5, state.traffic_level + change))
    
    def _manhattan_distance(self, pos1: Tuple[int, int], 
                           pos2: Tuple[int, int]) -> int:
        
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _move_toward(self, current: Tuple[int, int], 
                    target: Tuple[int, int]) -> Tuple[int, int]:
        
        x, y = current
        tx, ty = target
        
        # move in x direction first, then y
        if x < tx:
            return (x + 1, y)
        elif x > tx:
            return (x - 1, y)
        elif y < ty:
            return (x, y + 1)
        elif y > ty:
            return (x, y - 1)
        else:
            return current
    
    def get_observation(self, state: State) -> dict:
       # simulates noisy observations of the state
        observation = {
            'time': state.time,
            'taxis': [],
            'requests': [],
            'traffic_estimate': state.traffic_level + random.uniform(-0.1, 0.1)
        }
        
        for taxi in state.taxis:
            noisy_position = taxi.position
            # 10% chance of 1-step error
            if random.random() < 0.1:
                noise = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                noisy_position = (
                    max(0, min(self.grid_size - 1, taxi.position[0] + noise[0])),
                    max(0, min(self.grid_size - 1, taxi.position[1] + noise[1]))
                )
            
            observation['taxis'].append({
                'id': taxi.id,
                'position': noisy_position,
                'status': taxi.status
            })

        for request in state.requests:
            # 90% chance of observing request
            if random.random() < 0.9:
                observation['requests'].append({
                    'id': request.id,
                    'origin': request.origin,
                    'destination': request.destination,
                    'waiting_time': request.waiting_time
                })
        
        return observation