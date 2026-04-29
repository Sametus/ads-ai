# ADS-AI Hava Savunma RL Projesi

ADS-AI, Unity fizik simülasyonu içinde hareket eden bir roketin yaklaşan hedefi vurmayı öğrenmesi için geliştirilen reinforcement learning (pekiştirmeli öğrenme) projesidir. Unity sahnesi fizik, geometri ve telemetry üretir; Python tarafı bu verileri state haline getirir, reward hesaplar ve güncel sürümde SAC tabanlı ajan ile action üretir.

Bu README, projeyi ilk kez inceleyen bir kişinin kodu, deney geçmişini, mevcut başarısızlık noktalarını ve sonraki inceleme alanlarını hızlıca anlaması için hazırlanmıştır.

## Mevcut Durum

- Güncel takip edilen sürüm: `v15.0.4`.
- Aktif eğitim hattı sadece SAC'tir; PPO, teacher collect ve pretrain dosyaları güncel runtime'dan kaldırılmıştır.
- Son commit baz çizgisi: V10 hibrit discrete clock-direction denemesi başarısız olarak arşivlendi.
- V11, PPO eğitimine devam etmeden önce klasik güdüm algoritmasıyla sahnenin fiziksel olarak vurulabilir olup olmadığını ölçen sağlık testi aşamasıdır.
- Daha önceki pretrain denemesi kalıcı çözüm olarak tutulmadı; ilgili pretrain/geçici analiz dosyaları çalışma ağacından temizlendi.
- Root `logs/` ve `models/` klasörleri runtime çıktısıdır ve `.gitignore` kapsamındadır.
- Kalıcı geçmiş deneyler `archives/` altında saklanır.

Son bilinen V10 sonucu:

- Arşiv: `archives/v10_0_1_failed_up40/`
- Episode sayısı: `147`
- Success: `1/147` (`%0.680`)
- Dominant hata: `high_altitude`
- Tanı: Action/state mimarisi bazı durumlarda vurma üretebildi, fakat PPO bunu kararlı hedef yönelimine çeviremedi.

İlk V11 aracı:

