import argparse
from collections import Counter

import numpy as np

from env import ACTION_KEYS, ACTIVE_PHASE_CONFIG, CONTROL_MODE, Env


def make_action(policy, rng):
    action_size = len(ACTION_KEYS)

    if policy == "zero":
        return np.zeros(action_size, dtype=np.float32)
    if policy == "random":
        return rng.uniform(-1.0, 1.0, size=action_size).astype(np.float32)
    if policy == "forward":
        action = np.zeros(action_size, dtype=np.float32)
        action[-1] = 1.0
        return action

    raise ValueError(f"Bilinmeyen policy: {policy}")


def run_episode(env, policy, rng, max_steps):
    _, _, state, start_info = env.reset()
    episode_return = 0.0
    final_info = start_info

    for _ in range(max_steps):
        action = make_action(policy, rng)
        state, reward, done, info = env.step(action)
        episode_return += float(reward)
        final_info = info
        if done:
            break

    return {
        "done_reason": final_info.get("done_reason") or "not_done",
        "episode_return": episode_return,
        "episode_len": final_info.get("step_id", 0),
        "start_distance": start_info.get("distance", 0.0),
        "final_distance": final_info.get("distance", 0.0),
        "final_theta_deg": final_info.get("theta_deg", 0.0),
        "final_alignment": final_info.get("alignment", 0.0),
    }


def main():
    parser = argparse.ArgumentParser(
        description="SAC olmadan sabit/random action baseline kosar."
    )
    parser.add_argument("--policy", choices=["zero", "random", "forward"], default="zero")
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--max-steps", type=int, default=800)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    print(f"Phase: {ACTIVE_PHASE_CONFIG['name']}")
    print(f"Control mode: {CONTROL_MODE}")
    print(f"Action keys: {ACTION_KEYS}")
    print("")

    env = Env(args.ip, args.port)
    results = []

    try:
        for episode_index in range(1, args.episodes + 1):
            result = run_episode(env, args.policy, rng, args.max_steps)
            results.append(result)
            print(
                "[BASELINE {idx:03d}] policy={policy} done={done} len={length} "
                "return={ret:.3f} dist={dist:.3f} theta={theta:.2f} align={align:.3f}".format(
                    idx=episode_index,
                    policy=args.policy,
                    done=result["done_reason"],
                    length=result["episode_len"],
                    ret=result["episode_return"],
                    dist=result["final_distance"],
                    theta=result["final_theta_deg"],
                    align=result["final_alignment"],
                ),
                flush=True,
            )
    finally:
        env.close()

    counts = Counter(result["done_reason"] for result in results)
    success_count = counts.get("success", 0)
    print("")
    print(f"Policy: {args.policy}")
    print(f"Episodes: {len(results)}")
    print(f"Done reasons: {dict(counts)}")
    print(f"Success rate: {success_count}/{len(results)} = {success_count / max(len(results), 1):.3f}")


if __name__ == "__main__":
    main()
