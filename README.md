# ADS-AI Roket Güdüm Projesi

Bu proje, Unity fizik simülasyonu içinde hareket eden bir roketin yaklaşan bir hedefi vurmayı öğrenmesi için geliştirilmiş bir reinforcement learning (pekiştirmeli öğrenme) ortamıdır.

Unity tarafı roketi, hedefi, fizik adımlarını ve telemetry verisini üretir. Python tarafı bu veriden state (durum) çıkarır, reward (ödül) hesaplar ve güncel sürümde SAC tabanlı ajan ile action (eylem) üretir.

Bu README özellikle projeyi dışarıdan inceleyecek bir insanın, kodu açmadan önce şu sorulara cevap bulması için güncellendi:

- Projenin amacı ne?
- Şu an aktif algoritma hangisi?
- Daha önce neler denendi?
- Son training logları ne söylüyor?
- Mevcut başarısızlık modu ne?
- Bir uzmanın özellikle nereye bakması gerekir?

## Kısa Sonuç

Proje şu anda başarılı bir model teslim noktasında değildir. Güncel kod çalışır durumdadır, SAC training başlar ve Unity ile Python haberleşir; fakat son denemede ajan hedef vurma davranışını öğrenememiştir.

Kodda aktif deney:

```text
version: v15.1.11
phase: v15_1_11_phase_1_sac_radius700_less_lateral_more_up_y100
algorithm: SAC
control_mode: direct_accel
spawn_radius: 700
target_y: 100
max_step: 2400
reward: simple reset + theta > 110 terminal after short grace
action: learned direct steering
```

v15.1.6 baseline kontrolu:

| Policy | Episode | Done reason | Success |
|---|---:|---|---:|
| `zero` | 10 | `bad_angle` 10/10 | 0/10 |
| `random` | 10 | `bad_angle` 10/10 | 0/10 |

Yorum: Sifir veya rastgele action artik hedefi vuramiyor. Bu, v15.1.5'teki `%100 success` davranisinin SAC ogrenmesi degil, hedefe otomatik bakan action wrapper etkisi oldugunu dogrular. v15.1.6 ile basari gelirse bunu gercek policy ogrenmesi olarak incelemek daha anlamli olur.

Not: Aşağıdaki log özeti reward resetinden önceki `v15.1.2` koşusuna aittir. `v15.1.3` kodu yeni reward ile sıfırdan training başlatmak için hazırlandı. `v15.1.4` `theta > 90` olduğunda episode'u `bad_angle` terminaliyle bitiren denemeydi. `v15.1.5` action mimarisini tekrar `direct_accel` hedef-bakış moduna aldı, fakat başarı SAC öğrenmesi başlamadan geldi. `v15.1.6` sıfır action'ın hedefe otomatik bakmasını kaldırır; ajan direksiyon komutunu öğrenmek zorundadır. `v15.1.7` fazla erken `bad_angle` bitişlerini azaltmak için açıyı `110` dereceye gevşetir ve kısa bir tolerans süresi ekler. `v15.1.8` timeout süresini artırır; `v15.1.9` bu devam koşusunu `1600` step ve `1,000,000` toplam training step'e genişletir. `v15.1.10` genişletilmiş sahne için spawn radius'u `700` ve max step'i `2400` yapar. Aktif ayar yeniden `v15.1.11` değerlerine alınmıştır: fazla sağ-sol manevrayı azaltmak için yatay direksiyon otoritesi düşürülür, yukarı direksiyon otoritesi ayrı tutulur ve Unity direct bakış dönüşü sakinleştirilir.

Son loglardan çıkan ana tablo:

| Ölçüm | Değer |
|---|---:|
| Episode sayısı | 350 |
| Step sayısı | 165536 |
| Son SAC update | 165500 |
| Success / başarı | 0 |
| Collision / çarpışma | 0 |
| Low AGL / düşük irtifa bitişi | 319 |
| High altitude / yüksek irtifa bitişi | 27 |
| Wrong way / yanlış yön bitişi | 4 |

Yorum:

