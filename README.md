# ADS-AI Hava Savunma RL Projesi

ADS-AI, Unity fizik simülasyonu içinde hareket eden bir roketin yaklaşan hedefi vurmayı öğrenmesi için geliştirilen reinforcement learning (pekiştirmeli öğrenme) projesidir. Unity sahnesi fizik, geometri ve telemetry üretir; Python tarafı bu verileri state haline getirir, reward hesaplar ve PPO tabanlı ajan ile action üretir.

Bu README, projeyi hiç bilmeyen bir mühendisin kodu, deney geçmişini, mevcut başarısızlık noktalarını ve sonraki inceleme alanlarını hızlıca anlaması için hazırlanmıştır.

## Mevcut Durum

- Güncel takip edilen sürüm: `v10.0.2`.
- Son commit baz çizgisi: V10 hibrit discrete clock-direction denemesi başarısız olarak arşivlendi.
- V11/pretrain denemesi kalıcı çözüm olarak tutulmadı; ilgili pretrain/geçici analiz dosyaları çalışma ağacından temizlendi.
- Root `logs/` ve `models/` klasörleri runtime çıktısıdır ve `.gitignore` kapsamındadır.
- Kalıcı geçmiş deneyler `archives/` altında saklanır.

Son bilinen V10 sonucu:

- Arşiv: `archives/v10_0_1_failed_up40/`
- Episode sayısı: `147`
- Success: `1/147` (`%0.680`)
- Dominant hata: `high_altitude`
- Tanı: Action/state mimarisi bazı durumlarda vurma üretebildi, fakat PPO bunu kararlı hedef yönelimine çeviremedi.

Bu proje şu an "tamamlanmış başarılı model" durumunda değildir. Kod ve loglar, bir sonraki mühendislik incelemesi için korunmuş araştırma/deney ortamıdır.

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
    train.py                   PPO training döngüsü
    test.py                    Kaydedilmiş model ile test
    agent.py                   PPO actor-critic modeli
    env.py                     Python Env wrapper, reward, state/action
    settings.py                Port, rollout, checkpoint ayarları
    log.py                     CSV ve terminal logları
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
5. PPO ajan action üretir.
6. Python action'ı Unity'nin beklediği thrust/clock torque kanallarına çevirir.
7. Unity action'ı uygular ve yalnızca Python step isteği geldiğinde `Physics.Simulate` ile bir fizik adımı ilerler.
8. Python reward ve terminal koşullarını hesaplar.
9. Training loop rollout buffer'ına transition yazar.
10. `ROLLOUT_LEN` kadar step dolunca PPO update yapılır.

Bu tasarımda Unity gerçek zamanlı olarak serbest akmaz; fizik adımı Python step döngüsü tarafından kontrol edilir.

## Gereksinimler

Bu proje Windows üzerinde geliştirilmiştir.

- Unity: `6000.3.2f1`
- Python: `3.7.x`
- TensorFlow GPU için önerilen sürüm: `tensorflow==2.10.0`
- Ana paketler: `numpy`, `pandas`, `tensorflow`, `plotly`

Örnek ortam:

```powershell
conda create -n rl_codes python=3.7
conda activate rl_codes
pip install tensorflow==2.10.0 numpy pandas plotly
```

Not: Projede CUDA DLL yolu için `scripts/cuda_bootstrap.py` kullanılır. GPU bulunamazsa training CPU ile de başlar, fakat yavaş çalışır.

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
ROLLOUT_LEN = 1200
TOTAL_UPDATES = 10000
SAVE_EVERY_UPDATES = 20
MODEL_PREFIX = "ppo_v10_model"
STATE_PREFIX = "ppo_v10_state"
```

Checkpoint seçimi:

- Varsayılan: `models/` içindeki en yüksek update otomatik yüklenir.
- Manuel checkpoint:

```powershell
$env:ADS_AI_CHECKPOINT_UPDATE="40"
python scripts/train.py
```

### `scripts/train.py`

Training döngüsü:

- Unity bağlantısını açar.
- PPO ajanı kurar.
- Checkpoint varsa yükler.
- `ROLLOUT_LEN` kadar step toplar.
- PPO update yapar.
- `SAVE_EVERY_UPDATES` aralığıyla model kaydeder.

Önemli not: Rollout step bazlıdır, episode bazlı değildir. Bir episode erken `success` ile biterse rollout kesilmez; ortam resetlenir ve aynı update içinde yeni episode'lardan step toplanmaya devam edilir.

### `scripts/agent.py`

PPO ajanı:

- 3 katmanlı MLP.
- Her hidden layer: `512`, aktivasyon: `tanh`.
- Çıkışlar:
  - Continuous thrust mean.
  - Discrete direction logits.
  - Value estimate.

Temel PPO parametreleri:

```text
lr = 2.5e-5
gamma = 0.997
gae_lambda = 0.97
clip_eps = 0.08
ent_coef = 0.006
epochs = 4
batch_size = 256
target_kl = 0.006
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

Güncel V10 state boyutu `23`'tür:

