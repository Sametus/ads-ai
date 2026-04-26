# Tuning Memory

Bu dosya runtime tarafinda kullanilmaz.
Amac, faz/odul/manevra denemeleri icin notlari kod disinda tutmaktir.

## Current Manual Config

- Env runtime artik tek aktif config ile calisir.
- Aktif ayarlar `scripts/env.py` icindeki `ACTIVE_PHASE_CONFIG` alaninda tutulur.
- Faz gecisi yapmak yerine bu blok elle guncellenir.

## Current Focus

- Last archived phase: `v8.7.6 - Faz 2.2 up2520 archive`
- Current handoff checkpoint: `up2520`
- Current phase target: `v8.7.6 - Faz 2.2 radius 105-120 reward-grid row 1 archive`
- Current spawn radius: `105 - 120`
- Heading offset: `-2.5 .. +2.5`
- Max step: `520`
- Reward: angle-first dense shaping is active. `theta_progress_gain=1.665`, `alpha_beta_gain=0.465`, `angle_focus_gain=1.87`.
- Reward: distance/closing rewards are gated by positive alignment and good theta so target movement alone does not create misleading positive reward.
- Reward: `near_miss` terminal is active for `distance<=18m` and `theta>=75deg` after the grace window; penalty is `-90`.
- Reward: terminal scale is intentionally lighter (`success=180`, `high_altitude=-105`, `wrong_way=-115`, `low_agl=-110`, `timeout=-80`) because the correction signal should come from angle progress, not giant terminal values.
- Reward: altitude guardrail is moderate (`soft_ceiling_start=105`, `soft_ceiling_gain=0.018`, `max_altitude=145`) so good-angle climb can survive but high-altitude bad-angle escape is negative.
- Reward: curriculum row 1 thrust guard is active. `MIN_THRUST=690`, `MAX_THRUST=850`; `theta>55deg` iken `action_norm_0>-0.45` icin `thrust_gate_penalty` uygulanir.
- Reward: curriculum row 1 result: `thrust_gate_gain=1.65`, `theta_span=15`, `dist_scale=30`, `dist_floor=0.65`.
- PPO: `agent.py` reward-collapse experiments were reverted; do not change PPO until reward-only run is evaluated.
- Action: vertical / horizontal command limits are symmetric at `2.5 / 2.5`.
- Action: `beta_validity` now has a `0.25` floor so horizontal guidance is not fully disabled when the rocket is near vertical.

## Recent Intent

- Phase 2.0 retry ana oturumu basariliydi; `up2100` handoff secildi.
- `up2120` resume oturumu drift gosterdigi icin handoff olarak kullanilmadi.
- `up2100` sonrasi model/state dosyalari silindi.
- Ilk Faz 2.1 retry denemesi `up2102-up2129` araliginda toplam `%64.179` success verdi ama son pencere collapse gostergesi tasidi (`R20=%15`).
- Basarisiz episode'larda hedefe yaklasma var fakat theta kapanmiyor; v8.7.2 aci odakli reward tek basina yetmedi.
- v8.7.2 run'inda ilk 120 episode `%78.333`, 121+ penceresi `%13.889` success verdi; cokus start-distance kaynakli degil.
- En guclu yeni sinyal thrust drift: success episode'larda `action_norm_0=-0.325`, post-collapse failure episode'larda `action_norm_0=+0.243`. Bu yuzden v8.7.3 thrust guard aktif.
- v8.7.3 run'i da coktu: `183` episode `%53.005`, ilk 120 `%71.667`, 121+ `%17.460`. Success rate ile `mean_a0` korelasyonu `-0.8992`; post-collapse failure `mean_a0=+0.4449`.
- `20` dakika CUDA grid-search `35,815,424` aday taradi; secilen v8.7.4 parametreleri thrust drift'i daha sert kisitlar ve fiziksel thrust araligini `700-850` bandina daraltir.
- Retry `up2100` handoff uzerinden baslanacak. Model klasorunde `up2100` sonrasi model/state varsa temizlenmeli ya da `ADS_AI_CHECKPOINT_UPDATE=2100` ile acik checkpoint secilmeli.
- up2160 run'i guncel oturum filtresiyle (`update 2142-2160`, parcali `2161` haric) basarili kabul edildi: `117` episode, `109` success, `%93.162` success, tail `R20=%95`, `R50=%96`, `R100=%96`.
- up2160 snapshot grafigi ve ozetleri `docs/phase_planning/phase_2_1_up2160/` altinda tutulur.
- Sonraki faza gecis icin curriculum tablosunun ilk satiri adaydir: `105-120 radius`, `max_step=520`; ayar sadece snapshot commit/push tamamlandiktan sonra uygulanmali.
- Faz 2.2 `105-120 radius` kosusu `up2520` checkpoint'inde handoff olarak donduruldu. `up2162-up2520` araligi `1951` episode icinde `%78.575` success verdi; tail degerleri `R20=%85`, `R50=%88`, `R100=%86`.
- `up2580` ve ham log sonu `up2595` son durum olarak arsivlendi ama handoff secilmedi. `up2541-up2580` araligi `%66.038` success'e dustu; `125-130m` observed bandi `up2561-up2580` icinde `%14.286` success'e kadar indi. `up2595` tail biraz toparlansa da `R100=%74` ve hard-bin tail `%57.6` ile `up2520` seviyesine ulasamadi; ayrica `up2595` icin model checkpoint yok.
- Drift analizi, cokusun agirlikla yuksek thrust / aci kapanmama kombinasyonundan geldigini gosterdi. Collapse penceresinde `125-130m` near_miss ortalama `final_theta=90.13deg`, `mean_a0=-0.217`, `thrust_gate=91.29`; low_agl ortalama `mean_a0=0.558`, `thrust_gate=401.54`.
- Sonraki ara faz icin plan: `110-120 radius`, `max_step=520`, handoff `up2520`. Bu ara faz 105-110 kolay bandini kaldirip observed `120-130m` araligini calistiracak; `120-140` ana fazina dogrudan gecilmemeli.
- Ara faz reward hesabi: thrust gate baslangici `theta_start=50`, hedef thrust `target_norm=-0.50`, `gain=2.05`, `dist_scale=28`, `dist_floor=0.70` onerilir. Replay hesabinda bu degisim success episode'larda yaklasik `+0..+3` ek ceza, near_miss'te `+22..+50`, low_agl/collision'da `+140..+160` ek ceza uretti.

