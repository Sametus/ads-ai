import argparse
from statistics import mean

import settings
from env import Env
from sac_agent import SACAgent


def avg(rows, key):
    vals = [row[key] for row in rows if row.get(key) is not None]
    return sum(vals) / len(vals) if vals else 0.0


def run_episode(env, agent, offset, radius, target_y, max_steps, deterministic):
    _, _, state, start_info = env.reset_with_config(
        radius,
        radius,
        float(offset),
        float(offset),
        heading_offset_abs_min=0.0,
        target_y=target_y,
    )

    episode_return = 0.0
    final_info = start_info
    rows = []

    for _ in range(max_steps):
        action, _ = agent.act(state, deterministic=deterministic)
        next_state, reward, done, info = env.step(action)
        episode_return += float(reward)
        final_info = info

        rows.append({
            "step": int(info.get("step_id", 0)),
            "distance": float(info.get("distance", 0.0)),
            "theta": float(info.get("theta_deg", 0.0)),
            "closing": float(info.get("closing_speed", 0.0)),
            "a0": float(info.get("action_norm_0", 0.0)),
            "a1": float(info.get("action_norm_1", 0.0)),
            "a2": float(info.get("action_norm_2", 0.0)),
            "rel_vx": float(info.get("rel_vel_guidance_x", 0.0)),
            "rel_vz": float(info.get("rel_vel_guidance_z", 0.0)),
            "roll_error": abs(float(info.get("roll_error_deg", 0.0))),
        })

        state = next_state
        if done:
            break

    min_row = min(rows, key=lambda row: row["distance"]) if rows else {}
    min_step = int(min_row.get("step", 0))
    near = [row for row in rows if abs(row["step"] - min_step) <= 30]
    late = [row for row in rows if row["step"] >= 900]

    switches = 0
    prev_sign = None
    for row in late:
        sign = 1 if row["a0"] > 0.05 else -1 if row["a0"] < -0.05 else 0
        if sign == 0:
            continue
        if prev_sign is not None and sign != prev_sign:
            switches += 1
        prev_sign = sign

    return {
        "offset": offset,
        "done": final_info.get("done_reason") or "not_done",
        "len": int(final_info.get("step_id", len(rows))),
        "return": episode_return,
        "final_dist": float(final_info.get("distance", 0.0)),
        "final_theta": float(final_info.get("theta_deg", 0.0)),
        "final_closing": float(final_info.get("closing_speed", 0.0)),
        "min_dist": float(min_row.get("distance", 0.0)),
        "min_step": min_step,
        "min_theta": float(min_row.get("theta", 0.0)),
        "min_closing": float(min_row.get("closing", 0.0)),
        "near_a0": avg(near, "a0"),
        "near_rel_vx": avg(near, "rel_vx"),
        "near_rel_vz": avg(near, "rel_vz"),
        "near_closing": avg(near, "closing"),
        "near_roll_error": avg(near, "roll_error"),
        "late_a0": avg(late, "a0"),
        "late_abs_a0": avg([{"value": abs(row["a0"])} for row in late], "value"),
        "late_switches": switches,
        "late_n": len(late),
        "late_roll_error": avg(late, "roll_error"),
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate SAC on fixed target heading offsets.")
    parser.add_argument("--offsets", nargs="+", type=int, default=[-5, 5, -4, 4, -3, 3, -2, 2, -1, 1])
    parser.add_argument("--episodes-per-offset", type=int, default=1)
    parser.add_argument("--radius", type=float, default=700.0)
    parser.add_argument("--target-y", type=float, default=100.0)
    parser.add_argument("--max-steps", type=int, default=1200)
    parser.add_argument("--stochastic", action="store_true")
    args = parser.parse_args()

    settings.setup_gpu()
    settings.ensure_model_dir()

    agent = SACAgent()
    loaded_step = agent.load_checkpoint()
    if loaded_step == 0 and not agent.loaded_checkpoint:
        raise FileNotFoundError("SAC checkpoint bulunamadi.")

    env = Env(settings.IP, settings.PORT)
    results = []
    deterministic = not args.stochastic

    try:
        print(f"CONTROLLED_FIXED_OFFSET_TEST sac_step={loaded_step} deterministic={deterministic}", flush=True)
        for repeat in range(1, args.episodes_per_offset + 1):
            for offset in args.offsets:
                result = run_episode(env, agent, offset, args.radius, args.target_y, args.max_steps, deterministic)
                result["repeat"] = repeat
                results.append(result)
                print(
                    "OFFSET {offset:+d} rep={repeat} done={done} len={len} ret={return:.2f} "
                    "min_dist={min_dist:.2f}@{min_step} min_theta={min_theta:.1f} "
                    "min_closing={min_closing:.1f} near_a0={near_a0:.3f} "
                    "near_rel_vx={near_rel_vx:.2f} near_rel_vz={near_rel_vz:.2f} "
                    "late_a0={late_a0:.3f} late_abs_a0={late_abs_a0:.3f} "
                    "late_switches={late_switches}/{late_n} roll_near={near_roll_error:.2f}".format(**result),
                    flush=True,
                )
    finally:
        env.close()

    print("SUMMARY_BY_OFFSET", flush=True)
    for offset in sorted(set(row["offset"] for row in results)):
        arr = [row for row in results if row["offset"] == offset]
        succ = [row for row in arr if row["done"] == "success"]
        print(
            f"offset={offset:+d} n={len(arr)} success={len(succ)} "
            f"rate={len(succ) / max(len(arr), 1):.3f} "
            f"avg_min_dist={mean(row['min_dist'] for row in arr):.2f} "
            f"avg_near_rel_vx={mean(row['near_rel_vx'] for row in arr):.2f} "
            f"avg_near_a0={mean(row['near_a0'] for row in arr):.3f} "
            f"avg_roll_near={mean(row['near_roll_error'] for row in arr):.2f}",
            flush=True,
        )

    print("SUMMARY_BY_SIGN", flush=True)
    for name, pred in [("NEG", lambda row: row["offset"] < 0), ("POS", lambda row: row["offset"] > 0)]:
        arr = [row for row in results if pred(row)]
        if not arr:
            print(f"{name} n=0 success=0 rate=0.000", flush=True)
            continue
        succ = [row for row in arr if row["done"] == "success"]
        print(
            f"{name} n={len(arr)} success={len(succ)} "
            f"rate={len(succ) / max(len(arr), 1):.3f} "
            f"avg_min_dist={mean(row['min_dist'] for row in arr):.2f} "
            f"avg_near_rel_vx={mean(row['near_rel_vx'] for row in arr):.2f} "
            f"avg_near_a0={mean(row['near_a0'] for row in arr):.3f} "
            f"avg_roll_near={mean(row['near_roll_error'] for row in arr):.2f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
