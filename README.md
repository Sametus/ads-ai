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

Son aktif deney:

```text
version: v15.1.2
phase: v15_1_2_phase_1_sac_guidance_accel_launch_guard_target500_y100
algorithm: SAC
control_mode: guidance_accel
spawn_radius: 500
target_y: 100
max_step: 800
```

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
SAC_MODEL_PREFIX = sac_v15_1_2_guidance_accel_launch_guard_target500_y100
SAC_TOTAL_STEPS = 250000
SAC_BATCH_SIZE = 64
SAC_REPLAY_SIZE = 200000
SAC_START_TRAINING_STEPS = 8000
SAC_TRAIN_EVERY_STEPS = 32
SAC_GAMMA = 0.995
SAC_REWARD_SCALE = 0.02
SAC_INITIAL_ALPHA = 0.25
```

Aktif control mode:

```text
CONTROL_MODE = guidance_accel
```

Bu modda ajan doğrudan roket torku seçmez. Ajan 3 continuous action üretir:

```text
action[0] -> sağ/sol yanal ivme
action[1] -> yukarı/aşağı ivme
action[2] -> ileri ivme
```

Python bu üç değeri hedef doğrultusuna bağlı guidance frame içinde ivmeye çevirir. Unity bu ivmeyi uygular. Burun hedefe kilitlenmez; görsel gövde hareket/ivme yönüne göre hizalanır. Roll kontrolü öğrenme probleminden mümkün olduğunca ayrıştırılmaya çalışılmıştır.

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

Türkçe karşılıkları:

- `distance`: hedefe mesafe
- `alignment`: roketin hedefe hizalanması, cos(theta)
- `closing_speed`: hedefe yaklaşma hızı
- `theta`: roket/hedef görüş hattı açısı
- `low_agl`: düşük irtifa sebebiyle episode bitişi
- `high_altitude`: fazla yükselme sebebiyle episode bitişi
- `wrong_way`: hedefe göre ters yönde kalma

## Son Training Loglarının Yorumu

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
scripts/pn_guidance_test.py
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
| PN baseline ekle | Kısmen uygulandı, `scripts/pn_guidance_test.py` var. |
| Simülasyon RL'den önce sağlık testinden geçsin | Kısmen uygulandı; direct acceleration ve axis testleri yapıldı. |
| PPO yerine SAC veya TD3 dene | SAC'a geçildi. TD3 denenmedi. |
| HER düşün | Henüz uygulanmadı. |
| Curriculum adaptif olsun | Henüz tam uygulanmadı. Güncel koşu sabit radius 500. |
| CNN / egocentric grid representation dene | Henüz uygulanmadı. Mevcut state hâlâ hand-engineered. |
| Potential-based reward shaping | Henüz tam uygulanmadı; mevcut reward birçok dense bileşen içeriyor. |
| Tanh action saturation kontrolü | Kısmen loglanıyor; son davranış hâlâ incelenmeli. |

## Güncel Hipotez

Mevcut failure mode'un tek bir sebebi kesinleşmiş değildir. En güçlü hipotezler:

1. Reward mesafe azaltmayı erken aşamada fazla ödüllendiriyor, ama hedefi geçip kötü açıyla uzaklaşmayı yeterince erken cezalandırmıyor.
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
- `guidance_accel` action dönüşümü
- Unity tarafında direct acceleration uygulaması
- Hedef / roket frame dönüşümleri
- `theta`, `alignment`, `closing_speed`, `alpha`, `beta` tanımlarının tutarlılığı
- Episode loguna `closest_distance`, `closest_theta`, `closest_alignment`, `closest_closing_speed` gibi alanların eklenmesi
- SAC action dağılımı ve action saturation
- Sabit 500 radius yerine curriculum stratejisi

## Önerilen Sonraki Adım

Kod tarafında büyük mimari değişiklik yapmadan önce şu küçük ve ölçülebilir adımlar önerilir:

1. Episode boyunca en yakın geçişi logla:

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
    test.py                    Kaydedilmiş model ile test
    sac_agent.py               SAC actor/critic ve replay buffer
    env.py                     Python Env wrapper, reward, state/action
    settings.py                Port, rollout ve checkpoint ayarları
    log.py                     CSV ve terminal logları
    plot_sac_report.py         SAC training grafik üretimi
  archives/                    Eski faz/sürüm arşivleri
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

## Mevcut Durumun İnsan Diliyle Özeti

Bu proje çok sayıda mimari denemeden geçti. PPO küçük menzillerde umut verdi ama büyük radius altında gerçek güdüm davranışına genelleşmedi. Uzman önerileri sonrası PN, direct acceleration, teacher/pretrain ve sonunda SAC hattı denendi.

Bugünkü aktif SAC hattı roketi uçurabiliyor, anında çarpmıyor ve bazı anlarda hedefe yaklaştırıyor. Fakat hedefe yaklaşma davranışı vuruşa dönüşmüyor. Son loglarda roket episode sonunda hedefe doğru kapanmak yerine hedeften uzaklaşıyor; alignment negatifleşiyor ve çoğunlukla düşük irtifa ile bitiyor.

Bu nedenle sorun artık "kod hiç çalışmıyor" seviyesinde değil. Daha dar ve teknik bir problem var: state/reward/action tasarımı hedefi geçmeden, doğru açı ve kapanma hızıyla intercept davranışını öğrenmeye yetmiyor.

Bir sonraki mantıklı iş, büyük mimari sıçrama değil; önce loglamayı güçlendirip hedefin yanından geçme davranışını net ölçmek, sonra reward ve curriculum'u buna göre sadeleştirmektir.
