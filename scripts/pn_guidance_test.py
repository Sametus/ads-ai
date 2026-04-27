import argparse
import csv
import os
import time

import numpy as np

from env import Env


DEFAULT_OUTPUT = os.path.join("logs", "pn_guidance_test.csv")
EPS = 1e-6


def default_summary_output(step_output):
    """Adim CSV yolundan episode ozet CSV yolunu turetir."""
    root, ext = os.path.splitext(step_output)
    return f"{root}_summary{ext or '.csv'}"


def read_vec(info, prefix):
    """Log bilgisinden x/y/z vektorunu okur; telemetry eksikse sifir vektor doner."""
    return np.asarray(
        [
            float(info.get(f"{prefix}_x", 0.0)),
            float(info.get(f"{prefix}_y", 0.0)),
            float(info.get(f"{prefix}_z", 0.0)),
        ],
        dtype=np.float32,
    )


def unit_or_zero(value):
    """Vektoru guvenli sekilde birim vektore cevirir."""
    norm = float(np.linalg.norm(value))
    if norm <= EPS:
        return np.zeros(3, dtype=np.float32)
    return (value / norm).astype(np.float32)


def project_on_plane(value, normal):
    """Bir vektoru roket burnuna dik clock duzlemine indirger."""
    normal_u = unit_or_zero(normal)
    if np.linalg.norm(normal_u) <= EPS:
        return value.astype(np.float32)
    return (value - (np.dot(value, normal_u) * normal_u)).astype(np.float32)


def clamp_magnitude(value, max_magnitude):
    """Vektor buyuklugunu fiziksel limitte tutar; yon bilgisini bozmaz."""
    magnitude = float(np.linalg.norm(value))
    if magnitude <= EPS or magnitude <= max_magnitude:
        return value.astype(np.float32), False
    return (value * (max_magnitude / magnitude)).astype(np.float32), True


def lead_intercept_direction(rel_pos, target_vel, command_speed):
    """
    Basit onleme (lead) yonu hesaplar.

    Hedef sabit hizla giderse ve roket yaklasik command_speed ile ilerlerse
    kesisim noktasinin nerede olacagini tahmin eder. Cozum cikmazsa dogrudan
    hedef yonune doner; bu sadece PN testini daha okunur ve guvenli yapar.
    """
    speed = max(float(command_speed), EPS)
    a = float(np.dot(target_vel, target_vel) - (speed * speed))
    b = float(2.0 * np.dot(rel_pos, target_vel))
    c = float(np.dot(rel_pos, rel_pos))

    t_go = 0.0
    if abs(a) <= EPS:
        if abs(b) > EPS:
            candidate = -c / b
            if candidate > 0.0:
                t_go = candidate
    else:
        disc = (b * b) - (4.0 * a * c)
        if disc >= 0.0:
            root = float(np.sqrt(disc))
            candidates = [(-b - root) / (2.0 * a), (-b + root) / (2.0 * a)]
            positives = [value for value in candidates if value > 0.0]
            if positives:
                t_go = min(positives)

    aim_point = rel_pos + (target_vel * t_go)
    return unit_or_zero(aim_point), t_go


def positive_negative_channels(clock12_net, clock3_net):
    """Net clock komutlarini Unity'nin pozitif kanal yapisina ayirir."""
    return [
        max(0.0, clock12_net),
        max(0.0, -clock12_net),
        max(0.0, clock3_net),
        max(0.0, -clock3_net),
    ]


