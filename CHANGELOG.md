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

