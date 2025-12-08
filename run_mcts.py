# run_mcts.py

import numpy as np
import matplotlib.pyplot as plt
from environment import Environment
from reward import RewardConfiguration, computeStepReward
from greedy_policy import GreedyPolicy, GreedyConfiguration
from mcts_policy import MCTSPolicy
from metrics import EpisodeHistory, summarizedMetrics

reward_config = RewardConfiguration()

def run_episode(env, policy, horizon=100):
    state = env.create_initial_state()
    history = EpisodeHistory()
    total_reward = 0.0

    for t in range(horizon):
        history.noteNewRequests(state.requests)

        action = policy.selectAction(state)

        next_state = env.step(state, action)
        info = env.get_last_step_info()
        
        step_reward = computeStepReward(state, action, next_state, info, reward_config)
        total_reward += step_reward
        
        history.notePickups(t, info.get("picked_up_requests", []))
        history.noteDropoffs(t, info.get("completed_rides", []))
        history.noteCancellations(t, info.get("cancelled_requests", []))
        history.noteIdleTaxis(t, info.get("idle_taxis", []))

        state = next_state

    metrics = summarizedMetrics(history)
    metrics["total_reward"] = total_reward
    return metrics, total_reward


def run_experiment(num_episodes=20, horizon=100, mcts_iterations=100):
    #comp btwn greedy and mcts

    env = Environment(grid_size=10, num_taxis=5, request_rate=2.0, cancellation_prob=0.2)

    greedy_config = GreedyConfiguration()
    greedy_policy = GreedyPolicy(greedy_config, env)
    mcts_policy = MCTSPolicy(env, iterations=mcts_iterations)

    mcts_rewards = []
    greedy_rewards = []
    mcts_metrics = []
    greedy_metrics = []

    print("-" * 30)
    print(f"Running {num_episodes} episodes (horizon={horizon})")
    print(f"MCTS iterations per step: {mcts_iterations}")
    print("-" * 30)

    for i in range(num_episodes):
        # Reset request counter for fair comparison
        env.request_counter = 0
        metrics_m, mcts_r = run_episode(env, mcts_policy, horizon)
        
        env.request_counter = 0
        metrics_g, greedy_r = run_episode(env, greedy_policy, horizon)

        mcts_rewards.append(mcts_r)
        greedy_rewards.append(greedy_r)
        mcts_metrics.append(metrics_m)
        greedy_metrics.append(metrics_g)

        print(f"Episode {i+1} | MCTS: {mcts_r:7.2f} | Greedy: {greedy_r:7.2f} | "
              f"Diff: {mcts_r - greedy_r:+7.2f}")

    # Plot results
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(mcts_rewards, label="MCTS", marker='o')
    plt.plot(greedy_rewards, label="Greedy", marker='s')
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("MCTS vs Greedy Performance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_experiment(
        num_episodes=5,      
        horizon=50,         
        mcts_iterations=50   
    ) #changed for quicker runs, amend as needed