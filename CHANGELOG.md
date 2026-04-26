# v8.0 sürüm ailesi

> ## v8.1.0 - Phase 1.4 Archive Snapshot
>
> - **Phase 1.4 Freeze Point**: V8 gravity-based guidance kosusu `up1200` modelinde donduruldu. Bu nokta, en iyi rolling 100 success koridoruna (`episode 561-660`, `update 1188-1201`) dogrudan denk geldigi ve son `200-300` episode'da `%64-%67` bandini korudugu icin handoff modeli olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_4/` altina `ppo_model_up1200`, agent state, `episode_log.csv`, `update_log.csv`, rolling success-rate grafigi, success yogunluk grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis / 30 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.4 genelinde `5790` episode icinde `1235` success (%21.330) goruldu. En iyi rolling 100 success rate `%72.000`, en iyi rolling 200 success rate `%70.000` olarak kaydedildi. Son `200` episode'da success rate `%67.000` seviyesine kadar cikti.
> - **Phase Transition Decision**: Son `200` episode icinde `75-80` fiili baslangic mesafesi `%95.83`, `80-85` `%100`, `85-90` `%100` success urettigi icin bir sonraki fazin menzil bandi yukariya kaydirilacak sekilde `62-82 radius` olarak secildi. Heading araligi ve reward ailesi ilk denemede korunacak.

# v8.1 sürüm ailesi

> ## v8.0.0 - Gravity-Based Guidance State and Semantic Action Redesign
>
> - **State Contract Redesign**: RL observation 14 boyutta tutuldu, ancak alanlar tamamen guidance semantigine gore yeniden tanimlandi. Yeni observation artik `theta`, `alpha`, `beta`, guidance-frame bagil hizlar, guidance-frame turn-rate bilesenleri ve `forward_up_dot` tasiyor.
> - **Semantic Action Space**: Python -> Unity action anlami `thrust / pitch / yaw` yerine `thrust / vertical_cmd / horizontal_cmd` oldu. Unity bu semantic komutlari gravity tabanli guidance frame uzerinden local torque'a donusturuyor.
> - **Telemetry Expansion**: Step telemetry su yeni alanlarla genisletildi: guidance world/local eksenleri, guidance-frame hiz bilesenleri, guidance-frame acisal hiz bilesenleri ve uygulanan semantic turn komutlarinin world/local izdususleri.
> - **Logging and Test Pipeline Update**: `log.py`, `test.py`, `reward_test.py`, `reward_grid_search.py` ve `connector.py`, yeni `theta/alpha/beta` ve semantic action isimlerine uyarlandi. CSV basliklari V8 semasina gore otomatik yenilenir.
> - **Model Baseline Update**: PPO actor-critic omurgasi `512-512-512` olarak buyutuldu. Bu degisim yeni V8 temsil uzayi ile birlikte bastan egitim senaryosuna temel olmasi icin yapildi.
> - **Training Note**: V8 semantigi checkpoint formatini degil ama policy anlamini degistirdigi icin, eski checkpoint'lerden warm-start etmek yerine temiz egitim baslatmak tercih edilmelidir.

# v7.3 sürüm ailesi

> ## v7.3.0 - Phase 1.3 Archive Snapshot
>
> - **Phase 1.3 Freeze Point**: Faz 1.3 egitimi `up800` modelinde donduruldu. `up700` penceresi biraz daha yuksek ham pencere success rate gormesine ragmen, `up800` gec ve halen guclu bir checkpoint oldugu icin handoff noktasi olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_3/` altina `ppo_model_up800`, agent state, `episode_log.csv`, `update_log.csv`, success-rate grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis / 6 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.3 genelinde `1817` episode icinde `855` success (%47.056) goruldu. En iyi rolling 100 success rate `%67.000`, en iyi rolling 200 success rate `%61.000` olarak kaydedildi.
> - **Phase 2.1 Direction**: Bir sonraki adim ayni fazi tekrar uzatmak degil, `up800` uzerinden yumusak bir `Phase 2.1` gecisi yapmak olarak belirlendi. Bu nedenle fiili baslangic mesafesi cekirdegi korunup heading sapmasi ve horizon dikkatli sekilde artirilacak.

# v7.2 sürüm ailesi

> ## v7.2.0 - Phase 1.2 Archive Snapshot
>
> - **Phase 1.2 Freeze Point**: Faz 1.2 egitimi `up520` modelinde donduruldu. Bu nokta, en iyi kumulatif success rate'in `%27.957` ile `episode 930 / update 529` civarinda goruldugu koridora en yakin kayitli checkpoint olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_2/` altina `ppo_model_up520`, agent state, `episode_log.csv`, `update_log.csv`, success-rate grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis / 7 parcaya bolunmus arsivi eklendi.
> - **Observed Outcome**: Phase 1.2 genelinde `1621` episode icinde `308` success (%19.001) goruldu. En iyi rolling 200 success rate `%35.500` olarak `episode 724-923` koridorunda toplandi.
> - **Phase 1.3 Direction**: Bir sonraki adim zorlugu sertlestirmek degil, `up520` uzerinden peak davranisi stabilize etmek olarak belirlendi. Bu nedenle menzil bandinin `80-90` fiili mesafe cevresinde korunmasi ve optimizer tarafinda daha korumaci ayarlara gecilmesi not edildi.