- Script: `scripts/pn_guidance_test.py`
- Amaç: RL kullanmadan PN (Proportional Navigation / oransal güdüm) ile hedefin vurulup vurulamadığını test etmek.
- Çıktı: `logs/pn_guidance_test.csv`
- Özet çıktı: `logs/pn_guidance_test_summary.csv`
- Test seçenekleri: `--mode blend|pn|pursuit|accel|direct`, `--radius-min`, `--radius-max`, `--altitude-guard`, `--step-delay`, `--pause-on-success`
- Yorum: PN başarılı olursa simülasyon/action otoritesi yeterli kabul edilir ve sonraki adım öğretmen verisi toplamaktır. PN başarısız olursa önce Unity fizik, kuvvet, hedef hareketi ve action uygulaması incelenmelidir.
- V11.0.2 notu: Unity thrust artık `rocketPoint.forward` yönünden uygulanır. Düşük irtifada yukarı toparlama komutu korunur; yatay/aşağı yönlü dönüşler daha dikkatli uygulanır.
- V11.0.3 notu: `--altitude-guard` kalkışta sürekli yukarı basmayacak şekilde yumuşatıldı; guard sadece düşüş riski veya kritik alçak irtifa durumunda devreye girer.
- V11.0.4 notu: PN/ödül denemesine devam etmeden önce Unity action eksenleri tek tek test edilecek. `scripts/action_axis_test.py`, `clock_12/6/3/9` komutlarının beklenen yönde burun dönüşü üretip üretmediğini CSV özetleriyle ölçer.
- V11.0.5 notu: İlk axis audit sonucunda roll düzeltmesinin aktif steering sırasında baskın kaldığı görüldü. Roll kontrolü kaldırılmadı; fakat manevra komutu varken ve clock frame dik konumdayken roll torku ikincil seviyeye indirildi.
- V11.0.6 notu: `action_axis_test.py` içine `clock_12_after_clock_6` aşamalı testi eklendi. Roket dikken clock-12 tekil kalabildiği için önce roket eğilir, sonra clock-12 toparlama yönü ölçülür.
- V11.0.7 notu: Roll düzeltmesi artık sadece ölçeklenmiyor; aktif steering sırasında izin verilen roll correction limiti de küçülüyor. Böylece roll torku `±34` saturasyonuna kolayca vuramayacak.
- V11.0.8 notu: Fizik motoruna gönderilen son roll torku da `maxRollTorqueCommand=3.0` ile sınırlandı. Önceki limit command seviyesindeydi ve `rollTorqueScale * torqueScale` sonrası yine büyük z-torku oluşabiliyordu.
- V11.0.9 notu: Roll artık torkla bastırılmıyor; `suppressRollRate=1` ile her fizik adımı sonunda roketin kendi forward ekseni etrafındaki angular velocity bileşeni temizleniyor.
- V11.0.10 notu: Clock action artık açık çevrim tork değil, kapalı çevrim burun dönüş hızı isteği olarak uygulanır. `clockTurnRateTarget=1.8`, `clockTurnRateControllerGain=1.15`, `maxPitchYawTorqueCommand=3.2`.
- V11.0.11 notu: Roket tam dikken gravity tabanlı `clock_12` tanımsız kalır. Bu durumda artık roll/gövde yan ekseni yerine hedef bearing/cached guidance fallback kullanılır.
- V11.0.12 notu: PN test scriptine `--pn-sign` eklendi. Bu parametre pursuit yönünü bozmadan sadece PN/lead bileşeninin işaretini test etmek için kullanılır.
- V11.0.13 notu: Blend PN testine yakın mesafe handover eklendi. `--lead-fade-start` ve `--lead-fade-end` ile PN/lead etkisi yakında azalır, pursuit hedefe kilitleme etkisi baskın kalır.
- V11.0.14 notu: PN/lead vektörü pursuit ile toplanmadan önce normalize edilir. Böylece PN'in ham büyüklüğü yakın mesafede pursuit komutunu ezemez. Varsayılan blend ayarı `pursuit_blend=0.80`, `lead_fade_start=95`, `lead_fade_end=45`.
- V11.0.15 notu: PN baseline hâlâ success alamadığı için reward/RL yerine actuator otoritesi güncellendi. `clockTurnRateTarget=2.8`, `clockTurnRateControllerGain=1.8`, `maxPitchYawTorqueCommand=6.0`; PN test varsayılan thrust `700`.
- V11.0.16 notu: PN testine `--mode accel` eklendi. Bu mod PN'i doğrudan clock yönü olarak değil, LOS rate ve closing speed üzerinden yanal ivme komutu olarak hesaplar; ivmeyi `rocket_mass`, `thrust`, gravity compensation ve lateral acceleration limitleriyle sınırlar.
- V11.0.17 notu: 300 m testinde roket hedefe baksa bile uçuş yolu 20-28 m dışarıdan geçtiği için `--mode accel` içine hız hattı düzeltmesi eklendi. Yeni parametreler: `velocity_track_gain=0.25`, `velocity_accel_fraction=0.65`, `loft_weight=0.20`, `loft_agl=45`.
- V11.0.18 notu: Test için `--mode direct` eklendi. Bu mod clock/torque action zincirini bypass eder; Python dünya uzayında gerekli ivmeyi hesaplar, Unity bu ivmeyi doğrudan uygular ve roket burnunu hedefe kilitler. Amaç RL değil, sahnede vurmanın mümkün olduğunu kesin göstermek.
- V12.0.0 notu: RL action mimarisi direct acceleration olarak sadeleştirildi. Ajan artık `thrust + discrete clock` seçmez; `accel_right`, `accel_up`, `accel_forward` continuous action üretir. Python bu action'ı Unity direct packet formatına çevirir.
- V12.0.1 notu: Direct RL kalkış güvenliği eklendi. Reset sonrası ilk state saklanır, yerdeyken rastgele action'ın roketi yana/aşağı çarpması engellenir, direct look rotasyonu gravity-up referansı ile roll-free hale getirilir ve console log renkleri korunur.
- V13.0.0 notu: Uzman önerisine uygun olarak doğrudan random PPO yerine öğretmen destekli eğitim hattı eklendi. Önce `teacher_collect.py` çalışan direct controller ile veri toplar, sonra `teacher_pretrain.py` policy ağını bu action'lara yaklaştırır, en son `train.py` PPO fine-tune yapar.
- V14.0.0 notu: PPO fine-tune sırasında action dağılımı `forward≈1` ve pozitif `up` kanalına çökünce off-policy SAC deneme hattı eklendi. SAC, replay buffer sayesinde iyi teacher adımlarını tek rollout sonunda atmadan tekrar tekrar kullanır. Yeni komut: `python scripts/train_sac.py`.
- V15.0.0 notu: PPO ve teacher/pretrain aktif koddan kaldırıldı. `scripts/train.py` artık sadece SAC çalıştırır ve ajan sıfırdan, kendi stochastic actor'ü ile başlar.
- V15.0.2 notu: SAC canlı training logları için `scripts/plot_sac_report.py` eklendi. Bu script PPO dönemindeki faz grafiklerine benzer şekilde success, radius, reset haritası, action diagnostik ve hit pozisyonu PNG'leri üretir.
- V15.0.3 notu: SAC direct action artık serbest dünya ivmesi uygulamaz. Ajan hedef bakışına küçük sağ/yukarı sapma ve pozitif ileri ivme seçer; Unity egzoz efekti de `rocketPoint` arkasına hizalanır.
- V15.0.4 notu: Unity donmasını azaltmak için SAC update daha geç ve seyrek başlar. Direct mode'da burun tersine/yanına taşınan hız bileşenleri yumuşak sönümlenir.

