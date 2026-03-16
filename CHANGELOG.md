# v1.0 sürüm ailesi

> ## v1.0 - İlk kararlı sürüm
>
> - Unity ortamı ve sahne düzeni
> - PPO eğitim scriptleri ve ayarları
> - Rapor dokümanları ve 3D model dosyalarının `docs` altına taşınması
> - JSON bağımlılıklarının projeye eklenmesi
>
> ## v1.1 - Fizik senkronizasyonu ve reward güncellemeleri
>
> - Unity `Env` ortamında manuel fizik adımı (Physics.Simulate) ve güvenli reset akışı
> - Raycast tabanlı AGL (yerden yükseklik) ve grounded flag ile iyileştirilmiş state tanımı
> - Python `env.py` tarafında reward/terminal mantığının AGL ve grounded bilgisiyle güncellenmesi
> - Ortam problemlerine yönelik detaylı `docs/deep_research/deep-research-report.md` teknik analizi eklendi
>
> > ### v1.1.1 - Debug çizgileri ve görsel iyileştirme
> >
> > - Unity `Env` içinde debug çizgilerinin fizik adımıyla senkron çalışacak şekilde güncellenmesi
> > - Roket ileri yön çizgisinin `rocket` yerine `rocketPoint` referansıyla çizilerek görsel tutarlılığın artırılması
> > - **Kod düzeyi değişiklikler**
> >   - `Env.Update` içindeki `UpdateDebugLines()` çağrısı kaldırıldı; debug çizgileri artık her aksiyon adımında `StepOnce()` içinde, fizik simülasyonu (`Physics.Simulate`) sonrasında güncelleniyor.
> >   - `UpdateDebugLines()` fonksiyonunda ileri yön çizgisi hesabı `rocket.forward` yerine `rocketPoint.forward` kullanacak şekilde değiştirildi.
> >
> > ### v1.1.2 - AGL yönü ve kamera yumuşatma ayarları
> >
> > - `Env.ComputeAGL` içinde yerden yükseklik raycast yönü `-Physics.gravity.normalized` yerine sabit `Vector3.down` kullanacak şekilde sadeleştirildi.
> > - `CameraFollow` bileşeninde `positionDamping` ve `rotationDamping` değerleri yumuşak ama daha tepkisel bir takip için yeniden ayarlandı.
> >
> > ### v1.1.3 - AGL ray mesafesi ve max irtifa sınırı
> >
> > - Unity `Env` tarafında AGL hesaplaması için kullanılan `groundRayMax` değeri **100.0 → 180.0** olarak artırıldı (daha yüksek irtifalarda da yer tespiti yapabilmek için).
> > - Python `env.py` içinde `MAX_ALTITUDE` eşiği **250.0 → 150.0** olarak düşürüldü; yüksek irtifa cezalandırması artık daha erken devreye giriyor.
> >
> > ### v1.1.4 - Thrust limitlerinin yumuşatılması
> >
> > - Python `env.py` içinde thrust limitleri daha yumuşak ve kontrol edilebilir bir uçuş için güncellendi:
> >   - `MIN_THRUST`: **700.0 → 600.0**
> >   - `MAX_THRUST`: **1200.0 → 1000.0**
> >
> > ### v1.1.5 - Kamera damping ayarları ve sahne güncellemeleri
> >
> > - `CameraFollow.cs` bileşeninde takip yumuşatma değerleri daha akıcı bir görünüm için optimize edildi:
> >   - `positionDamping`: **12.0 → 10.0**
> >   - `rotationDamping`: **9.0 → 7.0**
> > - Unity tarafında sahne (`SampleScene.unity`) ve ortam düzenlemeleri güncellendi.
> >
> > ### v1.1.6 - Kamera damping optimizasyonu
> >
> > - `CameraFollow.cs` bileşeninde takip yumuşatma değerleri daha hassas ve akıcı bir takip için tekrar optimize edildi:
> >   - `positionDamping`: **10.0 → 7.0**
> >   - `rotationDamping`: **7.0 → 5.0**
>
> ## v1.2 - Kamera takip modernizasyonu
>
> - `CameraFollow.cs` içindeki `positionDamping` ve `rotationDamping` mantığı tamamen kaldırıldı. Kamera artık hedefi herhangi bir gecikme (smoothing/damping) olmadan doğrudan takip ediyor. Bu, özellikle yüksek hızlarda ve ani manevralarda takibin daha tutarlı olmasını sağlıyor.
>
> > ### v1.2.1 - Renkli loglama ve rapor taslağı
> >
> > - **Renkli loglama sistemi**: `scripts/log.py` içindeki bölüm sonu logları artık daha okunabilir olması için renklendirildi. Başarı (success), irtifa hataları (low_agl, high_altitude) ve zaman aşımı (timeout) durumları farklı ANSI renkleriyle terminale basılıyor.
> > - **Rapor taslağı**: `docs/rapor/` dizinine proje raporu taslak Word belgesi eklendi.
>
> # v2.0 sürüm ailesi
>
> > ## v2.0 - İrtifa hatası (height_error) bazlı state tanımı
> >
> > - **Major State Güncellemesi**: State tanımındaki `target_h` (mutlak hedef yüksekliği) çıkarılarak yerine `height_error` (hedef_yüksekliği - mevcut_irtifa) eklendi. Bu değişiklik hem Unity (`env.cs`) hem de Python (`env.py`) tarafında eşzamanlı olarak uygulandı.
> > - **Normalizasyon ve Loglama**: `env.py` üzerindeki normalizasyon katmanı yeni state yapısına göre güncellendi. `log.py` ve `test.py` üzerindeki tüm loglama mekanizmaları (CSV ve Console) `height_error` bilgisini içerecek şekilde revize edildi.
> > - **Gelişmiş Bölüm Analizi**: Bölüm sonu loglarına `final_height_error` metriği eklenerek eğitimin başarısı daha detaylı izlenebilir hale getirildi.
> > 
> > ## v2.0.1 - İrtifa sınırı optimizasyonu ve sahne temizliği
> >
> > - **İrtifa sınırı optimizasyonu**: `scripts/env.py` içinde `MAX_ALTITUDE` eşiği **150.0 -> 100.0** olarak düşürüldü. Bu, roketin çok fazla yükselmesini daha erken engelleyerek eğitimin daha verimli alanlara odaklanmasını sağlar.
> > - **Sahne temizliği**: `SampleScene.unity` içinde gereksiz AudioListener bileşenleri devre dışı bırakıldı ve çalışma ortamı optimize edildi.
> > - **Dosya temizliği**: Geçici Word dosyaları ve eski log kayıtları temizlendi.
> >
> > ## v2.0.2 - Güvenli irtifa artıtrımı
> >
> > - **Güvenli irtifa artırımı**: `scripts/env.py` içinde `MIN_AGL` (minimum yerden yükseklik) eşiği **0.20 -> 0.40** olarak artırıldı. Bu, rokete yerden daha güvenli bir mesafe bırakması için daha erken ceza verilmesini sağlar ve çarpışma riskini azaltır.
>
> > ## v2.0.3 - Debug çizgileri ve model güncellemeleri
> >
> > - **Görsel iyileştirmeler (Debug Lines)**: Unity sahnesindeki (`SampleScene.unity`) `LineRenderer` bileşenlerinin `widthMultiplier` değeri **0.05 -> 0.3** olarak artırıldı. Bu, takip edilen yörünge ve debug çizgilerinin daha belirgin olmasını sağlar.
> > - **Model güncellemeleri**: Yeni eğitim verileriyle güncellenen modeller (`models/`) projeye dahil edildi.
>
> # v3.0 sürüm ailesi
>
> > ## v3.0 - Ödül Fonksiyonu ve State Tanımı Revizyonu
> >
> > - **State Tanımı Güncellemesi**: State vektörü sonundaki `blend_w` (grounded flag) çıkarılarak yerine `time_remaining` (kalan süre oranı) eklendi. Bu, ajanın zaman kısıtına göre strateji değiştirmesine olanak tanıyor.
> > - **Ödül Fonksiyonu Overhaul**:
> >     - **Hizalama Ödülü (Alignment Bonus)**: Roket burnunun hedefe bakma derecesine göre (`target_dir_z`) ek ödül tanımlandı.
> >     - **Takla Cezası (Angular Velocity Penalty)**: Roketin kontrolsüz dönmesini engellemek için açısal hız büyüklüğüne bağlı ceza eklendi.
> >     - **Kapanma Hızı Ağırlığı**: Hedefe yaklaşma hızı ödülü (`closing_rate`) 2.5 katına çıkarıldı.
> > - **Eğitim Stabilitesi**:
> >     - `MIN_AGL` eşiği **0.25**'e çekilerek rampadan kalkış sırasındaki hatalı sonlanmalar engellendi.
> >     - `LOW_AGL_GRACE_STEPS` **15**'e çıkarılarak kalkış toleransı artırıldı.
> > - **Loglama ve Analiz**:
> >     - Konsol ve CSV loglarına `alignment` ve `ang_vel_mag` tanıları eklendi.
> >     - `log.py` içindeki GAE lambda bug'ı düzeltildi.
> > - **Model Yönetimi**: Eski model ve state dosyaları `models/old-models/` dizinine taşınarak çalışma alanı temizlendi.
>
> > ## v3.1.0 - Kaçış Terminali (Escape Logic) ve Renk Güncellemesi
> >
> > - **Kaçış Terminali (Escape Logic)**: Roketin hedeften kontrolsüzce uzaklaşmasını engellemek için yeni bir terminal koşulu eklendi. Başlangıç mesafesinin 1.5 katına çıkan roketler, 50 adım tolerans sonrası (`ESCAPE_GRACE_STEPS`) otomatik olarak durduruluyor.
> > - **Yeni Ceza**: Kaçış durumu için `-50.0` ceza puanı (`ESCAPE_PENALTY`) tanımlandı. Bu, değer fonksiyonunun hatalı yükselmesini (value function inflation) engeller.
> > - **Loglama Güncellemesi**: `log.py` içinde `escaped` durumu için turkuaz (`CYAN`) renk kodu eklendi, böylece konsol çıktılarında kaçış terminali kolayca ayırt edilebiliyor.
>
> > ## v3.1.1 - Ödül ve Ceza Parametre İyileştirmeleri
> >
> > - **Güvenlik Sınırı Güncellemesi**: `MIN_AGL` (minimum yerden yükseklik) eşiği **0.25 -> 0.35** olarak artırıldı. Bu, roketin yere daha güvenli bir mesafede kalmasını zorunlu kılar.
> > - **İrtifa Kısıtlaması**: `MAX_ALTITUDE` (maksimum irtifa) **100.0 -> 95.0** olarak düşürüldü.
> > - **Başarı Ödülü Artırımı**: `SUCCESS_REWARD` (başarı ödülü) **200.0 -> 210.0** olarak güncellendi.
> > - **Düşük İrtifa Cezası**: `LOW_ALTITUDE_PENALTY` (düşük irtifa cezası) **-70.0 -> -75.0** olarak artırıldı.
>
> > ## v3.2.0 - Başlangıç Koşulları Stabilizasyonu
> >
> > - **Heading Offset Kısıtlaması**: Reset sırasında roketin rastgele atanan başlangıç yönü sapması (heading offset) **±45 derece -> ±5 derece** aralığına düşürüldü. Bu, eğitimin başlangıç aşamasında daha kararlı bir öğrenme süreci sağlar.
>
> > ## v3.3.0 - Performans Zarflarının Genişletilmesi ve Eğitim Optimizasyonu
> >
> > - **Thrust ve Kontrol Kuvveti Artırımı**:
> >     - `MIN_THRUST` **600.0 -> 580.0**, `MAX_THRUST` **1000.0 -> 1050.0** olarak güncellendi.
> >     - `MAX_PITCH_FORCE` ve `MAX_YAW_FORCE` **1.5 -> 1.7** değerine çıkarılarak manevra kabiliyeti artırıldı.
> > - **İrtifa ve Ceza Güncellemeleri**:
> >     - `MAX_ALTITUDE` **95.0 -> 100.0** olarak esnetildi.
> >     - `HIGH_ALTITUDE_PENALTY` (yüksek irtifa cezası) **-80.0 -> -82.0** olarak güncellendi.
> > - **Eğitim ve Loglama Ayarları**:
> >     - `ROLLOUT_LEN` **1024 -> 1200** olarak artırıldı (daha uzun veri toplama periyodu).
> >     - `SAVE_EVERY_UPDATES` **16 -> 20** olarak güncellendi.
> >     - `STEP_PRINT_EVERY` **50 -> 25** yapılarak konsol takibi sıklaştırıldı.
>
> > ## v3.4.0 - İrtifa Hizalama ve Yer Yakınlık Uyarısı (Soft Floor)
> >
> > - **Yer Yakınlık Uyarısı (Soft Floor)**: Roketin 5m altına indiği durumlarda terminale girmeden önce sürekli bir ceza sinyali eklendi (`SOFT_FLOOR = 5.0`). Bu, ajanın yere tehlikeli yaklaşmasını erkenden fark etmesini sağlar.
> > - **İrtifa Hizalama Ödülü (Height Alignment)**: Ajanın hedef irtifaya (target altitude) sadık kalmasını teşvik etmek için `height_error` tabanlı yeni bir ödül eklendi (`HEIGHT_ALIGN_GAIN = 0.020`).
> > - **Kaçış Terminali Hassasiyeti**: `ESCAPE_MULTIPLIER` **1.5 -> 1.4** seviyesine düşürülerek hedeften uzaklaşma tespiti daha hassas hale getirildi.
> > - **Ödül Ağırlıkları İyileştirmesi**:
> >     - `DISTANCE_GAIN` **0.30 -> 0.35** ve `CLOSING_RATE_GAIN` **0.010 -> 0.017** olarak artırıldı.
> >     - `ALIGNMENT_GAIN` **0.04 -> 0.045** seviyesine çıkarıldı.
> >     - `STEP_PENALTY` ve `ANG_VEL_PENALTY` değerlerinde küçük yumuşatmalar yapıldı.
>
> > ## v3.4.1 - İrtifa Hizalama Hassasiyeti Artırımı
> >
> > - **İrtifa Hizalama Hassasiyeti**: `HEIGHT_ALIGN_GAIN` değeri **0.020 -> 0.035** olarak artırıldı ve ceza mantığı (`reward -= gain * error`) stabilize edildi. Bu, roketin hedef irtifaya çok daha sıkı tutunmasını sağlar.
>
> > ## v3.4.2 - Ödül İnce Ayarı ve Analiz Araçları
> >
> > - **İrtifa Hizalama Dengelenmesi**: `HEIGHT_ALIGN_GAIN` değeri **0.035 -> 0.015** seviyesine çekilerek ödül fonksiyonu daha dengeli hale getirildi. Bu, ajanın irtifa hatasına aşırı odaklanıp ana hedefi (mesafe) ihmal etmesini önler.
> > - **Yeni Analiz Scripti (`docs/analiz.py`)**: `step_log.csv` verilerini Pandas ile hızlıca analiz etmek için temel bir script eklendi.
> > - **Reward Test Ortamı (`scripts/reward_test.py`)**: TCP bağlantısı gerektirmeden `calculate_reward` mantığını farklı senaryolarla test etmeyi sağlayan kapsamlı bir unit-test benzeri script geliştirildi.
>
> # v4.0 - Curriculum Learning (Müfredatlı Öğrenme)
>
> > ## v4.0.0 - Müfredat Temelli Eğitimin Başlatılması (Adım 1)
> >
> > - **Curriculum Learning (CL) Geçişi**: Eğitimin daha sağlıklı ve dengeli ilerlemesi için aşamalı müfredat modeline geçildi.
> > - **Hareketsiz Hedef (Stationary Target)**: İlk eğitim aşamasında hedefin hareketi tamamen devre dışı bırakıldı (`TARGET_VELOCITY = 0.0`). Hedef, roketin tam tepesinde sabit bekleyecek şekilde konumlandırıldı.
> > - **Lokasyon Sabitleme**: Hedefin başlangıç konumu (px, pz) **(300, 300) -> (0, 0)** olarak güncellenerek eğitimin en basit senaryodan başlaması sağlandı.
> > - **Temiz Başlangıç**: CL sürecinin sağlıklı takibi için eski log ve model dosyaları temizlendi. Yeni müfredata uygun modeller bu sürümden itibaren kaydedilecek.
>
> > ## v4.0.1 - Müfredat Temelli Öğrenme - Adım 2: Stabilizasyon
> >
> > - **Başlangıç Oryantasyonu Sabitleme**: `env.py` içindeki `reset` fonksiyonunda `calculate_new_loc` devre dışı bırakılarak `px, pz, ry, rz = 0,0,0,0` olarak sabitlendi. Bu, ajanın her bölüme tam olarak aynı konum ve yönelimle başlamasını sağlar.
> > - **Eğitim Kararlılığı**: Rastgeleliğin (randomness) azaltılmasıyla ajanın temel hareketleri ve dengeyi daha hızlı öğrenmesi hedeflenmektedir.
>
> # v5.0 - Yeni State Tanımı ve Müfredat Gelişimi
>
> > ## v5.0.0 - Yeni State Tanımı ve Gelişmiş Loglama
> >
> > - **Major State Güncellemesi**: State vektöründen `closing_rate` çıkarılarak yerine `look_angle_rad` (bakış açısı - radyan) eklendi. Bu, ajanın hedefe olan yönelimini daha hassas algılamasını sağlar.
> > - **State Normalizasyonu**: Yeni eklenen bakış açısı için `LOOK_ANGLE_SCALE = np.pi` tanımlandı ve [0, 1] aralığına normalize edildi.
> > - **Gelişmiş Loglama**: `log.py` güncellenerek `step_log.csv` ve `episode_log.csv` dosyalarına `look_angle_rad` ve `look_angle_deg` verileri eklendi.
> > - **Müfredat Takibi**: Curriculum Learning Step 2 (Sabit Başlangıç) devam ederken yeni state yapısıyla eğitim kararlılığı hedefleniyor.
>
> > ## v5.0.0a - Reward Fonksiyonu ve Terminal Şart İyileştirmeleri
> >
> > - **Açı Odaklı Ödül (Angle Reward)**: `look_angle_rad` üzerinden hesaplanan `ANGLE_GAIN` ödülü eklendi. Burun hedefe baktıkça ödül artar, ters yöne döndükçe ceza verilir.
> > - **Yüksek Sapma Terminali (Bad Angle Terminal)**: Roketin hedeften 135 dereceden fazla saptığı durumlar için `bad_angle` terminali ve `-60` puanlık ceza tanımlandı.
> > - **İrtifa Hizalama Revizyonu**: İrtifa ödülü (`HEIGHT_ALIGN_GAIN`) artık lineer ceza yerine, 50m hata payı içerisinde pozitif bir çarpan olarak hesaplanıyor.
> > - **Dengeleme**: `DISTANCE_GAIN` değeri **0.35 -> 0.15** seviyesine çekilerek açısal ödüllerle uyumlu hale getirildi.
>
> > ## v5.0.1 - Ödül ve Terminal Şartı Refakatçı Düzenlemeleri
> >
> > - **Terminal Şartı Kaldırıldı**: `bad_angle` terminal şartı `env.py` dosyasından kaldırılarak ajanın aşırı yönelmelerde de öğrenmeye devam etmesi sağlandı.
> > - **Bakış Açısı Hesaplaması İyileştirildi (Unity)**: `env.cs` içerisinde bakış açısı (`look_angle_rad`) artık `Mathf.Acos` kullanılarak daha hassas ve kararlı bir şekilde hesaplanıyor.
>
> > ## v5.0.2 - Ödül Ölçeklendirme ve Başarı Metrikleri
> >
> > - **Reward Ölçeklendirme (Scale-up)**: `DISTANCE_GAIN` ve `ANGLE_GAIN` gibi temel ödül katsayıları artırılarak ajanın daha güçlü sinyallerle eğitilmesi sağlandı.
> > - **Başarı Oranı Takibi (Success Rate)**: `train.py` ve `log.py` güncellenerek eğitim süresince toplam episode ve başarı sayısı (success rate) anlık olarak takip edilmeye başlandı.
> > - **Dinamik Konsol Çıktısı**: Eğitim sırasında konsola yazdırılan metrikler daha detaylı hale getirilerek ilerleme görünürlüğü artırıldı.

