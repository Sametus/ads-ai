import argparse
import csv
import os
import time

import numpy as np

from env import Env


DEFAULT_OUTPUT = os.path.join("logs", "action_axis_test.csv")
EPS = 1e-6


COMMANDS = {
    # thrust_only sadece itki eksenini ve rocketPoint/body eksen uyumunu kontrol eder.
    "thrust_only": {
        "channels": [0.0, 0.0, 0.0, 0.0],
        "axis": "none",
        "expected_sign": 0.0,
        "pre_channels": None,
        "pre_steps": 0,
    },
    # Clock 12 gravity-up yonudur; burun yukari donmeye baslamali.
    "clock_12": {
        "channels": [1.0, 0.0, 0.0, 0.0],
        "axis": "clock12",
        "expected_sign": 1.0,
        "pre_channels": None,
        "pre_steps": 0,
    },
    # Clock 6 clock-12'nin tersidir; burun asagi donmeye baslamali.
    "clock_6": {
        "channels": [0.0, 1.0, 0.0, 0.0],
        "axis": "clock12",
        "expected_sign": -1.0,
        "pre_channels": None,
        "pre_steps": 0,
    },
    # Clock 3 yatay clock ekseninin pozitif tarafidir.
    "clock_3": {
        "channels": [0.0, 0.0, 1.0, 0.0],
        "axis": "clock3",
        "expected_sign": 1.0,
        "pre_channels": None,
        "pre_steps": 0,
    },
    # Clock 9 clock-3'un tersidir.
    "clock_9": {
        "channels": [0.0, 0.0, 0.0, 1.0],
        "axis": "clock3",
        "expected_sign": -1.0,
        "pre_channels": None,
        "pre_steps": 0,
    },
    # Roket dik kalkista gravity-up ile ayni hatta oldugu icin clock-12 tekil kalabilir.
    # Bu test once roketi clock-6 ile eger, sonra clock-12 toparlama isaretini olcer.
    "clock_12_after_clock_6": {
        "channels": [1.0, 0.0, 0.0, 0.0],
        "axis": "clock12",
        "expected_sign": 1.0,
        "pre_channels": [0.0, 1.0, 0.0, 0.0],
        "pre_steps": 60,
    },
}


def default_summary_output(step_output):
    """Adim CSV yolundan ozet CSV yolunu turetir."""
    root, ext = os.path.splitext(step_output)
    return f"{root}_summary{ext or '.csv'}"