def build_pn_action(info, args):
    """
    PN (Proportional Navigation / oransal gudum) komutunu hesaplar.

    Temel fikir: hedefin gorus cizgisi ne tarafa kayiyorsa roket burnu o kaymayi
    azaltacak tarafa dondurulur. Bu test RL degil; sadece sahnenin klasik gudumle
    vurulabilir olup olmadigini kontrol eder.
    """
    rel_pos = read_vec(info, "rel_pos_world")
    rel_vel = read_vec(info, "rel_vel_world")
    rocket_vel = read_vec(info, "rocket_vel_world")
    target_vel = read_vec(info, "target_vel_world")
    gravity = read_vec(info, "gravity_world")
    clock12 = read_vec(info, "clock_12_world")
    clock3 = read_vec(info, "clock_3_world")
    clock_forward = read_vec(info, "clock_forward_world")
    agl = float(info.get("agl", 0.0))
    rocket_vy = float(rocket_vel[1])

    if np.linalg.norm(target_vel) <= EPS:
        target_vel = rel_vel + rocket_vel
    if np.linalg.norm(gravity) <= EPS:
        gravity = np.asarray([0.0, -9.81, 0.0], dtype=np.float32)

    distance = max(float(np.linalg.norm(rel_pos)), EPS)
    los_dir = unit_or_zero(rel_pos)
    closing_speed = max(-float(np.dot(rel_vel, los_dir)), 0.0)

    # LOS rate: hedef gorus cizgisinin uzayda ne kadar hizli dondgunu anlatir.
    los_rate = np.cross(rel_pos, rel_vel) / max(distance * distance, EPS)
    # pn_sign sadece PN/lead bilesenini terslemek icindir.
    # Pursuit dogru calisirken blend bozuluyorsa bu parametre lead isaretini izole eder.
    pn_lateral = args.pn_sign * args.navigation_gain * closing_speed * np.cross(los_rate, los_dir)

    # Saf takip: roket burnunu dogrudan hedefin bulundugu clock yonune cevirir.
    target_lateral = project_on_plane(rel_pos, clock_forward)
    pursuit_vec = unit_or_zero(target_lateral)
    pn_vec = project_on_plane(pn_lateral, clock_forward)
    pn_dir = unit_or_zero(pn_vec)
    lead_weight = 1.0
    rocket_speed = float(np.linalg.norm(rocket_vel))
    accel_debug = {
        "pn_accel_limit": 0.0,
        "pn_limited_accel_mag": 0.0,
        "pn_accel_saturated": 0,
        "gross_accel": 0.0,
        "gravity_comp_accel": 0.0,
        "lead_t_go": 0.0,
        "lead_dir_dot_los": 0.0,
        "desired_accel_clock12": 0.0,
        "desired_accel_clock3": 0.0,
        "velocity_error_mag": 0.0,
        "velocity_correction_mag": 0.0,
        "velocity_correction_saturated": 0,
        "loft_factor": 0.0,
        "loft_accel_mag": 0.0,
    }

    # Mod secimi test icindir: once hangi mantigin sahnede ise yaradigini goruruz.
    if args.mode == "pursuit":
        command_vec = pursuit_vec
    elif args.mode == "pn":
        command_vec = pn_dir
    elif args.mode == "accel":
        # Gercek PN dogrudan "clock yonu" degil, yanal ivme komutu uretir.
        # Burada o ivmeyi thrust/mass limitine gore kisip, roket burnunun izleyecegi
        # istenen ivme yonune ceviriyoruz. Boylece test, kaynaklardaki PN zincirine
        # daha yakin olur: guidance -> acceleration command -> attitude/autopilot.
        gross_accel = max(float(args.thrust) / max(float(args.rocket_mass), EPS), EPS)
        gravity_mag = float(np.linalg.norm(gravity))
        gravity_up = unit_or_zero(-gravity)
        gravity_comp_accel = min(args.gravity_comp * gravity_mag, args.max_up_comp_fraction * gross_accel)

        auto_limit = np.sqrt(max((gross_accel * gross_accel) - (gravity_comp_accel * gravity_comp_accel), 0.0))
        pn_accel_limit = float(args.pn_accel_limit)
        if pn_accel_limit <= 0.0:
            pn_accel_limit = auto_limit * args.lateral_accel_fraction
        pn_limited, pn_saturated = clamp_magnitude(pn_lateral, pn_accel_limit)

        command_speed = max(args.intercept_speed_floor, rocket_speed)
        lead_dir, lead_t_go = lead_intercept_direction(rel_pos, target_vel, command_speed)
        if np.linalg.norm(lead_dir) <= EPS:
            lead_dir = los_dir

        # Burnun hedefe bakmasi tek basina yetmez; hiz vektoru de onleme hattina oturmali.
        # Bu duzeltme roketin 20-30m disaridan akip gecmesini azaltmak icin,
        # mevcut hiz ile istenen lead hiz yonu arasindaki farki ivme istegine cevirir.
        desired_velocity = lead_dir * command_speed
        velocity_error = desired_velocity - rocket_vel
        velocity_correction_raw = velocity_error * args.velocity_track_gain
        velocity_limit = auto_limit * args.velocity_accel_fraction
        velocity_correction, velocity_saturated = clamp_magnitude(velocity_correction_raw, velocity_limit)

        # Uzak menzilde roketin cok erken yatip irtifa kaybetmesini istemiyoruz.
        # Loft bias sadece uzaktayken ve AGL hedefin altindayken hafif yukari destek verir.
        loft_span = max(args.loft_fade_start - args.loft_fade_end, EPS)
        range_factor = float(np.clip((distance - args.loft_fade_end) / loft_span, 0.0, 1.0))
        altitude_factor = float(np.clip((args.loft_agl - agl) / max(args.loft_agl, EPS), 0.0, 1.0))
        loft_factor = range_factor * altitude_factor
        loft_accel = gravity_up * gross_accel * args.loft_weight * loft_factor

        desired_accel_dir = (
            args.accel_lead_weight * lead_dir
            + args.accel_pursuit_weight * los_dir
            + args.accel_pn_weight * (pn_limited / gross_accel)
            + (velocity_correction / gross_accel)
            + (loft_accel / gross_accel)
            + ((gravity_up * gravity_comp_accel) / gross_accel)
        )
        command_vec = project_on_plane(desired_accel_dir, clock_forward)
        lead_weight = args.accel_lead_weight
        accel_debug = {
            "pn_accel_limit": pn_accel_limit,
            "pn_limited_accel_mag": float(np.linalg.norm(pn_limited)),
            "pn_accel_saturated": int(bool(pn_saturated)),
            "gross_accel": gross_accel,
            "gravity_comp_accel": gravity_comp_accel,
            "lead_t_go": float(lead_t_go),
            "lead_dir_dot_los": float(np.dot(lead_dir, los_dir)),
            "desired_accel_clock12": float(np.dot(unit_or_zero(command_vec), unit_or_zero(clock12))),
            "desired_accel_clock3": float(np.dot(unit_or_zero(command_vec), unit_or_zero(clock3))),
            "velocity_error_mag": float(np.linalg.norm(velocity_error)),
            "velocity_correction_mag": float(np.linalg.norm(velocity_correction)),
            "velocity_correction_saturated": int(bool(velocity_saturated)),
            "loft_factor": float(loft_factor),
            "loft_accel_mag": float(np.linalg.norm(loft_accel)),
        }
    else:
        # Lead uzakta hedefin onunu kesmeye yardim eder; yakinda ise burnu hedefe kilitlemek daha onemlidir.
        # Bu nedenle mesafe azaldikca PN/lead agirligini azaltip pursuit'e yumusak gecis yapiyoruz.
        # PN vektorunun ham buyuklugu pursuit'i ezmesin diye sadece yonu kullanilir.
        fade_span = max(args.lead_fade_start - args.lead_fade_end, EPS)
        lead_weight = float(np.clip((distance - args.lead_fade_end) / fade_span, 0.0, 1.0))
        command_vec = lead_weight * pn_dir
        command_vec = command_vec + (args.pursuit_blend * pursuit_vec)

    command_dir = unit_or_zero(command_vec)
    if np.linalg.norm(command_dir) <= EPS:
        command_dir = unit_or_zero(target_lateral)

    guard_weight = 0.0
    if args.altitude_guard:
        # Irtifa korumasi sadece gercek dusus riski varsa devreye girer.
        # Eski denemede guard kalkista da calisip roketi fazla yukari firlatti; bu yuzden
        # yukselirken ve henuz kritik alcakta degilken ekstra yukari komut vermiyoruz.
        step_id = int(info.get("step_id", 0))
        agl_factor = np.clip((args.safe_agl - agl) / max(args.safe_agl, EPS), 0.0, 1.0)
        sink_factor = np.clip((-rocket_vy) / max(args.sink_speed_scale, EPS), 0.0, 1.0)
        critical_factor = np.clip((args.critical_agl - agl) / max(args.critical_agl, EPS), 0.0, 1.0)

        guard_need = 0.0
        if rocket_vy < 0.0:
            guard_need = max(agl_factor, sink_factor)
        elif step_id >= args.altitude_guard_grace and agl < args.critical_agl:
            guard_need = critical_factor

        guard_weight = float(np.clip(guard_need * args.altitude_guard_gain, 0.0, args.altitude_guard_gain))
        command_dir = unit_or_zero(command_dir + (guard_weight * unit_or_zero(clock12)))

    clock12_net = args.turn_sign * args.turn_strength * float(np.dot(command_dir, unit_or_zero(clock12)))
    clock3_net = args.turn_sign * args.turn_strength * float(np.dot(command_dir, unit_or_zero(clock3)))
    clock12_net = float(np.clip(clock12_net, -args.turn_strength, args.turn_strength))
    clock3_net = float(np.clip(clock3_net, -args.turn_strength, args.turn_strength))

    # PN testi training thrust araligina kilitlenmez; amac fiziksel olarak vurulabilirlik sinamaktir.
    thrust = float(max(0.0, args.thrust + (args.altitude_thrust_boost * guard_weight)))
    clock_channels = positive_negative_channels(clock12_net, clock3_net)
    denorm_action = [thrust] + clock_channels

    debug = {
        "pn_clock12_net": clock12_net,
        "pn_clock3_net": clock3_net,
        "pn_closing_speed": closing_speed,
        "pn_los_rate_mag": float(np.linalg.norm(los_rate)),
        "pn_lateral_mag": float(np.linalg.norm(pn_lateral)),
        "lead_weight": lead_weight,
        "altitude_guard_weight": guard_weight,
        "rocket_vy": rocket_vy,
        "mode": args.mode,
        **accel_debug,
    }
    return denorm_action, debug


