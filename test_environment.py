# test_environment.py
from environment import *

def test_basic_simulation():
    print("-" * 60)
    print("Basic Simulation test")
    print("-" * 60)

    # create environment
    env = Environment(grid_size=10, num_taxis=3, request_rate=0.5)

    # initial state
    state = env.create_initial_state()
    print(f"\nInitial State:")
    print(f"  Time: {state.time}")
    print(f"  Number of taxis: {len(state.taxis)}")
    print(f"  Taxis:")
    for taxi in state.taxis:
        print(f"    {taxi}")
    print(f"  Active requests: {len(state.requests)}")
    
    # simulate 10 timesteps
    print("\n" + "-" * 60)
    print("Simulation for 10 timesteps")
    print("-" * 60)
    
    for step in range(10):
        
        actions = [Action(taxi.id, "idle") for taxi in state.taxis]
        idle_taxis = [t for t in state.taxis if t.status == "idle"]
        if state.requests and idle_taxis:
            # assign first idle taxi to first req
            request = state.requests[0]
            actions[idle_taxis[0].id] = Action(
                taxi_id=idle_taxis[0].id,
                action_type="assign",
                target=request
            )
        next_state = env.step(state, actions)
        
        obs = env.get_observation(next_state)

        print(f"\n--- Timestep {next_state.time} ---")
        print(f"Active requests: {len(next_state.requests)}")
        print(f"Traffic level: {next_state.traffic_level:.2f}")
        print(f"Taxis:")
        for taxi in next_state.taxis:
            print(f"  Taxi {taxi.id}: pos={taxi.position}, status={taxi.status}")
        
        if next_state.requests:
            print(f"Requests:")
            for req in next_state.requests[:3]:  # show first 3 reqs
                print(f"  Request {req.id}: {req.origin} -> {req.destination}, "
                      f"waiting={req.waiting_time}")
        
        state = next_state
    
    print("Simulation completed successfully") # successful completion 

def test_state_transition():
    """
    Test that state transitions work correctly.
    """
    print("\n" + "-" * 60)
    print("State Transition Function test")
    print("-" * 60)
    
    env = Environment(grid_size=5, num_taxis=2, request_rate=0)
    
    # creat specific initial state
    taxi1 = Taxi(0, (0, 0))
    taxi2 = Taxi(1, (4, 4))
    request1 = Request(0, (2, 2), (3, 3), arrival_time=0)
    
    state = State([taxi1, taxi2], [request1], time=0)
    
    print(f"Initial state:")
    print(f"  Taxi 0 at {taxi1.position}, status: {taxi1.status}")
    print(f"  Taxi 1 at {taxi2.position}, status: {taxi2.status}")
    print(f"  Request 0: {request1.origin} -> {request1.destination}")
    
    # assign taxi 0 to request 0
    actions = [
        Action(0, "assign", target=request1),
        Action(1, "idle")
    ]
    
    next_state = env.step(state, actions)
    
    print(f"\nAfter assignment action:")
    print(f"  Taxi 0 at {next_state.taxis[0].position}, "
          f"status: {next_state.taxis[0].status}")
    print(f"  Taxi 0 destination: {next_state.taxis[0].destination}")
    print(f"  Taxi 0 remaining travel time: {next_state.taxis[0].remaining_travel_time}")

    # simulate movement
    for i in range(6):
        actions = [Action(0, "idle"), Action(1, "idle")]
        next_state = env.step(next_state, actions)
        print(f"\nStep {i+1}:")
        print(f"  Taxi 0 at {next_state.taxis[0].position}, "
              f"status: {next_state.taxis[0].status}")

def test_observation_model():

    print("\n" + "-" * 60)
    print("Observation Model test")
    print("-" * 60)
    
    env = Environment(grid_size=10, num_taxis=2, request_rate=1.0)
    state = env.create_initial_state()
    
    # generate multiple to see variability
    print("\nGenerating 3 observations from same state:")
    for i in range(3):
        obs = env.get_observation(state)
        print(f"\nObservation {i+1}:")
        print(f"  Observed taxis: {len(obs['taxis'])}")
        print(f"  Observed requests: {len(obs['requests'])}")
        print(f"  Traffic estimate: {obs['traffic_estimate']:.2f}")

if __name__ == "__main__":
    test_basic_simulation()
    test_state_transition()
    test_observation_model()