# V10.0.1 Failed Snapshot - up40

Bu arşiv V10 hibrit discrete clock-action denemesinin başarısız kapanışıdır.

## Kapsam

- Faz adı: `v10_0_1_phase_1_clock_reward_recovery_140_160`
- Checkpoint: `up40`
- Log aralığı: `update 1-56`
- Episode sayısı: `147`
- Başarı: `1/147` (`0.680%`)
- Son 100 episode başarı: `0/100`

## Sonuç Dağılımı

- `high_altitude`: `143`
- `wrong_way`: `2`
- `success`: `1`
- `low_agl`: `1`

## Gözlem

- İlk success `episode_id=6`, `update=3`, `step=268` içinde geldi.
- Bu success temizdi: final distance `4.23m`, final theta `24.24deg`, final alignment `0.912`.
- Buna rağmen sonraki kuyruk tamamen `high_altitude` ağırlıklı kaldı.
- Ortalama final theta `132.41deg`, final alignment `-0.661`, final distance `112.33m`.

## Karar

V10 action mimarisi V9'a göre daha doğru yönde olsa da saf PPO exploration hâlâ yeterli olmadı.
Reward düzeltmesi ilk başarıyı üretti fakat kararlı davranışa dönüşmedi.

Bir sonraki sürüm `v11` olacak:

- Reward değerleri loglardan offline tahminlenecek.
- Hafif orientation warm-start / behavior cloning pretraining eklenecek.
- PPO, rastgele policy yerine hedef yönüne bakan bir başlangıç policy'sinden devam edecek.

## Dosyalar

- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/step_log.csv.zip.part001`
- `logs/step_log.csv.zip.part002`
- `models/ppo_v10_model_up40.keras`
- `models/ppo_v10_state_up40.pkl.gz`
