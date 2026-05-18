import argparse
import csv
import glob
import os
import re
import time
from collections import defaultdict

import numpy as np

import settings
from env import Env
from sac_agent import SACAgent


DEFAULT_PREFIX = settings.SAC_MODEL_PREFIX
DEFAULT_OFFSETS = [-5.0, -3.0, 3.0, 5.0]
DEFAULT_MAX_CHECKPOINTS = 12
DEFAULT_VALID_MIN_CLOSING = -1.0
DEFAULT_VALID_MAX_THETA = 30.0
DEFAULT_VALID_MIN_ALIGNMENT = 0.866
DEFAULT_RADIUS = 700.0
DEFAULT_TARGET_Y = 100.0
DEFAULT_MAX_STEPS = 1200
DEFAULT_CHECKPOINT_PAUSE = 5.0
DEFAULT_EPISODE_PAUSE = 1.0
SAVE_INTERVAL = int(settings.SAC_SAVE_EVERY_STEPS)
START_TRAINING_STEPS = int(settings.SAC_START_TRAINING_STEPS)


def _float_or_none(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def discover_complete_steps(prefix):
    pattern = os.path.join(settings.MODELS_DIR, f"{prefix}_actor_step*.keras")
    steps = []
    for actor_path in glob.glob(pattern):
        match = re.search(r"_step(\d+)\.keras$", os.path.basename(actor_path))
        if not match:
            continue
        step_id = int(match.group(1))
        if step_id < START_TRAINING_STEPS:
            continue
        q1_path = os.path.join(settings.MODELS_DIR, f"{prefix}_q1_step{step_id}.keras")
        q2_path = os.path.join(settings.MODELS_DIR, f"{prefix}_q2_step{step_id}.keras")
        if os.path.exists(q1_path) and os.path.exists(q2_path):
            steps.append(step_id)
    return sorted(set(steps))


def _nearest_saved_step(update_id, available_steps):
    if not available_steps:
        return None
    if update_id is None:
        return None

    update_id = int(update_id)
    floor_step = (update_id // SAVE_INTERVAL) * SAVE_INTERVAL
    candidates = [step for step in available_steps if step <= floor_step]
    if candidates:
        return max(candidates)

    future_candidates = [step for step in available_steps if step >= update_id]
    if future_candidates:
        return min(future_candidates)

    return max(available_steps)


def score_steps_from_episode_log(prefix, available_steps, log_path):
    if not os.path.exists(log_path):
        return {}

    scores = defaultdict(float)
    counts = defaultdict(lambda: {"success": 0, "frontish": 0, "strict": 0, "episodes": 0})

    with open(log_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            phase_name = row.get("phase_name", "")
            if "v16_0_7" not in phase_name and prefix not in phase_name:
                continue

            update_id = _float_or_none(row.get("update_id"))
            step_id = _nearest_saved_step(update_id, available_steps)
            if step_id is None:
                continue

            done_reason = row.get("done_reason", "")
            final_closing = _float_or_none(row.get("final_closing_speed"))
            final_theta = _float_or_none(row.get("final_theta_deg"))
            final_alignment = _float_or_none(row.get("final_alignment"))
            episode_return = _float_or_none(row.get("episode_return")) or 0.0

            counts[step_id]["episodes"] += 1
            if done_reason == "success":
                counts[step_id]["success"] += 1
                scores[step_id] += 5.0 + max(-10.0, min(10.0, episode_return / 25.0))

                frontish = (
                    final_closing is not None
                    and final_theta is not None
                    and final_closing >= -4.0
                    and final_theta <= 38.0
                )
                strict = (
                    final_closing is not None
                    and final_theta is not None
                    and final_alignment is not None
                    and final_closing >= DEFAULT_VALID_MIN_CLOSING
                    and final_theta <= DEFAULT_VALID_MAX_THETA
                    and final_alignment >= DEFAULT_VALID_MIN_ALIGNMENT
                )
                if frontish:
                    counts[step_id]["frontish"] += 1
                    scores[step_id] += 50.0
                if strict:
                    counts[step_id]["strict"] += 1
                    scores[step_id] += 250.0

            elif done_reason in ("timeout", "missed_intercept"):
                scores[step_id] -= 1.0

    scored = {}
    for step_id, score in scores.items():
        # Cok az bolumle one cikmasin diye basit bir kararlilik duzeltmesi.
        scored[step_id] = score + counts[step_id]["success"] * 2.0 + counts[step_id]["frontish"] * 8.0
    return scored


def evenly_spaced_steps(available_steps, limit):
    if len(available_steps) <= limit:
        return list(available_steps)
    indexes = np.linspace(0, len(available_steps) - 1, limit).round().astype(int)
    return [available_steps[int(i)] for i in indexes]


def parse_steps(value):
    if not value:
        return None
    steps = []
    for part in value.split(","):
        part = part.strip()
        if part:
            steps.append(int(part))
    return steps


def parse_offsets(value):
    if not value:
        return list(DEFAULT_OFFSETS)
    offsets = []
    for part in value.split(","):
        part = part.strip()
        if part:
            offsets.append(float(part))
    return offsets


def choose_candidate_steps(prefix, available_steps, max_checkpoints, explicit_steps=None):
    if explicit_steps:
        available = set(available_steps)
        return [step for step in explicit_steps if step in available]

    episode_log = os.path.join("logs", "episode_log.csv")
    scores = score_steps_from_episode_log(prefix, available_steps, episode_log)

    selected = []
    if scores:
        ranked = sorted(scores, key=lambda step: (scores[step], step), reverse=True)
        selected.extend(ranked[:max_checkpoints])

    # En son checkpoint ve egitim icinden dagitilmis birkac aday da mutlaka girsin.
    if available_steps:
        selected.append(available_steps[-1])
    selected.extend(evenly_spaced_steps(available_steps, min(5, max_checkpoints)))

    deduped = []
    seen = set()
    for step in selected:
        if step not in seen:
            deduped.append(step)
            seen.add(step)
        if len(deduped) >= max_checkpoints:
            break
    return sorted(deduped)


def is_valid_intercept(info, min_closing, max_theta, min_alignment):
    trigger_hit = float(info.get("target_hit_trigger", 0.0) or 0.0) > 0.5
    ellipsoid_hit = float(info.get("target_hit_ellipsoid", 0.0) or 0.0) > 0.5
    raw_hit = trigger_hit or ellipsoid_hit or info.get("done_reason") == "success"
    target_closing = float(info.get("target_closing_speed", info.get("closing_speed", 0.0)) or 0.0)
    target_theta = float(info.get("target_theta_deg", info.get("theta_deg", 180.0)) or 180.0)
    target_alignment = float(info.get("target_alignment", info.get("alignment", -1.0)) or -1.0)

    valid = (
        raw_hit
        and target_closing >= min_closing
        and target_theta <= max_theta
        and target_alignment >= min_alignment
    )
    return valid, raw_hit, target_closing, target_theta, target_alignment


def run_episode(env, agent, offset, args):
    _, _, state, start_info = env.reset_with_config(
        args.radius,
        args.radius,
        offset,
        offset,
        heading_offset_abs_min=0.0,
        target_y=args.target_y,
    )

    episode_return = 0.0
    episode_len = 0
    done = False
    final_info = None
    min_target_distance = float("inf")
    min_distance_step = 0
    min_distance_theta = 180.0
    min_distance_closing = 0.0
    hit_step = None
    hit_info = None

    while not done and episode_len < args.max_steps:
        action, _ = agent.act(state, deterministic=True)
        next_state, reward, done, info = env.step(action)
        state = next_state
        episode_return += float(reward)
        episode_len += 1
        final_info = info

        target_distance = float(info.get("target_distance", info.get("distance", 0.0)) or 0.0)
        if target_distance < min_target_distance:
            min_target_distance = target_distance
            min_distance_step = int(info.get("step_id", episode_len) or episode_len)
            min_distance_theta = float(info.get("target_theta_deg", info.get("theta_deg", 180.0)) or 180.0)
            min_distance_closing = float(info.get("target_closing_speed", info.get("closing_speed", 0.0)) or 0.0)

        trigger_hit = float(info.get("target_hit_trigger", 0.0) or 0.0) > 0.5
        ellipsoid_hit = float(info.get("target_hit_ellipsoid", 0.0) or 0.0) > 0.5
        if hit_step is None and (trigger_hit or ellipsoid_hit):
            hit_step = int(info.get("step_id", episode_len) or episode_len)
            hit_info = dict(info)

    if final_info is None:
        final_info = start_info
        final_info["done_reason"] = "no_step"

    valid_info_source = hit_info if hit_info is not None else final_info
    valid, raw_hit, target_closing, target_theta, target_alignment = is_valid_intercept(
        valid_info_source,
        args.valid_min_closing,
        args.valid_max_theta,
        args.valid_min_alignment,
    )

    if valid:
        result = "VALID_INTERCEPT"
    elif raw_hit:
        result = "WEAK_OR_REAR_HIT"
    else:
        result = str(final_info.get("done_reason", "unknown")).upper()

    return {
        "offset": float(offset),
        "result": result,
        "valid_intercept": int(valid),
        "raw_hit": int(raw_hit),
        "done_reason": final_info.get("done_reason", "unknown"),
        "episode_len": int(episode_len),
        "episode_return": float(episode_return),
        "final_target_distance": float(final_info.get("target_distance", final_info.get("distance", 0.0)) or 0.0),
        "final_target_closing": float(final_info.get("target_closing_speed", final_info.get("closing_speed", 0.0)) or 0.0),
        "final_target_theta": float(final_info.get("target_theta_deg", final_info.get("theta_deg", 180.0)) or 180.0),
        "final_target_alignment": float(final_info.get("target_alignment", final_info.get("alignment", -1.0)) or -1.0),
        "hit_step": "" if hit_step is None else int(hit_step),
        "hit_target_closing": float(valid_info_source.get("target_closing_speed", valid_info_source.get("closing_speed", 0.0)) or 0.0),
        "hit_target_theta": float(valid_info_source.get("target_theta_deg", valid_info_source.get("theta_deg", 180.0)) or 180.0),
        "hit_target_alignment": float(valid_info_source.get("target_alignment", valid_info_source.get("alignment", -1.0)) or -1.0),
        "min_target_distance": float(min_target_distance),
        "min_distance_step": int(min_distance_step),
        "min_distance_theta": float(min_distance_theta),
        "min_distance_closing": float(min_distance_closing),
        "reset_heading_offset": float(start_info.get("reset_heading_offset", offset)),
        "reset_target_miss_distance": float(start_info.get("reset_target_miss_distance", 0.0)),
    }


def write_rows(path, rows):
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = [
        "checkpoint_step",
        "offset",
        "result",
        "valid_intercept",
        "raw_hit",
        "done_reason",
        "episode_len",
        "episode_return",
        "final_target_distance",
        "final_target_closing",
        "final_target_theta",
        "final_target_alignment",
        "hit_step",
        "hit_target_closing",
        "hit_target_theta",
        "hit_target_alignment",
        "min_target_distance",
        "min_distance_step",
        "min_distance_theta",
        "min_distance_closing",
        "reset_heading_offset",
        "reset_target_miss_distance",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def sleep_with_message(seconds, label):
    seconds = float(seconds)
    if seconds <= 0.0:
        return
    print(f"[BEKLE] {label}: {seconds:.1f} sn", flush=True)
    time.sleep(seconds)


def main():
    parser = argparse.ArgumentParser(
        description="Kayitli SAC checkpointlerini deterministik olarak hizli test eder."
    )
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--steps", default="", help="Virgulle ayrilmis checkpoint listesi. Bos kalirsa adaylar logdan secilir.")
    parser.add_argument("--max-checkpoints", type=int, default=DEFAULT_MAX_CHECKPOINTS)
    parser.add_argument("--offsets", default=",".join(str(v) for v in DEFAULT_OFFSETS))
    parser.add_argument("--radius", type=float, default=DEFAULT_RADIUS)
    parser.add_argument("--target-y", type=float, default=DEFAULT_TARGET_Y)
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
    parser.add_argument("--valid-min-closing", type=float, default=DEFAULT_VALID_MIN_CLOSING)
    parser.add_argument("--valid-max-theta", type=float, default=DEFAULT_VALID_MAX_THETA)
    parser.add_argument("--valid-min-alignment", type=float, default=DEFAULT_VALID_MIN_ALIGNMENT)
    parser.add_argument("--output", default=os.path.join("logs", "checkpoint_sweep_test.csv"))
    parser.add_argument("--checkpoint-pause", type=float, default=DEFAULT_CHECKPOINT_PAUSE)
    parser.add_argument("--episode-pause", type=float, default=DEFAULT_EPISODE_PAUSE)
    parser.add_argument("--no-stop-on-valid", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.seed)
    settings.setup_gpu()
    settings.ensure_model_dir()

    available_steps = discover_complete_steps(args.prefix)
    explicit_steps = parse_steps(args.steps)
    candidate_steps = choose_candidate_steps(
        args.prefix,
        available_steps,
        max(1, int(args.max_checkpoints)),
        explicit_steps=explicit_steps,
    )
    offsets = parse_offsets(args.offsets)

    print("=" * 100, flush=True)
    print("[CHECKPOINT SWEEP TEST]", flush=True)
    print(f"prefix={args.prefix}", flush=True)
    print(f"available_checkpoints={len(available_steps)} candidates={candidate_steps}", flush=True)
    print(
        "valid_intercept kosulu: "
        f"hit + closing>={args.valid_min_closing:.1f} + theta<={args.valid_max_theta:.1f} "
        f"+ alignment>={args.valid_min_alignment:.3f}",
        flush=True,
    )
    print(f"offsets={offsets} radius={args.radius:.1f} target_y={args.target_y:.1f}", flush=True)
    print(
        f"bekleme: checkpoint_arasi={args.checkpoint_pause:.1f} sn, "
        f"test_arasi={args.episode_pause:.1f} sn",
        flush=True,
    )

    if not candidate_steps:
        print("[HATA] Test edilecek checkpoint bulunamadi.", flush=True)
        return 1

    env = Env(settings.IP, settings.PORT)
    agent = SACAgent()
    rows = []

    exit_code = 0
    try:
        test_no = 0
        for checkpoint_index, step_id in enumerate(candidate_steps, start=1):
            print("-" * 100, flush=True)
            print(
                f"[CHECKPOINT {checkpoint_index}/{len(candidate_steps)}] "
                f"step={step_id}",
                flush=True,
            )
            if checkpoint_index > 1:
                sleep_with_message(args.checkpoint_pause, "siradaki checkpoint yuklenmeden once")

            print(f"[LOAD] checkpoint_step={step_id}", flush=True)
            agent.load_model_weights(step_id, args.prefix)

            checkpoint_rows = []
            for offset in offsets:
                test_no += 1
                print(
                    f"[TEST {test_no}] step={step_id} offset={offset:+.1f} basliyor",
                    flush=True,
                )
                result = run_episode(env, agent, offset, args)
                result["checkpoint_step"] = int(step_id)
                rows.append(result)
                checkpoint_rows.append(result)

                print(
                    f"[EP] test={test_no:<3} step={step_id:>7} off={offset:+.1f} "
                    f"{result['result']:<17} done={result['done_reason']:<16} "
                    f"len={result['episode_len']:>4} ret={result['episode_return']:>7.1f} "
                    f"hit_step={result['hit_step']} "
                    f"hit_close={result['hit_target_closing']:>6.1f} "
                    f"hit_theta={result['hit_target_theta']:>5.1f} "
                    f"min_dist={result['min_target_distance']:>6.1f}@{result['min_distance_step']}",
                    flush=True,
                )

                if result["valid_intercept"] and not args.no_stop_on_valid:
                    write_rows(args.output, rows)
                    print("[BULUNDU] Gecerli one-yaklasimli intercept bulundu; erken duruyorum.", flush=True)
                    return 0

                sleep_with_message(args.episode_pause, "siradaki test baslamadan once")

            valid_count = sum(row["valid_intercept"] for row in checkpoint_rows)
            raw_hit_count = sum(row["raw_hit"] for row in checkpoint_rows)
            weak_count = raw_hit_count - valid_count
            avg_min_dist = float(np.mean([row["min_target_distance"] for row in checkpoint_rows]))
            avg_hit_closing = float(np.mean([row["hit_target_closing"] for row in checkpoint_rows if row["raw_hit"]])) if raw_hit_count else 0.0
            print(
                f"[CKPT] step={step_id} valid={valid_count}/{len(checkpoint_rows)} "
                f"raw_hit={raw_hit_count}/{len(checkpoint_rows)} weak_or_rear={weak_count} "
                f"avg_min_dist={avg_min_dist:.1f} avg_hit_closing={avg_hit_closing:.1f}",
                flush=True,
            )

        write_rows(args.output, rows)
        best_rows = sorted(
            rows,
            key=lambda row: (
                row["valid_intercept"],
                row["raw_hit"],
                row["hit_target_closing"],
                -row["hit_target_theta"],
                -row["min_target_distance"],
            ),
            reverse=True,
        )
        print("=" * 100, flush=True)
        print("[EN IYI ADAYLAR]", flush=True)
        for row in best_rows[:8]:
            print(
                f"step={row['checkpoint_step']} off={row['offset']:+.1f} "
                f"{row['result']} hit_close={row['hit_target_closing']:.1f} "
                f"hit_theta={row['hit_target_theta']:.1f} min_dist={row['min_target_distance']:.1f}",
                flush=True,
            )
        print(f"[CSV] {args.output}", flush=True)
    except (ConnectionError, ConnectionResetError, OSError) as exc:
        exit_code = 2
        print("=" * 100, flush=True)
        print(f"[UNITY BAGLANTI KOPTU] {type(exc).__name__}: {exc}", flush=True)
        print("Unity Play mode'u bir kez stop/play yapip ayni komutu tekrar calistir.", flush=True)
        if rows:
            print(f"[PARTIAL] Su ana kadar tamamlanan test sayisi: {len(rows)}", flush=True)
    finally:
        if rows:
            write_rows(args.output, rows)
            print(f"[CSV] {args.output}", flush=True)
        env.close()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
