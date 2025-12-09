# TaxiScheduler
**0. Motivation and Overview**

Real-world taxi and ride-hailing systems must decide which vehicle should serve which request and when to move idle vehicles around the city. Those decisions directly affect rider wait times, cancellations, and fleet utilization. We wanted to study this decision problem in a controlled setting where we could actually see how different dispatch strategies behave over time in a stochastic environment with demand, traffic, and cancellations.

We defined success in terms of performance metrics aggregated over episodes; total discounted reward per episode, average rider wait time, average taxi idle time, number of completed rides, and number of cancellations. We ran both greedy and MCTS policies on the same environment parameters and compared their distributions and averages of these metrics over multiple episodes. MCTS is considered successful if, for a given computation budget, it can match or outperform the greedy baseline on total reward and reduce wait times and cancellations, recognizing that performance will vary across stochastic runs.

**1. Problem Statement**

We model a simplified version of a taxi dispatch system in a small city. Time is discrete, and the city is a grid. At each time step, ride requests appear at random origins and need to be served by a fleet of taxis. Each taxi can be idle, driving to a pickup location, or driving a passenger to their destination. Requests can also be cancelled if they wait too long.

The dispatch system has to decide, at every step, which taxi (if any) should be assigned to each waiting request, and whether any idle taxis should be moved (repositioned) to new locations. The goal is to maximize long-term reward, which combines positive reward for completed rides, costs for driving, penalties for making riders wait, and penalties for cancellations and idle time.

The problem is difficult and has many uncertainties because requests arrive stochastically over time, travel times are affected by stochastic traffic, and there are many possible ways to assign taxis to requests at every step.
We treat this as a planning / decision-making problem under uncertainty; given the current state (and potentially noisy observations of that state), choose an action that maximizes expected future reward.

**2. Related Solutions to Similar Problems**

Real-world ride-hailing platforms (e.g. taxi fleets, Uber/Lyft style systems) face very similar dispatch problems. Common approaches include:
* Dynamic trip-vehicle assignment: Link
* MPC for AMoD/ride-hailing: Link
* Large-scale RL dispatch: Link

**3. State Space, Actions, Transitions, and Observations**

**3.1 State Space**

We model the system state as:
* A set of taxis, each with:
  * id: integer ID
  * position: (x, y) grid coordinate
  * status: "idle", "en_route_to_pickup", or "occupied"
  * assigned_request: the request it is currently serving or going to pick up
  * destination: target position (pickup or dropoff)
  * remaining_travel_time: steps left until reaching the current destination
* A set of active requests, each with:
  * id: integer ID
  * origin: (x, y) pickup location
  * destination: (x, y) dropoff location
  * arrival_time: time step when the request appeared
  * waiting_time: how many steps the request has been waiting
  * is_cancelled: flag for whether the request has cancelled
* Global variables:
  * time: current time step
  * traffic_level: a continuous factor that affects travel delays

These are represented by the Taxi, Request, and State classes inside environment.py. The Environment class holds parameters like grid_size, num_taxis, request_rate, and cancellation_prob.

**3.2 Action Space**

At each time step, the policy outputs a list of Action objects; one action per taxi:
* Action(taxi_id, "idle") - taxi stays idle and keeps its current status (unless it is already en route or occupied).
* Action(taxi_id, "assign", target=request) - for an idle taxi, start driving toward the pickup location of request. This sets:
  * status = "en_route_to_pickup"
  * assigned_request = request
  * destination = request.origin
  * remaining_travel_time to the Manhattan distance to the origin
* Action(taxi_id, "move", target=position) - for an idle taxi, start repositioning toward some target cell on the grid.
We restrict candidate actions in our planners to keep the branching factor manageable:
* Greedy policy: only "idle" or "assign" to existing requests.
* MCTS: one base “all idle” joint action, plus alternatives where a single idle taxi is assigned to a specific request.

**3.3 Transition Model**

