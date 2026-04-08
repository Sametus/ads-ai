# Phase 1.7 Archive

Bu klasor, V8 guidance/action hattiyla kosulan Phase 1.7 egitim penceresinin dondurulmus arsividir.

## Icerik

- `models/ppo_model_up1740.keras`
- `models/ppo_state_up1740.pkl.gz`
- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/phase_1_7_success_rate.png`
- `logs/phase_1_7_success_rug.png`
- `logs/phase_1_7_reset_outcome_polar.png`
- `logs/phase_1_7_reset_radius_distribution.png`
- `logs/phase_1_7_reset_radius_phase_plan.png`
- `logs/step_log.csv.gz.part001` ... `logs/step_log.csv.gz.part019`

## Kisa Ozet

- Secilen devam modeli: `up1740`
- Arsivlenen log kapsami: `update 2131`e kadar
- Toplam episode satiri: `3948`
- Success sayisi: `2614`
- Genel success rate: `%66.211`
- Guncel rolling 100 success rate: `%5.000`
- Guncel rolling 200 success rate: `%5.000`
- Guncel rolling 300 success rate: `%5.667`
- En iyi rolling 100 success rate: `%100.000`
- En iyi rolling 200 success rate: `%98.000`
- En iyi rolling 300 success rate: `%95.000`
- En iyi 20-update koridoru: `update 1728-1747` (`%98.734` success)

Done reason dagilimi:

- `success`: `2614`
- `wrong_way`: `872`
- `high_altitude`: `344`
- `timeout`: `84`
- `low_agl`: `34`

## Kisa Analiz

- Phase 1.7 kosusu `75-85 radius` bandinin guclu bicimde ogrenildigini, ancak run fazla uzatilinca policy'nin gec kuyrukta ciddi sekilde drift ettigini gosterdi.
- Orta koridorda `update 1728-1747` bandi `%98.7` success ile fazin en guclu penceresi oldu; bu nedenle handoff modeli olarak `up1740` secildi.
- Son `200-300` episode penceresinde success rate `%5` bandina dustu ve baskin hata modu yeniden `wrong_way` ile `high_altitude` oldu; dolayisiyla son checkpoint degil, en iyi koridora yakin checkpoint kullanmak daha dogru bulundu.
- Bir sonraki faz icin dogal gecis `80-90 radius`, `max_step=480` olarak planlandi; heading ve reward ailesi ilk geciste korunacak.