- Eski bozuk denemelerdeki anında çarpışma problemi bu koşuda görünmüyor.
- Roket artık daha uzun uçuyor ve bazı anlarda hedefe yaklaşabiliyor.
- Buna rağmen son episode'larda hedefi yakalamıyor; çoğunlukla hedefi geçip sonra kötü hizalanma ve düşük irtifa ile bitiriyor.
- Bu haliyle training'i saatlerce sürdürmek mantıklı görünmüyor. Sistem tamamen yerinde saymıyor, ama doğru hedef davranışına da ilerlemiyor.

## Aktif Algoritma

Aktif algoritma SAC'tir.

SAC: Soft Actor-Critic / yumuşak aktör-eleştirmen.

Kısa açıklama:

- PPO gibi on-policy (sadece son topladığı rollout ile öğrenen) bir yöntem yerine off-policy (geçmiş deneyleri replay buffer içinde tekrar kullanan) bir yöntemdir.
- Continuous control (sürekli kontrol) problemlerinde daha verimli keşif yapabilmesi beklenir.
- Entropy / keşif rastlantısallığı üzerinden ajanı erken dönemde tek bir harekete çökmeden aramaya zorlar.

Bu projede aktif Python training scripti:

```text
scripts/train.py
```

Aktif SAC ayarları:

```text
SAC_MODEL_PREFIX = sac_v15_1_7_learned_direct_steer_angle110_grace_target500_y100
SAC_TOTAL_STEPS = 1000000
SAC_BATCH_SIZE = 64
SAC_REPLAY_SIZE = 200000
SAC_START_TRAINING_STEPS = 8000
SAC_TRAIN_EVERY_STEPS = 32
SAC_SAVE_REPLAY_BUFFER = True
SAC_LOAD_REPLAY_BUFFER = False
SAC_GAMMA = 0.995
SAC_REWARD_SCALE = 0.02
SAC_INITIAL_ALPHA = 0.25
```

Replay buffer da checkpoint ile beraber kaydedilir:

```text
models/sac_v15_1_7_learned_direct_steer_angle110_grace_target500_y100_replay_buffer.npz
```

Bu dosya, training yarida kesilip yeniden baslatildiginda SAC'in gecmis deney hafizasini geri yuklemek icindir. Eski run tamamlanip Python process kapandiysa o run'in RAM'deki replay buffer'i geriye donuk kurtarilamaz; dosya ancak bu ozellik eklendikten sonraki kosularda olusur.

Not: v15.1.8 ve sonrasında `SAC_MODEL_PREFIX` bilincli olarak `sac_v15_1_7...` kalir. Amaç mevcut checkpoint zincirini kaybetmeden, yeni faz ayarlarıyla eğitime devam etmektir.

Aktif control mode:

```text
CONTROL_MODE = direct_accel
```

Bu modda ajan doğrudan roket torku seçmez. Ajan 3 continuous action üretir:

```text
action[0] -> mevcut burun yönüne göre sağ/sol direksiyon
action[1] -> mevcut burun yönüne göre yukarı/aşağı direksiyon
action[2] -> pozitif ileri ivme şiddeti
```

Python bu üç değeri mevcut roket burnundan türetilen bir bakış yönüne ve bu yönde pozitif ivmeye çevirir. Hedef yönü state içinde ajana verilir, fakat action wrapper artık hedefe otomatik kilitlenmez. Unity roket burnunu komut edilen bakış yönüne hizalar ve yan/geri kaymayı yumuşatır.

v15.1.11 ile sağ-sol direksiyon ve yukarı direksiyon katsayıları ayrıdır. Sağ-sol aim offset `0.75`, yukarı aim offset `1.85`, ileri ivme bandı `20-55` olarak kullanılır; amaç fazla sağ-sol salınımı azaltıp dikey bileşeni korumaktır. Unity direct bakış dönüş hızı `420 deg/s`, yan hız söndürme karışımı `0.10`, direct hız limiti `140` değerinde tutulur.

## Unity - Python Akışı

1. Python, Unity'ye TCP üzerinden `reset` paketi yollar.
2. Unity roketi ve hedefi resetler.
3. Unity state ve telemetry verisini Python'a yollar.
4. Python observation/state vektörünü oluşturur.
5. SAC ajan action üretir.
6. Python action'ı aktif kontrol moduna göre Unity action paketine çevirir.
7. Unity action'ı uygular ve `Physics.Simulate` ile bir fizik adımı ilerler.
8. Python reward ve terminal koşullarını hesaplar.
9. Transition replay buffer'a eklenir.
10. Buffer yeterli doluluğa ulaşınca SAC mini-batch update yapar.

