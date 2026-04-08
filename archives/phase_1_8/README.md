# Phase 1.8 Archive

Bu klasor, V8 guidance/action hattiyla kosulan Phase 1.8 egitim penceresinin dondurulmus arsividir.

## Icerik

- `models/ppo_model_up1840.keras`
- `models/ppo_state_up1840.pkl.gz`
- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/phase_1_8_success_rate.png`
- `logs/phase_1_8_success_rug.png`
- `logs/phase_1_8_reset_outcome_polar.png`
- `logs/phase_1_8_reset_radius_distribution.png`
- `logs/phase_1_8_reset_radius_phase_plan.png`
- `logs/step_log.csv.gz.part001` ... `logs/step_log.csv.gz.part003`

## Kisa Ozet

- Secilen devam modeli: `up1840`
- Arsivlenen log kapsami: `update 1841`e kadar
- Toplam episode satiri: `687`
- Success sayisi: `623`
- Genel success rate: `%90.684`
- Guncel rolling 100 success rate: `%93.000`
- Guncel rolling 200 success rate: `%92.500`
- En iyi rolling 100 success rate: `%99.000`
- En iyi rolling 200 success rate: `%95.500`
- En iyi 20-update koridoru: `update 1800-1819` (`%97.297` success)

Done reason dagilimi:

- `success`: `623`
- `wrong_way`: `36`
- `high_altitude`: `24`
- `timeout`: `4`
- `low_agl`: `0`

## Kisa Analiz

- Phase 1.8 kosusu `80-90 radius` bandinin yeterli guclukte ogrenildigini gosterdi. Son `100-200` episode pencerelerinde success rate `%92-%95.5` bandinda kaldigi icin gec kuyrukta bozulma sinyali yok.
- En guclu update koridoru `1800-1819` araliginda `%97.297` success verdi; buna karsin son blok `1821-1840` da `%92.143` ile guclu kaldigi icin handoff modeli olarak `up1840` secildi.
- Radius bazli basari analizi `80-85` bandinin `%96.9`, `85-90` bandinin `%86.6` success verdigini gosterdi. Bu nedenle bir sonraki faz icin dogal gecis `85-95 radius`, `max_step=480` olarak secildi.
