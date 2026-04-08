# Tuning Memory

Bu dosya runtime tarafinda kullanilmaz.
Amac, faz/odul/manevra denemeleri icin notlari kod disinda tutmaktir.

## Current Manual Config

- Env runtime artik tek aktif config ile calisir.
- Aktif ayarlar `scripts/env.py` icindeki `ACTIVE_PHASE_CONFIG` alaninda tutulur.
- Faz gecisi yapmak yerine bu blok elle guncellenir.

## Current Focus

- Spawn radius: `55 - 90`
- Heading offset: `-5 .. +5`
- Max step: `400`
- Target height offset: `20`
- Torque scale: `1.85`
- Vertical / horizontal command limits: `3.2 / 3.2`

## Recent Intent

- `wrong_way` terminali erken tetiklenmeyecek kadar yumusatildi.
- `near_success_bonus` eklendi; success olmasa bile success'e en yakin hatalar daha yuksek shaping almali.
- Kod karmasasi azaltmak icin coklu faz secimi env runtime'dan kaldirildi.

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
- Kullanici ozellikle istemedikce eksik/yalin surum gonderilmemeli; varsayilan ciktı dolu ve aciklayici olmali.