Bu proje şu an "tamamlanmış başarılı model" durumunda değildir. Kod ve loglar, sonraki teknik inceleme için korunmuş araştırma/deney ortamıdır.

## Ana Hedef

Roket, başlangıçta rampadan dik veya dike yakın kalkar. Hedef belirli bir menzilden ve heading offset ile sahneye yerleştirilir, sabit hızla yaklaşır. Ajanın amacı:

- Roketin burnunu hedefe yöneltmek.
- Yeterli kapanma hızı üretmek.
- Yere çakılmadan ve aşırı yükselmeden hedefe yaklaşmak.
- `success_distance` ve `success_alignment` koşullarını sağlayarak hedefi vurmak.

Başarı terminal koşulu Python tarafında hesaplanır:

- Mesafe `success_distance` altında olmalı.
- `alignment = cos(theta)` değeri `success_alignment` üstünde olmalı.
- `closing_speed` minimum eşiği sağlamalı.

## Klasör Yapısı

```text
ads_ai/
  ads_ai/                     Unity projesi
    Assets/Scripts/Env.cs      Unity RL ortamı, fizik ve telemetry
    Assets/Scripts/Connector.cs TCP/JSON iletişim katmanı
    Assets/Scenes/             Unity sahneleri
  scripts/                     Python RL kodları
    train.py                   SAC off-policy training döngüsü
    test.py                    Kaydedilmiş model ile test
    sac_agent.py               SAC actor/critic ve replay buffer
    env.py                     Python Env wrapper, reward, state/action
    settings.py                Port, rollout, checkpoint ayarları
    log.py                     CSV ve terminal logları
    plot_sac_report.py         SAC canlı training grafik üretimi
    plot_phase_report.py       Statik grafik üretimi
    plot_phase_report_plotly.py Plotly HTML grafik üretimi
  archives/                    Faz/sürüm arşivleri
  docs/                        Notlar ve tuning belleği
  logs/                        Runtime logları, git'e alınmaz
  models/                      Runtime checkpoint'leri, git'e alınmaz
  CHANGELOG.md                 Kronolojik sürüm/faz notları
  VERSION                      Aktif repo sürümü
```

## Çalışma Akışı

1. Python, Unity'ye TCP üzerinden `reset` paketi yollar.
2. Unity hedefi ve roketi resetler.
3. Unity state ve telemetry paketini Python'a yollar.
4. Python state'i normalize eder.
5. SAC ajan action üretir.
6. Python action'ı aktif mimariye göre Unity direct-acceleration paketine çevirir.
7. Unity action'ı uygular ve yalnızca Python step isteği geldiğinde `Physics.Simulate` ile bir fizik adımı ilerler.
8. Python reward ve terminal koşullarını hesaplar.
9. SAC training loop replay buffer'a transition yazar.
10. Replay buffer yeterli veriye ulaşınca SAC mini-batch update yapar.

Bu tasarımda Unity gerçek zamanlı olarak serbest akmaz; fizik adımı Python step döngüsü tarafından kontrol edilir.

## Gereksinimler ve Sürüm Bilgisi

Bu proje Windows üzerinde geliştirilmiştir. Karşı tarafta sorunsuz açılabilmesi için Unity, Python ve Python kütüphane sürümlerinin mümkün olduğunca aynı tutulması önerilir.

### Doğrulanmış Yerel Ortam