Environment.step(state, actions) applies actions and stochastic dynamics to produce the next state. The update sequence is:
* Copy previous state
  * Makes a deep copy so planning algorithms can simulate without mutating the real state.
* Apply taxi actions: _process_taxi_actions:
  * For "assign" and an idle taxi:
    * Set taxi to "en_route_to_pickup" with destination at the request’s origin.
  * For "move" and an idle taxi:
    * Set the taxi’s destination and remaining travel time based on Manhattan distance.
  * "idle" leaves the taxi unchanged.
* Update taxi positions: _update_taxi_positions:
  * If remaining_travel_time <= 0:
    * If the taxi was "en_route_to_pickup", snap it to the origin, set it to "occupied", and start traveling toward the request’s destination. Remove the request from the active list.
    * If the taxi was "occupied", snap it to the destination, mark it "idle", and clear its assignment.
  * Else:
    * Move one step toward the destination using Manhattan moves.
    * Apply stochastic traffic delay: with probability proportional to traffic_level, add 1 step to remaining_travel_time.
* Generate new requests: _generate_new_requests:
  * Sample a number of new requests from a Poisson distribution with mean request_rate.
  * Randomly pick origins and destinations on the grid (ensuring they differ).
  * Create new Request objects with unique IDs and set arrival_time = state.time, append to state.requests.
* Update request waiting times and cancellations: _update_requests:
  * For each active request, increment waiting_time.
  * Independently cancel each request with probability cancellation_prob (set is_cancelled = True).
  * Remove cancelled requests from state.requests.
* Update traffic: _update_traffic:
  * Perform a random walk on traffic_level with small perturbations.
* Advance time
  * Increment state.time by 1.

**3.4 Observation Model**

We implement an observation model to simulate noisy and partial information:
* For each taxi, we observe:
  * id
  * A possibly noisy position (% chance of a one-step perturbation, clipped to grid bounds)
  * status
* For each request, we observe it with % probability; otherwise it is missed in the observation.
* We also observe a noisy estimate of traffic_level.

Environment.get_observation(state) returns a dictionary with keys like "taxis", "requests", and "traffic_estimate". For the planning experiments in this project, we mainly use the true state; the noisy observation model is there to demonstrate how partial observability could be integrated.

**4. Solution Methods**

We implemented and compared two dispatch policies; greedy baseline policy and Monte Carlo Tree Search (MCTS) policy. Both act on the current state and output a joint action (one Action per taxi). We also designed a reward function and metrics to evaluate performance.

**4.1 Reward Function**
The reward at each time step is:
* Positive
  * + profit_per_ride for each completed ride
* Costs
  * - travel_cost_per_step for each taxi that moved this time step
  * - wait_penalty_per_step for each active request in the next state
  * - cancel_penalty for each cancelled request
  * - idle_penalty_per_step for each idle taxi

We compute this in compute_step_reward(state, actions, next_state, info, cfg) where info is a dictionary constructed in experiments.py and contains:
* completed_rides: list of request IDs that completed this step
* cancelled_requests: list of request IDs that cancelled this step
* idle_taxis: list of taxi IDs that are idle in the next state
* moving_taxis: list of taxi IDs whose positions changed between state and next_state

The reward function itself just counts how many of each type of event happened and adds up the corresponding terms.

**4.2 Greedy Policy**

The greedy policy in greedy_policy.py works as follows:
* Start with all taxis set to "idle" actions.
* Build a list of idle taxis.
* Build a list of requests and sort it by waiting_time in descending order (longest waiting first).
* For each request in that sorted list:
  * If there are no idle taxis left, stop.
  * Find the idle taxi with the smallest Manhattan distance to the request’s origin.
  * Assign that taxi to the request (replace its action with "assign").

This policy tries to minimize current waiting time and travel distance, but it does not look ahead to future requests or traffic.

**4.3 MCTS Policy**

