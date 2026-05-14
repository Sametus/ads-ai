# v1.0 sürüm ailesi

> ## v1.0 - İlk kararlı sürüm
>
> - Unity ortamı ve sahne düzeni
> - PPO eğitim scriptleri ve ayarları
> - Rapor dokümanları ve 3D model dosyalarının `docs` altına taşınması
> - JSON bağımlılıklarının projeye eklenmesi
>

# v1.1 sürüm ailesi

> ## v1.1 - Fizik senkronizasyonu ve reward güncellemeleri
>
> - Unity `Env` ortamında manuel fizik adımı (Physics.Simulate) ve güvenli reset akışı
> - Raycast tabanlı AGL (yerden yükseklik) ve grounded flag ile iyileştirilmiş state tanımı
> - Python `env.py` tarafında reward/terminal mantığının AGL ve grounded bilgisiyle güncellenmesi
> - Ortam problemlerine yönelik detaylı `docs/deep_research/deep-research-report.md` teknik analizi eklendi
>

> ## v1.1.1 - Debug çizgileri ve görsel iyileştirme
>
> - Unity `Env` içinde debug çizgilerinin fizik adımıyla senkron çalışacak şekilde güncellenmesi
> - Roket ileri yön çizgisinin `rocket` yerine `rocketPoint` referansıyla çizilerek görsel tutarlılığın artırılması
> - **Kod düzeyi değişiklikler**
>   - `Env.Update` içindeki `UpdateDebugLines()` çağrısı kaldırıldı; debug çizgileri artık her aksiyon adımında `StepOnce()` içinde, fizik simülasyonu (`Physics.Simulate`) sonrasında güncelleniyor.
>   - `UpdateDebugLines()` fonksiyonunda ileri yön çizgisi hesabı `rocket.forward` yerine `rocketPoint.forward` kullanacak şekilde değiştirildi.
>

> ## v1.1.2 - AGL yönü ve kamera yumuşatma ayarları
>
> - `Env.ComputeAGL` içinde yerden yükseklik raycast yönü `-Physics.gravity.normalized` yerine sabit `Vector3.down` kullanacak şekilde sadeleştirildi.
> - `CameraFollow` bileşeninde `positionDamping` ve `rotationDamping` değerleri yumuşak ama daha tepkisel bir takip için yeniden ayarlandı.
>

> ## v1.1.3 - AGL ray mesafesi ve max irtifa sınırı
>
> - Unity `Env` tarafında AGL hesaplaması için kullanılan `groundRayMax` değeri **100.0 → 180.0** olarak artırıldı (daha yüksek irtifalarda da yer tespiti yapabilmek için).
> - Python `env.py` içinde `MAX_ALTITUDE` eşiği **250.0 → 150.0** olarak düşürüldü; yüksek irtifa cezalandırması artık daha erken devreye giriyor.
>

> ## v1.1.4 - Thrust limitlerinin yumuşatılması
>
> - Python `env.py` içinde thrust limitleri daha yumuşak ve kontrol edilebilir bir uçuş için güncellendi:
>   - `MIN_THRUST`: **700.0 → 600.0**
>   - `MAX_THRUST`: **1200.0 → 1000.0**
>

> ## v1.1.5 - Kamera damping ayarları ve sahne güncellemeleri
>
> - `CameraFollow.cs` bileşeninde takip yumuşatma değerleri daha akıcı bir görünüm için optimize edildi:
>   - `positionDamping`: **12.0 → 10.0**
>   - `rotationDamping`: **9.0 → 7.0**
> - Unity tarafında sahne (`SampleScene.unity`) ve ortam düzenlemeleri güncellendi.
>

> ## v1.1.6 - Kamera damping optimizasyonu
>
> - `CameraFollow.cs` bileşeninde takip yumuşatma değerleri daha hassas ve akıcı bir takip için tekrar optimize edildi:
>   - `positionDamping`: **10.0 → 7.0**
>   - `rotationDamping`: **7.0 → 5.0**

# v1.2 sürüm ailesi

> ## v1.2 - Kamera takip modernizasyonu
>
> - `CameraFollow.cs` içindeki `positionDamping` ve `rotationDamping` mantığı tamamen kaldırıldı. Kamera artık hedefi herhangi bir gecikme (smoothing/damping) olmadan doğrudan takip ediyor. Bu, özellikle yüksek hızlarda ve ani manevralarda takibin daha tutarlı olmasını sağlıyor.
>

> ## v1.2.1 - Renkli loglama ve rapor taslağı
>
> - **Renkli loglama sistemi**: `scripts/log.py` içindeki bölüm sonu logları artık daha okunabilir olması için renklendirildi. Başarı (success), irtifa hataları (low_agl, high_altitude) ve zaman aşımı (timeout) durumları farklı ANSI renkleriyle terminale basılıyor.
> - **Rapor taslağı**: `docs/rapor/` dizinine proje raporu taslak Word belgesi eklendi.

# v2.0 sürüm ailesi

> ## v2.0 - İrtifa hatası (height_error) bazlı state tanımı
>
> - **Major State Güncellemesi**: State tanımındaki `target_h` (mutlak hedef yüksekliği) çıkarılarak yerine `height_error` (hedef_yüksekliği - mevcut_irtifa) eklendi. Bu değişiklik hem Unity (`env.cs`) hem de Python (`env.py`) tarafında eşzamanlı olarak uygulandı.
> - **Normalizasyon ve Loglama**: `env.py` üzerindeki normalizasyon katmanı yeni state yapısına göre güncellendi. `log.py` ve `test.py` üzerindeki tüm loglama mekanizmaları (CSV ve Console) `height_error` bilgisini içerecek şekilde revize edildi.
> - **Gelişmiş Bölüm Analizi**: Bölüm sonu loglarına `final_height_error` metriği eklenerek eğitimin başarısı daha detaylı izlenebilir hale getirildi.
>

> ## v2.0.1 - İrtifa sınırı optimizasyonu ve sahne temizliği
>
> - **İrtifa sınırı optimizasyonu**: `scripts/env.py` içinde `MAX_ALTITUDE` eşiği **150.0 -> 100.0** olarak düşürüldü. Bu, roketin çok fazla yükselmesini daha erken engelleyerek eğitimin daha verimli alanlara odaklanmasını sağlar.
> - **Sahne temizliği**: `SampleScene.unity` içinde gereksiz AudioListener bileşenleri devre dışı bırakıldı ve çalışma ortamı optimize edildi.
> - **Dosya temizliği**: Geçici Word dosyaları ve eski log kayıtları temizlendi.
>

> ## v2.0.2 - Güvenli irtifa artıtrımı
>
> - **Güvenli irtifa artırımı**: `scripts/env.py` içinde `MIN_AGL` (minimum yerden yükseklik) eşiği **0.20 -> 0.40** olarak artırıldı. Bu, rokete yerden daha güvenli bir mesafe bırakması için daha erken ceza verilmesini sağlar ve çarpışma riskini azaltır.

> ## v2.0.3 - Debug çizgileri ve model güncellemeleri
>
> - **Görsel iyileştirmeler (Debug Lines)**: Unity sahnesindeki (`SampleScene.unity`) `LineRenderer` bileşenlerinin `widthMultiplier` değeri **0.05 -> 0.3** olarak artırıldı. Bu, takip edilen yörünge ve debug çizgilerinin daha belirgin olmasını sağlar.
> - **Model güncellemeleri**: Yeni eğitim verileriyle güncellenen modeller (`models/`) projeye dahil edildi.

# v3.0 sürüm ailesi

> ## v3.0 - Ödül Fonksiyonu ve State Tanımı Revizyonu
>
> - **State Tanımı Güncellemesi**: State vektörü sonundaki `blend_w` (grounded flag) çıkarılarak yerine `time_remaining` (kalan süre oranı) eklendi. Bu, ajanın zaman kısıtına göre strateji değiştirmesine olanak tanıyor.
> - **Ödül Fonksiyonu Overhaul**:
>     - **Hizalama Ödülü (Alignment Bonus)**: Roket burnunun hedefe bakma derecesine göre (`target_dir_z`) ek ödül tanımlandı.
>     - **Takla Cezası (Angular Velocity Penalty)**: Roketin kontrolsüz dönmesini engellemek için açısal hız büyüklüğüne bağlı ceza eklendi.
>     - **Kapanma Hızı Ağırlığı**: Hedefe yaklaşma hızı ödülü (`closing_rate`) 2.5 katına çıkarıldı.
> - **Eğitim Stabilitesi**:
>     - `MIN_AGL` eşiği **0.25**'e çekilerek rampadan kalkış sırasındaki hatalı sonlanmalar engellendi.
>     - `LOW_AGL_GRACE_STEPS` **15**'e çıkarılarak kalkış toleransı artırıldı.
> - **Loglama ve Analiz**:
>     - Konsol ve CSV loglarına `alignment` ve `ang_vel_mag` tanıları eklendi.
>     - `log.py` içindeki GAE lambda bug'ı düzeltildi.
> - **Model Yönetimi**: Eski model ve state dosyaları `models/old-models/` dizinine taşınarak çalışma alanı temizlendi.

# v3.1 sürüm ailesi

> ## v3.1.0 - Kaçış Terminali (Escape Logic) ve Renk Güncellemesi
>
> - **Kaçış Terminali (Escape Logic)**: Roketin hedeften kontrolsüzce uzaklaşmasını engellemek için yeni bir terminal koşulu eklendi. Başlangıç mesafesinin 1.5 katına çıkan roketler, 50 adım tolerans sonrası (`ESCAPE_GRACE_STEPS`) otomatik olarak durduruluyor.
> - **Yeni Ceza**: Kaçış durumu için `-50.0` ceza puanı (`ESCAPE_PENALTY`) tanımlandı. Bu, değer fonksiyonunun hatalı yükselmesini (value function inflation) engeller.
> - **Loglama Güncellemesi**: `log.py` içinde `escaped` durumu için turkuaz (`CYAN`) renk kodu eklendi, böylece konsol çıktılarında kaçış terminali kolayca ayırt edilebiliyor.

> ## v3.1.1 - Ödül ve Ceza Parametre İyileştirmeleri
>
> - **Güvenlik Sınırı Güncellemesi**: `MIN_AGL` (minimum yerden yükseklik) eşiği **0.25 -> 0.35** olarak artırıldı. Bu, roketin yere daha güvenli bir mesafede kalmasını zorunlu kılar.
> - **İrtifa Kısıtlaması**: `MAX_ALTITUDE` (maksimum irtifa) **100.0 -> 95.0** olarak düşürüldü.
> - **Başarı Ödülü Artırımı**: `SUCCESS_REWARD` (başarı ödülü) **200.0 -> 210.0** olarak güncellendi.
> - **Düşük İrtifa Cezası**: `LOW_ALTITUDE_PENALTY` (düşük irtifa cezası) **-70.0 -> -75.0** olarak artırıldı.

# v3.2 sürüm ailesi

> ## v3.2.0 - Başlangıç Koşulları Stabilizasyonu
>
> - **Heading Offset Kısıtlaması**: Reset sırasında roketin rastgele atanan başlangıç yönü sapması (heading offset) **±45 derece -> ±5 derece** aralığına düşürüldü. Bu, eğitimin başlangıç aşamasında daha kararlı bir öğrenme süreci sağlar.

# v3.3 sürüm ailesi

> ## v3.3.0 - Performans Zarflarının Genişletilmesi ve Eğitim Optimizasyonu
>
> - **Thrust ve Kontrol Kuvveti Artırımı**:
>     - `MIN_THRUST` **600.0 -> 580.0**, `MAX_THRUST` **1000.0 -> 1050.0** olarak güncellendi.
>     - `MAX_PITCH_FORCE` ve `MAX_YAW_FORCE` **1.5 -> 1.7** değerine çıkarılarak manevra kabiliyeti artırıldı.
> - **İrtifa ve Ceza Güncellemeleri**:
>     - `MAX_ALTITUDE` **95.0 -> 100.0** olarak esnetildi.
>     - `HIGH_ALTITUDE_PENALTY` (yüksek irtifa cezası) **-80.0 -> -82.0** olarak güncellendi.
> - **Eğitim ve Loglama Ayarları**:
>     - `ROLLOUT_LEN` **1024 -> 1200** olarak artırıldı (daha uzun veri toplama periyodu).
>     - `SAVE_EVERY_UPDATES` **16 -> 20** olarak güncellendi.
>     - `STEP_PRINT_EVERY` **50 -> 25** yapılarak konsol takibi sıklaştırıldı.

# v3.4 sürüm ailesi

> ## v3.4.0 - İrtifa Hizalama ve Yer Yakınlık Uyarısı (Soft Floor)
>
> - **Yer Yakınlık Uyarısı (Soft Floor)**: Roketin 5m altına indiği durumlarda terminale girmeden önce sürekli bir ceza sinyali eklendi (`SOFT_FLOOR = 5.0`). Bu, ajanın yere tehlikeli yaklaşmasını erkenden fark etmesini sağlar.
> - **İrtifa Hizalama Ödülü (Height Alignment)**: Ajanın hedef irtifaya (target altitude) sadık kalmasını teşvik etmek için `height_error` tabanlı yeni bir ödül eklendi (`HEIGHT_ALIGN_GAIN = 0.020`).
> - **Kaçış Terminali Hassasiyeti**: `ESCAPE_MULTIPLIER` **1.5 -> 1.4** seviyesine düşürülerek hedeften uzaklaşma tespiti daha hassas hale getirildi.
> - **Ödül Ağırlıkları İyileştirmesi**:
>     - `DISTANCE_GAIN` **0.30 -> 0.35** ve `CLOSING_RATE_GAIN` **0.010 -> 0.017** olarak artırıldı.
>     - `ALIGNMENT_GAIN` **0.04 -> 0.045** seviyesine çıkarıldı.
>     - `STEP_PENALTY` ve `ANG_VEL_PENALTY` değerlerinde küçük yumuşatmalar yapıldı.

> ## v3.4.1 - İrtifa Hizalama Hassasiyeti Artırımı
>
> - **İrtifa Hizalama Hassasiyeti**: `HEIGHT_ALIGN_GAIN` değeri **0.020 -> 0.035** olarak artırıldı ve ceza mantığı (`reward -= gain * error`) stabilize edildi. Bu, roketin hedef irtifaya çok daha sıkı tutunmasını sağlar.

> ## v3.4.2 - Ödül İnce Ayarı ve Analiz Araçları
>
> - **İrtifa Hizalama Dengelenmesi**: `HEIGHT_ALIGN_GAIN` değeri **0.035 -> 0.015** seviyesine çekilerek ödül fonksiyonu daha dengeli hale getirildi. Bu, ajanın irtifa hatasına aşırı odaklanıp ana hedefi (mesafe) ihmal etmesini önler.
> - **Yeni Analiz Scripti (`docs/analiz.py`)**: `step_log.csv` verilerini Pandas ile hızlıca analiz etmek için temel bir script eklendi.
> - **Reward Test Ortamı (`scripts/reward_test.py`)**: TCP bağlantısı gerektirmeden `calculate_reward` mantığını farklı senaryolarla test etmeyi sağlayan kapsamlı bir unit-test benzeri script geliştirildi.

# v4.0 - Curriculum Learning (Müfredatlı Öğrenme)

> ## v4.0.0 - Müfredat Temelli Eğitimin Başlatılması (Adım 1)
>
> - **Curriculum Learning (CL) Geçişi**: Eğitimin daha sağlıklı ve dengeli ilerlemesi için aşamalı müfredat modeline geçildi.
> - **Hareketsiz Hedef (Stationary Target)**: İlk eğitim aşamasında hedefin hareketi tamamen devre dışı bırakıldı (`TARGET_VELOCITY = 0.0`). Hedef, roketin tam tepesinde sabit bekleyecek şekilde konumlandırıldı.
> - **Lokasyon Sabitleme**: Hedefin başlangıç konumu (px, pz) **(300, 300) -> (0, 0)** olarak güncellenerek eğitimin en basit senaryodan başlaması sağlandı.
> - **Temiz Başlangıç**: CL sürecinin sağlıklı takibi için eski log ve model dosyaları temizlendi. Yeni müfredata uygun modeller bu sürümden itibaren kaydedilecek.

