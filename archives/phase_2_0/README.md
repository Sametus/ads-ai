# Phase 2.0 Archive

V8.6 Faz 2.0 retry kosusu `up2100` modelinde donduruldu.

## Handoff

- Secilen checkpoint: `up2100`
- Model: `models/ppo_model_up2100.keras`
- State: `models/ppo_state_up2100.pkl.gz`
- Faz config: `v8_6_phase_2_0_retry`
- Spawn radius: `90-100`
- Heading offset: `-2.5 .. +2.5`
- Max step: `480`

## Sonuc Ozeti

Loglar ayni faza ait iki training oturumu icerir. Ikinci oturum, log temizlenmeden `up2122` civarindan tekrar baslatildigi icin analizde ayri oturum olarak tutuldu.

### Oturum 1

- Tarih araligi: `2026-04-10 17:24:46 -> 2026-04-10 18:26:37`
- Update araligi: `up1942-up2132`
- Episode: `1209`
- Success: `1116`
- Genel success rate: `%92.308`
- Done dagilimi: `success=1116`, `high_altitude=74`, `wrong_way=13`, `timeout=5`, `low_agl=1`
- Son rolling: `R20=%85.0`, `R50=%86.0`, `R100=%91.0`, `R200=%92.5`

### Oturum 2

- Tarih araligi: `2026-04-11 13:54:09 -> 2026-04-11 13:59:40`
- Update araligi: `up2122-up2134`
- Episode: `66`
- Success: `45`
- Genel success rate: `%68.182`
- Done dagilimi: `success=45`, `high_altitude=13`, `wrong_way=5`, `timeout=2`, `low_agl=1`

## Checkpoint Karari

`up2120` ve sonrasi drift riski gosterdi. Uzun oturumdaki checkpoint pencereleri icinde `up2100` en guvenli handoff olarak secildi:

- `up2101-up2120` post-window success: `%94.615`
- Ortalama episode return: `195.82`
- Done dagilimi: `success=123`, `high_altitude=6`, `wrong_way=1`

## Start Distance Analizi

`start_distance`, ham spawn radius degil; Unity tarafindaki rocket/target point offsetleri nedeniyle gozlenen baslangic mesafesidir.

- `100-105`: `%97.167`
- `105-110`: `%92.603`
- `110-115`: `%79.739`

## Arsiv Icerigi

- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/step_log.csv.gz.part001..part006`
- `logs/phase_2_0_success_rate.png`
- `logs/phase_2_0_start_distance_distribution.png`
- `logs/phase_2_0_checkpoint_candidates.png`
- `logs/phase_2_0_reward_components.png`
- `logs/phase_2_0_turn_action_alignment.png`
- `logs/phase_2_0_resume_outcomes.png`
- `models/ppo_model_up2100.keras`
- `models/ppo_state_up2100.pkl.gz`
