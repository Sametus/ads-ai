# Phase 1.9 Archive Snapshot

Phase 1.9, `v8_5_phase_1_9` ayarlariyla `85-95 radius`, `heading +/-2.5` ve `max_step=480` uzerinde kosuldu.

## Selected Handoff

- Selected checkpoint: `up1920`
- Model: `models/ppo_model_up1920.keras`
- Agent state: `models/ppo_state_up1920.pkl.gz`
- Log coverage: `update 1842-1921`

`up1920` handoff icin secildi cunku son update blogu bozulmadan guclu kaldi. `1902-1921` blogunda `134` episode icinde `%98.507` success goruldu.

## Summary

- Episode count: `499`
- Success count: `448`
- Overall success rate: `%89.780`
- Last 20 success rate: `%95.000`
- Last 50 success rate: `%98.000`
- Last 100 success rate: `%98.000`
- Last 200 success rate: `%98.000`
- Last 300 success rate: `%95.333`
- Best rolling 50: `%100.000` at `episode 320-369`, `update 1895-1902`
- Best rolling 100: `%99.000` at `episode 309-408`, `update 1893-1908`
- Best rolling 200: `%98.000` at `episode 257-456`, `update 1886-1914`
- Best 20-update window: `%99.291` at `update 1897-1916`

## Outcome Split

- `success`: `448`
- `wrong_way`: `22`
- `high_altitude`: `20`
- `timeout`: `9`

Success episodes averaged `final_distance=14.499`, `final_theta=26.615 deg`, and `final_closing=+29.598`. Failure episodes remained dominated by `wrong_way` and `high_altitude`.

## Radius Analysis

- `80-85`: `20` episodes, `%100.000` success
- `85-90`: `212` episodes, `%97.170` success
- `90-95`: `190` episodes, `%85.263` success

Candidate next windows:

- `86-96`: `350` episodes, `%90.571` success
- `87-97`: `311` episodes, `%90.033` success
- `88-98`: `274` episodes, `%89.051` success
- `89-99`: `234` episodes, `%87.180` success
- `90-100`: `190` episodes, `%85.263` success

## Next Phase Decision

Next phase should start from `up1920` and move to:

- `name = v8_6_phase_2_0`
- `spawn_radius_min = 90.0`
- `spawn_radius_max = 100.0`
- `heading_offset = +/-2.5`
- `max_step = 480`
- reward unchanged

This is a deliberate progression from the solved `85-95` band into the upper band while preserving the current reward and control settings.