> ## v4.0.1 - Müfredat Temelli Öğrenme - Adım 2: Stabilizasyon
>
> - **Başlangıç Oryantasyonu Sabitleme**: `env.py` içindeki `reset` fonksiyonunda `calculate_new_loc` devre dışı bırakılarak `px, pz, ry, rz = 0,0,0,0` olarak sabitlendi. Bu, ajanın her bölüme tam olarak aynı konum ve yönelimle başlamasını sağlar.
> - **Eğitim Kararlılığı**: Rastgeleliğin (randomness) azaltılmasıyla ajanın temel hareketleri ve dengeyi daha hızlı öğrenmesi hedeflenmektedir.

# v5.0 - Yeni State Tanımı ve Müfredat Gelişimi

> ## v5.0.0 - Yeni State Tanımı ve Gelişmiş Loglama
>
> - **Major State Güncellemesi**: State vektöründen `closing_rate` çıkarılarak yerine `look_angle_rad` (bakış açısı - radyan) eklendi. Bu, ajanın hedefe olan yönelimini daha hassas algılamasını sağlar.
> - **State Normalizasyonu**: Yeni eklenen bakış açısı için `LOOK_ANGLE_SCALE = np.pi` tanımlandı ve [0, 1] aralığına normalize edildi.
> - **Gelişmiş Loglama**: `log.py` güncellenerek `step_log.csv` ve `episode_log.csv` dosyalarına `look_angle_rad` ve `look_angle_deg` verileri eklendi.
> - **Müfredat Takibi**: Curriculum Learning Step 2 (Sabit Başlangıç) devam ederken yeni state yapısıyla eğitim kararlılığı hedefleniyor.

> ## v5.0.0a - Reward Fonksiyonu ve Terminal Şart İyileştirmeleri
>
> - **Açı Odaklı Ödül (Angle Reward)**: `look_angle_rad` üzerinden hesaplanan `ANGLE_GAIN` ödülü eklendi. Burun hedefe baktıkça ödül artar, ters yöne döndükçe ceza verilir.
> - **Yüksek Sapma Terminali (Bad Angle Terminal)**: Roketin hedeften 135 dereceden fazla saptığı durumlar için `bad_angle` terminali ve `-60` puanlık ceza tanımlandı.
> - **İrtifa Hizalama Revizyonu**: İrtifa ödülü (`HEIGHT_ALIGN_GAIN`) artık lineer ceza yerine, 50m hata payı içerisinde pozitif bir çarpan olarak hesaplanıyor.
> - **Dengeleme**: `DISTANCE_GAIN` değeri **0.35 -> 0.15** seviyesine çekilerek açısal ödüllerle uyumlu hale getirildi.

> ## v5.0.1 - Ödül ve Terminal Şartı Refakatçı Düzenlemeleri
>
> - **Terminal Şartı Kaldırıldı**: `bad_angle` terminal şartı `env.py` dosyasından kaldırılarak ajanın aşırı yönelmelerde de öğrenmeye devam etmesi sağlandı.
> - **Bakış Açısı Hesaplaması İyileştirildi (Unity)**: `env.cs` içerisinde bakış açısı (`look_angle_rad`) artık `Mathf.Acos` kullanılarak daha hassas ve kararlı bir şekilde hesaplanıyor.

> ## v5.0.2 - Ödül Ölçeklendirme ve Başarı Metrikleri
>
> - **Reward Ölçeklendirme (Scale-up)**: `DISTANCE_GAIN` ve `ANGLE_GAIN` gibi temel ödül katsayıları artırılarak ajanın daha güçlü sinyallerle eğitilmesi sağlandı.
> - **Başarı Oranı Takibi (Success Rate)**: `train.py` ve `log.py` güncellenerek eğitim süresince toplam episode ve başarı sayısı (success rate) anlık olarak takip edilmeye başlandı.
> - **Dinamik Konsol Çıktısı**: Eğitim sırasında konsola yazdırılan metrikler daha detaylı hale getirilerek ilerleme görünürlüğü artırıldı.

> ### Faz 1 - Tamamlandı
> - Modeller ve loglar ilk kez commit edildi; scripts değişmedi.
> - **Başlangıç konfigürasyonu** (`env.py` v5.0.2 ile aynı):
>   - `TARGET_VELOCITY = 0.0` (hedef sabit)
>   - `reset`: `px, pz, ry, rz = 0, 0, 0, 0` (sabit başlangıç)
>   - `calculate_new_loc()` içinde `px = 0 * np.cos(theta)`, `pz = 0 * np.sin(theta)` (efektif sabit konum)
>   - `ANGLE_GAIN = 0.22`, `DISTANCE_GAIN = 0.15`
> - Büyük log dosyaları 40MB parçalara bölünerek GitHub'a yedeklendi.

> ### Faz 2 - Tamamlandı
> - Faz 2 müfredatlı eğitimi (Curriculum Learning) tamamlandı.
> - **env.py değişiklikleri** (Faz 1 → Faz 2, git diff ile):
>   - `calculate_new_loc()`: `px`/`pz` artık `0 * np.cos(theta)` / `0 * np.sin(theta)` yerine `np.random.randint(0,3) * np.cos(theta)` / `np.random.randint(0,3) * np.sin(theta)` (0–2 birim, yakın alan)
>   - `reset`: `px, pz, ry, rz = 0,0,0,0` → `px, pz, ry, rz = calculate_new_loc()` (dinamik konum ve rz kuzeye yönelik)

> ### Faz 3 - Tamamlandı
> - Faz 3 final eğitimi ve stabilizasyon tamamlandı.
> - **env.py değişiklikleri** (Faz 2 → Faz 3, git diff ile):
>   - Başlangıç mesafe çarpanı: `np.random.randint(0,3)` → `np.random.randint(1,5.5)` (1–4 birim, daha geniş alan)
> - Tüm modeller ve loglar GitHub'a yedeklendi.

> ### Faz 4 - Tamamlandı
> - Faz 4 eğitimi tamamlandı.
> - **env.py değişiklikleri** (Faz 3 → Faz 4):
>   - Başlangıç mesafe çarpanı: `np.random.randint(1,5.5)` → `np.random.randint(2,7)` (2–6 birim, daha geniş alan)

> ### Faz 5 - Tamamlandı
> - Faz 5 eğitimi tamamlandı.
> - **env.py değişiklikleri** (Faz 4 → Faz 5):
>   - Başlangıç mesafe çarpanı: `np.random.randint(2,7)` → `np.random.randint(3,10)` (3–9 birim, daha geniş alan)

> ### Faz 6 - Tamamlandı
> - Faz 6 eğitimi tamamlandı.
> - **env.py değişiklikleri** (Faz 5 → Faz 6):
>   - Başlangıç mesafe çarpanı: `np.random.randint(3,10)` → `np.random.randint(4,11)` (4–10 birim, daha geniş alan)

> ### Faz 7 - Tamamlandı
> - Faz 7 eğitimi tamamlandı.
> - **env.py değişiklikleri** (Faz 6 → Faz 7):
>   - Başlangıç mesafe çarpanı: `np.random.randint(4,11)` → `np.random.randint(7,13)` (7–12 birim, daha geniş alan)
>   - Ödül ve ceza ayarları: `ANGLE_GAIN = 0.22 → 0.30`, `SUCCESS_REWARD = 210.0 → 250.0`, `HIGH_ALTITUDE_PENALTY = -82.0 → -85.0`, `ESCAPE_PENALTY = -50.0 → -60.0`
> - **Log yönetimi**: `logs/step_log.csv` Faz 7 için `logs/step_log_faz7.zip` olarak sıkıştırıldı ve aktif dosya sıfırlandı (büyük dosya uyarılarını azaltmak için).

> ### Faz 8 - Tamamlandı
> - Faz 8 eğitimi tamamlandı.
> - **env.py değişiklikleri** (Faz 7 → Faz 8):
>   - Başlangıç mesafe çarpanı: `np.random.randint(5.5,12.5)` → `np.random.randint(7,13)` (yaklaşık 6–12 birimden 7–12 birime, daha uzak minimum mesafe)

> ### Faz 9 - Tamamlandı
> - Faz 9 eğitimi tamamlandı.
> - **env.py değişiklikleri** (Faz 8 → Faz 9):
>   - Başlangıç mesafe çarpanı: `np.random.randint(7,13)` → `np.random.randint(9,16)` (9–15 birim, hedef başlangıç mesafesi belirgin şekilde büyüdü)
>   - Ödül ve ceza ayarları:
>     - `STEP_PENALTY = -0.018 → -0.022` (adım başına ceza biraz artırıldı)
>     - `DISTANCE_GAIN = 0.15 → 0.17`, `ANGLE_GAIN = 0.30 → 0.40`
>     - `ANG_VEL_PENALTY = 0.004 → 0.005`
>     - `ESCAPE_PENALTY = -60.0 → -70.0`, `ESCAPE_GRACE_STEPS = 50 → 55`
>     - `HEIGHT_ALIGN_GAIN = 0.015 → 0.020`

> ### Faz 10 - Başarısız (Tamamlandı)
> - Faz 10 eğitimi **tamamlandı ancak hedeflenen başarı seviyesine ulaşamadı**.
> - **env.py değişiklikleri** (Faz 9 → Faz 10):
>   - Başlangıç mesafe çarpanı: `np.random.randint(9,16)` → `np.random.randint(10.5,20)` (yaklaşık 11–19 birim; çok uzak başlangıç menzili)
>   - Maksimum adım sayısı: `max_step = 1300` → `max_step = 255` (epizot süresi ciddi biçimde kısaltıldı)
>   - Ödül/ceza parametreleri:
>     - `STEP_PENALTY = -0.022 → -0.030` (her adım için daha sert ceza)
>     - `HIGH_ALTITUDE_PENALTY = -85.0 → -90.0`
>     - `TIMEOUT_PENALTY = -60.0 → -90.0`
>     - `HEIGHT_ALIGN_GAIN = 0.020 → 0.025`
>   - Kaçış (escape) mantığı: ESCAPE terminal bloğu yoruma alınarak devre dışı bırakıldı (kaçış durumları artık terminal olmuyor).
> - **Başarı oranı (success rate)**: **%54.34** — önceki fazlara kıyasla belirgin düşüş; bu nedenle Faz 10 **başarısız** olarak işaretlendi ve bir önceki faz (Faz 9) kalıcı referans olarak korunuyor.

# v6.0 sürüm ailesi

> ## v6.0.0 - Guidance-First State Overhaul ve Repo Temizligi
>
> - **Observation Contract Break**: RL state yapisi 20 boyuttan 18 boyutlu guidance-first observation setine gecirildi.
> - **Unity -> Python Senkron Revizyonu**: JSON paket sozlesmesi yeni state alanlarina gore tekrar tasarlandi.
> - **Reward Refactor**: Reward mantigi mesafe ilerlemesi, LOS alignment, pozitif kapanma hizi, acisal hiz cezasi ve irtifa hizalama sinyalleri ile yeniden kuruldu.
> - **Loglama / Analiz Guncellemesi**: `log.py`, `test.py`, `reward_test.py` ve `docs/analiz.py` yeni V6 alanlari uzerinden calisacak sekilde guncellendi.
> - **Repo Temizligi**: Pre-V6 log ve model artefaktlari once arsivlendi, ardindan repo kokundeki runtime ciktilari gitten cikarildi.

# v7.0 sürüm ailesi

> ## v7.0.0 - Full Telemetry Step Logging
>
> - **Unified Step Trace**: Unity tarafindan gelen ham geometri ve fizik telemetry verileri ile Python tarafinda uretilen action, value, logp, reward breakdown ve cumulative return bilgileri tek `step_log.csv` satirinda birlestirildi.
> - **Packet Contract Expansion**: Unity -> Python JSON sozlesmesine `telemetry` bolumu eklendi. Roket, hedef ve roket-hedef ciftine ait world/local konum, rotasyon, hiz, acisal hiz, relative vector ve gravity alanlari artik state disi debug verisi olarak tasiniyor.
> - **Reward Auditability**: Step log artik `reward_step_penalty`, `reward_distance`, `reward_alignment`, `reward_closing`, `reward_angular_penalty`, `reward_altitude`, `reward_soft_floor_penalty` ve `reward_terminal` kolonlarini ayri ayri sakliyor.
> - **Training Introspection**: Python tarafinda `action_norm_*`, `action_logp`, `value_pred`, `episode_return_so_far`, `phase_id`, `phase_name` ve `max_step` alanlari da step bazinda kaydediliyor.
> - **Schema-Safe Logging**: `log.py`, yeni baslik ile mevcut CSV basligi farkliysa eski loglari `.bak_YYYYMMDD_HHMMSS.csv` olarak arsivleyip temiz V7 dosyalari aciyor.
> - **State/Telemetry Separation**: RL observation 14 boyutlu sade guidance state olarak korundu; genis debug verisi ise ayri telemetry kanalina tasinarak analiz kolaylastirildi.

# v7.1 sürüm ailesi

> ## v7.1.0 - Phase 1.1 Archive Snapshot
>
> - **Phase 1.1 Freeze Point**: Faz 1.1 egitimi `up340` modelinde donduruldu ve Phase 1.2 warm-start noktasi olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_1/` altina `ppo_model_up340`, agent state, `episode_log.csv`, `update_log.csv`, success rate grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis/parcalanmis arsivi eklendi.
> - **Documentation Update**: README ve changelog, Phase 1.1 sonuc ozeti ve sonraki Phase 1.2 gecis niyeti ile guncellendi.
> - **Observed Outcome**: Phase 1.1 kosusunda `1640` episode icinde `161` success (%9.817) goruldu; baskin failure modu `high_altitude` olarak kaldigi icin bir sonraki adim reward ince ayari olarak planlandi.

# v7.2 sürüm ailesi

> ## v7.2.0 - Phase 1.2 Archive Snapshot
>
> - **Phase 1.2 Freeze Point**: Faz 1.2 egitimi `up520` modelinde donduruldu. Bu nokta, en iyi kumulatif success rate'in `%27.957` ile `episode 930 / update 529` civarinda goruldugu koridora en yakin kayitli checkpoint olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_2/` altina `ppo_model_up520`, agent state, `episode_log.csv`, `update_log.csv`, success-rate grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis / 7 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.2 genelinde `1621` episode icinde `308` success (%19.001) goruldu. En iyi rolling 200 success rate `%35.500` olarak `episode 724-923` koridorunda toplandi.
> - **Phase 1.3 Direction**: Bir sonraki adim zorlugu sertlestirmek degil, `up520` uzerinden peak davranisi stabilize etmek olarak belirlendi. Bu nedenle menzil bandinin `80-90` fiili mesafe cevresinde korunmasi ve optimizer tarafinda daha korumaci ayarlara gecilmesi not edildi.

# v7.3 sürüm ailesi

