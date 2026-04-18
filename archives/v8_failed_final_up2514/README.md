# V8 Failed Final Snapshot - up2514

This archive closes the V8 guidance/reward architecture as an unsuccessful branch before moving to the V9 clock-guidance state/action redesign.

## Snapshot

- Runtime phase: `v8_7_phase_2_3_radius_105_120_safe_climb_guidance`
- Source checkpoint for the retry: `up2500`
- Logged update range: `2502-2514`
- Episode count: `50`
- Mean return: `-223.984`
- Median return: `-109.455`
- Mean episode length: `298.74`

## Outcomes

- `success`: `4 / 50` (`8.0%`)
- `near_miss`: `28 / 50` (`56.0%`)
- `wrong_way`: `9 / 50` (`18.0%`)
- `low_agl`: `7 / 50` (`14.0%`)
- `high_altitude`: `1 / 50` (`2.0%`)
- `timeout`: `1 / 50` (`2.0%`)

## Diagnosis

The V8 reward/action representation could occasionally produce valid intercepts, but it did not provide the policy with a sufficiently stable direction representation. Failures clustered around two patterns:

- The rocket reached the target neighborhood but did not keep the nose aligned, producing dominant `near_miss` outcomes around `final_theta ~= 77 deg`.
- Continued PPO updates drifted toward high-thrust / same-pattern steering modes that increased `low_agl` and `wrong_way` failures.

The phase was therefore closed as a failed architecture rather than extended with more reward-only tuning.

## Archived Artifacts

- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/step_log.csv.zip`
- `models/ppo_model_up2500.keras`
- `models/ppo_state_up2500.pkl.gz`

## Next Direction

V9 will replace the sign-based `vertical_cmd` / `horizontal_cmd` action interpretation with a clock-guidance representation:

- State exposes target direction around the rocket as clock channels.
- Action uses thrust plus four independent clock-direction channels.
- Success threshold is tightened toward `10m` to avoid counting loose near passes as hits.