## Graph Output Standard

- Grafik uretildiginde yalniz cizim degil, okunmasi icin gerekli sayisal bilgi de ustunde yer almali.
- Grafik basliklarinda `surum - faz` yazimi kullanilmali.
  `active/current/proposed` gibi genel etiketler kullanilmamali.
- Faz bantlari gosterilecekse sadece gercekte var olan fazlar cizilmeli.
  Oneri fazi ancak kullanici acikca isterse eklenmeli.

### Success Rate Graph

- Kumulatif success rate cizgisi olmali.
- Rolling `50`, `100`, `200` success rate cizgileri olmali.
- Grafikte metin olarak su bilgiler yazilmali:
  - toplam episode
  - toplam success
  - genel success rate
  - guncel rolling `50 / 100 / 200`
  - en iyi rolling `50 / 100 / 200`

### Success Rug

- Her success episode tek tek gosterilmeli.
- `y` ekseni bilgi tasimiyorsa gizlenmeli.
- Grafikte metin olarak su bilgiler yer almali:
  - toplam success
  - episode araligi
  - varsa kullanilan filtre (`upXXXX sonrasi` gibi)

### Reset Outcome Polar

- Done reason renk lejanti her zaman olmali.
- Faz/surum ismi baslikta yazilmali.
- Metin kutusunda su ozet olmali:
  - toplam reset sayisi
  - success sayisi
  - wrong_way sayisi
  - high_altitude sayisi
  - low_agl sayisi

### Reset Radius Distribution

- Her radius bin icin done reason dagilimi cizilmeli.
- Mumkunse ayni bin icin success rate de gorunur olmali.
- Her bin icinde veya hemen ustunde su bilgiler olmali:
  - `% success`
  - `n`
  - `S`
  - `WW`
  - `HA`
  - `LA`

### Reset Radius Phase Plan

- Standart PNG ciktisi `scripts/plot_phase_report.py` icindeki `plot_radius_phase_plan` fonksiyonundan uretilir.
- Ust grafik: observed `start_distance` binlerine gore success rate barlari.
- Alt grafik: sol tarafta satir isimleri olacak sekilde uc serit kullanmali: `configured phase`, `observed bins`, `bin SR`.
- Alt grafik: mevcut configured faz radius bandi, observed `start_distance` bin kutulari ve observed bin success-rate cizgisi.
- Faz etiketi `surum - faz` formatinda olmali; `active/current/proposed` veya yalniz `P1/P2` gibi baglamsiz etiketler kullanilmamali.
- Curriculum CSV'deki `planned_phase` degerleri `P1/P2` olarak gosterilmemeli; bunlar proje faz numarasi degil, sadece grid-search satir numarasidir.
- Gelecek/oneri faz bantlari varsayilan olarak cizilmemeli; sadece mevcut configured faz ve observed aralik gosterilmeli.
- Her bin uzerinde `% success`, `n`, `S`, `NM`, `WW`, `LA` bilgileri yazilmali.
- Alt grafikte de her bin icin `% success`, `n`, `S` degerleri gorunmeli.
- Alt grafikte observed bin kutulari radius araligiyla etiketlenmeli (`115-120m` gibi); mavi kutularin faz degil observed `start_distance` binleri oldugu grafikte yazmali.
- Aciklama kutusu grafigin saginda sabit durmali ve icerigi kapatmamalidir: `n = total episodes`, `S = success`, `NM = near_miss`, `WW = wrong_way`, `LA = low_agl`, `HA = high_altitude`, `TO = timeout`.