> > ### Faz 1 - Tamamlandı
> > - Modeller ve loglar ilk kez commit edildi; scripts değişmedi.
> > - **Başlangıç konfigürasyonu** (`env.py` v5.0.2 ile aynı):
> >   - `TARGET_VELOCITY = 0.0` (hedef sabit)
> >   - `reset`: `px, pz, ry, rz = 0, 0, 0, 0` (sabit başlangıç)
> >   - `calculate_new_loc()` içinde `px = 0 * np.cos(theta)`, `pz = 0 * np.sin(theta)` (efektif sabit konum)
> >   - `ANGLE_GAIN = 0.22`, `DISTANCE_GAIN = 0.15`
> > - Büyük log dosyaları 40MB parçalara bölünerek GitHub'a yedeklendi.
>
> > ### Faz 2 - Tamamlandı
> > - Faz 2 müfredatlı eğitimi (Curriculum Learning) tamamlandı.
> > - **env.py değişiklikleri** (Faz 1 → Faz 2, git diff ile):
> >   - `calculate_new_loc()`: `px`/`pz` artık `0 * np.cos(theta)` / `0 * np.sin(theta)` yerine `np.random.randint(0,3) * np.cos(theta)` / `np.random.randint(0,3) * np.sin(theta)` (0–2 birim, yakın alan)
> >   - `reset`: `px, pz, ry, rz = 0,0,0,0` → `px, pz, ry, rz = calculate_new_loc()` (dinamik konum ve rz kuzeye yönelik)
>
> > ### Faz 3 - Tamamlandı
> > - Faz 3 final eğitimi ve stabilizasyon tamamlandı.
> > - **env.py değişiklikleri** (Faz 2 → Faz 3, git diff ile):
> >   - Başlangıç mesafe çarpanı: `np.random.randint(0,3)` → `np.random.randint(1,5.5)` (1–4 birim, daha geniş alan)
> > - Tüm modeller ve loglar GitHub'a yedeklendi.
>
> > ### Faz 4 - Tamamlandı
> > - Faz 4 eğitimi tamamlandı.
> > - **env.py değişiklikleri** (Faz 3 → Faz 4):
> >   - Başlangıç mesafe çarpanı: `np.random.randint(1,5.5)` → `np.random.randint(2,7)` (2–6 birim, daha geniş alan)
>
> > ### Faz 5 - Tamamlandı
> > - Faz 5 eğitimi tamamlandı.
> > - **env.py değişiklikleri** (Faz 4 → Faz 5):
> >   - Başlangıç mesafe çarpanı: `np.random.randint(2,7)` → `np.random.randint(3,10)` (3–9 birim, daha geniş alan)
>
> > ### Faz 6 - Tamamlandı
> > - Faz 6 eğitimi tamamlandı.
> > - **env.py değişiklikleri** (Faz 5 → Faz 6):
> >   - Başlangıç mesafe çarpanı: `np.random.randint(3,10)` → `np.random.randint(4,11)` (4–10 birim, daha geniş alan)
>
> > ### Faz 7 - Tamamlandı
> > - Faz 7 eğitimi tamamlandı.
> > - **env.py değişiklikleri** (Faz 6 → Faz 7):
> >   - Başlangıç mesafe çarpanı: `np.random.randint(4,11)` → `np.random.randint(7,13)` (7–12 birim, daha geniş alan)
> >   - Ödül ve ceza ayarları: `ANGLE_GAIN = 0.22 → 0.30`, `SUCCESS_REWARD = 210.0 → 250.0`, `HIGH_ALTITUDE_PENALTY = -82.0 → -85.0`, `ESCAPE_PENALTY = -50.0 → -60.0`
> > - **Log yönetimi**: `logs/step_log.csv` Faz 7 için `logs/step_log_faz7.zip` olarak sıkıştırıldı ve aktif dosya sıfırlandı (büyük dosya uyarılarını azaltmak için).