def append_row(writer, episode_index, info, debug, args):
    """Her adimi CSV'ye yazar; boylece sonra grafik ve hata analizi yapabiliriz."""
    writer.writerow(
        {
            "episode_index": episode_index,
            "episode_id": info.get("episode_id"),
            "step_id": info.get("step_id"),
            "done_reason": info.get("done_reason"),
            "success": int(bool(info.get("success", False))),
            "distance": info.get("distance"),
            "theta_deg": info.get("theta_deg"),
            "alpha_deg": info.get("alpha_deg"),
            "beta_deg": info.get("beta_deg"),
            "closing_speed": info.get("closing_speed"),
            "agl": info.get("agl"),
            "reward": info.get("reward"),
            "thrust": info.get("thrust"),
            "clock_12_cmd": info.get("clock_12_cmd"),
            "clock_6_cmd": info.get("clock_6_cmd"),
            "clock_3_cmd": info.get("clock_3_cmd"),
            "clock_9_cmd": info.get("clock_9_cmd"),
            "pn_clock12_net": debug.get("pn_clock12_net"),
            "pn_clock3_net": debug.get("pn_clock3_net"),
            "pn_closing_speed": debug.get("pn_closing_speed"),
            "pn_los_rate_mag": debug.get("pn_los_rate_mag"),
            "pn_lateral_mag": debug.get("pn_lateral_mag"),
            "pn_accel_limit": debug.get("pn_accel_limit"),
            "pn_limited_accel_mag": debug.get("pn_limited_accel_mag"),
            "pn_accel_saturated": debug.get("pn_accel_saturated"),
            "gross_accel": debug.get("gross_accel"),
            "gravity_comp_accel": debug.get("gravity_comp_accel"),
            "lead_t_go": debug.get("lead_t_go"),
            "lead_dir_dot_los": debug.get("lead_dir_dot_los"),
            "desired_accel_clock12": debug.get("desired_accel_clock12"),
            "desired_accel_clock3": debug.get("desired_accel_clock3"),
            "velocity_error_mag": debug.get("velocity_error_mag"),
            "velocity_correction_mag": debug.get("velocity_correction_mag"),
            "velocity_correction_saturated": debug.get("velocity_correction_saturated"),
            "loft_factor": debug.get("loft_factor"),
            "loft_accel_mag": debug.get("loft_accel_mag"),
            "lead_weight": debug.get("lead_weight"),
            "altitude_guard_weight": debug.get("altitude_guard_weight"),
            "rocket_vy": debug.get("rocket_vy"),
            "mode": args.mode,
            "navigation_gain": args.navigation_gain,
            "pn_sign": args.pn_sign,
            "turn_strength": args.turn_strength,
            "turn_sign": args.turn_sign,
            "pursuit_blend": args.pursuit_blend,
            "rocket_mass": args.rocket_mass,
            "intercept_speed_floor": args.intercept_speed_floor,
            "gravity_comp": args.gravity_comp,
            "max_up_comp_fraction": args.max_up_comp_fraction,
            "lateral_accel_fraction": args.lateral_accel_fraction,
            "pn_accel_limit_arg": args.pn_accel_limit,
            "accel_lead_weight": args.accel_lead_weight,
            "accel_pursuit_weight": args.accel_pursuit_weight,
            "accel_pn_weight": args.accel_pn_weight,
            "velocity_track_gain": args.velocity_track_gain,
            "velocity_accel_fraction": args.velocity_accel_fraction,
            "loft_weight": args.loft_weight,
            "loft_agl": args.loft_agl,
            "loft_fade_start": args.loft_fade_start,
            "loft_fade_end": args.loft_fade_end,
            "lead_fade_start": args.lead_fade_start,
            "lead_fade_end": args.lead_fade_end,
            "altitude_guard": int(bool(args.altitude_guard)),
            "safe_agl": args.safe_agl,
            "critical_agl": args.critical_agl,
            "altitude_guard_grace": args.altitude_guard_grace,
            "altitude_guard_gain": args.altitude_guard_gain,
            "altitude_thrust_boost": args.altitude_thrust_boost,
            "terminal_max_altitude": args.terminal_max_altitude,
            "radius_min": args.radius_min,
            "radius_max": args.radius_max,
            # Unity action audit alanlari: PN komutu ile fizik tepkisi ayni yonde mi bakmak icin yazilir.
            "target_clock_12": info.get("target_clock_12"),
            "target_clock_6": info.get("target_clock_6"),
            "target_clock_3": info.get("target_clock_3"),
            "target_clock_9": info.get("target_clock_9"),
            "rel_vel_clock_12": info.get("rel_vel_clock_12"),
            "rel_vel_clock_6": info.get("rel_vel_clock_6"),
            "rel_vel_clock_3": info.get("rel_vel_clock_3"),
            "rel_vel_clock_9": info.get("rel_vel_clock_9"),
            "rel_vel_forward": info.get("rel_vel_forward"),
            "turn_rate_clock_12": info.get("turn_rate_clock_12"),
            "turn_rate_clock_6": info.get("turn_rate_clock_6"),
            "turn_rate_clock_3": info.get("turn_rate_clock_3"),
            "turn_rate_clock_9": info.get("turn_rate_clock_9"),
            "turn_rate_roll": info.get("turn_rate_roll"),
            "clock_validity": info.get("clock_validity"),
            "forward_up_dot": info.get("forward_up_dot"),
            "action_clock12_raw": info.get("action_clock12_raw"),
            "action_clock3_raw": info.get("action_clock3_raw"),
            "action_clock12_net": info.get("action_clock12_net"),
            "action_clock3_net": info.get("action_clock3_net"),
            "low_altitude_turn_scale": info.get("low_altitude_turn_scale"),
            "clock12_scale": info.get("clock12_scale"),
            "clock3_scale": info.get("clock3_scale"),
            "beta_validity_applied": info.get("beta_validity_applied"),
            "roll_control_scale": info.get("roll_control_scale"),
            "suppressed_roll_rate": info.get("suppressed_roll_rate"),
            "desired_clock_turn_world_x": info.get("desired_clock_turn_world_x"),
            "desired_clock_turn_world_y": info.get("desired_clock_turn_world_y"),
            "desired_clock_turn_world_z": info.get("desired_clock_turn_world_z"),
            "command_turn_world_x": info.get("command_turn_world_x"),
            "command_turn_world_y": info.get("command_turn_world_y"),
            "command_turn_world_z": info.get("command_turn_world_z"),
            "command_turn_local_x": info.get("command_turn_local_x"),
            "command_turn_local_y": info.get("command_turn_local_y"),
            "command_turn_local_z": info.get("command_turn_local_z"),
            "torque_command_local_x": info.get("torque_command_local_x"),
            "torque_command_local_y": info.get("torque_command_local_y"),
            "torque_command_local_z": info.get("torque_command_local_z"),
            "rocket_turn_clock_signed_x": info.get("rocket_turn_clock_signed_x"),
            "rocket_turn_clock_signed_y": info.get("rocket_turn_clock_signed_y"),
            "rocket_turn_clock_signed_z": info.get("rocket_turn_clock_signed_z"),
        }
    )