> ## v7.3.0 - Phase 1.3 Archive Snapshot
>
> - **Phase 1.3 Freeze Point**: Faz 1.3 egitimi `up800` modelinde donduruldu. `up700` penceresi biraz daha yuksek ham pencere success rate gormesine ragmen, `up800` gec ve halen guclu bir checkpoint oldugu icin handoff noktasi olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_3/` altina `ppo_model_up800`, agent state, `episode_log.csv`, `update_log.csv`, success-rate grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis / 6 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.3 genelinde `1817` episode icinde `855` success (%47.056) goruldu. En iyi rolling 100 success rate `%67.000`, en iyi rolling 200 success rate `%61.000` olarak kaydedildi.
> - **Phase 2.1 Direction**: Bir sonraki adim ayni fazi tekrar uzatmak degil, `up800` uzerinden yumusak bir `Phase 2.1` gecisi yapmak olarak belirlendi. Bu nedenle fiili baslangic mesafesi cekirdegi korunup heading sapmasi ve horizon dikkatli sekilde artirilacak.

# v8.0 sürüm ailesi

> ## v8.0.0 - Gravity-Based Guidance State and Semantic Action Redesign
>
> - **State Contract Redesign**: RL observation 14 boyutta tutuldu, ancak alanlar tamamen guidance semantigine gore yeniden tanimlandi. Yeni observation artik `theta`, `alpha`, `beta`, guidance-frame bagil hizlar, guidance-frame turn-rate bilesenleri ve `forward_up_dot` tasiyor.
> - **Semantic Action Space**: Python -> Unity action anlami `thrust / pitch / yaw` yerine `thrust / vertical_cmd / horizontal_cmd` oldu. Unity bu semantic komutlari gravity tabanli guidance frame uzerinden local torque'a donusturuyor.
> - **Telemetry Expansion**: Step telemetry su yeni alanlarla genisletildi: guidance world/local eksenleri, guidance-frame hiz bilesenleri, guidance-frame acisal hiz bilesenleri ve uygulanan semantic turn komutlarinin world/local izdususleri.
> - **Logging and Test Pipeline Update**: `log.py`, `test.py`, `reward_test.py`, `reward_grid_search.py` ve `connector.py`, yeni `theta/alpha/beta` ve semantic action isimlerine uyarlandi. CSV basliklari V8 semasina gore otomatik yenilenir.
> - **Model Baseline Update**: PPO actor-critic omurgasi `512-512-512` olarak buyutuldu. Bu degisim yeni V8 temsil uzayi ile birlikte bastan egitim senaryosuna temel olmasi icin yapildi.
> - **Training Note**: V8 semantigi checkpoint formatini degil ama policy anlamini degistirdigi icin, eski checkpoint'lerden warm-start etmek yerine temiz egitim baslatmak tercih edilmelidir.

# v8.1 sürüm ailesi

> ## v8.1.0 - Phase 1.4 Archive Snapshot
>
> - **Phase 1.4 Freeze Point**: V8 gravity-based guidance kosusu `up1200` modelinde donduruldu. Bu nokta, en iyi rolling 100 success koridoruna (`episode 561-660`, `update 1188-1201`) dogrudan denk geldigi ve son `200-300` episode'da `%64-%67` bandini korudugu icin handoff modeli olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_4/` altina `ppo_model_up1200`, agent state, `episode_log.csv`, `update_log.csv`, rolling success-rate grafigi, success yogunluk grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis / 30 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.4 genelinde `5790` episode icinde `1235` success (%21.330) goruldu. En iyi rolling 100 success rate `%72.000`, en iyi rolling 200 success rate `%70.000` olarak kaydedildi. Son `200` episode'da success rate `%67.000` seviyesine kadar cikti.
> - **Phase Transition Decision**: Son `200` episode icinde `75-80` fiili baslangic mesafesi `%95.83`, `80-85` `%100`, `85-90` `%100` success urettigi icin bir sonraki fazin menzil bandi yukariya kaydirilacak sekilde `62-82 radius` olarak secildi. Heading araligi ve reward ailesi ilk denemede korunacak.

# v8.2 sürüm ailesi

> ## v8.2.0 - Phase 1.5 Archive Snapshot
>
> - **Phase 1.5 Freeze Point**: V8 guidance/action kosusu `up1380` modelinde donduruldu. Bu nokta, son `200-300` episode koridorunda success rate'in `%91` bandina oturdugu ve `up1384`e kadar performansin yuksek kaldigi pencerenin icinde yer aldigi icin handoff modeli olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_5/` altina `ppo_model_up1380`, agent state, `episode_log.csv`, `update_log.csv`, secilmis success/radius analiz grafikleri ve buyuk `step_log.csv` dosyasinin sikistirilmis / 5 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.5 genelinde `1291` episode icinde `1015` success (%78.621) goruldu. En iyi rolling 100 success rate `%95.000`, en iyi rolling 200 success rate `%92.500`, en iyi rolling 300 success rate `%91.667` olarak kaydedildi.
> - **Phase Transition Decision**: Yari-cap bazli basari analizi `60-75` bandinin artik buyuk olcude ogrenildigini, asil kirilma noktasinin `75+` oldugunu gosterdi. Bu nedenle bir sonraki faz icin menzil bandi `71-81 radius` olarak secildi; heading araligi ve reward ailesi ilk geciste korunacak.

# v8.3 sürüm ailesi

> ## v8.3.0 - Phase 1.6 Archive Snapshot
>
> - **Phase 1.6 Freeze Point**: `71-81 radius` bandinda kosulan egitim `up1460` modelinde donduruldu. Bu nokta, son `100-300` episode koridorunda success rate'in `%94-%95` bandinda stabil kaldigi ve `update 1462`ye kadar dusmeden devam ettigi pencerenin icinde yer aldigi icin handoff modeli olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_6/` altina `ppo_model_up1460`, agent state, `episode_log.csv`, `update_log.csv`, secilmis success/radius analiz grafikleri ve buyuk `step_log.csv` dosyasinin sikistirilmis / 2 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.6 genelinde `637` episode satiri icinde `600` success (%94.192) goruldu. En iyi rolling 100 success rate `%100.000`, en iyi rolling 200 success rate `%98.500`, en iyi rolling 300 success rate `%97.333` olarak kaydedildi.
> - **Phase Transition Decision**: Yari-cap bazli analiz `70-75` bandinin neredeyse tamamen cozuldugunu (`%99.6`), `75-80` bandinin de cok guclu oldugunu (`%93.4`) gosterdi. Bu nedenle bir sonraki faz icin menzil bandi `75-85 radius` olarak secildi; heading ve reward ailesi ilk geciste korunacak.

# v8.4 sürüm ailesi

> ## v8.4.0 - Phase 1.7 Archive Snapshot
>
> - **Phase 1.7 Freeze Point**: `75-85 radius` bandinda kosulan egitim uzun sure devam ettirildiginde gec kuyrukta ciddi policy drift urettigi icin son checkpoint yerine orta koridordaki en iyi pencereye yakin olan `up1740` modelinde donduruldu. En iyi 20-update koridoru `update 1728-1747` araliginda `%98.734` success verdi.
> - **Artifact Archiving**: `archives/phase_1_7/` altina `ppo_model_up1740`, agent state, `episode_log.csv`, `update_log.csv`, secilmis success/radius analiz grafikleri ve buyuk `step_log.csv` dosyasinin sikistirilmis / 19 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.7 genelinde `3948` episode icinde `2614` success (%66.211) goruldu. Ancak son `100-300` episode pencerelerinde success rate `%5-%5.7` bandina dustu; buna karsin en iyi rolling 100 success rate `%100.000`, en iyi rolling 200 success rate `%98.000`, en iyi rolling 300 success rate `%95.000` olarak kaydedildi.
> - **Phase Transition Decision**: Gec kuyruktaki bozulmaya ragmen orta koridor analizi `75-85 radius` bandinin ogrenildigini gosterdi. Bu nedenle bir sonraki faz icin menzil bandi `80-90 radius`, `max_step=480` olarak secildi; heading ve reward ailesi ilk geciste korunacak.

# v8.5 sürüm ailesi

> ## v8.5.0 - Phase 1.8 Archive Snapshot
>
> - **Phase 1.8 Freeze Point**: `80-90 radius` bandinda kosulan egitim `up1840` modelinde donduruldu. Bu noktada son `100-200` episode pencerelerinde success rate `%92-%92.5` bandinda kaldigi ve son update bloklari da guclu seyrini korudugu icin handoff modeli olarak son checkpoint kullanildi.
> - **Artifact Archiving**: `archives/phase_1_8/` altina `ppo_model_up1840`, agent state, `episode_log.csv`, `update_log.csv`, secilmis success/radius analiz grafikleri ve `step_log.csv` dosyasinin sikistirilmis / 3 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.8 genelinde `687` episode icinde `623` success (%90.684) goruldu. En iyi rolling 100 success rate `%99.000`, en iyi rolling 200 success rate `%95.500`; en iyi 20-update koridoru ise `update 1800-1819` araliginda `%97.297` success olarak kaydedildi.
> - **Phase Transition Decision**: Yari-cap bazli analiz `80-85` bandinin `%96.9`, `85-90` bandinin `%86.6` success verdigini gosterdi. Bu nedenle bir sonraki faz icin menzil bandi `85-95 radius` olarak secildi; heading ve reward ailesi korunurken `max_step=480` sabit tutulacak.

# v8.6 sürüm ailesi