### General Rule

- Bir grafikte kisa etiket kullaniliyorsa, ayni grafikte o etiketlerin anlami da aciklanmali.
- Sadece gorsel trend degil, karar vermeyi saglayan sayisal ozet de grafikte bulunmali.
- Kullanici ozellikle istemedikce eksik veya yalin surum gonderilmemeli; varsayilan cikti dolu ve aciklayici olmali.

### V9 Clock Action Alignment

- V9 ve sonrasi icin standart faz grafiklerine `clock_action_alignment` PNG ve Plotly HTML ciktisi eklenmeli.
- Bu grafik `target_clock_12/6/3/9` ile `clock_12/6/3/9_cmd` kolonlarini karsilastirmali.
- Ana karar sinyali `clock_vector_cosine` olmali: `+1` hedef kanalina dogru, `0` etkisiz/yan, `-1` hedefin tersine hareket demektir.
- `dominant channel match ratio`, net command magnitude, target clock magnitude ve clock reward terimleri ayni grafikte gorunmeli.
- V9 clock kolonlari yoksa grafik bos hata vermemeli; bunun V9 loglari yazildiktan sonra dolacagini aciklayan placeholder uretmeli.

## Phase Transition Checklist

- 1. Mevcut fazi sadece aktif `phase_name` filtresi ile analiz et.
- 2. Rolling success oranlari ve en iyi update koridorunu hesapla.
- 3. Reset radius / done reason grafiklerini uret.
- 4. Handoff checkpoint `upXXXX` sec.
- 5. `env.py`yi once biten faz state'ine geri alip snapshot arsivini cikar.
- 6. README / CHANGELOG / VERSION guncelle.
- 7. Snapshot commit ve push tamamla.
- 8. Ancak bundan sonra yeni faz ayarini `env.py` icinde uygula.
- 9. Gerekirse secilen `upXXXX` sonrasi modelleri sil.
- 10. Canli loglari temizleyip yeni run'a hazir birak.

## Offline Curriculum Reward Planning

- Ciktilar `docs/phase_planning/` altina yazilir; runtime/model/log dosyalarini degistirmez.
- Radius 500'e kadar her faz icin ayri reward aramak istendiginde kullanilacak arac:
  `C:\Python310\python.exe scripts\curriculum_reward_grid_search.py --max-radius 500 --seconds-per-phase 720 --device cuda --candidates-per-round 65536 --batch-size 2048 --label v8_7_4_radius500_reward_grid`
- Bu arac tek bir sonraki radius secmez; faz merdiveni olusturur ve her faz icin ayri reward/guard grid-search ciktisi verir.
- Curriculum ciktisi gelecek radiuslar icin offline ekstrapolasyondur; her yeni fazdan sonra taze Unity loglari incelenmeden tablonun bir sonraki satiri otomatik uygulanmaz.

## Curriculum Reward Grid Result

- Final result file: `docs/phase_planning/curriculum_reward_summary_v8_7_4_radius500_reward_grid_20260412_184355.txt`.
- Best-per-phase CSV: `docs/phase_planning/curriculum_reward_best_per_phase_v8_7_4_radius500_reward_grid_20260412_184355.csv`.
- Run details: CUDA, `7217.0s`, `213,843,968` candidates, source phase `v8_7_phase_2_1_thrust_guard_v2`.
- Source snapshot: `242` episodes, `207` success, `27` near_miss, `5` low_agl, `3` wrong_way, success rate `%85.537`.
- Important limitation: future radius bands do not have real Unity logs yet; this is an offline extrapolation and must be validated phase-by-phase with fresh logs.
- Current run stays unchanged. Do not apply the curriculum table while the current phase is running.
- Mid-training check rule: inspect current run logs first; only then decide whether the next curriculum row is still valid.