def append_summary_row(writer, episode_index, start_info, final_info, best_info, args):
    """Episode sonunda kisa ozet yazar; hangi senaryo ise yaradi hizli gorulur."""
    writer.writerow(
        {
            "episode_index": episode_index,
            "episode_id": final_info.get("episode_id"),
            "done_reason": final_info.get("done_reason"),
            "success": int(bool(final_info.get("success", False))),
            "steps": final_info.get("step_id"),
            "reset_radius": start_info.get("distance"),
            "reset_heading_offset": start_info.get("reset_heading_offset"),
            "reset_target_miss_distance": start_info.get("reset_target_miss_distance"),
            "min_distance": best_info.get("distance"),
            "theta_at_min_distance": best_info.get("theta_deg"),
            "agl_at_min_distance": best_info.get("agl"),
            "closing_at_min_distance": best_info.get("closing_speed"),
            "final_distance": final_info.get("distance"),
            "final_theta_deg": final_info.get("theta_deg"),
            "final_closing_speed": final_info.get("closing_speed"),
            "final_agl": final_info.get("agl"),
            "mode": args.mode,
            "navigation_gain": args.navigation_gain,
            "pn_sign": args.pn_sign,
            "turn_strength": args.turn_strength,
            "turn_sign": args.turn_sign,
            "pursuit_blend": args.pursuit_blend,
            "thrust": args.thrust,
            "rocket_mass": args.rocket_mass,
            "intercept_speed_floor": args.intercept_speed_floor,
            "gravity_comp": args.gravity_comp,
            "max_up_comp_fraction": args.max_up_comp_fraction,
            "lateral_accel_fraction": args.lateral_accel_fraction,
            "pn_accel_limit_arg": args.pn_accel_limit,
            "accel_lead_weight": args.accel_lead_weight,
            "accel_pursuit_weight": args.accel_pursuit_weight,
            "accel_pn_weight": args.accel_pn_weight,
            "velocity_track_gain": args.velocity_track_gain,
            "velocity_accel_fraction": args.velocity_accel_fraction,
            "loft_weight": args.loft_weight,
            "loft_agl": args.loft_agl,
            "loft_fade_start": args.loft_fade_start,
            "loft_fade_end": args.loft_fade_end,
            "lead_fade_start": args.lead_fade_start,
            "lead_fade_end": args.lead_fade_end,
            "altitude_guard": int(bool(args.altitude_guard)),
            "safe_agl": args.safe_agl,
            "critical_agl": args.critical_agl,
            "altitude_guard_grace": args.altitude_guard_grace,
            "altitude_guard_gain": args.altitude_guard_gain,
            "altitude_thrust_boost": args.altitude_thrust_boost,
            "terminal_max_altitude": args.terminal_max_altitude,
            "radius_min": args.radius_min,
            "radius_max": args.radius_max,
        }
    )