Unity sahnesi gerçek zamanda serbest akmaz; Python step isteği geldikçe fizik ilerler.

## Başarı Koşulu

Başarı Python tarafında şu koşullarla hesaplanır:

```text
distance <= success_distance
alignment >= success_alignment
closing_speed >= success_min_closing
```

Güncel aktif fazda:

```text
success_distance = 10.0
success_alignment = 0.90
success_min_closing = 0.0
```

## Güncel Reward Tasarımı

v15.1.3 ile önceki karmaşık dense reward bileşenleri kaldırıldı. Bu denemenin amacı reward hacking riskini azaltıp ajana yalnızca temel güdüm sinyallerini vermektir.

Aktif reward:

```text
reward =
  step_penalty
  + distance_progress_reward
  + alignment_reward
  + closing_reward
  + terminal_reward
```

Anlamları:

- `step_penalty`: gereksiz uzayan episode için küçük zaman maliyeti.
- `distance_progress_reward`: bir önceki step'e göre hedefe yaklaşmayı ödüllendirir, uzaklaşmayı cezalandırır.
- `alignment_reward`: roketin hedef görüş hattına dönük olmasını ödüllendirir.
- `closing_reward`: hedefe doğru pozitif kapanma hızını ödüllendirir.
- `terminal_reward`: success, collision, low altitude, high altitude, wrong way ve timeout için tek seferlik bitiş ödül/cezası.

Kasıtlı olarak kaldırılan eski bileşenler: yakın başarı bonusları, roll/angular cezaları, thrust gate cezaları, clock action alignment reward'ları, düşük irtifa kaçış bonusları ve çok parçalı açı shaping terimleri.

v15.1.4 ve sonrası ek terminal kuralı:

```text
step_count > 25 and theta_deg > 110.0 -> done_reason = bad_angle, terminal_reward = -50
```

Bu kuralın amacı, ajan hedefin yanından geçip açı çok açıldıktan sonra boş yere kaçmayı öğrenmesin diye episode'u erken kesmektir. v15.1.7 ve sonrasında eşik 110 dereceye çekildi ve ilk 25 step için tolerans verildi; böylece ajan ilk manevra aramasında hemen terminal yemeden toparlama deneyebilir.

Türkçe karşılıkları:

- `distance`: hedefe mesafe
- `alignment`: roketin hedefe hizalanması, cos(theta)
- `closing_speed`: hedefe yaklaşma hızı
- `theta`: roket/hedef görüş hattı açısı
- `low_agl`: düşük irtifa sebebiyle episode bitişi
- `high_altitude`: fazla yükselme sebebiyle episode bitişi
- `wrong_way`: hedefe göre ters yönde kalma

## Son Training Loglarının Yorumu

Bu bölüm reward resetinden önceki `v15.1.2` SAC koşusunu anlatır.

Son koşuda toplam 350 episode incelendi.

Episode bitiş sebepleri:

| Done reason | Sayı | Yorum |
|---|---:|---|
| `low_agl` | 319 | Ana failure mode. Roket sonunda yere çok yaklaşıyor. |
| `high_altitude` | 27 | Bazı denemelerde fazla yükseliyor. |
| `wrong_way` | 4 | Hedefe göre ters yön/uzaklaşma. |
| `success` | 0 | Başarı yok. |
| `collision` | 0 | Bu iyi; anında çarpışma problemi görünmüyor. |

İlk 50 episode ile son 50 episode karşılaştırması:

| Metrik | İlk 50 | Son 50 | Yorum |
|---|---:|---:|---|
| Ortalama episode uzunluğu | 323 step | 511 step | Daha uzun uçuyor. |
| Ortalama final distance | 220 | 294 | Terminal mesafe kötüleşmiş. |
| Ortalama final theta | 80 derece | 155 derece | Hedef açısı çok kötüleşmiş. |
| Ortalama final alignment | 0.159 | -0.892 | Son durumda hedefin tersine bakıyor. |
| Ortalama final closing speed | +25.8 | -71.9 | Son durumda hedeften uzaklaşıyor. |
| Success | 0 | 0 | Öğrenilmiş vuruş yok. |

Step bazlı gözlem:

| Metrik | İlk 5000 step | Son 5000 step | Yorum |
|---|---:|---:|---|
| Ortalama distance | 382 | 302 | Bazı yaklaşma davranışı var. |
| Minimum distance | 156 | 72 | Hedefe bazen ciddi yaklaşıyor. |
| Ortalama theta | 42 derece | 71 derece | Açısal kalite kötüleşiyor. |
| Ortalama AGL | 13.4 | 22.2 | Roket daha fazla havada kalıyor. |
| Ortalama closing speed | 49.7 | 22.0 | Yaklaşma hızı zayıflıyor. |

Bu tablo önemli: ajan bazen hedefe yaklaşabiliyor, fakat yaklaşmayı terminal başarıya çeviremiyor. En olası davranış şu:

```text
Roket başlangıçta mesafeyi azaltıyor.
Sonra hedefin yanından/geçiş koridorundan kaçıyor.
Episode sonunda hedef arkasında kalıyor.
Alignment negatifleşiyor.
Closing speed negatifleşiyor.
Low AGL veya wrong_way ile bitiyor.
```

Bu nedenle güncel training'i "hiçbir şey öğrenmiyor" diye değil, "yanlış veya eksik ödüllendirilen bir geçiş davranışına kayıyor" diye okumak daha doğru olur.

## Daha Önce Denenen Yaklaşımlar

### PPO dönemi

Başlangıçta PPO kullanıldı. Küçük spawn radius değerlerinde başarı oranları görüldü; fakat radius büyüdükçe bu başarıların gerçek güdümden çok geometri ezberine benzer davranışlar olduğu düşünüldü.

Özet problem:

- Küçük radius: hedef rampanın üstünden geçtiği için rastgele/yarı-ezber hareketler başarı üretebildi.
- Büyük radius: ajan gerçek LOS takibi öğrenmek zorunda kaldı.
- PPO, özellikle artan radius ve heading sapması altında kararlı hedef yönelimi üretemedi.

### PN baseline

Uzman önerisi doğrultusunda PN (Proportional Navigation / oransal güdüm) baseline denemeleri için script eklendi:

```text
Audit scriptleri teslim temizliginde runtime klasorunden kaldirildi.
```

Amaç RL'den önce simülasyonun fiziksel olarak çözülebilir olup olmadığını test etmekti.

Bu süreçte clock action, roll, thrust yönü, body frame / guidance frame dönüşümleri ve action eksenleri incelendi.

### Direct acceleration baseline

Roketin tork/clock zincirinden bağımsız olarak vurmanın mümkün olup olmadığını görmek için direct acceleration modu eklendi. Bu mod RL için nihai çözüm değil, "sahne fiziksel olarak çözülebilir mi?" sorusuna cevap arayan bir sağlık testi olarak kullanıldı.

### Teacher / pretrain denemesi

Bir ara öğretmen veri toplama ve behavior cloning / davranış kopyalama hattı denendi. Amaç çalışan bir controller'dan veri toplayıp policy'yi önceden ısıtmaktı.

Bu hat kalıcı çözüm olarak tutulmadı. Güncel aktif runtime sadeleştirildi ve SAC tek ana training yolu olarak bırakıldı.

### SAC geçişi

PPO'nun exploration ve sample efficiency sorunları nedeniyle off-policy SAC'a geçildi. SAC'ın replay buffer kullanması ve entropy regularization ile keşif yapması bu problem için daha uygun görüldü.

Ancak güncel SAC denemesi de henüz başarı üretmedi.

## Uzman Önerileri ve Uygulama Durumu

Daha önce alınan uzman önerilerinin projedeki karşılığı:

| Öneri | Durum |
|---|---|
| PN baseline ekle | Uygulandı; teslim temizliğinde runtime scripti kaldırıldı, bulgular CHANGELOG/docs içinde duruyor. |
| Simülasyon RL'den önce sağlık testinden geçsin | Kısmen uygulandı; direct acceleration ve axis testleri yapıldı. |
| PPO yerine SAC veya TD3 dene | SAC'a geçildi. TD3 denenmedi. |
| HER düşün | Henüz uygulanmadı. |
| Curriculum adaptif olsun | Henüz tam uygulanmadı. Güncel koşu sabit radius 500. |
| CNN / egocentric grid representation dene | Henüz uygulanmadı. Mevcut state hâlâ hand-engineered. |
| Potential-based reward shaping | Henüz tam uygulanmadı; v15.1.3'te eski çok parçalı dense reward kaldırılıp basit reward reset denemesi başlatıldı. |
| Tanh action saturation kontrolü | Kısmen loglanıyor; son davranış hâlâ incelenmeli. |