Bu README güncellenirken yerel `rl_codes` conda ortamında doğrulanan sürümler:

| Bileşen | Sürüm | Not |
|---|---:|---|
| İşletim sistemi | Windows | Proje PowerShell ve Windows path yapısı ile kullanıldı |
| Unity Editor | `6000.3.2f1` | `ads_ai/ProjectSettings/ProjectVersion.txt` içinde kayıtlı |
| Unity revision | `6000.3.2f1 (a9779f353c9b)` | Aynı dosyada kayıtlı |
| Python | `3.7.16` | `C:\Users\husey\miniconda3\envs\rl_codes\python.exe` |
| TensorFlow | `2.10.1` | SAC modeli ve checkpoint yükleme/kaydetme için gerekli |
| Keras | `2.10.0` | TensorFlow bağımlılığı olarak kullanılıyor |
| NumPy | `1.21.6` | State/action/reward hesapları |
| Pandas | `1.3.5` | CSV log ve analiz okuma |
| Matplotlib | `3.5.3` | Statik grafik scriptleri |
| Seaborn | `0.12.2` | Yerel ortamda mevcut; temel training için şart değil |
| Pillow | `9.5.0` | Matplotlib görsel işlemleri için dolaylı/opsiyonel |
| Protobuf | `3.19.6` | TensorFlow uyumluluğu için önemli |
| h5py | `3.8.0` | Keras model dosyaları için kullanılır |
| SciPy | `1.7.3` | Yerel ortamda mevcut; temel training için doğrudan şart değil |
| scikit-learn | `1.0.2` | Yerel ortamda mevcut; mevcut runtime kodu için şart değil |

Yerel ortamda `plotly` kurulu değildir. Bu nedenle `scripts/plot_phase_report_plotly.py` çalıştırılacaksa ayrıca kurulmalıdır.

### Ana Training İçin Minimum Python Paketleri

Core training/test akışı için gerekli ana paketler:

```text
tensorflow==2.10.1
numpy==1.21.6
pandas==1.3.5
matplotlib==3.5.3
protobuf==3.19.6
h5py==3.8.0
```

Statik grafikler için `matplotlib` yeterlidir. Plotly HTML grafikler için ek paket gerekir:

```text
plotly
```

### Önerilen Kurulum

Sıfırdan conda ortamı oluşturmak için:

```powershell
conda create -n rl_codes python=3.7.16
conda activate rl_codes
python -m pip install --upgrade pip
python -m pip install tensorflow==2.10.1 numpy==1.21.6 pandas==1.3.5 matplotlib==3.5.3 seaborn==0.12.2 pillow==9.5.0 protobuf==3.19.6 h5py==3.8.0
```

Plotly raporları da kullanılacaksa:

```powershell
python -m pip install plotly
```

### GPU Durumu

TensorFlow GPU kullanımı için Windows üzerinde TensorFlow `2.10.x` ailesi tercih edilmiştir. Yerel kontrolde TensorFlow GPU cihazı görememiştir:

```text
tf.config.list_physical_devices("GPU") -> []
```

Yerel uyarı:

```text
cudnn64_8.dll not found
```

Bu, GPU ile çalıştırmak için uyumlu NVIDIA driver, CUDA ve cuDNN kurulumunun tamamlanması gerektiğini gösterir. Projedeki `scripts/cuda_bootstrap.py`, conda ortamındaki `Library/bin` ve `DLLs` klasörlerini `PATH` içine eklemeye çalışır; ancak eksik DLL dosyasını kendisi kurmaz.

GPU doğrulama komutu:

```powershell
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

Çıktı `[]` ise training CPU ile başlar. CPU ile çalışır fakat eğitim süresi belirgin şekilde uzar.

### Ortam Doğrulama Komutları

Karşı taraf kurulumu yaptıktan sonra şu komutlarla sürümleri kontrol edebilir:

```powershell
python --version
python -c "import tensorflow as tf; print(tf.__version__)"
python -c "import numpy as np; print(np.__version__)"
python -c "import pandas as pd; print(pd.__version__)"
python -c "import matplotlib; print(matplotlib.__version__)"
```

Unity sürümü için:

```powershell
Get-Content ads_ai\ProjectSettings\ProjectVersion.txt
```

## Unity Tarafı

Unity projesi:

```text
ads_ai/
```

Ana script:

```text
ads_ai/Assets/Scripts/Env.cs
```

Önemli Unity davranışları:

- `Env.cs` sınıf adı ile dosya adı eşleşmelidir. Unity script component eklerken sınıf adı bulunamazsa `Env.cs` / `Env` eşleşmesi kontrol edilmelidir.
- `Connector.cs` Python ile TCP bağlantısı kurar.
- `Env.cs` gelen action paketlerini uygular.
- `StepOnce()` içinde hedef hareket ettirilir, roket action alır, fizik simüle edilir, yeni state Python'a gönderilir.
- Target yüksekliği varsayılan olarak sabit tutulur.
- Roll hard-lock değildir; roll stabilization torque ile baskılanır.

Unity inspector içinde önemli alanlar:

- `rocket`, `rocketPoint`, `target`, `targetPoint`
- `rocketRb`, `targetRb`
- `thrustScale`
- `torqueScale`
- `rollTorqueScale`
- `rollStabilizationGain`
- `rollDampingGain`
- `betaValidityFloor`
- `targetSpeed`

Scene dosyası serialized değerleri sakladığı için sadece `Env.cs` içindeki default değerleri değiştirmek bazen Unity sahnesindeki mevcut component değerlerini değiştirmez. Şüphe varsa `SampleScene.unity` serialized değerleri de kontrol edilmelidir.

## Python Tarafı

### `scripts/settings.py`

Temel runtime ayarları burada tutulur:

```python
IP = "127.0.0.1"
PORT = 5005
SAC_MODEL_PREFIX = "sac_v15_forward_damped"
SAC_TOTAL_STEPS = 250000
SAC_BATCH_SIZE = 64
SAC_REPLAY_SIZE = 200000
SAC_START_TRAINING_STEPS = 12000
SAC_TRAIN_EVERY_STEPS = 32
SAC_SAVE_EVERY_STEPS = 5000
```

Checkpoint seçimi otomatik yapılır. `models/` içindeki en yüksek SAC step numarasına sahip actor bulunursa yüklenir; model yoksa eğitim sıfırdan başlar.

### `scripts/train.py`

Training döngüsü:

- Unity bağlantısını açar.
- `SACAgent` actor/critic ağlarını kurar.
- Checkpoint varsa yükler, yoksa sıfırdan başlar.
- İlk step'ten itibaren action SAC actor tarafından üretilir; teacher/pretrain yoktur.
- Her transition replay buffer'a yazılır.
- Replay buffer `SAC_START_TRAINING_STEPS` eşiğini geçince SAC update yapar.
- `SAC_SAVE_EVERY_STEPS` aralığıyla actor/critic checkpoint kaydeder.

### `scripts/sac_agent.py`

SAC ajanı:

- Actor ve iki ayrı critic ağı içerir.
- Replay buffer ile geçmiş transition'ları tekrar kullanır.
- Target critic ağları `SAC_TAU` ile yumuşak güncellenir.
- Çıkışlar:
  - Actor: `aim_right`, `aim_up`, `forward_accel` anlamına gelen 3 continuous action üretir.
  - Critic: state/action çifti için Q değeri.

Temel SAC parametreleri:

```text
SAC_ACTOR_LR = 3.0e-5
SAC_CRITIC_LR = 1.0e-4
SAC_ALPHA_LR = 3.0e-5
SAC_INITIAL_ALPHA = 0.25
SAC_GAMMA = 0.995
SAC_TAU = 0.005
SAC_REWARD_SCALE = 0.02
SAC_BATCH_SIZE = 64
```

### `scripts/env.py`

Python Env wrapper:

- Reset konumlarını hesaplar.
- Unity state paketini parse eder.
- State normalizasyonu yapar.
- Action'ı Unity action formatına çevirir.
- Reward hesaplar.
- Terminal koşullarını belirler.
- Log için telemetry alanlarını düzleştirir.

## State Tasarımı

Güncel direct-acceleration state boyutu `16`'dır:

| Alan | Açıklama |
|---|---|
| `distance` | Roket-hedef mesafesi |
| `rel_dir_right/up/forward` | Hedef yönünün guidance frame bileşenleri |
| `rel_vel_right/up/forward` | Hedef-roket göreli hızının guidance frame bileşenleri |
| `rocket_vel_right/up/forward` | Roket hızının guidance frame bileşenleri |
| `closing_speed` | Hedefe yaklaşma hızı |
| `theta_rad` | Roket burnu ile hedef doğrultusu arasındaki genel açı |
| `agl` | Above ground level, yerden yükseklik |
| `alt_error` | Hedef ile roket arasındaki irtifa farkı |
| `target_speed` | Hedef hızı |
| `rocket_speed` | Roket hızı |

Normalizasyon:

- Mesafe, hız ve irtifa gibi değerler `tanh` ile sıkıştırılır.
- Açılar radyan olarak taşınır.
- Direct state içinde clock kanalları aktif observation değildir; eski clock alanları log/diagnostic için korunabilir.

## Action Tasarımı

V15.0.3 sonrası aktif action boyutu `3`'tür:

| Action | Açıklama |
|---|---|
| `aim_right` | Hedef bakış yönüne sağ/sol sapma ekler, `[-1, 1]` |
| `aim_up` | Hedef bakış yönüne gravity-up/down sapma ekler, `[-1, 1]` |
| `forward_accel` | Pozitif ileri ivme büyüklüğünü seçer; negatif değer geri itki değil düşük ileri itki demektir |

Python bu normalized action'ı önce hedef bakış yönüne küçük sapma olarak ekler:

```text
look_dir = normalize(target_dir + right_ref * aim_right + up_ref * aim_up)
```

Sonra yalnızca bu bakış yönünde pozitif ileri ivme üretir:

```text
accel_mag = lerp(DIRECT_ACTION_MIN_ACCEL, DIRECT_ACTION_MAX_ACCEL, (forward_accel + 1) / 2)
accel_world = look_dir * accel_mag
```

Unity'ye giden direct packet:

```text
[-7777, accel_x, accel_y, accel_z, look_x, look_y, look_z]
```

`-7777` marker'ı Unity tarafında eski thrust/clock torque yolunu bypass eder. Unity dünya ivmesini uygular ve roket burnunu aynı `look_dir` yönüne hizalar. Bu kısıt, roketin burnu başka yöne bakarken yanlamasına veya geri geri itilmesini engellemek için eklendi.

## Reward Tasarımı

Reward çok bileşenli olarak hesaplanır. Her bileşen step log içinde ayrı kolon olarak tutulur.

Ana bileşenler:

- Step penalty.
- Mesafe ilerlemesi.
- Alignment.
- Closing speed.
- Theta progress.
- Alpha/beta progress.
- Direct mode'da eski clock reward bileşenlerinin çoğu sıfırlanır veya sadece diagnostic/log amacıyla kalır.
- Near-success bonus.
- Reverse/wrong-way penalty.
- Roll ve angular velocity cezası.
- Soft floor / soft ceiling.
- Thrust gate.
- Low altitude escape/control/sink penalty.
- Terminal reward/penalty.

Terminal durumları:

| Terminal | Anlam |
|---|---|
| `success` | Mesafe, alignment ve closing koşulları sağlandı |
| `collision` | Roket yere/sahneye çarptı |
| `low_agl` | Yerden yükseklik düşük eşiğin altına indi |
| `high_altitude` | Roket maksimum irtifayı aştı |
| `wrong_way` | Hedeften uzaklaşma ve büyük açı paterni oluştu |
| `timeout` | Episode maksimum step sayısına ulaştı |

Önemli problem: Terminal reward büyüklüğü tek başına yeterli olmadı. Başarıya giden ara davranışları doğru işaretleyen reward bileşenleri hâlâ projenin en kritik teknik konularından biridir.

## Loglar

Runtime logları:

```text
logs/step_log.csv
logs/episode_log.csv
logs/update_log.csv
```

`step_log.csv`:

- Her physics step için state, action, reward breakdown ve telemetry içerir.
- Çok hızlı büyür.
- Git'e alınmaz.

`episode_log.csv`:

- Her episode sonunda başlangıç/final mesafe, açı, irtifa, terminal reason ve return içerir.

`update_log.csv`:

- Her SAC update/log aralığı sonrası loss, entropy, alpha ve learning rate içerir.

Kalıcı analiz için önemli loglar faz bitişinde `archives/` altına taşınmalıdır.

## Grafikler

Statik grafik scripti:

```powershell
python scripts/plot_phase_report.py
```

SAC canlı training grafik scripti:

```powershell
python scripts/plot_sac_report.py --phase-contains v15_0_4 --out-dir logs\plots
```

Plotly interaktif grafik scripti:

```powershell
python scripts/plot_phase_report_plotly.py
```

Bu scriptler faz raporlarında genellikle şu grafikleri üretmek için kullanıldı:

- Success rate.
- Success episode yoğunluğu.
- Reset radius dağılımı.
- Radius/outcome polar grafik.
- Faz sınırlarıyla radius-success planı.
- Clock action alignment analizleri.
- SAC action/direct acceleration diagnostikleri.
- Success varsa hedefin vurulduğu dünya konumları.

## Nasıl Çalıştırılır

1. Unity Hub ile `ads_ai/` Unity projesini aç.
2. Unity Editor içinde `SampleScene` sahnesini aç.
3. Unity'de Play'e bas ve Python bağlantısını bekle.
4. Ayrı PowerShell terminalinde proje köküne gel.

```powershell
cd C:\Users\husey\Desktop\ads_ai
conda activate rl_codes
```

5. Training başlat.

```powershell
python scripts/train.py
```

6. Test için:

```powershell
python scripts/test.py
```

## Yeni Faz Denemesi Nasıl Yapılır

Bu repo artık tek aktif faz mantığıyla çalışır. Faz değiştirmek için:

1. `scripts/env.py` içindeki `ACTIVE_PHASE_CONFIG` düzenlenir.
2. `spawn_radius_min/max`, `max_step`, reward katsayıları değiştirilir.
3. Eski faz log/model dosyaları arşivlenir.
4. Root `logs/` temizlenir.
5. Kullanılmayacak checkpoint'ler root `models/` altından silinir.
6. Yeni faz çalıştırılır.

Önerilen disiplin:

- Train edilmemiş yeni faz ayarları commitlenmemelidir.
- Önce eski faz arşivlenmeli ve commit/push yapılmalıdır.
- Sonra yeni faz local olarak uygulanıp run edilmelidir.

## Arşiv Geçmişi

Önemli arşivler:

| Arşiv | Kısa not |
|---|---|
| `archives/phase_1_1` - `phase_1_9` | Erken curriculum fazları, kısa menzil başarı denemeleri |
| `archives/phase_2_0` | Daha yüksek başarı oranı görülen önceki faz snapshot'ı |
| `archives/phase_2_2` | `up2520` handoff, sonrasında drift gözlendi |
| `archives/v8_failed_final_up2514` | V8 final başarısız snapshot |
| `archives/v9_0_0_failed_up100` | Continuous clock-channel action başarısız snapshot |
| `archives/v10_0_1_failed_up40` | Hybrid discrete clock-direction V10 başarısız snapshot |

Kronolojik detaylar için:

```text
CHANGELOG.md
docs/tuning_memory.md
```

## Deneylerden Çıkan Ana Dersler

### 1. Kısa menzilde başarı genelleşmedi

Erken fazlarda daha yakın spawn radius değerlerinde yüksek success oranları görüldü. Radius arttıkça target artık roket rampasının üzerinden geçerken tesadüfen vurulmuyor; roketin aktif yönelme öğrenmesi gerekiyor.

### 2. Reward terminal cezası tek başına çözüm olmadı

`wrong_way`, `low_agl` veya `high_altitude` cezalarını büyütmek davranışı kararlı şekilde düzeltmedi. Asıl eksik, başarıya giden ara davranışların yeterince net ve dengeli ödüllendirilmesiydi.

### 3. Action/state temsilinde çok deneme yapıldı

V8 gravity-based signed angle yapısı denenmiştir. V9 continuous clock-channel action denenmiştir. V10 discrete clock-direction action denenmiştir. V10 bazı başarı örnekleri üretse de kararlı policy oluşturamadı.

### 4. Roll ve clock frame ilişkisi kritik

Roket roll yapmadığında bile roketin "sağ/sol/yukarı/aşağı" anlamı hedef yönüne ve gravity referansına göre değişir. Bu nedenle body-frame pitch/yaw yerine gravity/clock referanslı state-action tasarımı yapılmıştır.

### 5. PPO credit assignment problemi belirgin

Success terminali çoğu zaman episode sonunda gelir. Başarıya sebep olan erken yönelme action'larına reward sinyali zayıf ulaşabilir. Bu, reward shaping veya auxiliary learning ile ele alınmalıdır.

## Bilinen Açık Problemler

Sonraki incelemede özellikle şu başlıklar kontrol edilmelidir:

1. State yeterli mi?

   Hedef yönü, göreli hız, roket angular velocity, roll durumu ve gravity frame ilişkisi gerçekten Markovian karar için yeterli mi?

2. Action doğru mu?

   Discrete clock-direction action yön seçimini sadeleştiriyor, fakat dönüş büyüklüğünü ajandan alıyor mu? Şu an dönüş büyüklüğü sabit çarpanla geliyor.

3. Reward yönlendirici mi?

   Success'e yaklaşan ama vurmayan episode'lar başarısız episode'lardan yeterince ayrılıyor mu?

4. Terminal koşulları erken mi kesiyor?

   `wrong_way`, `low_agl`, `high_altitude` terminal koşulları recovery şansını kesiyor olabilir.

5. Curriculum doğru mu?

   Yakın menzilde öğrenilen davranış uzak menzile taşınmıyor olabilir. Spawn radius ve target heading stratejisi yeniden tasarlanabilir.

6. PPO tek başına yeterli mi?

   Bu problem için imitation learning, model-based guidance, scripted autopilot baseline veya curriculum teacher gerekebilir.

7. Unity fizik parametreleri tutarlı mı?

   Torque, thrust, roll stabilization ve scene serialized değerleri kodla uyumlu mu?

## Önerilen İnceleme Sırası

1. `archives/v10_0_1_failed_up40/README.md` dosyasını oku.
2. `scripts/env.py` içindeki `STATE_KEYS`, `ACTION_KEYS`, `ACTIVE_PHASE_CONFIG` ve reward hesaplarını incele.
3. `ads_ai/Assets/Scripts/Env.cs` içindeki `BuildClockFrame`, `ApplyAction`, `BuildStatePacket` akışını incele.
4. `logs/episode_log.csv` ve `step_log.csv` üzerinden success / wrong_way / high_altitude step örneklerini karşılaştır.
5. Reward breakdown kolonlarında success'e yaklaşan step'lerde hangi bileşenlerin pozitif/negatif olduğunu ölç.
6. Action distribution ile target clock direction eşleşmesini analiz et.
7. Önce scripted baseline ile hedefe yönelme mümkün mü test et.
8. Baseline mümkünse aktif SAC reward/action tasarımını baseline davranışına göre yeniden sadeleştir.

## Temizlik Notu

Bu snapshot'ta aşağıdaki geçici dosyalar tutulmaz:

- `pretrain_lab/`
- `reward_lab/`
- Root `logs/` içeriği
- Root `models/` içeriği

Bunlar runtime/deneme çıktısı olduğu için kalıcı teknik incelemede arşivlenmiş faz logları ve tracked kod tercih edilmelidir.

## Önemli Uyarılar

- Bu proje şu anda başarılı final model üretmiş değildir.
- `archives/` içindeki bazı eski fazlar yüksek success oranı göstermiş olsa da bunlar daha kolay curriculum koşullarına aittir.
- Daha uzak menzil ve daha gerçekçi interception koşullarında policy kararsızlaşmıştır.
- Bir sonraki ciddi adım, reward katsayısı ezbere değiştirmek yerine state-action-reward tasarımının birlikte gözden geçirilmesidir.

## Kısa Komut Özeti

```powershell
# V15 SAC-only training
python scripts/train.py