def run(args):
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    if args.summary_output is None:
        args.summary_output = default_summary_output(args.output)
    os.makedirs(os.path.dirname(args.summary_output), exist_ok=True)

    env = Env(args.ip, args.port)
    if args.terminal_max_altitude is not None:
        # PN saglik testinde yuksek irtifa terminalini komut satirindan esnetebiliriz.
        # Bu training faz ayarini kalici degistirmez; sadece mevcut test kosusu icindir.
        env.phase["max_altitude"] = float(args.terminal_max_altitude)
    if args.max_steps is not None:
        # 300m gibi uzun testlerde komut satirindaki max-steps gercek terminale de yansimali.
        # Aksi halde script 1000 dese bile env.py icindeki 700 step timeout erken keser.
        env.phase["max_step"] = int(args.max_steps)
        env.max_step = int(args.max_steps)

    success_count = 0
    done_counts = {}

    fieldnames = [
        "episode_index",
        "episode_id",
        "step_id",
        "done_reason",
        "success",
        "distance",
        "theta_deg",
        "alpha_deg",
        "beta_deg",
        "closing_speed",
        "agl",
        "reward",
        "thrust",
        "clock_12_cmd",
        "clock_6_cmd",
        "clock_3_cmd",
        "clock_9_cmd",
        "pn_clock12_net",
        "pn_clock3_net",
        "pn_closing_speed",
            "pn_los_rate_mag",
            "pn_lateral_mag",
            "pn_accel_limit",
            "pn_limited_accel_mag",
            "pn_accel_saturated",
            "gross_accel",
            "gravity_comp_accel",
            "lead_t_go",
            "lead_dir_dot_los",
            "desired_accel_clock12",
            "desired_accel_clock3",
            "velocity_error_mag",
            "velocity_correction_mag",
            "velocity_correction_saturated",
            "loft_factor",
            "loft_accel_mag",
            "lead_weight",
            "altitude_guard_weight",
            "rocket_vy",
        "mode",
        "navigation_gain",
        "pn_sign",
        "turn_strength",
            "turn_sign",
            "pursuit_blend",
            "rocket_mass",
            "intercept_speed_floor",
            "gravity_comp",
            "max_up_comp_fraction",
            "lateral_accel_fraction",
            "pn_accel_limit_arg",
            "accel_lead_weight",
            "accel_pursuit_weight",
            "accel_pn_weight",
            "velocity_track_gain",
            "velocity_accel_fraction",
            "loft_weight",
            "loft_agl",
            "loft_fade_start",
            "loft_fade_end",
            "lead_fade_start",
            "lead_fade_end",
        "altitude_guard",
        "safe_agl",
        "critical_agl",
        "altitude_guard_grace",
        "altitude_guard_gain",
        "altitude_thrust_boost",
        "terminal_max_altitude",
        "radius_min",
        "radius_max",
        "target_clock_12",
        "target_clock_6",
        "target_clock_3",
        "target_clock_9",
        "rel_vel_clock_12",
        "rel_vel_clock_6",
        "rel_vel_clock_3",
        "rel_vel_clock_9",
        "rel_vel_forward",
        "turn_rate_clock_12",
        "turn_rate_clock_6",
        "turn_rate_clock_3",
        "turn_rate_clock_9",
        "turn_rate_roll",
        "clock_validity",
        "forward_up_dot",
        "action_clock12_raw",
        "action_clock3_raw",
        "action_clock12_net",
        "action_clock3_net",
        "low_altitude_turn_scale",
        "clock12_scale",
        "clock3_scale",
        "beta_validity_applied",
        "roll_control_scale",
        "suppressed_roll_rate",
        "desired_clock_turn_world_x",
        "desired_clock_turn_world_y",
        "desired_clock_turn_world_z",
        "command_turn_world_x",
        "command_turn_world_y",
        "command_turn_world_z",
        "command_turn_local_x",
        "command_turn_local_y",
        "command_turn_local_z",
        "torque_command_local_x",
        "torque_command_local_y",
        "torque_command_local_z",
        "rocket_turn_clock_signed_x",
        "rocket_turn_clock_signed_y",
        "rocket_turn_clock_signed_z",
    ]

    summary_fieldnames = [
        "episode_index",
        "episode_id",
        "done_reason",
        "success",
        "steps",
        "reset_radius",
        "reset_heading_offset",
        "reset_target_miss_distance",
        "min_distance",
        "theta_at_min_distance",
        "agl_at_min_distance",
        "closing_at_min_distance",
        "final_distance",
        "final_theta_deg",
        "final_closing_speed",
        "final_agl",
        "mode",
        "navigation_gain",
        "pn_sign",
        "turn_strength",
        "turn_sign",
        "pursuit_blend",
        "thrust",
        "rocket_mass",
        "intercept_speed_floor",
        "gravity_comp",
        "max_up_comp_fraction",
        "lateral_accel_fraction",
        "pn_accel_limit_arg",
        "accel_lead_weight",
        "accel_pursuit_weight",
        "accel_pn_weight",
        "velocity_track_gain",
        "velocity_accel_fraction",
        "loft_weight",
        "loft_agl",
        "loft_fade_start",
        "loft_fade_end",
        "lead_fade_start",
        "lead_fade_end",
        "altitude_guard",
        "safe_agl",
        "critical_agl",
        "altitude_guard_grace",
        "altitude_guard_gain",
        "altitude_thrust_boost",
        "terminal_max_altitude",
        "radius_min",
        "radius_max",
    ]

    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f, open(
            args.summary_output, "w", newline="", encoding="utf-8"
        ) as sf:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            summary_writer = csv.DictWriter(sf, fieldnames=summary_fieldnames)
            summary_writer.writeheader()

            for episode_index in range(1, args.episodes + 1):
                if args.radius_min is None or args.radius_max is None:
                    _, _, _, info = env.reset()
                else:
                    _, _, _, info = env.reset_with_config(
                        radius_min=args.radius_min,
                        radius_max=args.radius_max,
                        heading_offset_min=args.heading_offset_min,
                        heading_offset_max=args.heading_offset_max,
                        heading_offset_abs_min=args.heading_offset_abs_min,
                        target_y=args.target_y,
                    )
                done = False
                final_info = info
                final_debug = {}
                start_info = dict(info)
                best_info = dict(info)

                print(
                    f"[PN RESET] ep={episode_index}/{args.episodes} "
                    f"mode={args.mode} radius={info['distance']:.2f} "
                    f"heading={info['reset_heading_offset']:.2f}"
                )

                while not done and env.step_count < args.max_steps:
                    action, debug = build_pn_action(info, args)
                    _, _, reward, done, info = env.step_direct_action(action, action_label="pn_guidance")
                    final_info = info
                    final_debug = debug
                    if float(info.get("distance", 1e9)) < float(best_info.get("distance", 1e9)):
                        best_info = dict(info)
                    append_row(writer, episode_index, info, debug, args)

                    if info["step_id"] % args.print_every == 0:
                        print(
                            f"[PN STEP] ep={episode_index:<3} st={info['step_id']:<4} "
                            f"dist={info['distance']:.2f} theta={info['theta_deg']:.2f} "
                            f"cls={info['closing_speed']:.2f} agl={info['agl']:.2f} "
                            f"cmd12={debug['pn_clock12_net']:.2f} cmd3={debug['pn_clock3_net']:.2f} "
                            f"guard={debug['altitude_guard_weight']:.2f} "
                            f"alim={debug['pn_accel_limit']:.1f} amag={debug['pn_limited_accel_mag']:.1f} "
                            f"verr={debug['velocity_error_mag']:.1f} loft={debug['loft_factor']:.2f}"
                        )

                    # Gorsel izleme icin istege bagli yavaslatma.
                    if args.step_delay > 0.0:
                        time.sleep(args.step_delay)

                if not done:
                    final_info["done_reason"] = "manual_timeout"

                reason = final_info.get("done_reason", "unknown")
                done_counts[reason] = done_counts.get(reason, 0) + 1
                if reason == "success":
                    success_count += 1
                    print("[PN HIT] Success goruldu. Unity sahnesinde final konumu kontrol edebilirsin.")
                    if args.pause_on_success:
                        input("[PN HIT] Devam etmek icin Enter'a bas...")

                print(
                    f"[PN END] ep={episode_index}/{args.episodes} reason={reason} "
                    f"len={final_info.get('step_id')} dist={final_info.get('distance'):.2f} "
                    f"theta={final_info.get('theta_deg'):.2f} "
                    f"best_dist={best_info.get('distance'):.2f} "
                    f"best_theta={best_info.get('theta_deg'):.2f} "
                    f"cmd12={final_debug.get('pn_clock12_net', 0.0):.2f} "
                    f"cmd3={final_debug.get('pn_clock3_net', 0.0):.2f}"
                )
                append_summary_row(summary_writer, episode_index, start_info, final_info, best_info, args)

        print("=" * 80)
        print("[PN SUMMARY]")
        print(f"Episodes      : {args.episodes}")
        print(f"Success       : {success_count}/{args.episodes} ({100.0 * success_count / max(args.episodes, 1):.2f}%)")
        print(f"Done counts   : {done_counts}")
        print(f"CSV output    : {args.output}")
        print(f"Summary CSV   : {args.summary_output}")

    finally:
        env.close()