### Curriculum Radius Plan

- Phase 1: `105-120`, `max_step=520`.
- Phase 2: `120-140`, `max_step=540`.
- Phase 3: `140-165`, `max_step=560`.
- Phase 4: `165-195`, `max_step=580`.
- Phase 5: `195-230`, `max_step=600`.
- Phase 6: `230-270`, `max_step=640`.
- Phase 7: `270-315`, `max_step=660`.
- Phase 8: `315-365`, `max_step=700`.
- Phase 9: `365-425`, `max_step=760`.
- Phase 10: `425-500`, `max_step=820`.

### Next Candidate Row

- Use this only after the current phase is evaluated with live logs.
- Radius: `110-120`, `max_step=520`, handoff `up2520`.
- `theta_progress_gain=1.75`, `alpha_beta_gain=0.465`, `axis_error_penalty_gain=0.28`, `angle_focus_gain=2.05`.
- `turn_toward_gain=0.40`, `action_alignment_gain=0.075`, `reverse_penalty_gain=0.45`, `near_success_gain=0.30`.
- `MIN_THRUST=690`, `MAX_THRUST=850`.
- `thrust_gate_gain=2.05`, `thrust_gate_target_norm=-0.50`, `thrust_gate_theta_start_deg=50`, `thrust_gate_theta_span_deg=15`.
- `thrust_gate_distance_scale=28`, `thrust_gate_distance_floor=0.70`.

## V8 Closure Decision

- V8 was closed at `v8.7.7` as an unsuccessful architecture after the final `v8_7_phase_2_3_radius_105_120_safe_climb_guidance` retry.
- Final V8 snapshot: `archives/v8_failed_final_up2514/`.
- Final retry used `up2500` as source checkpoint and logged `update 2502-2514`, `50` episodes.
- Outcome: `success=4/50 (%8.0)`, `near_miss=28/50 (%56.0)`, `wrong_way=9/50 (%18.0)`, `low_agl=7/50 (%14.0)`.
- Diagnosis: reward-only tuning could not stabilize direction control. The policy reached the target neighborhood but failed to keep nose alignment, and later PPO updates drifted toward high-thrust / repeated steering patterns.
- Future documentation should describe V8 as a reward-heavy, sign-based action architecture that was abandoned in favor of V9 clock-guidance.

## V9 Versioning Rule

- V9 starts a new state/action architecture, not a continuation of V8 checkpoints.
- Version family format:
  - Base architecture: `v9.0`.
  - First phase under this architecture: `v9.0.0`.
  - Second phase under the same architecture: `v9.0.1`.
  - If phases show a jump-level architecture or curriculum improvement, bump to `v9.1`.
- V9 should use clock-guidance state/action naming in docs and logs.
- V9 first runnable phase is `v9.0.0` / `v9_0_0_phase_1_clock_guidance_140_160`.
- V9 checkpoint files use `ppo_v9_model_upXXXX.keras` and `ppo_v9_state_upXXXX.pkl.gz` so V8 checkpoints are not loaded accidentally.
- Initial V9 curriculum:
  - Radius: `140-160m`.
  - Heading offset: `-5..5deg`, with `0deg` excluded (`abs(offset) >= 1deg`).
  - Success: `distance <= 10m`, `alignment >= 0.90`, `closing_speed >= 0`.
  - Main diagnostic: target clock channels vs action clock channels.
- Initial V9 roll suppression was increased after the first short run:
  - `rollTorqueScale=3.6`.
  - `rollStabilizationGain=22`.
  - `rollDampingGain=12`.
  - `maxRollCorrection=5.25`.

## V9 Closure Decision

- V9 continuous clock-channel steering was closed as unsuccessful at `up100`.
- Archive: `archives/v9_0_0_failed_up100/`.
- Outcome over `update 1-100`: `310` episodes, `0` success, `70` near_miss, `240` high_altitude.
- Diagnosis:
  - Narrow heading offset helped the rocket enter the target corridor more often.
  - It still did not learn nose alignment; final theta stayed around `137deg`.
  - Target/action clock-channel match stayed near the random four-way baseline (`~25%`).
  - Opposite continuous channels could coactivate, diluting net maneuver direction.
  - `near_miss` was a trap terminal because it ended bad-angle close passes early.
- Next version must be `v10.0.0` because the action type changes.
- V10 direction:
  - Remove `near_miss` terminal; keep it as diagnostic/log only.
  - Use hybrid PPO action: continuous thrust plus discrete clock-direction steering.
  - Treat V10 checkpoints as incompatible with V9 checkpoints.

