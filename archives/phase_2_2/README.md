# Phase 2.2 Archive Snapshot

Phase 2.2, `v8_7_phase_2_2_radius_105_120_reward_grid` ayarlariyla `105-120 radius`, `heading +/-2.5` ve `max_step=520` uzerinde kosuldu.

## Selected Handoff

- Selected checkpoint: `up2520`
- Model: `models/ppo_model_up2520.keras`
- Agent state: `models/ppo_state_up2520.pkl.gz`
- Raw log coverage: `update 2162-2595`
- Handoff analysis window: `update 2162-2520`

`up2520` handoff icin secildi cunku son `100` episode penceresi `R100=%86` ve `125-130m` hard-bin tail success `%81.25` verdi. `up2580` daha yeni olmasina ragmen drift gosterdigi icin secilmedi. Ham loglar `up2595` seviyesine kadar uzandi fakat bu noktada model checkpoint yoktu; tail `R100=%74` ve `125-130m` hard-bin tail `%57.6` oldugu icin karar degismedi.

## Handoff Summary

- Episode count: `1951`
- Success count: `1533`
- Overall success rate: `%78.575`
- Last 20 success rate: `%85.000`
- Last 50 success rate: `%88.000`
- Last 100 success rate: `%86.000`
- Done distribution: `success=1533`, `near_miss=354`, `low_agl=42`, `wrong_way=19`, `timeout=2`, `high_altitude=1`

## Radius Analysis

Observed `start_distance`, ham spawn radius degil; Unity tarafindaki rocket/target point offsetleri nedeniyle configured `105-120` spawn kosulu yaklasik `115-130m` observed mesafe uretti.

- `115-120m`: `628` episode, `%88.057` success
- `120-125m`: `683` episode, `%84.627` success
- `125-130m`: `640` episode, `%62.813` success

## Drift Check

`up2580` durumunda genel success `%77.499` olsa da tail metrikleri bozuldu:

- `R20=%70`
- `R50=%68`
- `R100=%62`
- `up2561-up2580` hard-bin `125-130m`: `28` episode, `%14.286` success

`up2595` ham log sonu kismi toparlanma gosterdi ama handoff icin yeterli degildi ve model checkpoint olusmadi:

- `R20=%75`
- `R50=%80`
- `R100=%74`
- `up2595` tail hard-bin `125-130m`: `33` episode, `%57.6` success

Step-log replay analizi cokusun agirlikla aci kapanmadan yuksek thrust kullanimindan geldigini gosterdi:

- Handoff tail `125-130m` success: `mean_a0=-0.996`, `thrust_gate=0.00`
- Handoff tail `125-130m` near_miss: `mean_a0=-0.762`, `thrust_gate=36.25`
- Collapse `125-130m` near_miss: `mean_a0=-0.217`, `thrust_gate=91.29`
- Collapse `125-130m` low_agl: `mean_a0=0.558`, `thrust_gate=401.54`

## Next Phase Decision

Next run should start from `up2520` and use an intermediate phase:

- `name = v8_7_phase_2_2b_radius_110_120_angle_recovery`
- `spawn_radius_min = 110.0`
- `spawn_radius_max = 120.0`
- `heading_offset = +/-2.5`
- `max_step = 520`

Reward should keep the same angle-first structure but tighten the thrust gate while not punishing successful low-thrust hits:

- `theta_progress_gain=1.75`
- `angle_focus_gain=2.05`
- `turn_toward_gain=0.40`
- `action_alignment_gain=0.075`
- `near_success_gain=0.30`
- `reverse_penalty_gain=0.45`
- `thrust_gate_gain=2.05`
- `thrust_gate_target_norm=-0.50`
- `thrust_gate_theta_start_deg=50`
- `thrust_gate_theta_span_deg=15`
- `thrust_gate_distance_scale=28`
- `thrust_gate_distance_floor=0.70`

## Archive Contents

- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/phase_2_2_handoff_up2520_*`
- `logs/phase_2_2_live_up2580_*`
- `logs/phase_2_2_live_up2595_*`
- `models/ppo_model_up2520.keras`
- `models/ppo_state_up2520.pkl.gz`

Full `step_log.csv` gzip parcalari lokal arsivde `logs/step_log.csv.gz.part001..part011` olarak tutuldu. Bu parcalar toplamda yaklasik `646 MB` oldugu icin push paketini bozmayacak sekilde git snapshot'ina eklenmedi; step-log replay ozetleri bu README icinde kayitli.
