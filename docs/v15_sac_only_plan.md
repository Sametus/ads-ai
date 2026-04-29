# V15 SAC-Only Plan

## Karar

Bu surumde aktif egitim hatti sadece SAC'tir. PPO agent, PPO train loop, teacher collect ve pretrain dosyalari aktif koddan kaldirildi.

## Neden?

V13/V14 denemelerinde pretrain ve ogretmen warm-start, davranisi daha kontrollu baslatabilir gibi gorundu. Fakat mevcut karar, algoritma karsilastirmasini daha temiz yapmak: SAC sifirdan baslayacak ve replay buffer ile kendi deneyiminden ogrenecek.

## Aktif Komut

```powershell
C:\Users\husey\miniconda3\envs\rl_codes\python.exe scripts\train.py
```

## Aktif Checkpoint

SAC checkpoint prefix'i:

```text
sac_v15_forward_damped
```

Kaydedilen dosyalar:

- `models/sac_v15_forward_damped_actor_stepXXXX.keras`
- `models/sac_v15_forward_damped_q1_stepXXXX.keras`
- `models/sac_v15_forward_damped_q2_stepXXXX.keras`
- `models/sac_v15_forward_damped_state_stepXXXX.pkl.gz`

## Ilk Loglarda Bakilacak Sinyaller

- `action_norm_2` yine surekli `1.0` tavanina yapiyor mu?
- `action_norm_1` surekli pozitif kalip `high_altitude` uretiyor mu?
- `entropy` ve `alpha` cok hizli dusuyor mu?
- Success olmasa bile episode uzunlugu artiyor mu?

## v15.0.3 Action Notu

SAC action boyutu hala `3`, fakat anlam degisti. Son guvenli run `sac_v15_forward_damped`
checkpoint prefix'i ve `v15_0_4_phase_1_sac_forward_damped_140_160` faz adi ile baslar:

- `action_norm_0`: hedef bakisina sag/sol aim offset ekler.
- `action_norm_1`: hedef bakisina yukari/asagi aim offset ekler.
- `action_norm_2`: pozitif ileri ivme buyuklugunu secer.

Bu degisiklikten once action dogrudan dunya ivmesine cevriliyordu. Loglarda roket hizinin burun yonundeki bileseni sik sik negatife dustugu icin bu fiziksel olmayan yan/geri hareket uretti. Yeni mantikta Unity'ye giden ivme `look_dir * accel_mag` oldugu icin roket artik burnunun tersine itilmez.

## v15.0.4 Runtime Guvenlik Notu

- Direct mode Unity tarafinda yan/geri hiz bilesenini yumusak sondurur. Bu, roket burnu dondugu halde eski hizla yan yan kayma goruntusunu azaltir.
- Aim offset `0.35` ile sinirlidir. Ajan hedef hattindan tamamen kopamaz; sadece kucuk sag/yukari duzeltme arar.
- SAC update `12000` stepte baslar ve `32` stepte bir yapilir. Bu, Unity Play mode'da gradient update kaynakli donma hissini azaltmak icindir.
- SAC batch `64`, hidden unit `96` yapildi. Bu ayar performans yerine once kararlilik ve izlenebilirlik icin secildi.
- `final_distance` ve `closing_speed` tamamen kotulesiyor mu, yoksa kovalama davranisi basliyor mu?

## 2026-04-29 Hız ve Yer Sürünmesi Düzeltmesi

- SAC ilk eğitim update'i `1024` stepte başlıyordu ve Unity-Python senkron akışını ağırlaştırıyordu.
- `SAC_START_TRAINING_STEPS=4096`, `SAC_TRAIN_EVERY_STEPS=8`, `SAC_BATCH_SIZE=128`, `SAC_HIDDEN_UNITS=128` yapıldı.
- Roket yerde sürünürken `AGL` yaklaşık `0.20-0.45m` kaldığı için eski `min_agl=0.18` terminali kaçırıyordu.
- `min_agl=0.60`, `low_agl_grace_steps=80` yapıldı; roket kalkıştan sonra yerde sürünürse episode erken `low_agl` biter.