## V10 Versioning Rule

- V10 starts because the action type changed from continuous clock-channel vector to hybrid continuous/discrete policy.
- V10 checkpoints use `ppo_v10_model_upXXXX.keras` and `ppo_v10_state_upXXXX.pkl.gz`; never resume V10 from V9 model files.
- First phase is `v10.0.0` / `v10_0_0_phase_1_hybrid_discrete_clock_140_160`.
- Phase naming under this architecture:
  - `v10.0.0`: first runnable hybrid discrete clock phase.
  - `v10.0.1`, `v10.0.2`: same architecture, curriculum/reward phase increments.
  - `v10.1`: only if state/action/curriculum logic changes at jump level.
- V10 action contract inside PPO:
  - Action 0: continuous `thrust` in `[-1, 1]`.
  - Action 1: categorical `turn_direction` id.
- V10 Unity contract remains the same five values after Python denormalization:
  - `[thrust, clock_12_cmd, clock_6_cmd, clock_3_cmd, clock_9_cmd]`.
- Direction classes:
  - `0 hold`.
  - `1 clock_12`.
  - `2 clock_12_3`.
  - `3 clock_3`.
  - `4 clock_3_6`.
  - `5 clock_6`.
  - `6 clock_6_9`.
  - `7 clock_9`.
  - `8 clock_9_12`.
- `near_miss` is not a terminal in V10. It should be tracked as `near_miss_candidate` only.
- V10 graph/report tooling should still include clock action alignment because denormalized Unity action channels remain available in `step_log.csv`.

## V10 Failure Analysis - No Maneuver / High Altitude

- Current V10 run logs reached `up172` with `529` completed episodes and `0` success.
- All completed episodes ended as `high_altitude`; mean final theta stayed near `149deg`, mean final distance near `112m`.
- The rocket was not learning target-directed maneuver:
  - `action_target_cos` stayed near `0.0` across update windows.
  - `turn_target_cos` stayed near `0.0`.
  - terminal episodes still had strong negative alignment (`~ -0.85`).
- Root cause in reward/action coupling:
  - Raw `clock_validity` was almost always near zero while the rocket was vertical (`median ~0.018`, `94% < 0.1`).
  - `reward_clock_action_alignment` and wrong-channel penalty were multiplied by this value, so action direction learning was effectively silent.
  - Old mean clock action alignment reward was only `~0.0029/step`.
- V10 retune applied after this analysis:
  - New retry phase name: `v10_0_1_phase_1_clock_reward_recovery_140_160`.
  - `clock_reward_validity_floor=0.70`.
  - `clock_action_alignment_gain=1.20`.
  - `clock_wrong_channel_penalty_gain=1.20`.
  - Old-log recalculation: random-policy net clock reward is near zero (`~-0.002/step`), while oracle target direction is strongly positive (`~0.626/step`).
  - Unity maneuver authority increased for vertical launch: `betaValidityFloor=0.75`, `torqueScale=1.8`, `lowAltitudeMinTurnScale=0.35`, `lowAltitudeTurnDampFullAgl=10`.
  - `SampleScene.unity` serialized Env values must be kept in sync with `Env.cs`; this run fixed old scene overrides that still had `betaValidityFloor=0.25`, `torqueScale=1.45`, `rollStabilizationGain=22`, `rollDampingGain=12`.
  - Thrust range reduced to `620-700` and ceiling tightened (`soft_ceiling_start=80`, `max_altitude=125`) to break pure vertical high-altitude behavior.

## V10 Closure Decision

- V10 was closed as unsuccessful after `v10_0_1_phase_1_clock_reward_recovery_140_160`.
- Archive: `archives/v10_0_1_failed_up40/`.
- Handoff/final checkpoint kept for analysis: `ppo_v10_model_up40.keras`.
- Outcome over `update 1-56`: `147` episodes.
- Done reasons:
  - `high_altitude=143`.
  - `wrong_way=2`.
  - `success=1`.
  - `low_agl=1`.
- Success rate: `%0.680`.
- Tail success:
  - Last `20` episodes: `%0`.
  - Last `50` episodes: `%0`.
  - Last `100` episodes: `%0`.
- Diagnosis:
  - V10 action structure can maneuver, and the first success was geometrically clean.
  - It still did not stabilize into repeatable interception.
  - Reward-only tuning plus pure PPO exploration is not reliable enough for delivery risk.
- Next version must be V11.
- V11 scope:
  - Keep offline reward estimation in `reward_lab`.
  - Add orientation warm-start / behavior cloning pretraining.
  - Use Turkish, short, plain code comments for newly written code.