# Test
python scripts/test.py

# Unity action eksen testi
python scripts/action_axis_test.py --episodes-per-command 1 --steps 120 --step-delay 0.02

# PN klasik gudum saglik testi
python scripts/pn_guidance_test.py --episodes 5 --radius-min 140 --radius-max 160

# Acceleration-autopilot PN saglik testi
python scripts/pn_guidance_test.py --mode accel --episodes 5 --radius-min 140 --radius-max 160 --target-y 50 --terminal-max-altitude 140 --output logs/pn_accel_v11017.csv

# 300m acceleration PN testi
python scripts/pn_guidance_test.py --mode accel --episodes 5 --radius-min 280 --radius-max 300 --target-y 50 --terminal-max-altitude 180 --max-steps 1000 --output logs/pn_accel_v11017_r280_300.csv

# Direct-guidance hedef vurma testi
python scripts/pn_guidance_test.py --mode direct --episodes 5 --radius-min 280 --radius-max 300 --target-y 50 --terminal-max-altitude 240 --max-steps 1000 --output logs/pn_direct_v11018_r280_300.csv

# SAC canlı training PNG raporu
python scripts/plot_sac_report.py --phase-contains v15_0_4 --out-dir logs\plots

# Statik faz raporu
python scripts/plot_phase_report.py

# Plotly faz raporu
python scripts/plot_phase_report_plotly.py
```