## Güncel Hipotez

Mevcut failure mode'un tek bir sebebi kesinleşmiş değildir. En güçlü hipotezler:

1. Önceki reward tasarımında reward hacking riski vardı; v15.1.3 bu yüzden hedefe yönelme, hedefe yaklaşma ve kapanma hızı dışında ara sinyalleri kaldıran sade bir deneme olarak başlatıldı.
2. Terminal log sadece final distance gösterdiği için "en yakın geçiş mesafesi" net görünmüyor. Closest approach metriği episode loguna eklenmeli.
3. Sabit 500 radius, sıfırdan SAC için fazla sert olabilir. Önce daha küçük ama gerçek güdüm gerektiren radius bandında davranışı oturtmak gerekebilir.
4. State representation elle tasarlanmış olduğu için angle wrapping, frame dönüşümü veya normalizasyon hataları policy'yi yanıltıyor olabilir.
5. Guidance acceleration modu roketi uçuruyor, fakat hedefin yanından geçtikten sonra tekrar toparlanma davranışını öğretmek için reward ve termination tasarımı zayıf kalıyor olabilir.

## Bir Uzmanın Özellikle Bakması Gereken Yerler

Öncelikli dosyalar:

```text
scripts/env.py
scripts/sac_agent.py
scripts/train.py
scripts/settings.py
ads_ai/Assets/Scripts/Env.cs
ads_ai/Assets/Scripts/Connector.cs
```

Özellikle incelenmesi gereken başlıklar:

- `scripts/env.py` içindeki reward bileşenleri ve terminal koşulları
- `direct_accel` öğrenilen direksiyon action dönüşümü
- Unity tarafında direct acceleration uygulaması
- Hedef / roket frame dönüşümleri
- `theta`, `alignment`, `closing_speed`, `alpha`, `beta` tanımlarının tutarlılığı
- Episode loguna `closest_distance`, `closest_theta`, `closest_alignment`, `closest_closing_speed` gibi alanların eklenmesi
- SAC action dağılımı ve action saturation
- Sabit 500 radius yerine curriculum stratejisi

## Önerilen Sonraki Adım

Kod tarafında büyük mimari değişiklik yapmadan önce şu küçük ve ölçülebilir adımlar önerilir:

1. Final modeli Unity sahnesi açıkken test et:

```text
conda run -n rl_codes python scripts/final_test.py
```

Bu komut seçilen final checkpoint'i yükler ve sen durdurana kadar kısa başarı/kaçırma/timeout bilgisini konsola yazar.

2. Episode boyunca en yakın geçişi logla:

```text
closest_distance
closest_theta_deg
closest_alignment
closest_closing_speed
closest_step
```

2. Hedefin yanından geçip uzaklaşan episode'ları ayrı done reason ile bitir:

```text
near_pass_wrong_geometry
```

3. Reward'u sadece "mesafe azaldı" davranışını değil, yakın mesafede iyi açı ve pozitif closing speed'i ödüllendirecek şekilde sadeleştir.

4. Sabit radius 500 yerine küçükten büyüğe kontrollü curriculum kullan:

```text
radius 150 -> 250 -> 350 -> 500
```

5. Her değişiklikten sonra uzun training yerine 200-500 episode health-check yap.

## Klasör Yapısı

```text
ads_ai/
  ads_ai/                     Unity projesi
    Assets/Scripts/Env.cs      Unity RL ortamı, fizik ve telemetry
    Assets/Scripts/Connector.cs TCP/JSON iletişim katmanı
    Assets/Scenes/             Unity sahneleri
  scripts/                     Python RL kodları
    train.py                   Aktif SAC training döngüsü
    final_test.py              Final checkpoint ile teslim/demo testi
    sac_agent.py               SAC actor/critic ve replay buffer
    env.py                     Python Env wrapper, reward, state/action
    settings.py                Port, rollout ve checkpoint ayarları
    log.py                     CSV ve terminal logları
    plot_sac_report.py         SAC training grafik üretimi
    plot_success_scatter.py    Success scatter ve rolling success grafiği
  docs/                        Notlar, analizler ve rapor taslakları
  logs/                        Güncel runtime logları, Git LFS ile paylaşılır
  models/                      Güncel SAC checkpoint'leri, Git LFS ile paylaşılır
  teacher_data/                 Eski teacher/pretrain verisi, Git LFS ile paylaşılır
  CHANGELOG.md                 Kronolojik sürüm notları
  VERSION                      Aktif repo sürümü
```