| Alan | Açıklama |
|---|---|
| `distance` | Roket-hedef mesafesi |
| `theta_rad` | Roket burnu ile hedef doğrultusu arasındaki genel açı |
| `alpha_rad` | Gravity referanslı dikey signed angle |
| `beta_rad` | Gravity referanslı yatay signed angle |
| `target_clock_12/6/3/9` | Hedefin roket burnu etrafındaki clock frame yönü |
| `closing_speed` | Hedefe yaklaşma hızı |
| `rel_vel_clock_12/6/3/9` | Clock frame içinde göreli hız bileşenleri |
| `rel_vel_forward` | Roket burnu doğrultusundaki göreli hız |
| `turn_rate_clock_12/6/3/9` | Roket burnunun clock frame yönlerindeki dönüş hızı |
| `turn_rate_roll` | Burnun ileri ekseni etrafındaki roll hızı |
| `clock_validity` | Clock frame'in ne kadar güvenilir olduğu |
| `forward_up_dot` | Roket burnu ile gravity-up ilişkisi |
| `agl` | Above ground level, yerden yükseklik |
| `alt_error` | Hedef ile roket arasındaki irtifa farkı |

Normalizasyon:

- Mesafe, hız ve irtifa gibi değerler `tanh` ile sıkıştırılır.
- Açılar radyan olarak taşınır.
- Clock kanalları `0..1` aralığında tutulur.

## Action Tasarımı

V10 action boyutu `2`'dir:

| Action | Açıklama |
|---|---|
| `thrust` | Continuous değer, `[-1, 1]` aralığından gerçek thrust aralığına çevrilir |
| `turn_direction` | Discrete/categorical clock yön sınıfı |

Discrete yön sınıfları:

| ID | Yön |
|---|---|
| `0` | `hold` |
| `1` | `clock_12` |
| `2` | `clock_12_3` |
| `3` | `clock_3` |
| `4` | `clock_3_6` |
| `5` | `clock_6` |
| `6` | `clock_6_9` |
| `7` | `clock_9` |
| `8` | `clock_9_12` |

Python bu discrete yönü şu Unity action kanallarına genişletir:

```text
[thrust, clock_12_cmd, clock_6_cmd, clock_3_cmd, clock_9_cmd]
```

Unity tarafında zıt kanallar netleştirilir:

```text
clock12Net = clock_12_cmd - clock_6_cmd
clock3Net  = clock_3_cmd  - clock_9_cmd
```

Bu net komut, roket burnu etrafında gravity referanslı clock frame ile torque'a çevrilir.

## Reward Tasarımı

Reward çok bileşenli olarak hesaplanır. Her bileşen step log içinde ayrı kolon olarak tutulur.

Ana bileşenler:

- Step penalty.
- Mesafe ilerlemesi.
- Alignment.
- Closing speed.
- Theta progress.
- Alpha/beta progress.
- Target clock yönüne dönüş.
- Clock action alignment.
- Wrong-channel penalty.
- Coactivation penalty.
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

Önemli problem: Terminal reward büyüklüğü tek başına yeterli olmadı. Başarıya giden ara davranışları doğru işaretleyen reward bileşenleri hâlâ projenin en kritik mühendislik alanıdır.

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

- Her PPO update sonrası loss, entropy, KL, clip fraction ve learning rate içerir.

Kalıcı analiz için önemli loglar faz bitişinde `archives/` altına taşınmalıdır.

## Grafikler

Statik grafik scripti:

```powershell
python scripts/plot_phase_report.py
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

6. Belirli checkpoint ile başlatmak istersen:

```powershell
$env:ADS_AI_CHECKPOINT_UPDATE="40"
python scripts/train.py
```

7. Test için:

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

Bir mühendis incelemesinde özellikle şu başlıklar kontrol edilmelidir:

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

## Mühendis İçin Önerilen İnceleme Sırası

1. `archives/v10_0_1_failed_up40/README.md` dosyasını oku.
2. `scripts/env.py` içindeki `STATE_KEYS`, `ACTION_KEYS`, `ACTIVE_PHASE_CONFIG` ve reward hesaplarını incele.
3. `ads_ai/Assets/Scripts/Env.cs` içindeki `BuildClockFrame`, `ApplyAction`, `BuildStatePacket` akışını incele.
4. `logs/episode_log.csv` ve `step_log.csv` üzerinden success / wrong_way / high_altitude step örneklerini karşılaştır.
5. Reward breakdown kolonlarında success'e yaklaşan step'lerde hangi bileşenlerin pozitif/negatif olduğunu ölç.
6. Action distribution ile target clock direction eşleşmesini analiz et.
7. Önce scripted baseline ile hedefe yönelme mümkün mü test et.
8. Baseline mümkünse PPO reward/action tasarımını baseline davranışına göre yeniden sadeleştir.

## Temizlik Notu

Bu snapshot'ta aşağıdaki geçici dosyalar tutulmaz:

- `pretrain_lab/`
- `reward_lab/`
- Root `logs/` içeriği
- Root `models/` içeriği

Bunlar runtime/deneme çıktısı olduğu için kalıcı mühendislik incelemesinde arşivlenmiş faz logları ve tracked kod tercih edilmelidir.

## Önemli Uyarılar

- Bu proje şu anda başarılı final model üretmiş değildir.
- `archives/` içindeki bazı eski fazlar yüksek success oranı göstermiş olsa da bunlar daha kolay curriculum koşullarına aittir.
- Daha uzak menzil ve daha gerçekçi interception koşullarında policy kararsızlaşmıştır.
- Bir sonraki ciddi adım, reward katsayısı ezbere değiştirmek yerine state-action-reward tasarımının birlikte gözden geçirilmesidir.

## Kısa Komut Özeti

```powershell
# Training
python scripts/train.py

# Belirli checkpoint ile training
$env:ADS_AI_CHECKPOINT_UPDATE="40"
python scripts/train.py

# Test
python scripts/test.py

# Statik faz raporu
python scripts/plot_phase_report.py

# Plotly faz raporu
python scripts/plot_phase_report_plotly.py
```