> > ### Faz 8 - Tamamlandı
> > - Faz 8 eğitimi tamamlandı.
> > - **env.py değişiklikleri** (Faz 7 → Faz 8):
> >   - Başlangıç mesafe çarpanı: `np.random.randint(5.5,12.5)` → `np.random.randint(7,13)` (yaklaşık 6–12 birimden 7–12 birime, daha uzak minimum mesafe)

> > ### Faz 9 - Tamamlandı
> > - Faz 9 eğitimi tamamlandı.
> > - **env.py değişiklikleri** (Faz 8 → Faz 9):
> >   - Başlangıç mesafe çarpanı: `np.random.randint(7,13)` → `np.random.randint(9,16)` (9–15 birim, hedef başlangıç mesafesi belirgin şekilde büyüdü)
> >   - Ödül ve ceza ayarları:
> >     - `STEP_PENALTY = -0.018 → -0.022` (adım başına ceza biraz artırıldı)
> >     - `DISTANCE_GAIN = 0.15 → 0.17`, `ANGLE_GAIN = 0.30 → 0.40`
> >     - `ANG_VEL_PENALTY = 0.004 → 0.005`
> >     - `ESCAPE_PENALTY = -60.0 → -70.0`, `ESCAPE_GRACE_STEPS = 50 → 55`
> >     - `HEIGHT_ALIGN_GAIN = 0.015 → 0.020`