## Repo ve Büyük Dosya Notu

Uzmanın projeyi kendi bilgisayarında açabilmesi için Unity kaynak dosyaları repo içinde tutulur:

```text
ads_ai/Assets/
ads_ai/Packages/
ads_ai/ProjectSettings/
ads_ai/*.csproj
ads_ai/*.sln
```

Şu klasörler bilinçli olarak repo dışında tutulur:

```text
ads_ai/Library/
ads_ai/Temp/
ads_ai/obj/
ads_ai/.vs/
ads_ai/UserSettings/
```

Bunlar Unity/IDE tarafından yerel makinede yeniden üretilen cache ve kullanıcı ayarı dosyalarıdır. Projeyi çalıştırmak için gerekli kaynak değillerdir.

Güncel `logs/`, `models/` ve `teacher_data/` klasörleri Git LFS ile paylaşılır. Bunun sebebi özellikle `logs/step_log.csv` dosyasının tek başına yüzlerce MB'a çıkmasıdır. Repoyu klonlayan kişinin büyük log/model dosyalarını eksiksiz alabilmesi için Git LFS kurulu olmalıdır.

## Kurulum

Bu proje Windows ve Unity üzerinde geliştirilmiştir.

Unity:

```text
Unity Editor 6000.3.2f1
```

Python için mevcut kod TensorFlow 2.10 ailesine göre hazırlanmıştır. Windows GPU desteği için eski TensorFlow uyumluluğu sebebiyle Python 3.7 kullanılmıştır.

Önerilen conda ortamı:

```powershell
conda create -n rl_codes python=3.7.16
conda activate rl_codes
python -m pip install --upgrade pip
python -m pip install tensorflow==2.10.1 numpy==1.21.6 pandas==1.3.5 matplotlib==3.5.3 protobuf==3.19.6 h5py==3.8.0
```

GPU kontrolü:

```powershell
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

Çıktı `[]` ise TensorFlow GPU görmüyor demektir ve training CPU ile çalışır.

## Çalıştırma

1. Unity projesini aç:

```text
ads_ai/
```

2. Unity sahnesini başlat.

3. Python ortamını aç:

```powershell
conda activate rl_codes
```

4. Training başlat:

```powershell
python scripts/train.py
```

5. SAC grafik raporu üretmek için:

```powershell
python scripts/plot_sac_report.py
```

## Mevcut Teknik Durum Özeti

Proje çalışır durumdadır: Unity-Python haberleşmesi, SAC training döngüsü, checkpoint üretimi ve loglama aktif olarak çalışmaktadır. Ancak güncel deney başarılı bir hedef vurma modeli üretmemiştir.

PPO küçük radius değerlerinde umut vermiş, fakat radius büyüdükçe davranış gerçek güdüme genelleşmemiştir. Bu nedenle uzman önerileri doğrultusunda PN baseline, direct acceleration, teacher/pretrain ve son olarak SAC hattı denenmiştir.

Aktif SAC koşusunda roket anında çarpmadan uçabilmekte ve bazı adımlarda hedefe yaklaşabilmektedir. Fakat bu yaklaşma vuruşa dönüşmemektedir. Son loglarda episode sonunda alignment negatifleşmekte, closing speed negatife dönmekte ve roket çoğunlukla düşük irtifa ile bitmektedir.

Güncel sorun çalışma altyapısından çok kontrol ve öğrenme tasarımı tarafındadır. State/reward/action tasarımı, hedefin yanından geçmeden doğru açı ve pozitif kapanma hızıyla intercept davranışı üretmeye yetmemektedir.

Bir sonraki odak, büyük mimari değişiklikten önce `closest_distance`, `closest_alignment`, `closest_closing_speed` gibi metrikleri episode seviyesinde loglamak; ardından reward ve curriculum tasarımını bu verilere göre sadeleştirmektir.