# v7.1 sürüm ailesi

> ## v7.1.0 - Phase 1.1 Archive Snapshot
>
> - **Phase 1.1 Freeze Point**: Faz 1.1 egitimi `up340` modelinde donduruldu ve Phase 1.2 warm-start noktasi olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_1/` altina `ppo_model_up340`, agent state, `episode_log.csv`, `update_log.csv`, success rate grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis/parcalanmis arsivi eklendi.
> - **Documentation Update**: README ve changelog, Phase 1.1 sonuc ozeti ve sonraki Phase 1.2 gecis niyeti ile guncellendi.
> - **Observed Outcome**: Phase 1.1 kosusunda `1640` episode icinde `161` success (%9.817) goruldu; baskin failure modu `high_altitude` olarak kaldigi icin bir sonraki adim reward ince ayari olarak planlandi.

# v7.0 sürüm ailesi

> ## v7.0.0 - Full Telemetry Step Logging
>
> - **Unified Step Trace**: Unity tarafindan gelen ham geometri ve fizik telemetry verileri ile Python tarafinda uretilen action, value, logp, reward breakdown ve cumulative return bilgileri tek `step_log.csv` satirinda birlestirildi.
> - **Packet Contract Expansion**: Unity -> Python JSON sozlesmesine `telemetry` bolumu eklendi. Roket, hedef ve roket-hedef ciftine ait world/local konum, rotasyon, hiz, acisal hiz, relative vector ve gravity alanlari artik state disi debug verisi olarak tasiniyor.
> - **Reward Auditability**: Step log artik `reward_step_penalty`, `reward_distance`, `reward_alignment`, `reward_closing`, `reward_angular_penalty`, `reward_altitude`, `reward_soft_floor_penalty` ve `reward_terminal` kolonlarini ayri ayri sakliyor.
> - **Training Introspection**: Python tarafinda `action_norm_*`, `action_logp`, `value_pred`, `episode_return_so_far`, `phase_id`, `phase_name` ve `max_step` alanlari da step bazinda kaydediliyor.
> - **Schema-Safe Logging**: `log.py`, yeni baslik ile mevcut CSV basligi farkliysa eski loglari `.bak_YYYYMMDD_HHMMSS.csv` olarak arsivleyip temiz V7 dosyalari aciyor.
> - **State/Telemetry Separation**: RL observation 14 boyutlu sade guidance state olarak korundu; genis debug verisi ise ayri telemetry kanalina tasinarak analiz kolaylastirildi.

# v6.0 sürüm ailesi

> ## v6.0.0 - Guidance-First State Overhaul ve Repo Temizligi
>
> - **Observation Contract Break**: RL state yapisi 20 boyuttan 18 boyutlu guidance-first observation setine gecirildi.
> - **Unity -> Python Senkron Revizyonu**: JSON paket sozlesmesi yeni state alanlarina gore tekrar tasarlandi.
> - **Reward Refactor**: Reward mantigi mesafe ilerlemesi, LOS alignment, pozitif kapanma hizi, acisal hiz cezasi ve irtifa hizalama sinyalleri ile yeniden kuruldu.
> - **Loglama / Analiz Guncellemesi**: `log.py`, `test.py`, `reward_test.py` ve `docs/analiz.py` yeni V6 alanlari uzerinden calisacak sekilde guncellendi.
> - **Repo Temizligi**: Pre-V6 log ve model artefaktlari once arsivlendi, ardindan repo kokundeki runtime ciktilari gitten cikarildi.

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
> - **Next Architecture Decision**: V11, reward tahminleme aracini ve hafif orientation warm-start / behavior cloning pretraining'i birlikte kullanacak. Bu sayede PPO rastgele policy yerine hedef yonune bakan bir baslangic policy'sinden fine-tune edilecek.