def safe_float(info, key, default=0.0):
    """Eksik telemetry alanini testi durdurmadan sayiya cevirir."""
    try:
        return float(info.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def parse_command_list(value):
    """Komut listesini virgullu metinden okur."""
    names = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [name for name in names if name not in COMMANDS]
    if unknown:
        raise ValueError(f"Bilinmeyen command: {unknown}. Gecerli: {list(COMMANDS)}")
    return names


def build_action(command_name, thrust, turn_strength, step_id):
    """Sabit test komutunu Unity action formatina cevirir."""
    command = COMMANDS[command_name]
    channels = command["channels"]
    if step_id <= int(command.get("pre_steps", 0)) and command.get("pre_channels") is not None:
        channels = command["pre_channels"]
    scaled_channels = [turn_strength * value for value in channels]
    return [float(thrust)] + scaled_channels


def open_csv(path, fieldnames):
    """CSV klasorunu olusturur ve writer hazirlar."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    handle = open(path, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    return handle, writer


def append_step_row(writer, command_name, episode_index, info):
    """Her fizik adimini yazar; sonradan eksen isareti buradan kontrol edilir."""
    writer.writerow(
        {
            "command": command_name,
            "episode_index": episode_index,
            "episode_id": info.get("episode_id"),
            "step_id": info.get("step_id"),
            "done_reason": info.get("done_reason"),
            "distance": info.get("distance"),
            "theta_deg": info.get("theta_deg"),
            "agl": info.get("agl"),
            "thrust": info.get("thrust"),
            "clock_12_cmd": info.get("clock_12_cmd"),
            "clock_6_cmd": info.get("clock_6_cmd"),
            "clock_3_cmd": info.get("clock_3_cmd"),
            "clock_9_cmd": info.get("clock_9_cmd"),
            "action_clock12_raw": info.get("action_clock12_raw"),
            "action_clock3_raw": info.get("action_clock3_raw"),
            "action_clock12_net": info.get("action_clock12_net"),
            "action_clock3_net": info.get("action_clock3_net"),
            "measured_turn_clock12": info.get("rocket_turn_clock_signed_x"),
            "measured_turn_clock3": info.get("rocket_turn_clock_signed_y"),
            "measured_roll_rate": info.get("rocket_turn_clock_signed_z"),
            "low_altitude_turn_scale": info.get("low_altitude_turn_scale"),
            "clock12_scale": info.get("clock12_scale"),
            "clock3_scale": info.get("clock3_scale"),
            "beta_validity_applied": info.get("beta_validity_applied"),
            "roll_control_scale": info.get("roll_control_scale"),
            "roll_correction_cmd": info.get("roll_correction_cmd"),
            "roll_correction_limit": info.get("roll_correction_limit"),
            "roll_torque_limit": info.get("roll_torque_limit"),
            "suppressed_roll_rate": info.get("suppressed_roll_rate"),
            "torque_local_x": info.get("torque_command_local_x"),
            "torque_local_y": info.get("torque_command_local_y"),
            "torque_local_z": info.get("torque_command_local_z"),
            "command_turn_local_x": info.get("command_turn_local_x"),
            "command_turn_local_y": info.get("command_turn_local_y"),
            "command_turn_local_z": info.get("command_turn_local_z"),
            "rocket_point_body_forward_dot": info.get("rocket_point_body_forward_dot"),
            "rocket_point_body_up_dot": info.get("rocket_point_body_up_dot"),
            "rocket_point_body_right_dot": info.get("rocket_point_body_right_dot"),
        }
    )


def summarize_rows(rows, command_name, turn_threshold):
    """Bir komut icin ortalama tepkiyi hesaplar."""
    command = COMMANDS[command_name]
    axis = command["axis"]
    expected_sign = command["expected_sign"]

    mean_turn12 = float(np.mean([row["turn12"] for row in rows])) if rows else 0.0
    mean_turn3 = float(np.mean([row["turn3"] for row in rows])) if rows else 0.0
    mean_roll = float(np.mean([row["roll"] for row in rows])) if rows else 0.0
    mean_net12 = float(np.mean([row["net12"] for row in rows])) if rows else 0.0
    mean_net3 = float(np.mean([row["net3"] for row in rows])) if rows else 0.0
    mean_suppressed_roll = float(np.mean([row["suppressed_roll"] for row in rows])) if rows else 0.0
    mean_body_forward_dot = float(np.mean([row["body_forward_dot"] for row in rows])) if rows else 0.0

    measured_value = 0.0
    sign_ok = True
    strength_ok = True
    if axis == "clock12":
        measured_value = mean_turn12
        sign_ok = expected_sign * measured_value > 0.0
        strength_ok = abs(measured_value) >= turn_threshold
    elif axis == "clock3":
        measured_value = mean_turn3
        sign_ok = expected_sign * measured_value > 0.0
        strength_ok = abs(measured_value) >= turn_threshold

    return {
        "axis": axis,
        "expected_sign": expected_sign,
        "mean_turn12": mean_turn12,
        "mean_turn3": mean_turn3,
        "mean_roll": mean_roll,
        "mean_net12": mean_net12,
        "mean_net3": mean_net3,
        "mean_suppressed_roll_rate": mean_suppressed_roll,
        "measured_value": measured_value,
        "sign_ok": int(bool(sign_ok)),
        "strength_ok": int(bool(strength_ok)),
        "mean_body_forward_dot": mean_body_forward_dot,
    }


def run(args):
    commands = parse_command_list(args.commands)
    summary_output = args.summary_output or default_summary_output(args.output)

    step_fields = [
        "command",
        "episode_index",
        "episode_id",
        "step_id",
        "done_reason",
        "distance",
        "theta_deg",
        "agl",
        "thrust",
        "clock_12_cmd",
        "clock_6_cmd",
        "clock_3_cmd",
        "clock_9_cmd",
        "action_clock12_raw",
        "action_clock3_raw",
        "action_clock12_net",
        "action_clock3_net",
        "measured_turn_clock12",
        "measured_turn_clock3",
        "measured_roll_rate",
        "low_altitude_turn_scale",
        "clock12_scale",
        "clock3_scale",
        "beta_validity_applied",
        "roll_control_scale",
        "roll_correction_cmd",
        "roll_correction_limit",
        "roll_torque_limit",
        "suppressed_roll_rate",
        "torque_local_x",
        "torque_local_y",
        "torque_local_z",
        "command_turn_local_x",
        "command_turn_local_y",
        "command_turn_local_z",
        "rocket_point_body_forward_dot",
        "rocket_point_body_up_dot",
        "rocket_point_body_right_dot",
    ]

    summary_fields = [
        "command",
        "episode_index",
        "steps_used",
        "final_done_reason",
        "final_distance",
        "final_theta_deg",
        "final_agl",
        "axis",
        "expected_sign",
        "measured_value",
        "mean_turn12",
        "mean_turn3",
        "mean_roll",
        "mean_net12",
        "mean_net3",
        "mean_suppressed_roll_rate",
        "sign_ok",
        "strength_ok",
        "mean_body_forward_dot",
    ]

    env = Env(args.ip, args.port)
    step_file, step_writer = open_csv(args.output, step_fields)
    summary_file, summary_writer = open_csv(summary_output, summary_fields)

    try:
        for command_name in commands:
            for episode_index in range(1, args.episodes_per_command + 1):
                _, _, _, info = env.reset_with_config(
                    radius_min=args.radius_min,
                    radius_max=args.radius_max,
                    heading_offset_min=args.heading_offset_min,
                    heading_offset_max=args.heading_offset_max,
                    heading_offset_abs_min=args.heading_offset_abs_min,
                    target_y=args.target_y,
                )

                rows_for_summary = []
                final_info = dict(info)
                done = False

                print(
                    f"[AXIS RESET] command={command_name} ep={episode_index}/{args.episodes_per_command} "
                    f"radius={info['distance']:.2f} heading={info['reset_heading_offset']:.2f}"
                )

                while not done and env.step_count < args.steps:
                    next_step_id = int(env.step_count) + 1
                    action = build_action(command_name, args.thrust, args.turn_strength, next_step_id)
                    _, _, _, done, info = env.step_direct_action(action, action_label=f"axis_{command_name}")
                    final_info = dict(info)
                    append_step_row(step_writer, command_name, episode_index, info)

                    # Ilk adimlarda rigidbody henuz tepkiyi biriktirmemis olabilir; o yuzden warmup sonrasi olceriz.
                    main_phase_start = int(COMMANDS[command_name].get("pre_steps", 0)) + args.warmup_steps
                    if int(info.get("step_id", 0)) >= main_phase_start:
                        rows_for_summary.append(
                            {
                                "turn12": safe_float(info, "rocket_turn_clock_signed_x"),
                                "turn3": safe_float(info, "rocket_turn_clock_signed_y"),
                                "roll": safe_float(info, "rocket_turn_clock_signed_z"),
                                "net12": safe_float(info, "action_clock12_net"),
                                "net3": safe_float(info, "action_clock3_net"),
                                "suppressed_roll": safe_float(info, "suppressed_roll_rate"),
                                "body_forward_dot": safe_float(info, "rocket_point_body_forward_dot"),
                            }
                        )

                    if args.step_delay > 0.0:
                        time.sleep(args.step_delay)

                summary = summarize_rows(rows_for_summary, command_name, args.turn_threshold)
                summary_writer.writerow(
                    {
                        "command": command_name,
                        "episode_index": episode_index,
                        "steps_used": final_info.get("step_id"),
                        "final_done_reason": final_info.get("done_reason"),
                        "final_distance": final_info.get("distance"),
                        "final_theta_deg": final_info.get("theta_deg"),
                        "final_agl": final_info.get("agl"),
                        **summary,
                    }
                )

                status = "OK" if summary["sign_ok"] and summary["strength_ok"] else "WARN"
                print(
                    f"[AXIS {status}] command={command_name:<11} axis={summary['axis']:<7} "
                    f"mean_turn12={summary['mean_turn12']:+.4f} "
                    f"mean_turn3={summary['mean_turn3']:+.4f} "
                    f"body_forward_dot={summary['mean_body_forward_dot']:+.4f} "
                    f"reason={final_info.get('done_reason')}"
                )

        print("=" * 80)
        print("[AXIS SUMMARY]")
        print(f"Step CSV    : {args.output}")
        print(f"Summary CSV : {summary_output}")
        print("Yorumlama   : clock_12/3 pozitif, clock_6/9 negatif isaret vermeli.")
    finally:
        step_file.close()
        summary_file.close()


def build_parser():
    parser = argparse.ArgumentParser(description="Unity action eksenlerini sabit komutlarla test eder.")
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--commands", default="thrust_only,clock_12,clock_6,clock_3,clock_9,clock_12_after_clock_6")
    parser.add_argument("--episodes-per-command", type=int, default=1)
    parser.add_argument("--steps", type=int, default=120)
    parser.add_argument("--warmup-steps", type=int, default=15)
    parser.add_argument("--thrust", type=float, default=900.0)
    parser.add_argument("--turn-strength", type=float, default=1.0)
    parser.add_argument("--turn-threshold", type=float, default=0.01)
    parser.add_argument("--radius-min", type=float, default=140.0)
    parser.add_argument("--radius-max", type=float, default=160.0)
    parser.add_argument("--heading-offset-min", type=float, default=-5.0)
    parser.add_argument("--heading-offset-max", type=float, default=5.0)
    parser.add_argument("--heading-offset-abs-min", type=float, default=2.0)
    parser.add_argument("--target-y", type=float, default=50.0)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", default=None)
    parser.add_argument("--step-delay", type=float, default=0.0)
    return parser


if __name__ == "__main__":
    run(build_parser().parse_args())