> > ### Faz 10 - Başarısız (Tamamlandı)
> > - Faz 10 eğitimi **tamamlandı ancak hedeflenen başarı seviyesine ulaşamadı**.
> > - **env.py değişiklikleri** (Faz 9 → Faz 10):
> >   - Başlangıç mesafe çarpanı: `np.random.randint(9,16)` → `np.random.randint(10.5,20)` (yaklaşık 11–19 birim; çok uzak başlangıç menzili)
> >   - Maksimum adım sayısı: `max_step = 1300` → `max_step = 255` (epizot süresi ciddi biçimde kısaltıldı)
> >   - Ödül/ceza parametreleri:
> >     - `STEP_PENALTY = -0.022 → -0.030` (her adım için daha sert ceza)
> >     - `HIGH_ALTITUDE_PENALTY = -85.0 → -90.0`
> >     - `TIMEOUT_PENALTY = -60.0 → -90.0`
> >     - `HEIGHT_ALIGN_GAIN = 0.020 → 0.025`
> >   - Kaçış (escape) mantığı: ESCAPE terminal bloğu yoruma alınarak devre dışı bırakıldı (kaçış durumları artık terminal olmuyor).
> > - **Başarı oranı (success rate)**: **%54.34** — önceki fazlara kıyasla belirgin düşüş; bu nedenle Faz 10 **başarısız** olarak işaretlendi ve bir önceki faz (Faz 9) kalıcı referans olarak korunuyor.