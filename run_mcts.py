# run_mcts.py

import matplotlib.pyplot as plt
import random
import numpy as np
from environment import Environment
from reward import RewardConfiguration, computeStepReward
from greedy_policy import GreedyPolicy, GreedyConfiguration
from mcts_policy import MCTSPolicy
from metrics import EpisodeHistory, summarizedMetrics

from settings import (
    GRID_SIZE,
    NUM_TAXIS,
    REQUEST_RATE,
    CANCELLATION_PROB,
    EPISODES,
    HORIZON,
    MCTS_ITERATIONS,
)

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


def run_experiment(num_episodes=EPISODES, horizon=HORIZON, mcts_iterations=MCTS_ITERATIONS):
    # comp btwn greedy and mcts
    
    greedy_config = GreedyConfiguration()
    
    mcts_rewards = []
    greedy_rewards = []
    mcts_metrics = []
    greedy_metrics = []

    print("-" * 30)
    print(f"Running {num_episodes} episodes (horizon={horizon})")
    print(f"MCTS iterations per step: {mcts_iterations}")
    print("-" * 30)

    for i in range(num_episodes):
       
        env_mcts = Environment(
            grid_size=GRID_SIZE,
            num_taxis=NUM_TAXIS,
            request_rate=REQUEST_RATE,
            cancellation_prob=CANCELLATION_PROB,
        )
        mcts_policy = MCTSPolicy(env_mcts, iterations=mcts_iterations)
        metrics_m, mcts_r = run_episode(env_mcts, mcts_policy, horizon)
        
        env_greedy = Environment(
            grid_size=GRID_SIZE,
            num_taxis=NUM_TAXIS,
            request_rate=REQUEST_RATE,
            cancellation_prob=CANCELLATION_PROB,
        )
        greedy_policy = GreedyPolicy(greedy_config, env_greedy)
        metrics_g, greedy_r = run_episode(env_greedy, greedy_policy, horizon)

        mcts_rewards.append(mcts_r)
        greedy_rewards.append(greedy_r)
        mcts_metrics.append(metrics_m)
        greedy_metrics.append(metrics_g)

        print(
            f"Episode {i+1:2d} | MCTS: {mcts_r:7.2f} | Greedy: {greedy_r:7.2f} | "
            f"Diff: {mcts_r - greedy_r:+7.2f}"
        )
    
    # summary 
    print("\n" + "-"*30)
    print("SUMMARY STATISTICS")
    print("-"* 30)
    print(f"MCTS   Mean: {np.mean(mcts_rewards):7.2f} ± {np.std(mcts_rewards):6.2f}")
    print(f"Greedy Mean: {np.mean(greedy_rewards):7.2f} ± {np.std(greedy_rewards):6.2f}")
    print(f"Difference:  {np.mean(mcts_rewards) - np.mean(greedy_rewards):+7.2f}")

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

run_experiment(num_episodes=EPISODES, horizon=HORIZON, mcts_iterations=MCTS_ITERATIONS)