def parse_args():
    parser = argparse.ArgumentParser(description="V11 PN gudum saglik testi")
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=700)
    parser.add_argument("--print-every", type=int, default=50)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", default=None)
    parser.add_argument("--mode", choices=["blend", "pn", "pursuit", "accel"], default="blend")
    parser.add_argument("--navigation-gain", type=float, default=4.0)
    parser.add_argument("--pn-sign", type=float, choices=[-1.0, 1.0], default=1.0)
    parser.add_argument("--turn-strength", type=float, default=1.2)
    parser.add_argument("--turn-sign", type=float, choices=[-1.0, 1.0], default=1.0)
    parser.add_argument("--pursuit-blend", type=float, default=0.80)
    parser.add_argument("--rocket-mass", type=float, default=50.0)
    parser.add_argument("--intercept-speed-floor", type=float, default=45.0)
    parser.add_argument("--gravity-comp", type=float, default=0.95)
    parser.add_argument("--max-up-comp-fraction", type=float, default=0.78)
    parser.add_argument("--lateral-accel-fraction", type=float, default=0.85)
    parser.add_argument("--pn-accel-limit", type=float, default=0.0)
    parser.add_argument("--accel-lead-weight", type=float, default=0.90)
    parser.add_argument("--accel-pursuit-weight", type=float, default=0.45)
    parser.add_argument("--accel-pn-weight", type=float, default=1.00)
    parser.add_argument("--velocity-track-gain", type=float, default=0.25)
    parser.add_argument("--velocity-accel-fraction", type=float, default=0.65)
    parser.add_argument("--loft-weight", type=float, default=0.20)
    parser.add_argument("--loft-agl", type=float, default=45.0)
    parser.add_argument("--loft-fade-start", type=float, default=260.0)
    parser.add_argument("--loft-fade-end", type=float, default=120.0)
    parser.add_argument("--lead-fade-start", type=float, default=95.0)
    parser.add_argument("--lead-fade-end", type=float, default=45.0)
    parser.add_argument("--thrust", type=float, default=700.0)
    parser.add_argument("--altitude-guard", action="store_true")
    parser.add_argument("--safe-agl", type=float, default=35.0)
    parser.add_argument("--critical-agl", type=float, default=10.0)
    parser.add_argument("--altitude-guard-grace", type=int, default=80)
    parser.add_argument("--altitude-guard-gain", type=float, default=0.85)
    parser.add_argument("--altitude-thrust-boost", type=float, default=300.0)
    parser.add_argument("--sink-speed-scale", type=float, default=25.0)
    parser.add_argument("--terminal-max-altitude", type=float, default=None)
    parser.add_argument("--radius-min", type=float, default=None)
    parser.add_argument("--radius-max", type=float, default=None)
    parser.add_argument("--heading-offset-min", type=float, default=-5.0)
    parser.add_argument("--heading-offset-max", type=float, default=5.0)
    parser.add_argument("--heading-offset-abs-min", type=float, default=1.0)
    parser.add_argument("--target-y", type=float, default=50.0)
    parser.add_argument("--step-delay", type=float, default=0.0)
    parser.add_argument("--pause-on-success", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
