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
