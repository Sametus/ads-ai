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
