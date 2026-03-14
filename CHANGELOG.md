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