> ## v8.6.0 - Phase 1.9 Archive Snapshot
>
> - **Phase 1.9 Freeze Point**: `85-95 radius` bandinda kosulan egitim `up1920` modelinde donduruldu. Son blok olan `update 1902-1921` araligi `134` episode icinde `%98.507` success verdigi icin son checkpoint handoff modeli olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_9/` altina `ppo_model_up1920`, agent state, `episode_log.csv`, `update_log.csv`, secilmis success/radius analiz grafikleri ve `step_log.csv` dosyasinin sikistirilmis / 2 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.9 genelinde `499` episode icinde `448` success (%89.780) goruldu. En iyi rolling 100 success rate `%99.000`, en iyi rolling 200 success rate `%98.000`; en iyi 20-update koridoru ise `update 1897-1916` araliginda `%99.291` success olarak kaydedildi.
> - **Phase Transition Decision**: Yari-cap bazli analiz `85-90` bandinin `%97.170`, `90-95` bandinin `%85.263` success verdigini gosterdi. Bu nedenle bir sonraki faz icin menzil bandi `90-100 radius` olarak secildi; heading, reward ailesi ve `max_step=480` ilk geciste korunacak.

> ## v8.6.1 - Phase 2.0 Retry Archive Snapshot
>
> - **Phase 2.0 Retry Freeze Point**: `90-100 radius` bandinda kosulan Faz 2.0 retry egitimi `up2100` modelinde donduruldu. `up2101-up2120` post-window penceresi `%94.615` success ve `195.82` ortalama return verdigi icin handoff modeli olarak `up2100` secildi.
> - **Artifact Archiving**: `archives/phase_2_0/` altina `ppo_model_up2100`, agent state, `episode_log.csv`, `update_log.csv`, secilmis success/start-distance/checkpoint/reward/turn-action analiz grafikleri ve buyuk `step_log.csv` dosyasinin sikistirilmis / 6 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Ana oturumda `1209` episode icinde `1116` success (%92.308) goruldu. Ikinci oturum ayni faza ait `up2122` resume denemesidir; log temizlenmeden basladigi icin ayri analiz edildi ve `%68.182` success ile drift riski gosterdigi icin handoff olarak kullanilmadi.
> - **Reward/Action Decision**: `turn_toward` ve `action_alignment` reward sinyalleri korundu; PPO fine-tune ayarlari `lr=2e-5`, `clip_eps=0.08`, `ent_coef=0.004`, `target_kl=0.0025` olarak birakildi.
> - **Phase Transition Decision**: Gozlenen start-distance bantlari `100-105=%97.167`, `105-110=%92.603`, `110-115=%79.739` verdi. Ust band tam stabil olmadigi icin bir sonraki faz kontrollu genisletme olarak `95-105 radius`, `max_step=500`, heading `±2.5` ile baslatilacak.

# v8.7 sürüm ailesi

> ## v8.7.0 - Phase 2.1 Training Prep
>
> - **Runtime Phase Activation**: Aktif manuel config `v8_7_phase_2_1` olarak ayarlandi.
> - **Curriculum Window**: `up2100` handoff modeli uzerinden `95-105 radius`, heading `±2.5`, `max_step=500` ile kontrollu genisletme baslatilacak.
> - **Reward/Action Policy**: Faz 2.0 retry'da kullanilan reward/action ailesi korunacak; yeni fazda sadece radius/max-step penceresi genisletildi.

> ## v8.7.1 - Phase 2.1 Collapse Analysis
>
> - **Collapse Observation**: Ilk Faz 2.1 retry denemesinde `up2102-up2129` araliginda toplam success `%64.179` goruldu, ancak son pencere hizla dustu (`R20=%15`, `R50=%40`, `R100=%56`).
> - **Failure Geometry**: Basarisiz episode'larin buyuk bolumu hedefe yaklasabildi ama burun acisi kapanmadi; `high_altitude` hatalarinda ortalama min-distance `7.43m`, theta `110.3°`, alignment `-0.335` bulundu.
> - **Decision**: Terminal cezalari buyutmek tek basina secilmedi. `agent.py` uzerindeki PPO denemeleri geri alindi; yeni deneme sadece `env.py` reward tasarimini aci-kapatma odakli yapacak.

> ## v8.7.2 - Phase 2.1 Angle Reward Prep
>
> - **Runtime Phase Activation**: Aktif manuel config `v8_7_phase_2_1_angle_reward` olarak ayarlandi; handoff checkpoint `up2100` olarak korunacak.
> - **Curriculum Window**: `95-105 radius`, heading `±2.5`, `max_step=500` ile ayni spawn kosulu korunacak.
> - **Reward Retune**: Distance/closing odulu iyi burun acisi ve pozitif alignment ile gate edildi; theta progress `0.90`, alpha/beta progress `0.30`, angle-focus `1.10` olarak aci kapatma sinyali belirginlestirildi.
> - **Near-Miss Guardrail**: `distance<=18m` ve `theta>=75°` durumunda `near_miss=-90` eklendi; hedefin uzerinden aci kapatmadan gecen episode success gibi odullenmeyecek.
> - **Terminal Scale**: Terminal cezalari hafif tutuldu (`high_altitude=-105`, `wrong_way=-115`, `low_agl=-110`, `timeout=-80`, `success=180`); hedef, terminal buyutmek yerine ara reward ile burnu hedefe cevirmek.
> - **Altitude Guardrail**: `max_altitude=145`, `soft_ceiling_start=105`, `soft_ceiling_gain=0.018`; iyi aciyla yuksek irtifa ilerlemesi pozitif kalirken kotu aciyla yuksekten kacis negatiflesir.

> ## v8.7.3 - Phase 2.1 Thrust Guard Prep
>
> - **Collapse Observation**: `v8_7_phase_2_1_angle_reward` run'inda `192` episode icinde `%54.167` success goruldu. Ilk `120` episode `%78.333` success iken `121+` penceresi `%13.889` success'e dustu; start-distance ortalamasi neredeyse degismedi (`111.34` -> `110.80`).
> - **Root Cause Candidate**: Cokus 20 PPO update civarina denk geliyor (`ROLLOUT_LEN=1200`, yaklasik `5-7` episode/update). Basarili episode'larda ortalama `action_norm_0=-0.325` (`~759 thrust`), post-collapse failure episode'larda `action_norm_0=+0.243` (`~892 thrust`) oldu.
> - **Reward/Action Decision**: Ana duzeltme terminal buyutmek degil; aci kapanmadan gaz artisini engellemek. Thrust mapping `650-950` bandina daraltildi ve `theta>35°` iken `action_norm_0>-0.20` icin `thrust_gate_penalty` eklendi.
> - **Checkpoint Decision**: Bu run'dan olusan `up2120` handoff olarak kullanilmamali. Yeni retry `up2100` uzerinden baslatilmali; run oncesi `up2120` silinmeli ya da `ADS_AI_CHECKPOINT_UPDATE=2100` set edilmeli.

> ## v8.7.4 - Phase 2.1 Deep Reward Grid Search
>
> - **Deep Search**: `20` dakika CUDA grid-search calistirildi (`35,815,424` aday, `35,380` step satiri). Raporlar `docs/reward_research/summary_20260411_171943.txt` ve ilgili CSV dosyalarina yazildi.
> - **Measured Collapse**: `v8_7_phase_2_1_thrust_guard` run'i `183` episode icinde `%53.005` success verdi. Ilk `120` episode `%71.667`, `121+` penceresi `%17.460` success'e dustu.
> - **Root Cause Confirmation**: Success rate ile `mean_a0` korelasyonu `-0.8992`, `high_a0_frac` korelasyonu `-0.8979`; post-collapse failure mean `action_norm_0=+0.4449`, success mean `action_norm_0=-0.2318`.
> - **Action Sign Check**: Action/turn sign mevcut konvansiyonda dogru gorundu; lag-10 korelasyonlari `score_pos theta_corr=0.21141`, `turn_pos theta_corr=0.47170` ve ters isaret negatif.
> - **Reward/Action Decision**: Thrust mapping `700-850` bandina daraltildi. Grid'in sectigi thrust gate kullanildi: `gain=0.75`, `target=-0.25`, `theta_start=45`, `theta_span=20`, `dist_scale=40`, `dist_floor=0.50`.

> ## v8.7.5 - Phase 2.1 up2160 Archive Snapshot
>
> - **Phase 2.1 Freeze Point**: `v8_7_phase_2_1_thrust_guard_v2` kosusu `up2160` checkpoint'inde donduruldu. Analiz sadece guncel oturum olan `update 2142-2160` araligina uygulandi; eski `2102-2141` oturumu ve parcali `2161` episode'lari karar hesabina katilmadi.
> - **Observed Outcome**: Guncel oturumda `117` episode icinde `109` success, `7` near_miss ve `1` wrong_way goruldu; success rate `%93.162` oldu. Kuyruk rolling degerleri `R20=%95.000`, `R30=%96.667`, `R50=%96.000`, `R100=%96.000` olarak stabil kaldigi icin faz gecisine uygun bulundu.
> - **Reward/Action Diagnostics**: Success episode'larda mean `action_norm_0=-0.5884`, fail episode'larda `-0.2630` olculdu; onceki thrust drift belirtisi bu oturumda gorulmedi. Fail episode'lar hedefe yaklasabildi fakat theta kapanmadi (`theta_at_min_distance=74.003`, `final_theta=83.275`), bu nedenle sonraki fazda aci odakli reward ailesi korunacak.
> - **Artifact Archiving**: `docs/phase_planning/phase_2_1_up2160/` altina summary, episode diagnostics CSV, rolling success grafigi, success rug ve start-distance outcome grafigi eklendi.
> - **Curriculum Planning**: `docs/phase_planning/curriculum_reward_summary_v8_7_4_radius500_reward_grid_20260412_184355.txt` sonucu referans alindi. Bir sonraki faz icin ilk aday `105-120 radius`, `max_step=520`; ancak yeni faz ayari bu snapshot commitinden sonra ayri olarak uygulanacak.

> ## v8.7.6 - Phase 2.2 up2520 Archive Snapshot
>
> - **Phase 2.2 Freeze Point**: `v8_7_phase_2_2_radius_105_120_reward_grid` kosusu `up2520` checkpoint'inde donduruldu. `up2580` daha yeni olmasina ragmen drift tasidigi icin handoff olarak secilmedi.
> - **Observed Outcome**: `update 2162-2520` araligi `1951` episode icinde `1533` success verdi (`%78.575`). Tail metrikleri `R20=%85`, `R50=%88`, `R100=%86`; observed start-distance bantlari `115-120=%88.06`, `120-125=%84.63`, `125-130=%62.81`.
> - **Drift Observation**: `up2541-up2580` araligi `%66.038` success'e dustu. En kritik bant olan `125-130m`, `up2561-up2580` penceresinde `%14.286` success'e kadar indi; dominant hatalar `near_miss` ve `low_agl` oldu. Ham loglar `up2595` seviyesine kadar uzandi, ancak yeni checkpoint kaydedilmedi ve `up2595` tail (`R100=%74`, hard-bin tail `%57.6`) yine `up2520` seviyesine cikamadi.
> - **Reward Diagnostics**: Collapse penceresinde `125-130m` near_miss ortalama `final_theta=90.13deg`, `mean_a0=-0.217`, `thrust_gate=91.29`; low_agl ortalama `mean_a0=0.558`, `thrust_gate=401.54`. Bu nedenle terminal ceza buyutmek yerine aci kapanmadan gaz artisini daha erken cezalandiran thrust gate secildi.
> - **Artifact Archiving**: `archives/phase_2_2/` altina `up2520` model/state, raw episode/update loglari, statik PNG raporlari ve Plotly HTML raporlari eklendi. Full `step_log.csv` boyutu push paketini asiri buyuttugu icin bolunmus gzip parcasi lokal arsivde tutuldu, git snapshot'ina eklenmedi. `up2520` handoff raporu ile `up2580/up2595` drift raporlari birlikte saklandi.
> - **Next Phase Decision**: Dogrudan `120-140 radius` fazina gecmek yerine ara faz secildi: `110-120 radius`, `max_step=520`, handoff `up2520`. Reward ayari `theta_progress_gain=1.75`, `angle_focus_gain=2.05`, `action_alignment_gain=0.075`, `thrust_gate_gain=2.05`, `thrust_gate_target_norm=-0.50`, `theta_start=50`, `dist_floor=0.70` olacak; ayar snapshot commit/push sonrasi uygulanacak.

> ## v8.7.7 - V8 Failed Final Snapshot
>
> - **Final V8 Decision**: `v8_7_phase_2_3_radius_105_120_safe_climb_guidance` mimarisi basarisiz olarak kapatildi. Reward-only duzeltmeler ve safe-climb guardrail'leri kismi iyilesme saglasa da state/action temsili hedef yonunu kararlı tasiyamadigi icin V8 daha fazla genisletilmeyecek.
> - **Observed Outcome**: Final snapshot `update 2502-2514` araliginda `50` episode icerir. Success `4/50` (`%8.0`), near_miss `28/50` (`%56.0`), wrong_way `9/50` (`%18.0`), low_agl `7/50` (`%14.0`) olarak olculdu. Ortalama return `-223.984`, median return `-109.455`.
> - **Failure Diagnosis**: Basarisizligin ana nedeni terminal ceza buyuklugu degil, yon temsilidir. Roket hedef yakinine ulasabildigi halde burun acisini koruyamadi (`near_miss` ortalama final theta yaklasik `77deg`) ve PPO update'leri yuksek-thrust / tekrar eden steering moduna kayarak `low_agl` ve `wrong_way` pattern'lerini yeniden uretti.
> - **Artifact Archiving**: `archives/v8_failed_final_up2514/` altina final V8 episode/update loglari, sikistirilmis step log snapshot'i ve kaynak `up2500` checkpoint'i eklendi.
> - **Next Architecture Decision**: V9, sign-based `vertical_cmd/horizontal_cmd` yerine clock-guidance state/action temsiline gececek. Action seti `thrust + clock_12/clock_6/clock_3/clock_9` kanallari olacak; success mesafesi gevsek `12-15m` bandindan `10m` hedefe cekilecek.

# v9.0 sürüm ailesi

> ## v9.0.0 - Phase 1 Clock-Guidance Training Prep
>
> - **Architecture Reset**: V9, V8 checkpoint'leri ile uyumlu olmayan yeni state/action sozlesmesi baslatir. Bu nedenle model prefix'i `ppo_v9_model` / `ppo_v9_state` olarak ayrildi ve egitim sifirdan baslayacak.
> - **State Redesign**: Roket burnu etrafinda gravity referansli clock frame kuruldu. State'e `target_clock_12/6/3/9`, `rel_vel_clock_12/6/3/9`, `turn_rate_clock_12/6/3/9`, `clock_validity` ve clock telemetry alanlari eklendi.
> - **Action Redesign**: Eski `vertical_cmd/horizontal_cmd` yerine `thrust + clock_12_cmd + clock_6_cmd + clock_3_cmd + clock_9_cmd` kullanilir. Zıt clock kanallari Unity tarafinda bileşkeye cevrilir ve roket burnu etrafindaki clock frame uzerinden torque uygulanir.
> - **Reward Redesign**: Clock action alignment, wrong-channel penalty ve coactivation penalty eklendi. Boylece hedef hangi clock kanalindaysa modelin ayni kanali acmasi, ters kanali ve zit coactivation'i azaltmasi beklenir.
> - **Curriculum Reset**: V9 Phase 1 `140-160m` radius ile baslar. Ilk run sonrasi heading offset `±5deg` olarak daraltildi ve `0deg` dislandi; hedef tam uzerden gecmeyecek ama ilk clock-guidance denemesi icin daha okunabilir olacak.
> - **Success Tightening**: Success mesafesi `10m`, alignment sarti `0.90`, success reward `260` olarak ayarlandi.
> - **Roll Suppression Tuning**: Rocket roll hareketi hard-lock edilmeden daha guclu bastirildi. Scene ve `Env.cs` icinde `rollTorqueScale=3.6`, `rollStabilizationGain=22`, `rollDampingGain=12`, `maxRollCorrection=5.25` olarak senkronlandi.
> - **Analysis Tooling**: Standart PNG ve Plotly faz raporlarina V9 `clock_action_alignment` grafigi eklendi. Bu grafik target clock kanallari ile action clock kanallarini, dominant kanal eslesmesini ve clock reward terimlerini update bazinda izler.
> - **Repo Cleanup**: Eski hard-coded `plot_success.py`, gecici `_live.py`, Python `__pycache__` ve takip edilmeyen eski failed-run arsivleri temizlendi; V8 final arsivi korundu.
> - **Versioning Rule**: Bu faz `v9.0.0` olarak adlandirilir. Ayni mimaride sonraki fazlar `v9.0.1`, `v9.0.2` seklinde ilerler; fazlarda sıcrama niteliginde mimari/curriculum degisimi olursa `v9.1` ailesine gecilir.

> ## v9.0.1 - V9 Continuous Clock-Channel Failed Snapshot
>
> - **Run Closure**: V9 continuous clock-channel mimarisi `up100` checkpoint'inde basarisiz olarak kapatildi. Snapshot `archives/v9_0_0_failed_up100/` altina alindi; statik PNG, Plotly HTML raporlari, episode/update loglari, parcali step trace ve `up100` model/state eklendi.
> - **Observed Outcome**: `update 1-100` araliginda `310` episode tamamlandi. Success `0/310` (`%0.0`), near_miss `70/310` (`%22.58`), high_altitude `240/310` (`%77.42`) olarak olculdu. Son `50` episode icinde `12` near_miss ve `38` high_altitude goruldu.
> - **Failure Diagnosis**: Heading offset daraltildiktan sonra roket hedef koridoruna daha sik girdi, ancak burnu hedefe cevirmedi. Ortalama final theta `137.12deg`, final alignment `-0.696`, final closing speed `-29.34m/s` seviyesinde kaldi.
> - **Action Diagnosis**: Target/action dominant clock-channel eslesmesi rastgele dort kanal seviyesinde kaldi (`~%25`). Continuous `clock_12/6/3/9` kanallari zit kanal coactivation'ina izin verdigi icin net manevra yonu sikca sulandi.
> - **Near-Miss Decision**: `near_miss` terminali tuzak olarak degerlendirildi. Yakindan ama kotu aciyla gecen episode'u erken kapattigi icin modelin recovery ve aci kapatma ogrenmesini kesiyor. V10'da terminal olmayacak, sadece diagnostic/log sinyali olarak kalacak.
> - **Next Architecture Decision**: Action turu degisecegi icin sonraki deneme `v10.0.0` olarak baslatilacak. V10, continuous thrust ile discrete clock-direction steering'i hibrit PPO policy olarak kullanacak.

# v10.0 sürüm ailesi

> ## v10.0.0 - Hybrid Discrete Clock-Direction Training Prep
>
> - **Architecture Break**: Action turu degistigi icin V10, V9 checkpoint'leri ile uyumlu degildir. Model prefix'i `ppo_v10_model` / `ppo_v10_state` olarak ayrildi ve egitim sifirdan baslayacak.
> - **Hybrid PPO Action**: Policy artik iki action uretir: continuous `thrust` ve categorical `turn_direction`. Discrete yon sinifi Python tarafinda mevcut Unity clock torque kanallarina (`clock_12/6/3/9`) genisletilir.
> - **Direction Set**: Steering siniflari `hold`, `clock_12`, `clock_12_3`, `clock_3`, `clock_3_6`, `clock_6`, `clock_6_9`, `clock_9`, `clock_9_12` olarak tanimlandi. Boylece zit continuous kanallarin ayni anda acilip net yonu sulandirmasi engellenir.
> - **Near-Miss Removal**: `near_miss` artik terminal degildir. Kosul sadece `near_miss_candidate` olarak loglanir; hedef yakinindan kotu aciyla gecen episode recovery sansi bulabilir.
> - **Reward Compatibility**: Clock action alignment reward'i korunur, ancak discrete action komutu reward hesabinda kendi `DISCRETE_TURN_STRENGTH` olcegine normalize edilir. Bu sayede dogru discrete yon secimi zayif odullenmez.
> - **PPO Update**: Actor head continuous thrust Gaussian'i ve discrete direction categorical logits'i birlikte optimize eder. Entropy ve KL hedefi categorical exploration icin hafif genisletildi (`ent_coef=0.006`, `target_kl=0.006`).
> - **Runnable Phase**: Ilk V10 fazi `v10_0_0_phase_1_hybrid_discrete_clock_140_160`; radius `140-160m`, heading offset `±5deg` fakat `0deg` haric, success mesafesi `10m` olarak korunur.

> ## v10.0.1 - Clock Reward Recovery Prep
>
> - **Failure Observation**: Ilk V10 run'i `up172` civarinda hala `0` success verdi; tamamlanan episode'larin tamamı `high_altitude` ile bitti. Ortalama final theta yaklasik `149deg`, action/target clock cosine ise update boyunca `0` civarinda kaldi.
> - **Root Cause**: Roket dik uctugu icin `clock_validity` median degeri `~0.018` seviyesindeydi. Clock action alignment reward'i bu degerle carpildigi icin dogru yon secimi pratikte odullenmiyordu.
> - **Reward Fix**: `clock_reward_validity_floor=0.70`, `clock_action_alignment_gain=1.20`, `clock_wrong_channel_penalty_gain=1.20` olarak ayarlandi. Eski log uzerinde hesaplanan random-policy net clock reward `~0`, oracle dogru yon reward'i ise `~0.626/step`.
> - **Maneuver Fix**: Unity tarafinda dik konumda turn yetkisi artirildi: `betaValidityFloor=0.75`, `torqueScale=1.8`, `lowAltitudeMinTurnScale=0.35`, `lowAltitudeTurnDampFullAgl=10`.
> - **Scene Sync**: `SampleScene.unity` icindeki serialize edilmis Env component de ayni degerlere cekildi; Unity'nin eski inspector override'lariyla calismasi engellendi.
> - **Altitude Fix**: Duz yukari high-altitude davranisini kirmak icin thrust araligi `620-700`, `soft_ceiling_start=80`, `max_altitude=125`, `high_altitude_penalty=-150` yapildi.
> - **Runnable Phase**: Yeni retry fazi `v10_0_1_phase_1_clock_reward_recovery_140_160`; eski V10 log/model dosyalari temizlenerek sifirdan kosulacak.

> ## v10.0.2 - V10 Failed Final Snapshot
>
> - **Final V10 Decision**: V10 hibrit discrete clock-action mimarisi `up40` checkpoint'i ile basarisiz olarak kapatildi. Snapshot `archives/v10_0_1_failed_up40/` altina alindi.
> - **Observed Outcome**: `update 1-56` araliginda `147` episode tamamlandi. Success `1/147` (`%0.680`), `high_altitude=143`, `wrong_way=2`, `low_agl=1` olarak olculdu. Son `100` episode icinde success gorulmedi.
> - **Success Note**: Tek success `episode_id=6`, `update=3`, `step=268` icinde geldi; final distance `4.23m`, final theta `24.24deg`, alignment `0.912` oldugu icin vurma kosulu temizdi.
> - **Failure Diagnosis**: Reward/scene duzeltmesi ilk vurus davranisini uretse de saf PPO exploration kararlı policy'ye donusemedi. Ortalama final theta `132.41deg`, final alignment `-0.661`, final distance `112.33m` seviyesinde kaldi.
> - **Next Architecture Decision**: V11, doğrudan reward katsayisi degistirmek yerine once klasik gudum saglik testiyle baslayacak. PN basarili olursa sonraki adim PN verisi toplama ve ogretili baslangic; PN basarisiz olursa once simülasyon/action otoritesi incelenecek.

# v11.0 sürüm ailesi

> ## v11.0.0 - PN Klasik Güdüm Sağlık Testi
>
> - **Teknik Karar**: V11, reward katsayisi degistirerek baslamaz. Once sahnenin klasik gudumle vurulabilir olup olmadigi test edilir. Boylece sorun PPO/reward tarafinda mi, yoksa Unity fizik/action/kuvvet tarafinda mi daha net ayrilir.
> - **Yeni Script**: `scripts/pn_guidance_test.py` eklendi. Script RL modeli kullanmadan PN (Proportional Navigation / oransal gudum) komutu uretir ve Unity'ye dogrudan `[thrust, clock_12, clock_6, clock_3, clock_9]` action paketi yollar.
> - **Env Yardimci Metodu**: `scripts/env.py` icine `step_direct_action()` eklendi. Bu metot PPO action normalizasyonunu atlayarak klasik algoritmalarin fiziksel Unity action'ini dogrudan test etmesini saglar.
> - **Parametreler**: `navigation_gain=4.0`, `turn_strength=1.2`, `turn_sign=1.0`, `pursuit_blend=0.25`, `thrust=MAX_THRUST`, `episodes=20`, `max_steps=700`.
> - **Cikti Dosyasi**: PN test adimlari `logs/pn_guidance_test.csv` icine yazilir. Kaydedilen alanlar arasinda `distance`, `theta_deg`, `closing_speed`, `agl`, PN komutlari ve done reason bulunur.
> - **Dokumantasyon**: `docs/v11_experiment_plan.md` eklendi. V11 ve sonrasi icin sirali deney akisi yazildi: PN saglik testi, PN verisi toplama, ogretili baslangic, PPO disi algoritma ve en son reward shaping revizyonu.
> - **README / VERSION**: Aktif takip surumu `v11.0.0` olarak guncellendi; README icine PN saglik testinin amaci ve yorumlama kurali eklendi.
> - **Beklenen Etki**: PN basarili olursa problem ogretilecek davranisin PPO tarafinda kesfedilememesidir. PN basarisiz olursa once sahne, kuvvetler, hedef hareketi ve action uygulamasi incelenecektir.

> ## v11.0.1 - Detayli PN Test Araci
>
> - **Deney Sonucu**: Ilk V11 PN testlerinde iki isaret denendi. `turn_sign=1` ve `turn_sign=-1` kosullarinda `0/20` success goruldu. Buna ragmen `turn_sign=1` testinde en yakin mesafe `3.41m` seviyesine indi; bu, sahnenin tamamen imkansiz olmadigini ama roket burnu/aci hizalamasinin yetersiz kaldigini gosterdi.
> - **PN Modlari**: `scripts/pn_guidance_test.py` icine `--mode blend|pn|pursuit` eklendi. `blend` PN ve saf hedefe donme sinyalini karistirir, `pn` sadece LOS kaymasini azaltmaya calisir, `pursuit` roket burnunu dogrudan hedefin bulundugu clock yonune cevirir.
> - **Radius Kontrolu**: Script artik `--radius-min`, `--radius-max`, `--heading-offset-min`, `--heading-offset-max`, `--heading-offset-abs-min` ve `--target-y` parametrelerini alir. Boylece `300m` nihai senaryo RL curriculum'a girmeden once klasik gudumle test edilebilir.
> - **Gorsel Izleme**: `--step-delay` ve `--pause-on-success` eklendi. Bu sayede Unity sahnesinde roketin hedefi vurdugu an daha yavas ve gorunur izlenebilir.
> - **Env Yardimci Metodu**: `scripts/env.py` icine `reset_with_config()` ve `_send_reset_values()` eklendi. Bu metotlar training fazini bozmadan PN testinin ozel radius/heading ile reset atmasini saglar.
> - **Ozet CSV**: Script artik adim CSV'sine ek olarak `*_summary.csv` uretir. Ozet dosyada reset radius, heading offset, min distance, min distance anindaki theta, final distance, final theta ve done reason bulunur.
> - **Parametreler**: Varsayilanlar `mode=blend`, `navigation_gain=4.0`, `turn_strength=1.2`, `turn_sign=1.0`, `pursuit_blend=0.25`, `thrust=MAX_THRUST`, `episodes=20`, `max_steps=700`.
> - **README / VERSION / Plan**: Aktif takip surumu `v11.0.1` olarak guncellendi; README ve `docs/v11_experiment_plan.md` detayli PN test akisini aciklar.

> ## v11.0.2 - Unity Action ve Irtifa Guvenligi Duzeltmesi
>
> - **Kok Neden Analizi**: 300m pursuit testinde roket hedefe yaklasirken `collision/low_agl` ile bitti. Roket kütlesi `50kg`, V10 training thrust ust siniri `700N` oldugu icin thrust/agirlik orani yaklasik `1.43` seviyesindeydi. Hedefe yatildiginda thrust'in yukari bileseni agirligi tasimaya yetmiyor.
> - **Unity Thrust Ekseni**: `ads_ai/Assets/Scripts/Env.cs` icinde thrust uygulamasi `rocketRb.AddRelativeForce(Vector3.forward...)` yerine `rocketRb.AddForce(rocketPoint.forward...)` oldu. Boylece state/debug tarafinda roket burnu olarak kullanilan `rocketPoint.forward` ile fiziksel itki ekseni ayni referansa baglandi.
> - **Dusuk Irtifa Action Guvenligi**: `Env.cs` icinde `lowAltitudeUpTurnMinScale=0.90` eklendi. Dusuk irtifada clock-12 yani gravity-up toparlama komutu artik fazla kisilmaz; clock-6 ve yatay clock-3/9 komutlari mevcut low-altitude damping ile daha dikkatli uygulanir.
> - **Scene Sync**: `ads_ai/Assets/Scenes/SampleScene.unity` icindeki Env component'e `lowAltitudeUpTurnMinScale: 0.9` eklendi. Unity Inspector serialize degerleri script varsayilanini ezmesin diye sahne de senkronlandi.
> - **PN Test Guvenligi**: `scripts/pn_guidance_test.py` icine `--altitude-guard`, `--safe-agl`, `--altitude-guard-gain`, `--altitude-thrust-boost` ve `--sink-speed-scale` parametreleri eklendi. Guard aktifken roket yere yaklasir veya asagi hizlanirsa komuta yukari bilesen eklenir.
> - **PN Test Thrust**: `scripts/pn_guidance_test.py` varsayilan thrust degeri `1400` yapildi ve PN testindeki thrust training araligina kilitlenmedi. Bu degisiklik PPO training action araligini degistirmez; sadece klasik fiziksel vurulabilirlik testi icindir.
> - **Log Parametreleri**: PN adim/ozet CSV'lerine `altitude_guard_weight`, `rocket_vy`, `altitude_guard`, `safe_agl`, `altitude_guard_gain` ve `altitude_thrust_boost` alanlari eklendi.
> - **README / VERSION / Plan**: Aktif takip surumu `v11.0.2` olarak guncellendi; README ve `docs/v11_experiment_plan.md` yeni Unity action/irtifa guvenligi notlarini icerir.

> ## v11.0.3 - Altitude Guard Yumusatma
>
> - **Deney Sonucu**: V11.0.2 guarded 300m testinde `0/5` success goruldu ve tum episode'lar `high_altitude` ile bitti. Guard kalkista AGL dusuk oldugu icin ilk adimdan itibaren `altitude_guard_weight≈1.49` uretip thrust'i `~3584N` seviyesine cikardi.
> - **Kok Neden**: Guard mantigi sadece "AGL dusuk" bilgisini yeterli sayiyordu. Roket zaten yukari hizlanirken bile ekstra yukari komut ve thrust boost verdi; bu da low-alt problemini high-alt problemine cevirdi.
> - **Guard Fix**: `scripts/pn_guidance_test.py` icinde guard artik sadece roket asagi hizlaniyorsa veya `altitude_guard_grace` sonrasi `critical_agl` altindaysa devreye girer. Kalkista yukselirken ekstra yukari komut verilmez.
> - **Parametreler**: PN test thrust varsayilani `1400 -> 1200`, `altitude_guard_gain=0.85`, `altitude_thrust_boost=300`, `critical_agl=10`, `altitude_guard_grace=80` olarak ayarlandi.
> - **Terminal Override**: `--terminal-max-altitude` eklendi. Bu opsiyon sadece PN saglik testinde `env.phase["max_altitude"]` degerini gecici esnetir; training faz ayarini kalici degistirmez.
> - **Log Parametreleri**: PN CSV alanlarina `critical_agl`, `altitude_guard_grace` ve `terminal_max_altitude` eklendi.
> - **README / VERSION / Plan**: Aktif takip surumu `v11.0.3` olarak guncellendi; README ve `docs/v11_experiment_plan.md` guard yumusatma notlarini icerir.

> ## v11.0.4 - Unity Action Axis Audit
>
> - **Deney Karari**: V11.0.3 PN/pursuit denemesinde roket hedefe yaklastiktan sonra drift/orbit davranisi gosterdi. Bu nedenle yeni adim PN parametresi kurcalamak degil, Unity action eksenlerini tek tek olcmektir.
> - **Yeni Script**: `scripts/action_axis_test.py` eklendi. Script `thrust_only`, `clock_12`, `clock_6`, `clock_3`, `clock_9` sabit komutlarini uygular ve her kanal icin olculen burun donus isaretini CSV'ye yazar.
> - **Beklenen Isaretler**: `clock_12` icin `rocket_turn_clock_signed_x > 0`, `clock_6` icin `< 0`, `clock_3` icin `rocket_turn_clock_signed_y > 0`, `clock_9` icin `< 0` beklenir. Isaret ters veya cok zayifsa sorun reward degil, action/fizik mapping tarafindadir.
> - **Telemetry Genisletme**: `Env.cs` ve `scripts/env.py` icine `thrust_world`, `desired_clock_turn_world`, `command_turn_world/local`, `torque_command_world/local`, `action_clock12_raw/net`, `action_clock3_raw/net`, `low_altitude_turn_scale`, `clock12_scale`, `clock3_scale`, `beta_validity_applied` ve rocketPoint/body eksen dot alanlari eklendi.
> - **Scene Debug Rays**: `Env.cs` icinde `drawActionAuditRays` ve `actionAuditRayLength` eklendi. Scene view'da cyan burun/itki, yesil clock-12, sari clock-3, beyaz hedef, magenta istenen donus ve kirmizi tork ray'i cizilir.
> - **Scene Sync**: `SampleScene.unity` icindeki Env component'e `drawActionAuditRays=1`, `actionAuditRayLength=12` yazildi. Unity Inspector degerleri script varsayilanini ezmesin diye sahne de senkron tutuldu.
> - **Takip Surumu**: `VERSION` ve README aktif surumu `v11.0.4` olacak sekilde guncellendi. Bu audit temiz gecmeden PN baseline, pretraining veya reward shaping asamasina gecilmeyecek.

> ## v11.0.5 - Roll Kontrol Onceligi Duzeltmesi
>
> - **Audit Bulgusu**: Ilk `action_axis_test.py` kosusunda `clock_6`, `clock_3` ve `clock_9` beklenen isarette tepki verdi; ancak `clock_12` yukari toparlama kanali beklenen pozitif burun donusunu net uretmedi. Ayni kosuda aktif steering sirasinda roll torku `torque_local_z≈±34` seviyesine kadar saturasyona gitti.
> - **Kok Neden Yorumu**: Roll stabilizer tamamen yanlis degil, fakat pitch/yaw manevra komutu verilirken roll duzeltmesi fazla baskin kaliyordu. Bu durum ozellikle dik kalkis/clock frame gecisinde steering komutunu sulandirip drift davranisini buyutebilir.
> - **Unity Degisikligi**: `Env.cs` icinde roll duzeltmesine iki olcek eklendi: `activeSteeringRollScale=0.35` ve `rollValidityFloor=0.15`. Manevra komutu buyudukce ve clock frame dik konumdayken roll duzeltmesi ikincil hale gelir.
> - **Scene Sync**: `SampleScene.unity` icindeki Env component'e `activeSteeringRollScale: 0.35` ve `rollValidityFloor: 0.15` eklendi.
> - **Telemetry**: `roll_control_scale` ve `roll_correction_cmd` alanlari `Env.cs`, `scripts/env.py` ve `scripts/action_axis_test.py` tarafina eklendi. Boylece sonraki axis audit'te roll baskisinin ne kadar kisildigi sayisal gorulecek.
> - **Beklenen Etki**: Roll baskisi tamamen yumusatilmadi; sadece aktif pitch/yaw komutu sirasinda direksiyonun onune gecmesi engellendi. Sonraki zorunlu test tekrar `action_axis_test.py` kosusudur.

> ## v11.0.6 - Aşamali Clock-12 Audit
>
> - **Audit Bulgusu**: V11.0.5 axis tekrarinda roll baskisi ortalamada azaldi (`roll_control_scale` yaklasik `0.05-0.16` bandina indi), fakat saf `clock_12` komutu hala beklenen pozitif burun donusunu uretmedi.
> - **Geometri Yorumu**: Roket dik kalkista `rocketPoint.forward` ile gravity-up neredeyse ayni hatta oldugu icin `clock_12` yonu tekillesiyor. Bu durumda "daha yukari don" komutu fiziksel/koordinatsal olarak belirsiz kalabilir.
> - **Script Degisikligi**: `scripts/action_axis_test.py` icine `clock_12_after_clock_6` staged komutu eklendi. Bu test once `60` step `clock_6` uygular, roketi gravity-up ekseninden ayirir, sonra `clock_12` komutunun toparlama isaretini olcer.
> - **Default Test Seti**: Varsayilan `--commands` listesine `clock_12_after_clock_6` eklendi. Bundan sonraki axis audit hem saf dik kalkis hem de egildikten sonraki toparlama davranisini raporlayacak.
> - **Takip Surumu**: `VERSION` ve README `v11.0.6` olarak guncellendi. Bu test temiz cikmadan PN/autopilot baseline'a gecilmeyecek.

> ## v11.0.7 - Roll Saturation Clamp
>
> - **Audit Bulgusu**: V11.0.6 axis tekrarinda `clock_12_after_clock_6` isaret olarak temiz cikti (`sign_ok=1`, mean turn12 pozitif). Ancak kullanici gozlemi ve loglar bazi kanallarda asiri roll oldugunu dogruladi: `clock_12/3/9` kosularinda anlik roll rate `~3.9 rad/s`, `torque_local_z` ise yer yer `±34` saturasyonuna cikti.
> - **Kok Neden**: Roll correction sinyali V11.0.5'te olceklenmis olsa da son clamp hala tam `maxRollCorrection=5.25` ile yapiliyordu. Bu nedenle buyuk roll error/damping anlarinda kucuk olcek bile tam z-tork limitine vurabiliyordu.
> - **Unity Degisikligi**: `Env.cs` icinde roll correction artik iki asamada sinirlanir: once steering/validity ile olceklenir, sonra aktif steering sirasinda dinamik `rollCorrectionLimit` ile clamp edilir.
> - **Telemetry**: `roll_correction_limit` alanlari `Env.cs`, `scripts/env.py` ve `scripts/action_axis_test.py` tarafina eklendi. Sonraki testte roll sinyalinin hangi limite carpildigi CSV'den gorulecek.
> - **Takip Surumu**: `VERSION` ve README `v11.0.7` olarak guncellendi. Beklenen etki roll'u tamamen serbest birakmadan, aktif pitch/yaw manevrasinda buyuk roll tork darbelerini engellemektir.

> ## v11.0.8 - Fiziksel Roll Tork Limiti
>
> - **Audit Bulgusu**: V11.0.7 axis tekrarinda kalkis aninda hala asiri roll goruldu. Loglar `clock_3/clock_9` ilk 20 step icinde `measured_roll_rate≈3.9 rad/s` ve `torque_local_z≈±23.9` seviyelerini gosterdi.
> - **Kok Neden**: V11.0.7'de roll correction command seviyesi sinirlandi; fakat fizik motoruna gitmeden once `rollTorqueScale=3.6` ve `torqueScale=1.8` carpanlari uygulaninca z-tork tekrar buyudu.
> - **Unity Degisikligi**: `Env.cs` icinde `maxRollTorqueCommand=3.0` eklendi. `AddRelativeTorque` oncesinde son `scaledTorqueCommand.z` bu aralikta clamp edilir; x/y pitch-yaw torklari aynen kalir.
> - **Scene Sync**: `SampleScene.unity` Env component'e `maxRollTorqueCommand: 3` eklendi.
> - **Telemetry**: `roll_torque_limit` alanlari `Env.cs`, `scripts/env.py` ve `scripts/action_axis_test.py` tarafina eklendi.
> - **Takip Surumu**: `VERSION` ve README `v11.0.8` olarak guncellendi. Beklenen etki kalkis anindaki buyuk roll impulse'larini azaltmak, fakat roll baskisini tamamen kapatmamaktir.

> ## v11.0.9 - Roll Rate Projection
>
> - **Audit Karari**: V11.0.8 sonrasi `torque_local_z` `±3` bandinda sinirlandi, fakat roketin roll inertia'si pitch/yaw inertia'sina gore yaklasik `13.3x` dusuk oldugu icin kalkis roll'u hala gorulebildi.
> - **Tasarim Karari**: Bu projede roket roll kontrolu ogrenmeyecek; roll-free varsayimi sim tarafinda garanti edilecek. Bu, onceki tasarim tartismalarinda "roket roll yapmiyor" kabulune daha uygundur.
> - **Unity Degisikligi**: `Env.cs` icine `suppressRollRate=true` ve `rollRateSuppressBlend=1.0` eklendi. Her `Physics.Simulate()` sonrasi `rocketPoint.forward` ekseni etrafindaki angular velocity bileseni projekte edilip temizlenir.
> - **Roll Torque Degisikligi**: Projection aktifken roll stabilizer z-torku sifirlanir. Pitch/yaw torklari korunur; sadece forward ekseni etrafindaki roll rate temizlenir.
> - **Scene Sync**: `SampleScene.unity` Env component'e `suppressRollRate: 1` ve `rollRateSuppressBlend: 1` eklendi.
> - **Telemetry**: `suppressed_roll_rate` alanlari `Env.cs`, `scripts/env.py` ve `scripts/action_axis_test.py` tarafina eklendi. Axis summary artik `mean_suppressed_roll_rate` raporlar.
> - **Takip Surumu**: `VERSION` ve README `v11.0.9` olarak guncellendi. Beklenen test sonucu `clock_3/clock_9` kalkisinda roll rate'in sifira yakin kalmasidir.

> ## v11.0.10 - Clock Turn-Rate Controller
>
> - **Audit Bulgusu**: `pn_roll_fixed_blend_audit_v1109.csv` logunda PN action ile Unity net action ayni zincirde ilerledi, fakat yakin mesafede mevcut acisal hiz komutu ezdi. `dist<50m` penceresinde burun donus yonu hedef clock yonune karsi calisti; bu durum clock isaretinin tamamen ters olmasindan cok acik cevrim tork uygulamasinin gec kalmasina isaret etti.
> - **Unity Degisikligi**: `Env.cs` icinde clock action uygulamasi acik cevrim torktan kapali cevrim burun donus hizi kontrolune cevrildi. Action artik "su yone tork bas" degil, "burnu su clock yonunde donder" istegi gibi yorumlanir.
> - **Yeni Parametreler**: `clockTurnRateTarget=1.8`, `clockTurnRateControllerGain=1.15`, `maxPitchYawTorqueCommand=3.2` eklendi. Bu degerler yakin geciste eski acisal momentumun hedef yonunu ezmesini azaltmak icin secildi.
> - **Scene Sync**: `SampleScene.unity` Env component'e yeni turn-rate controller parametreleri yazildi; Unity Inspector script default degerlerini ezmeyecek.
> - **Beklenen Etki**: PN/pursuit testinde `theta_at_min_distance` degeri dusmeli ve `dist<50m` penceresinde `rocket_turn_clock_signed` ile target clock yonu arasindaki uyum pozitife donmelidir. Bu test temizlenmeden reward/PPO tuning'e gecilmeyecek.

> ## v11.0.11 - Clock Singularity Fallback
>
> - **Audit Bulgusu**: V11.0.10 PN testinde roket hedefi kovalar gibi davrandi ve `5.7m` / `8.7m` yakin gecisler goruldu, fakat en yakin anda theta `125-132deg` seviyesine cikti. Action uygulamasi iyilesse de roketin tam dik kalkis bolgesinde clock-12 yonu hala zayif tanimliydi.
> - **Clock Koku**: Roket forward ekseni gravity-up ile paralelken gravity tabanli `clock_12` matematiksel olarak tanimsizdir. Eski fallback `rocketPoint.up` kullaniyordu; bu da silindirik roketin roll/govde yan eksenine bagli keyfi bir saat yonu uretir.
> - **Unity Degisikligi**: `Env.cs` icindeki `BuildClockFrame()` fallback'i degistirildi. Gravity projection sifirken `clock_12` once hedef bearing'inden, bu yoksa cached guidance yonunden kurulur. Boylece dik kalkista keyfi govde ekseni yerine hedefe gore kararlı bir clock baslangici secilir.
> - **Beklenen Etki**: Saf `clock_12` axis testi artik dik kalkista daha anlamli bir yonde tepki vermeli; PN/pursuit testinde ilk yon secimi daha az rastgele olmali. Bu degisiklik clock mimarisini atmadan onceki son temel saglamlastirma adimidir.

> ## v11.0.12 - PN Lead Sign Isolation
>
> - **Audit Bulgusu**: V11.0.11 pursuit testi clock/action zincirinin duzeldigini gosterdi: `dist<50m` penceresinde action-target ve turn-target uyumu neredeyse `1.0` oldu. Ancak pursuit hedefi arkadan kovalamaya dusup `23-25m` bandinda kaldi.
> - **Blend Bulgusu**: V11.0.11 blend testi `10.38m`, `12.97m`, `19.53m` yakin gecisler uretti; fakat yakinlasma aninda PN/lead komutu hedef clock yonunun tersine calistigi icin theta `56-63deg` bandinda kaldi.
> - **Script Degisikligi**: `scripts/pn_guidance_test.py` icine `--pn-sign` eklendi. Bu parametre sadece PN/lead bilesenini tersler; pursuit bileseni ve genel action sign ayni kalir.
> - **Beklenen Test**: `--pn-sign -1` ile blend testinde theta dusuyorsa problem clock mimarisi degil, PN lead isaretidir. Dusmuyorsa lead karisimi fazla baskindir veya action mimarisi hedef vektor tabanli yeni tasarima gecmelidir.

> ## v11.0.13 - Yakın Mesafe Pursuit Handover
>
> - **Audit Bulgusu**: `--pn-sign -1` testi kotu cikti. Min distance `66-71m`, theta `121-124deg` seviyesinde kaldi; yani PN/lead isaretini tamamen terslemek yanlis yoldur.
> - **Tasarim Karari**: Pozitif PN/lead uzakta hedefin onunu kesmeye yariyor, fakat yakin geciste fazla baskin kalip burun hizalamasini geciktiriyor. Bu nedenle lead'i tamamen terslemek yerine mesafeye bagli azaltmak daha mantikli.
> - **Script Degisikligi**: `scripts/pn_guidance_test.py` icine `--lead-fade-start` ve `--lead-fade-end` eklendi. Blend modunda distance `lead_fade_start` altina indikce PN/lead agirligi azalir, `lead_fade_end` altinda pursuit yani dogrudan hedefe bakma baskin kalir.
> - **Log Alanlari**: PN adim CSV'sine `lead_weight`; adim ve ozet CSV'lerine `lead_fade_start`, `lead_fade_end` eklendi. Boylece yakin geciste lead'in gercekten azaldigi logdan gorulebilir.
> - **Varsayilanlar**: `lead_fade_start=70m`, `lead_fade_end=25m`. Beklenen etki `10-20m` yakin geciste theta'nin `56-63deg` bandindan daha dusuk seviyeye inmesidir.

> ## v11.0.14 - Normalized Lead Blend
>
> - **Audit Bulgusu**: V11.0.13 ile min distance `3.33m`, `4.77m`, `9.13m` seviyesine indi; fakat en yakin anda theta `136-167deg` oldu. Handover yakinda lead'i sifirlasa da roket `40-70m` bandinda PN etkisiyle hedef clock yonunun tersine acisal hiz biriktirdi.
> - **Kok Neden**: Blend toplami `PN vektoru + pursuit vektoru` seklindeydi. PN vektoru ham buyukluk olarak pursuit unit vektorunden cok daha buyuk olabildigi icin `lead_weight` dusse bile pursuit komutunu ezebiliyordu.
> - **Script Degisikligi**: `scripts/pn_guidance_test.py` icinde PN/lead vektoru artik pursuit ile toplanmadan once normalize edilir. Blend artik iki yon vektoru arasinda yapilir; ham PN buyuklugu sadece debug amaciyla loglanir.
> - **Varsayilanlar**: `pursuit_blend=0.80`, `lead_fade_start=95m`, `lead_fade_end=45m` olarak guncellendi. Amac uzakta onleme bilgisini korumak, 45m altinda ise burnu hedefe kilitlemektir.
> - **Beklenen Etki**: `dist<50m` penceresinde `cos action-target` yukselmeli ve en yakin mesafede theta `136-167deg` gibi arkaya bakma degerlerinden belirgin sekilde dusmelidir.

> ## v11.0.15 - Pitch/Yaw Authority Baseline
>
> - **Audit Bulgusu**: V11.0.14, theta'yi `49-58deg` bandina indirdi fakat success alamadi. Loglarda action-target uyumu `dist<50m` icin `~0.999` oldu; yani komut dogru, fakat burun donus hizi hedefe yetisemedi. Pitch/yaw torku yakin gecis oncesinde limite vurdu.
> - **Karar**: Bu asamada reward veya PPO'ya gecmek yanlis olur. Klasik algoritma success alamiyorsa RL de ayni actuator limitine carpacaktir.
> - **Unity Degisikligi**: `Env.cs` icindeki pitch/yaw otoritesi artirildi: `clockTurnRateTarget=2.8`, `clockTurnRateControllerGain=1.8`, `maxPitchYawTorqueCommand=6.0`.
> - **Scene Sync**: `SampleScene.unity` Env component de ayni degerlerle senkronlandi.
> - **PN Test Ayari**: `scripts/pn_guidance_test.py` varsayilan thrust'i `700` yapildi. Bu, RL training thrust ust siniriyle ayni banda daha yakin bir klasik baseline verir.
> - **Beklenen Etki**: `dist<20m` penceresinde theta `50deg` civarindan success kosuluna yaklasmali. Eger PN hala success alamazsa bir sonraki karar clock action mimarisini degil, torque tabanli actuator modelini daha dogrudan hedef vektoru kontrolune cevirmektir.

> ## v11.0.16 - Acceleration PN Baseline
>
> - **Internet/Kaynak Bulgusu**: PN kaynaklari, oransal gudumun dogrudan "clock yonune don" komutu degil, LOS rate ve closing speed uzerinden yanal ivme komutu urettigini gosterdi. Bu ivme komutu normalde ayrica bir autopilot/flight-control katmani tarafindan takip edilir.
> - **Kok Neden Yorumu**: V11.0.15 torque otoritesi artinca roket daha oynak oldu, fakat success gelmedi. Loglarda min mesafe `15-17m` bandindan `25-34m` bandina kotulesti. Bu, eksigin sadece tork buyuklugu degil, PN ivme komutunu takip eden ara katman oldugunu gosterir.
> - **Script Degisikligi**: `scripts/pn_guidance_test.py` icine `--mode accel` eklendi. Bu mod `pn_lateral = N * closing_speed * LOS_rate` mantigini korur, PN ivmesini normalize edip kaybetmez.
> - **Fizik Limiti**: Yeni mod `rocket_mass=50`, `thrust=700`, `gravity_comp=0.95`, `max_up_comp_fraction=0.78`, `lateral_accel_fraction=0.85` parametreleriyle ulasilabilir ivme siniri hesaplar. Boylece PN komutu fiziksel olarak uygulanamayacak kadar buyurse sinirlanir.
> - **Lead / Pursuit Karisimi**: `intercept_speed_floor=45`, `accel_lead_weight=0.90`, `accel_pursuit_weight=0.45`, `accel_pn_weight=1.00` eklendi. Lead hedefin onunu kesmeye, pursuit ise yakin mesafede burnu hedefe kilitlemeye yardim eder.
> - **Log Alanlari**: PN CSV'lerine `pn_accel_limit`, `pn_limited_accel_mag`, `pn_accel_saturated`, `gross_accel`, `gravity_comp_accel`, `lead_t_go`, `lead_dir_dot_los`, `desired_accel_clock12`, `desired_accel_clock3` alanlari eklendi.
> - **README / VERSION**: Aktif takip surumu `v11.0.16` yapildi. Bu test basarili olmadan reward/PPO tuning'e geri donulmeyecek.

> ## v11.0.17 - Velocity Path Correction
>
> - **300m Deney Bulgusu**: `pn_accel_v11016_r280_300` ve lead agirlikli kosuda success gelmedi. En yakin mesafe `21-28m`, theta ise cogu episode'da `3-16deg` bandindaydi. Yani roket hedefe bakiyor, fakat hiz/trajectory hatti hedefin 20m disindan akip geciyordu.
> - **Kok Neden Yorumu**: Burnu hedefe cevirmek yeterli degil; PN'in pratikte basarmasi gereken sey hiz vektorunu da onleme hattina oturtmaktir. Mevcut accel modunda bu hiz-hatti hatasi dogrudan cezalandirilmiyordu.
> - **Script Degisikligi**: `scripts/pn_guidance_test.py --mode accel` icine velocity tracking eklendi. `desired_velocity = lead_dir * command_speed` hesaplanir, mevcut `rocket_vel` ile farki ivme istegine cevrilir.
> - **Yeni Parametreler**: `velocity_track_gain=0.25`, `velocity_accel_fraction=0.65`, `loft_weight=0.20`, `loft_agl=45`, `loft_fade_start=260`, `loft_fade_end=120`.
> - **Loft Mantigi**: Uzak menzilde ve roket AGL hedefinin altindayken hafif yukari bias eklenir. Amac roketin 300m senaryoda cok erken yatip irtifa kaybetmesini azaltmaktir.
> - **Log Alanlari**: PN CSV'lerine `velocity_error_mag`, `velocity_correction_mag`, `velocity_correction_saturated`, `loft_factor`, `loft_accel_mag` eklendi. Boylece 300m testinde miss sebebi artik hiz hatti ve loft tarafindan da okunabilir.
> - **Max Step Fix**: PN testinde `--max-steps` artik sadece script loop'unu degil, `env.phase["max_step"]` ve `env.max_step` degerlerini de gunceller. Onceki 300m testinde komut 1000 olsa bile env tarafinda timeout 700 stepte bitiyordu.
> - **README / VERSION**: Aktif takip surumu `v11.0.17` yapildi. Beklenen etki 300m testinde `min_distance` degerini `21-28m` bandindan success threshold'a yaklastirmaktir.

> ## v11.0.18 - Direct Guidance Baseline
>
> - **Karar**: Klasik accel PN 300m testinde hala hedefi kacirinca, clock/torque action zinciri bypass edilerek dogrudan dunya ivmesi baseline'i eklendi. Bu RL icin nihai action degil; sadece sahnenin hedefi kesin vurabildigini gosteren referans testtir.
> - **Unity Degisikligi**: `Env.cs` icine direct action paketi eklendi. Paket formati `[-7777, accel_x, accel_y, accel_z, look_x, look_y, look_z]`. `-7777` marker'i gorulunce Unity normal `thrust/clock` yolunu kullanmaz, `ForceMode.Acceleration` ile dunya ivmesini uygular.
> - **Roll/Debug Duzeltmesi**: Direct mode'da `rocketPoint.forward` hedef yonune kilitlenir ve `directZeroAngularVelocity=true` ile kafa karistiran roll/donus artefaktlari sifirlanir. Scene view'da direct mode icin yesil/sari clock eksenleri cizilmez; sadece cyan burun, beyaz hedef, magenta look ve kirmizi ivme cizilir.
> - **Python Degisikligi**: `scripts/env.py` icindeki `step_direct_action()` artik 7 elemanli direct action paketini kesmeden Unity'ye yollar. Reward/action cezasi icin bu paket sahte clock action gibi yorumlanmaz.
> - **PN Test Degisikligi**: `scripts/pn_guidance_test.py --mode direct` eklendi. Python `t_go` hesaplar, `rocket_accel = 2*(rel_pos + rel_vel*t_go)/t_go^2` denklemiyle gereken ivmeyi bulur, gravity compensation uygular ve ivmeyi `direct_max_accel=90` ile sinirlar.
> - **Yeni Parametreler**: `direct_speed=85`, `direct_close_speed=65`, `direct_close_distance=90`, `direct_min_tgo=0.35`, `direct_max_tgo=7.5`, `direct_max_accel=90`, `direct_velocity_damping=0.0`.
> - **Beklenen Etki**: 280-300m testte success gorulmeli. Bu test basarili olup clock/torque PN basarisiz kalirsa sorun reward degil, mevcut action uygulama mimarisinin fazla dolayli ve zor ogrenilir olmasidir.

# v12.0 sürüm ailesi

> ## v12.0.0 - RL Direct Acceleration Architecture
>
> - **Mimari Karar**: V11 direct baseline hedefi vurdu. Bu nedenle RL tarafinda eski `thrust + discrete clock direction` action mimarisi birakildi ve `direct_accel` mimarisine gecildi.
> - **Action Seti**: `scripts/env.py` icinde `ACTION_KEYS = ["accel_right", "accel_up", "accel_forward"]`. Ajan 3 continuous action uretir; her biri `[-1, 1]` araligindadir.
> - **Unity Packet**: Python action'i guidance frame'den dunya ivmesine cevirir ve Unity'ye `[-7777, accel_x, accel_y, accel_z, look_x, look_y, look_z]` paketi yollar. `-7777` marker'i Unity tarafinda direct mode'u acar.
> - **State Seti**: Clock agirlikli state yerine sade direct state kullanilir: distance, hedef yonu, relative velocity, rocket velocity, closing speed, theta, AGL, altitude error, target speed ve rocket speed. Toplam state boyutu `16`.
> - **Agent Degisikligi**: `scripts/agent.py` artik categorical direction head kullanmaz. Tek actor head `action_mu` ile 3 continuous action uretir; `log_std` boyutu da action sayisi kadardir.
> - **Reward Sadelestirme**: Aktif faz `v12_0_0_phase_1_direct_accel_140_160` oldu. Clock action alignment, wrong channel, coactivation, turn-toward ve roll/angle karmaşasi sifirlandi. Ana sinyal distance progress, closing speed, success terminal ve sade altitude guvenligidir.
> - **Checkpoint Ayrimi**: `scripts/settings.py` model prefix'i `ppo_v12_direct_model`, state prefix'i `ppo_v12_direct_state` oldu. Eski V10/V11 checkpoint'leri action boyutu degistigi icin otomatik yuklenmez.
> - **Console Log**: `scripts/log.py` direct mode'da eski thrust/clock action yerine `Acc: [x, y, z]` dunya ivmesini yazar. Boylece train sirasinda ajanin ne tarafa ivme verdigi okunabilir.
> - **Sade Kod Notu**: Eski PN/clock test kodlari silinmedi; karsilastirma ve raporlama icin korunur. Training yolu ise artik direct acceleration mimarisini kullanir.

> ## v12.0.1 - Direct Launch Safety and Roll-Free Look Fix
>
> - **Kok Neden**: Ilk V12 run loglarinda `episode 1-4` cok erken `collision`, `episode 5` ise `low_agl` oldu. AGL baslangici `~0.40m` oldugu icin rastgele PPO action'i yerdeyken yana/asagi ivme uretip roketi rampadan kopariyordu. Ayrica `reset()` sonrasi ilk telemetry `last_raw_state` icine yazilmadigi icin ilk action hedef frame'i yerine fallback dunya eksenleriyle hesaplanabiliyordu.
> - **Python Duzeltmesi**: `scripts/env.py` icinde resetten sonra `last_raw_state` saklanir. `DIRECT_ACTION_MAX_ACCEL` `90 -> 65` yapildi. Kalkis filtresi eklendi: AGL `8m` altinda veya ilk `80` stepte minimum yukari ivme, kucuk ileri bias ve yanal ivme limiti uygulanir. Bu filtre hedefe gitmeyi cozmez; sadece rastgele ilk action'in yerde ani carpismaya donusmesini engeller.
> - **Unity Duzeltmesi**: `Env.cs` direct look rotasyonu artik sadece `FromToRotation` ile burun hizalamaz. Gravity-up referansli `LookRotation` kullanilir; boylece direct mode'da govde roll'u keyfi kalmaz. Reset aninda direct action cache'i ve roket rigidbody poz/rot degerleri de temizlenir.
> - **Console / Log Duzeltmesi**: `scripts/log.py` episode final satirlarinda onceki renkli terminal mantigi korunur. Step ve reset satirlari bilerek renksiz birakildi. Reset satiri artik `Target Pos` yaninda `Rocket Pos` da yazar; boylece konsoldaki target reset konumu roket rampadan ayrildi sanilmaz. `clock_validity` duplicate CSV header'i kaldirildi.
> - **Beklenen Etki**: V12.0.1 ile roket kalkista yerde takla/yan carpma yapmamali, Scene view'daki direct look cizgileri roll gibi yorumlanacak sekilde donmemeli ve ilk episode'lar en azindan fiziksel olarak okunabilir hale gelmelidir.

# v13.0 sürüm ailesi

> ## v13.0.0 - Teacher-Guided Warm Start
>
> - **Mimari Karar**: Uzman onerisine gore random PPO ile devam etmek yerine once direct guidance controller ogretmen yapildi. V11 direct test hedefi vurdugu icin bu controller artik veri toplama kaynagi olarak kullanilir.
> - **Yeni Moduller**: `scripts/teacher_policy.py` eklendi. Bu dosya direct guidance formulu ile 3 boyutlu RL action'i uretir: `accel_right`, `accel_up`, `accel_forward`.
> - **Veri Toplama**: `scripts/teacher_collect.py` eklendi. Unity Play moddayken episode kosar, basarili episode'lardan state/action ciftleri toplar ve `teacher_data/v13_teacher_direct_140_160.npz` dosyasina yazar.
> - **Pretrain**: `scripts/teacher_pretrain.py` eklendi. PPO actor agini ogretmen action'larini taklit edecek sekilde behavior cloning ile egitir ve `models/ppo_v13_teacher_direct_model_up0.keras` checkpoint'ini olusturur.
> - **Training Guvenligi**: `scripts/train.py`, V13 teacher checkpoint yoksa baslamaz. Boylece model tekrar sifirdan random action ile yerde surunme/roll pattern'i uretmez.
> - **Settings**: `MODEL_PREFIX` `ppo_v13_teacher_direct_model`, `STATE_PREFIX` `ppo_v13_teacher_direct_state` oldu. Teacher data runtime cikti oldugu icin `.gitignore` icine `/teacher_data/` eklendi.
> - **Dokumantasyon**: `docs/v13_expert_plan.md` eklendi. V13 komut sirasini ve basari kriterini aciklar.

# v14.0 sürüm ailesi

> ## v14.0.0 - SAC Off-Policy Direct Acceleration Trial
>
> - **Deney Karari**: V13 kisa PPO fine-tune loglarinda policy `forward≈1.0` ve pozitif `up` kanalina coktu. Roket hedefe baksa bile mesafe buyuyup `high_altitude` terminali baskin geldi. Bu nedenle ayni direct acceleration action uzayinda PPO yerine SAC denenecek.
> - **Yeni Agent**: `scripts/sac_agent.py` eklendi. Dosya replay buffer, SAC actor, iki critic, target critic, otomatik entropy katsayisi ve checkpoint save/load mantigini icerir.
> - **Yeni Train Loop**: `scripts/train_sac.py` eklendi. Bu dongu PPO rollout yerine replay buffer kullanir; ilk adimlarda teacher action'larini kucuk noise ile buffer'a koyar, sonra SAC policy action uretir.
> - **Teacher Warm-Start**: SAC checkpoint yoksa actor, `teacher_data/v13_teacher_direct_140_160.npz` dosyasindan kisa behavior cloning ile isinir. Bu, random direct acceleration'in roketi kalkista bozmasini azaltmak icindir.
> - **Checkpoint Ayrimi**: SAC checkpoint'leri PPO'dan ayri tutulur: `sac_v14_direct_actor_step*.keras`, `sac_v14_direct_q1_step*.keras`, `sac_v14_direct_q2_step*.keras`.
> - **Parametreler**: `SAC_REPLAY_SIZE=200000`, `SAC_BATCH_SIZE=256`, `SAC_REWARD_SCALE=0.02`, `SAC_INITIAL_ALPHA=0.20`, `SAC_ACTOR_LR=3e-5`, `SAC_CRITIC_LR=1e-4`, `SAC_TEACHER_WARMUP_STEPS=2500`, `SAC_TEACHER_NOISE=0.025`.
> - **Dokumantasyon**: `docs/v14_sac_plan.md` eklendi. Bu dosya SAC denemesinin amacini, komut akisini ve ilk loglarda hangi sinyallere bakilacagini aciklar.

# v15.0 sürüm ailesi

> ## v15.0.0 - SAC-Only Scratch Training
>
> - **Mimari Karar**: Aktif egitim hatti sadece SAC olacak sekilde sadeleştirildi. PPO agent, PPO train loop, teacher collect ve pretrain dosyalari aktif koddan kaldirildi.
> - **Train Komutu**: `scripts/train.py` artik dogrudan SAC training dongusudur. Ayri `train_sac.py` dosyasi kaldirildi.
> - **Pretrain Karari**: SAC icin teacher warm-start, behavior cloning ve teacher replay warmup kullanilmiyor. Ajan sifirdan baslar ve ilk step'ten itibaren kendi stochastic SAC actor'u ile action uretir.
> - **Checkpoint Ayrimi**: Aktif checkpoint prefix'i `sac_v15_direct_scratch` oldu. Boylece onceki PPO/V13/V14 modelleri otomatik yuklenmez.
> - **Settings Sadelestirme**: `settings.py` icinden PPO model prefix/state prefix, PPO checkpoint yardimcilari ve teacher/pretrain parametreleri cikarildi.
> - **Test Komutu**: `scripts/test.py` SAC actor checkpoint'i yukleyecek sekilde guncellendi.
> - **Dokumantasyon**: `docs/v15_sac_only_plan.md` eklendi. Ilk train loglarinda izlenecek action/entropy/terminal sinyalleri not edildi.
>

> ## v15.0.1 - SAC Runtime Responsiveness and Ground-Skim Terminal
>
> - **FPS Kok Neden**: SAC ilk update'i `1024` stepte basliyor ve her stepte gradient update deniyordu. Unity fizik adimi Python step'ini bekledigi icin bu, Play mode'da agir FPS/donma hissi uretti.
> - **SAC Hafifletme**: `SAC_START_TRAINING_STEPS=4096`, `SAC_TRAIN_EVERY_STEPS=8`, `SAC_BATCH_SIZE=128`, `SAC_HIDDEN_UNITS=128` yapildi. Replay buffer yine kullanilir, fakat training her Unity step'ini bloke etmez.
> - **Ground-Skim Kok Neden**: Loglarda roket yerde surunurken `AGL` `0.20-0.45m` bandinda kaldi, `grounded_flag=0` geldi ve eski `min_agl=0.18` terminali kacirdi.
> - **Terminal Duzeltmesi**: Aktif fazda `min_agl=0.60`, `low_agl_grace_steps=80` yapildi. Roket kalkistan sonra yerde surunurse episode erken `low_agl` ile biter.
>

> ## v15.0.2 - SAC Live Plot Report Tooling
>
> - **Yeni Grafik Scripti**: `scripts/plot_sac_report.py` eklendi. Bu script SAC/V15 loglarini training devam ederken okuyup PNG raporlari uretir.
> - **Standart Grafikler**: `summary`, `success_rug`, `reset_radius_phase_plan`, `reset_map`, `action_diagnostics` ve `hit_positions` grafikleri tek komutla uretilir.
> - **Canli Log Guvenligi**: `step_log.csv` buyuk oldugu icin chunk/stride ile okunur; training ayni anda CSV yazarken olusabilecek yarim satirlar atlanir.
> - **Okunabilir Faz Plani**: Radius grafiğinde outcome renkleri, success rate cizgisi, faz/surum bandi, `n` ve `S%` etiketleri standart hale getirildi.
>

> ## v15.0.3 - Forward-Aligned Direct SAC Action and Exhaust Fix
>
> - **Kok Neden**: Canli loglarda roket hizinin burun yonundeki bileseni satirlarin yaklasik `%48`inde negatife dustu. Bu, V15 direct acceleration action'inin roket govdesinden bagimsiz dunya ivmesi uyguladigini gosterdi.
> - **Action Duzeltmesi**: `scripts/env.py` icinde SAC action semantigi degistirildi. `action[0]` ve `action[1]` hedef bakisina sag/yukari aim offset ekler; `action[2]` yalnizca pozitif ileri ivme buyuklugu secer.
> - **Fiziksel Kisit**: Unity'ye giden direct accel artik hedefe bakan `look_dir` boyunca pozitif ivme olarak hesaplanir. Boylece roket burnu baska yere bakarken yan/geri ivme uygulanmaz.
> - **Kalkis Guvenligi**: Eski serbest `min_up/min_forward/side_limit` filtresi yerine kalkis boyunca hedef bakis yonune yumusak gravity-up bias eklenir.
> - **Egzoz Duzeltmesi**: `Env.cs` icinde rocket exhaust her step `rocketPoint` arkasina ve `-rocketPoint.forward` yonune hizalanir. Particle simulation space world yapilarak eski dumanin roketle birlikte yapay sekilde donmesi engellenir.
> - **Checkpoint Ayrimi**: Action anlami degistigi icin model prefix'i `sac_v15_forward_aligned`, aktif faz adi `v15_0_3_phase_1_sac_forward_aligned_140_160` yapildi. Eski V15 direct-scratch checkpoint'leri bu run'a otomatik yuklenmez.
>

> ## v15.0.4 - Unity Responsiveness and Side-Slip Damping
>
> - **Donma Teshisi**: `update_log.csv` incelendiginde `4096` step sonrasi SAC gradient update baslayinca 250 step suresi belirgin sekilde uzadi. Unity fizik adimi Python'u bekledigi icin Play mode donuyormus gibi gorundu.
> - **SAC Hafifletme**: `SAC_START_TRAINING_STEPS=12000`, `SAC_TRAIN_EVERY_STEPS=32`, `SAC_BATCH_SIZE=64`, `SAC_HIDDEN_UNITS=96`, `SAC_LOG_EVERY_STEPS=500` yapildi. Ilk gozlem safhasi daha akici kalir, update bloklari daha seyrek calisir.
> - **Hiz Sondurme**: `Env.cs` direct mode icine `DampenDirectSideSlip()` eklendi. Roket burnu hedefe donse bile onceki hiz nedeniyle yan/geri kayma suruyordu; yan hiz yumusak azaltildi, geri hiz daha sert sonduruldu.
> - **Aim Limit**: `DIRECT_ACTION_AIM_OFFSET=0.35` yapildi. Ajan hedef bakisindan tamamen kopamaz; ilk random SAC action'lari akrobatik/yanlayarak ucus uretmemelidir.
> - **Yeni Prefix/Faz**: Action ve runtime davranisi degistigi icin checkpoint prefix'i `sac_v15_forward_damped`, faz adi `v15_0_4_phase_1_sac_forward_damped_140_160` oldu.

# v15.1 sürüm ailesi

> ## v15.1.2 - SAC Guidance Acceleration Handoff
>
> - **Aktif algoritma**: PPO ve teacher/pretrain akışları aktif runtime'dan çıkarıldı; güncel eğitim hattı SAC (Soft Actor-Critic / yumuşak aktör-eleştirmen) üzerinde çalışıyor.
> - **Kontrol modu**: Ajan artık `guidance_accel` modunda 3 continuous action üretir. Python bu değerleri hedef doğrultusuna bağlı sağ/yukarı/ileri ivme komutlarına çevirir; Unity bu ivmeyi uygular ve görsel gövdeyi hareket yönüne hizalar.
> - **Deney ayarı**: Aktif faz `v15_1_2_phase_1_sac_guidance_accel_launch_guard_target500_y100`; hedef yüksekliği `100`, spawn radius `500`, maksimum episode uzunluğu `800` step.
> - **Son gözlem**: 350 episode ve 165500 update sonunda success yoktur. Çarpışma problemi giderilmiş görünür; roket daha uzun uçmaktadır. Ancak son episode'larda hedefe yaklaşma davranışı terminal başarıya dönüşmemiş, roket çoğunlukla hedefi geçip ters hizalanma ile `low_agl` bitirmiştir.
> - **Repo temizliği**: Unity/IDE tarafından üretilen `.csproj`, `.sln`, `.slnx`, `.vscode` dosyaları ve root runtime logları artık git dışında tutulur. Ham runtime logları yerel analiz için korunabilir, fakat repo'ya commit edilmez.
> - **Handoff amacı**: README, projeyi dışarıdan okuyacak bir uzmana mevcut mimariyi, geçmiş kararları, güncel başarısızlık modunu ve önerilen sonraki inceleme başlıklarını anlatacak şekilde güncellendi.

> ## v15.1.3 - Simple Reward Reset
>
> - **Uzman Geri Bildirimi**: Mevcut reward tasarımında reward hacking riski olduğu değerlendirildi. Bu nedenle eski çok parçalı dense reward bileşenleri sıfırlandı.
> - **Yeni Reward Çekirdeği**: Aktif reward artık sadece küçük step penalty, mesafe ilerlemesi, hedefe hizalanma, pozitif closing speed ve terminal ödül/ceza bileşenlerinden oluşur.
> - **Kaldırılan Bileşenler**: Yakın başarı bonusları, roll/angular cezaları, thrust gate cezaları, clock action alignment reward'ları, düşük irtifa kaçış bonusları ve çok parçalı açı shaping terimleri aktif runtime'dan çıkarıldı.
> - **Yeni Prefix/Faz**: Eski reward ile eğitilmiş checkpoint'ler otomatik yüklenmesin diye model prefix'i `sac_v15_1_3_simple_reward_target500_y100`, faz adı `v15_1_3_phase_1_sac_simple_reward_target500_y100` yapıldı.
> - **Deney Amacı**: Bu sürüm başarı iddiası taşımaz; amaç SAC öğrenmesini en sade hedefe yönelme ve hedefe yaklaşma sinyaliyle yeniden başlatıp logları daha okunur hale getirmektir.

> ## v15.1.4 - 90 Degree Angle Terminal
>
> - **Log Gözlemi**: v15.1.3 loglarında hedefe yaklaşma ve closing reward doğru çalışsa da, roket hedefin yanından geçerken `theta` açısı 90 derecenin üstüne çıktıktan sonra hâlâ episode içinde kalabiliyordu.
> - **Yeni Terminal Kuralı**: `theta_deg > 90.0` olduğunda episode artık `bad_angle` sebebiyle biter ve `bad_angle_penalty=-50` terminal cezası alır.
> - **Amaç**: Ajanın hedefi geçip kaçma davranışını replay buffer içinde uzun süre toplamaması; kötü açıya giren geçişlerin erken, net ve okunur şekilde cezalandırılması.
> - **Yeni Prefix/Faz**: Terminal koşulu değiştiği için model prefix'i `sac_v15_1_4_angle90_terminal_target500_y100`, faz adı `v15_1_4_phase_1_sac_angle90_terminal_target500_y100` yapıldı.

> ## v15.1.5 - Direct Target-Look Action Reset
>
> - **Action Bulgusu**: `guidance_accel` modunda ajan sadece guidance frame içinde ivme seçiyordu; Unity ise roket burnunu komut edilen yöne değil, çoğunlukla mevcut hız yönüne hizalıyordu. Bu yüzden roket ateşlendikten sonra yan yatıp düşebiliyor ve ajan gerçek bir burun/nişan kontrolü öğrenemiyordu.
> - **Kontrol Modu Değişikliği**: Aktif runtime `direct_accel` moduna alındı. Ajan artık hedef bakışına sağ/sol ve yukarı/aşağı küçük aim offset ile pozitif ileri ivme şiddeti seçer.
> - **Hareket Yetkisi**: `DIRECT_ACTION_AIM_OFFSET=0.45`, `DIRECT_ACTION_MIN_ACCEL=18`, `DIRECT_ACTION_MAX_ACCEL=46` yapıldı. Bu değerler roketin hedef hattından tamamen kopmadan manevra yapmasına izin verirken aşırı hızlanmayı azaltır.
> - **Unity Davranışı**: `direct_accel` paketinde Unity roket burnunu komut edilen bakış yönüne hizalar ve yan/geri kaymayı `DampenDirectSideSlip()` ile yumuşatır. Böylece görsel theta metriği pasif hız yönüne değil, action'ın istediği bakış yönüne daha yakın kalır.
> - **Yeni Prefix/Faz**: Action semantiği değiştiği için model prefix'i `sac_v15_1_5_direct_target_look_angle90_target500_y100`, faz adı `v15_1_5_phase_1_sac_direct_target_look_angle90_target500_y100` yapıldı.

> ## v15.1.6 - Learned Direct Steering
>
> - **Baseline Bulgusu**: v15.1.5 koşusunda ilk episode'lardan itibaren `%100 success` görüldü; `SAC_START_TRAINING_STEPS=8000` öncesinde loss değerleri `0` kaldığı için bu başarı SAC öğrenmesi değil, hedef-bakış action wrapper etkisiydi.
> - **Action Düzeltmesi**: `direct_accel` korunur, fakat sıfır action artık hedefe otomatik bakmaz. Python `look_dir = rocket_forward + right*a0*offset + up*a1*offset` hesaplar; hedef yönü sadece state içinde kalır.
> - **Öğrenme Gereksinimi**: Ajan hedefe dönmek için `action[0]` ve `action[1]` direksiyon komutlarını gerçekten öğrenmelidir. Böylece random/sıfır policy'nin hedefi kolayca vurması engellenir.
> - **Hareket Yetkisi**: Otomatik hedef kilidi kaldırıldığı için direksiyon aralığı `DIRECT_ACTION_AIM_OFFSET=1.60` yapıldı; `DIRECT_ACTION_MIN_ACCEL=18`, `DIRECT_ACTION_MAX_ACCEL=46` korunur.
> - **Baseline Aracı**: `scripts/action_baseline.py` eklendi. Unity Play moddayken SAC kullanmadan `zero`, `random` veya `forward` action ile kısa episode serileri koşup success'in wrapper'dan mı geldiğini ölçer.
> - **Baseline Sonucu**: `zero` policy 10/10 episode'da `bad_angle` ile bitti ve `0/10 success` üretti. `random` policy de 10/10 episode'da `bad_angle` ile bitti ve `0/10 success` üretti. Bu sonuç v15.1.6'da otomatik başarı kalmadığını gösterir.
> - **Yeni Prefix/Faz**: Action semantiği yeniden değiştiği için model prefix'i `sac_v15_1_6_learned_direct_steer_angle90_target500_y100`, faz adı `v15_1_6_phase_1_sac_learned_direct_steer_angle90_target500_y100` yapıldı.

> ## v15.1.7 - Relaxed Bad Angle Terminal
>
> - **Log Gözlemi**: v15.1.6'nın ilk koşusunda episode'ların büyük kısmı `bad_angle` ile çok erken bitti. Loss değerleri hâlâ `0` idi çünkü SAC warmup eşiği olan `8000` step'e ulaşılmamıştı; buna rağmen terminal kuralının fazla sert olduğu görüldü.
> - **Terminal Gevşetmesi**: `bad_angle` eşiği `theta_deg > 90.0` yerine `theta_deg > 110.0` yapıldı. Ayrıca ilk `25` step içinde `bad_angle` terminali devreye girmez.
> - **Amaç**: Ajanın hedefi tamamen arkasına almadan önce kısa süre toparlama manevrası denemesine izin vermek; fakat uzun süre yanlış yöne kaçan davranışı yine kesmek.
> - **Checkpoint Ayrımı**: Terminal kuralı değiştiği için model prefix'i `sac_v15_1_7_learned_direct_steer_angle110_grace_target500_y100`, faz adı `v15_1_7_phase_1_sac_learned_direct_steer_angle110_grace_target500_y100` yapıldı.
> - **Replay Buffer Kaydı**: SAC replay buffer artık checkpoint sırasında `models/<prefix>_replay_buffer.npz` dosyasına kaydedilir ve resume sırasında geri yüklenir. Böylece yarıda kesilen training sadece model ağırlıklarıyla değil, mümkünse deney hafızasıyla da devam eder.

> ## v15.1.8 - Extended Timeout Continuation
>
> - **Log Gözlemi**: v15.1.7 son koşusunda episode'lar çoğunlukla `timeout` ile bitiyordu; fakat `step=800` sonunda roket hâlâ hedefe yaklaşıyor ve final mesafe yaklaşık `85-100m` bandında kalıyordu. Bu nedenle timeout erken kesiyor olabilir.
> - **Timeout Genişletmesi**: Aktif faz `max_step=800` yerine `max_step=1200` kullanır. Böylece hedefe doğru kapanan episode'lara daha fazla zaman tanınır.
> - **Training Devamı**: `SAC_TOTAL_STEPS=250000` yerine `500000` yapıldı. Mevcut `step250000` checkpoint'inden devam edebilmek için `SAC_MODEL_PREFIX` bilinçli olarak `sac_v15_1_7_learned_direct_steer_angle110_grace_target500_y100` kaldı.
> - **Yeni Faz Adı**: Faz adı `v15_1_8_phase_1_sac_extended_timeout_angle110_grace_target500_y100` oldu. Bu, loglarda timeout genişletmesini eski koşudan ayırmak içindir; model dosya prefix'i resume için değişmedi.

> ## v15.1.9 - Longer Timeout and 1M Continuation
>
> - **Timeout Genişletmesi**: Aktif faz `max_step=1200` yerine `max_step=1600` kullanır. Amaç, hedefe kapanma davranışı sürüyorsa episode'u erken kesmemek.
> - **Training Tavanı**: `SAC_TOTAL_STEPS=500000` yerine `1000000` yapıldı.
> - **Checkpoint Devamı**: Mevcut `step250000` checkpoint'inden devam edebilmek için `SAC_MODEL_PREFIX` yine `sac_v15_1_7_learned_direct_steer_angle110_grace_target500_y100` olarak korunur.
> - **Yeni Faz Adı**: Faz adı `v15_1_9_phase_1_sac_extended_timeout1600_angle110_grace_target500_y100` oldu.

> ## v15.1.10 - Wider Scene Radius and Longer Episode
>
> - **Sahne Genişletme**: Unity sahnesi genişletildiği için aktif spawn radius `500 -> 700` yapıldı.
> - **Daha Uzun Episode**: Roketin hedefe yaklaşma davranışına daha fazla zaman tanımak için `max_step=1600 -> 2400` yapıldı.
> - **Checkpoint Devamı**: Mevcut öğrenmeyi kullanmak için `SAC_MODEL_PREFIX` yine `sac_v15_1_7_learned_direct_steer_angle110_grace_target500_y100` olarak korunur.
> - **Yeni Faz Adı**: Faz adı `v15_1_10_phase_1_sac_radius700_timeout2400_angle110_grace_target_y100` oldu.

> ## v15.1.11 - Less Lateral Maneuver and More Up Authority
>
> - **Canlı Gözlem**: Roket hedefe yöneliyor fakat fazla sağ-sol manevra yaptığı için hızını koruyamıyor; hedef kendisine doğru gelip geçerken roket zaman kaybediyor.
> - **Action Yetkisi Ayrımı**: Tek `DIRECT_ACTION_AIM_OFFSET=1.60` yerine sağ-sol ve yukarı direksiyon katsayıları ayrıldı. Yatay/sağ-sol katsayı `DIRECT_ACTION_RIGHT_AIM_OFFSET=0.75`, yukarı katsayı `DIRECT_ACTION_UP_AIM_OFFSET=1.85` yapıldı.
> - **Unity Direct Sakinleştirme**: `directLookRateDeg=720 -> 420` yapıldı. Roket burnu artık her step daha az sert döner; hedefe giderken sürekli yön değiştirip hız kaybetmesi azaltılmaya çalışılır.
> - **Yan Hız Kaybı Azaltma**: `directVelocityAlignBlend=0.18 -> 0.10` yapıldı. Fazla sağ-sol kırmada biriken yan hız hâlâ söndürülür, fakat her küçük yön değişiminde hızın aşırı silinmesi azaltılır.
> - **Replay Buffer Kararı**: Model prefix aynı kaldı ve mevcut checkpoint zincirinden devam edilebilir. Ancak bu sürümde action/fizik ölçeği değiştiği için eski agresif manevra replay buffer'ı otomatik yüklenmez; yeni koşu sırasında buffer yine kaydedilir.
> - **Yeni Faz Adı**: Faz adı `v15_1_11_phase_1_sac_radius700_less_lateral_more_up_y100` oldu.

> ## v15.1.12 - Slight Less Dawdle Tuning
>
> - **Canlı Gözlem**: v15.1.11 sonrası roket hedefe daha iyi yaklaştı, fakat hâlâ hafif oyalanma ve sağ-sol salınım kaldı.
> - **Hafif Ayar**: Sağ-sol direksiyon katsayısı `0.75 -> 0.68` düşürüldü. Yukarı direksiyon katsayısı `1.85 -> 1.95` yapıldı.
> - **İleri İvme Tabanı**: Minimum ileri ivme `20 -> 23` yapıldı. Maksimum ivme `55` olarak kaldı; amaç roketi aşırı hızlandırmak değil, düşük action değerlerinde fazla zaman kaybını azaltmaktır.
> - **Unity Değişmedi**: v15.1.11'deki `directLookRateDeg=420` ve `directVelocityAlignBlend=0.10` korunur.
> - **Yeni Faz Adı**: Faz adı `v15_1_12_phase_1_sac_radius700_slight_less_dawdle_y100` oldu.

> ## v15.1.13 - More Forward Energy
>
> - **Canlı Gözlem**: Roket hedefe güzelce yaklaşıyor ve hedef üstünden geçtikten sonra peşinden gitmeye çalışıyor, fakat hız/enerji yetersiz kaldığı için yetişemiyor.
> - **İleri İvme Artışı**: `DIRECT_ACTION_MIN_ACCEL=23 -> 30`, `DIRECT_ACTION_MAX_ACCEL=55 -> 72` yapıldı.
> - **Direksiyon Korundu**: Sağ-sol/yukarı aim offset değerleri korunur (`0.68`, `1.95`). Amaç oluşan takip davranışını bozmak değil, aynı davranışa daha fazla ileri enerji vermektir.
> - **Unity Hız Limiti**: `directMaxSpeed=140` korunur; bu sürüm ivme bandını artırır ama maksimum hız limitini değiştirmez.
> - **Yeni Faz Adı**: Faz adı `v15_1_13_phase_1_sac_radius700_more_forward_energy_y100` oldu.

> ## v15.1.14 - Balanced Energy and Angle Hold
>
> - **Canlı Gözlem**: v15.1.13 ile roket çok hızlandı; hedef gelmeden yüksek irtifaya kaçtı ve hedef açısını kaybetmeye başladı. Loglarda yakın mesafeye rağmen çoğu bölüm `bad_angle`, bir bölüm de `high_altitude` ile bitti.
> - **İvme Orta Noktası**: `DIRECT_ACTION_MIN_ACCEL=30 -> 27`, `DIRECT_ACTION_MAX_ACCEL=72 -> 64` yapıldı. Bu değerler v15.1.12'den güçlü, v15.1.13'ten sakin bir ara ayardır.
> - **Yukarı Otorite Azaltıldı**: `DIRECT_ACTION_UP_AIM_OFFSET=1.95 -> 1.70` yapıldı. Sağ-sol katsayı `0.68` olarak korundu.
> - **Hız Limiti**: Unity direct hız limiti `directMaxSpeed=140 -> 120` yapıldı. Amaç hedef sonrası takip için hâlâ yeterli hız bırakmak, fakat hedef gelmeden aşırı yükselip açıyı kaybetmeyi azaltmaktır.
> - **Yeni Faz Adı**: Faz adı `v15_1_14_phase_1_sac_radius700_balanced_energy_angle_hold_y100` oldu.

> ## v15.1.15 - Balanced Energy With More Maneuver
>
> - **Canlı Gözlem**: v15.1.14 ile enerji daha dengeli oldu, fakat açı kapanması fazla zayıfladı; manevra otoritesinin biraz geri verilmesi gerekti.
> - **Manevra Artışı**: Sağ-sol direksiyon katsayısı `0.68 -> 0.74`, yukarı direksiyon katsayısı `1.70 -> 1.82` yapıldı.
> - **Enerji Korundu**: İleri ivme bandı `27-64`, Unity direct hız limiti `120`, direct bakış dönüş hızı `420 deg/s` ve yan hız söndürme `0.10` olarak korundu.
> - **Yeni Faz Adı**: Faz adı `v15_1_15_phase_1_sac_radius700_balanced_energy_more_maneuver_y100` oldu.

> ## v15.1.16 - More Maneuver, Slightly Slower
>
> - **Canlı Gözlem**: Manevra biraz daha artırılabilir; hız ise çok hafif kısılabilir.
> - **Manevra Artışı**: Sağ-sol direksiyon katsayısı `0.74 -> 0.82`, yukarı direksiyon katsayısı `1.82 -> 1.90` yapıldı.
> - **Hafif Hız Kısma**: İleri ivme bandı `27-64 -> 26-61`, Unity direct hız limiti `120 -> 115` yapıldı.
> - **Korunanlar**: Direct bakış dönüş hızı `420 deg/s` ve yan hız söndürme `0.10` olarak kaldı.
> - **Yeni Faz Adı**: Faz adı `v15_1_16_phase_1_sac_radius700_more_maneuver_slight_slower_y100` oldu.