The MCTS policy in mcts_policy.py uses the environment as a generative model and approximates the action that maximizes expected future reward over a short horizon.
The following are key components:
* Nodes and tree - each node stores a state, a pointer to its parent, the index of the action taken from the parent, and statistics: visit count and accumulated reward.
* Candidate joint actions (generate_candidate_actions) - for a given state:
  * Start with the “all taxis idle” joint action.
  * For each idle taxi and each active request, create a joint action that assigns exactly that taxi to that request (others remain idle).
  * This keeps the branching factor manageable while still exploring meaningful assignments.
* Simulation routine (_run_simulation) - for each simulation:
  * Selection - from the root, follow child nodes using:
$$
		 			Q(s,a) / N(s,a)+ c sqrt(logN(s) / N(s,a))
$$
    where r is average reward, N is parent visits, n is child visits, and c is an exploration parameter.
  * Expansion - when a leaf node is expanded, the algorithm generates all legal joint actions for that state. For each joint action, it simulates one environment step using Environment.step, creates a child node corresponding to the resulting next state, and adds it as a child of the leaf node.
  * Rollout - from the expanded node, simulate additional random actions up to a fixed depth. Rollouts accumulate an approximate reward signal using an environment-based reward.
  * Backpropagation - propagate the total return back up the tree, updating visits and total_reward for each ancestor node.
* Action selection at the root - after running a fixed number of simulations (e.g. 50), we examine the children of the root and pick the action index with the highest average reward (total_reward / visits). The corresponding joint action is returned as the decision for the current time step.

This method is approximately optimal with respect to the truncated horizon defined by max_depth and the number of simulations. It uses the full transition model (including traffic and request arrivals) to estimate future consequences of current assignments. Although it is approximate, it consistently outperforms the greedy policy because it explicitly simulates future states and weighs delayed rewards (e.g., reducing future waiting penalties) rather than making only short-horizon (greedy) assignments.

**5. Implementation**

**5.1 Computing Decisions from Sequences of States / Observations**

Our main driver code lives in experiments.py and the runner scripts run_greedy.py and run_mcts.py.
For each episode:
* Create an Environment instance and an initial State.
* At each time step:
  * Call policy.selectAction(state) to get a joint action for all taxis.
  * Call env.step(state, actions) to get next_state.
  * Detect which requests were completed or cancelled, which taxis were idle or moved, and update an EpisodeHistory object.
  * Compute the step reward using compute_step_reward.
  * Set state = next_state and continue.

EpisodeHistory in metrics.py records, for each request, its arrival, pickup, dropoff, and cancellation times, as well as idle time for each taxi. From this history we compute:
* Average wait time
* Average idle time per taxi
* Number of completed rides
* Total revenue (sum of step rewards)

We then run many episodes for each policy and compare summaries of these metrics.
For greater ease of comparison, a basic line chart will also be plotted upon running of ‘run_mcts.py’ to observe the difference in performances of MCTS vs Greedy.

**5.2 Conclusion**

The policies operate on the true state, but the environment also provides a noisy observation model that could be used in a POMDP extension. Within the scope of this project, we treat the problem as an MDP with stochastic transitions and approximate the optimal dispatch policy using MCTS, while using a greedy baseline as a simple comparison.

Overall, the system:
* Takes in a sequence of environment states (generated from the simulator).
* Uses either a greedy heuristic or MCTS to compute actions.
* Applies those actions and the stochastic transition model to roll forward.
* Tracks rewards and metrics to evaluate how effective the decision-making is.

We defined a clear problem, specified the MDP components, implemented two planning methods (one approximate lookahead, one baseline heuristic), and demonstrated how they compute decisions and affect system performance in simulation.

**6: How to Reproduce**

1. Clone repository
2. Change parameters in `settings.py` to your liking
3. Run greedy baseline: `python run_greedy.py`
4. Run MCTS policy: `python run_mcts.py`
5. Results will be printed to console and saved as figures

The main files are:
* `environment.py`: Environment implementation
* `greedy_policy.py`: Greedy baseline
* `mcts_policy.py`: MCTS planner
* `metrics.py`: Performance tracking
* `experiments.py`: Evaluation framework
