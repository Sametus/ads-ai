# Tuning Memory

Bu dosya runtime tarafinda kullanilmaz.
Amac, faz/odul/manevra denemeleri icin notlari kod disinda tutmaktir.

## Current Manual Config

- Env runtime artik tek aktif config ile calisir.
- Aktif ayarlar `scripts/env.py` icindeki `ACTIVE_PHASE_CONFIG` alaninda tutulur.
- Faz gecisi yapmak yerine bu blok elle guncellenir.

## Current Focus

- Last archived phase: `v8.6 - Faz 2.0 retry`
- Current handoff checkpoint: `up2100`
- Current phase target: `v8.6 - Faz 2.0 retry`
- Planned next phase: `v8.7 - Faz 2.1`
- Planned next spawn radius: `95 - 105`
- Heading offset: `-2.5 .. +2.5`
- Max step: `480`
- Planned next max step: `500`
- Reward: `turn_toward` shaping now rewards angular velocity that closes signed `alpha/beta`.
- Reward: `action_alignment` gives a small direct signal when vertical/horizontal action signs match signed `alpha/beta`.
- Reward: high-altitude escape is stricter (`soft_ceiling_start=90`, nonlinear ceiling penalty, `max_altitude=135`, `high_altitude_penalty=-130`).
- PPO: gentler fine-tune from `up2100` (`lr=2e-5`, `clip_eps=0.08`, `ent_coef=0.004`, `target_kl=0.0025`).
- Action: vertical / horizontal command limits are symmetric at `2.5 / 2.5`.
- Action: `beta_validity` now has a `0.25` floor so horizontal guidance is not fully disabled when the rocket is near vertical.

## Recent Intent

- Phase 2.0 retry ana oturumu basariliydi; `up2100` handoff secildi.
- `up2120` resume oturumu drift gosterdigi icin handoff olarak kullanilmadi.
- `up2100` sonrasi model/state dosyalari silindi.
- Faz 2.1 kontrollu genisletme: `95-105 radius`, `max_step=500`, reward/action seti korunacak.

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

- Ust grafik: radius binlerine gore success rate barlari
- Alt grafik: faz bantlari ve mini success-rate cizgisi
- Her bin uzerinde su bilgiler yazilmali:
  - `% success`
  - `n`
  - `S`
  - `WW`
  - `HA`
  - `LA`
- Ayrica grafikte kucuk bir aciklama kutusu olmali:
  - `n = toplam episode`
  - `S = success`
  - `WW = wrong_way`
  - `HA = high_altitude`
  - `LA = low_agl`

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
