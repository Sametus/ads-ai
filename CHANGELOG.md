# v6.0 surum ailesi

> ## v6.0.0 - Guidance-First State Overhaul ve Repo Temizligi
>
> - **Observation Contract Break**: RL state yapisi 20 boyuttan 18 boyutlu guidance-first observation setine gecirildi. `target_dir`, `roc_vel`, `look_angle_rad` ve `height_error` gibi tekrar eden alanlar kaldirildi; yerlerine `los_yaw_*`, `los_pitch_*`, `closing_speed`, `agl` ve `alt_error` tabanli yeni observation seti getirildi.
> - **Unity -> Python Senkron Revizyonu**: Unity `Env.cs`, Python `env.py` ve `connector.py` arasindaki JSON paket sozlesmesi yeni state alanlarina gore tekrar tasarlandi. `grounded_flag` artik reward/terminal mantigi icin ham sinyal olarak ayri tasiniyor.
> - **Reward Refactor**: Reward mantigi mesafe ilerlemesi, LOS alignment, pozitif kapanma hizi, acisal hiz cezasi ve irtifa hizalama sinyallerini birlikte kullanacak sekilde yeniden kuruldu.
> - **Loglama / Analiz Guncellemesi**: `log.py`, `test.py`, `reward_test.py` ve `docs/analiz.py` yeni V6 alanlari (`closing_speed`, `los_yaw_deg`, `los_pitch_deg`, `agl`, `alt_error`, `alignment`, `grounded_flag`) uzerinden calisacak sekilde guncellendi.
> - **Repo Temizligi**: Pre-V6 log ve model artefaktlari once arsiv commit'i ile korundu, ardindan repo kokundeki `logs/` ve `models/` ciktilari gitten cikarildi. `.gitignore` V6 politikasi ile runtime artefaktlarini varsayilan olarak disarida birakacak sekilde guncellendi.
> - **Hazirlik Surumu**: Bu surum curriculum faz mesafelerini ve hareketsiz hedef mantigini bilincli olarak korur; moving-target final senaryosu icin once state/reward tabanini saglamlastirmayi hedefler.
# v1.0 sÃ¼rÃ¼m ailesi

> ## v1.0 - Ä°lk kararlÄ± sÃ¼rÃ¼m
>
> - Unity ortamÄ± ve sahne dÃ¼zeni
> - PPO eÄŸitim scriptleri ve ayarlarÄ±
> - Rapor dokÃ¼manlarÄ± ve 3D model dosyalarÄ±nÄ±n `docs` altÄ±na taÅŸÄ±nmasÄ±
> - JSON baÄŸÄ±mlÄ±lÄ±klarÄ±nÄ±n projeye eklenmesi
>
> ## v1.1 - Fizik senkronizasyonu ve reward gÃ¼ncellemeleri
>
> - Unity `Env` ortamÄ±nda manuel fizik adÄ±mÄ± (Physics.Simulate) ve gÃ¼venli reset akÄ±ÅŸÄ±
> - Raycast tabanlÄ± AGL (yerden yÃ¼kseklik) ve grounded flag ile iyileÅŸtirilmiÅŸ state tanÄ±mÄ±
> - Python `env.py` tarafÄ±nda reward/terminal mantÄ±ÄŸÄ±nÄ±n AGL ve grounded bilgisiyle gÃ¼ncellenmesi
> - Ortam problemlerine yÃ¶nelik detaylÄ± `docs/deep_research/deep-research-report.md` teknik analizi eklendi
>
> > ### v1.1.1 - Debug Ã§izgileri ve gÃ¶rsel iyileÅŸtirme
> >
> > - Unity `Env` iÃ§inde debug Ã§izgilerinin fizik adÄ±mÄ±yla senkron Ã§alÄ±ÅŸacak ÅŸekilde gÃ¼ncellenmesi
> > - Roket ileri yÃ¶n Ã§izgisinin `rocket` yerine `rocketPoint` referansÄ±yla Ã§izilerek gÃ¶rsel tutarlÄ±lÄ±ÄŸÄ±n artÄ±rÄ±lmasÄ±
> > - **Kod dÃ¼zeyi deÄŸiÅŸiklikler**
> >   - `Env.Update` iÃ§indeki `UpdateDebugLines()` Ã§aÄŸrÄ±sÄ± kaldÄ±rÄ±ldÄ±; debug Ã§izgileri artÄ±k her aksiyon adÄ±mÄ±nda `StepOnce()` iÃ§inde, fizik simÃ¼lasyonu (`Physics.Simulate`) sonrasÄ±nda gÃ¼ncelleniyor.
> >   - `UpdateDebugLines()` fonksiyonunda ileri yÃ¶n Ã§izgisi hesabÄ± `rocket.forward` yerine `rocketPoint.forward` kullanacak ÅŸekilde deÄŸiÅŸtirildi.
> >
> > ### v1.1.2 - AGL yÃ¶nÃ¼ ve kamera yumuÅŸatma ayarlarÄ±
> >
> > - `Env.ComputeAGL` iÃ§inde yerden yÃ¼kseklik raycast yÃ¶nÃ¼ `-Physics.gravity.normalized` yerine sabit `Vector3.down` kullanacak ÅŸekilde sadeleÅŸtirildi.
> > - `CameraFollow` bileÅŸeninde `positionDamping` ve `rotationDamping` deÄŸerleri yumuÅŸak ama daha tepkisel bir takip iÃ§in yeniden ayarlandÄ±.
> >
> > ### v1.1.3 - AGL ray mesafesi ve max irtifa sÄ±nÄ±rÄ±
> >
> > - Unity `Env` tarafÄ±nda AGL hesaplamasÄ± iÃ§in kullanÄ±lan `groundRayMax` deÄŸeri **100.0 â†’ 180.0** olarak artÄ±rÄ±ldÄ± (daha yÃ¼ksek irtifalarda da yer tespiti yapabilmek iÃ§in).
> > - Python `env.py` iÃ§inde `MAX_ALTITUDE` eÅŸiÄŸi **250.0 â†’ 150.0** olarak dÃ¼ÅŸÃ¼rÃ¼ldÃ¼; yÃ¼ksek irtifa cezalandÄ±rmasÄ± artÄ±k daha erken devreye giriyor.
> >
> > ### v1.1.4 - Thrust limitlerinin yumuÅŸatÄ±lmasÄ±
> >
> > - Python `env.py` iÃ§inde thrust limitleri daha yumuÅŸak ve kontrol edilebilir bir uÃ§uÅŸ iÃ§in gÃ¼ncellendi:
> >   - `MIN_THRUST`: **700.0 â†’ 600.0**
> >   - `MAX_THRUST`: **1200.0 â†’ 1000.0**
> >
> > ### v1.1.5 - Kamera damping ayarlarÄ± ve sahne gÃ¼ncellemeleri
> >
> > - `CameraFollow.cs` bileÅŸeninde takip yumuÅŸatma deÄŸerleri daha akÄ±cÄ± bir gÃ¶rÃ¼nÃ¼m iÃ§in optimize edildi:
> >   - `positionDamping`: **12.0 â†’ 10.0**
> >   - `rotationDamping`: **9.0 â†’ 7.0**
> > - Unity tarafÄ±nda sahne (`SampleScene.unity`) ve ortam dÃ¼zenlemeleri gÃ¼ncellendi.
> >
> > ### v1.1.6 - Kamera damping optimizasyonu
> >
> > - `CameraFollow.cs` bileÅŸeninde takip yumuÅŸatma deÄŸerleri daha hassas ve akÄ±cÄ± bir takip iÃ§in tekrar optimize edildi:
> >   - `positionDamping`: **10.0 â†’ 7.0**
> >   - `rotationDamping`: **7.0 â†’ 5.0**
>
> ## v1.2 - Kamera takip modernizasyonu
>
> - `CameraFollow.cs` iÃ§indeki `positionDamping` ve `rotationDamping` mantÄ±ÄŸÄ± tamamen kaldÄ±rÄ±ldÄ±. Kamera artÄ±k hedefi herhangi bir gecikme (smoothing/damping) olmadan doÄŸrudan takip ediyor. Bu, Ã¶zellikle yÃ¼ksek hÄ±zlarda ve ani manevralarda takibin daha tutarlÄ± olmasÄ±nÄ± saÄŸlÄ±yor.
>
> > ### v1.2.1 - Renkli loglama ve rapor taslaÄŸÄ±
> >
> > - **Renkli loglama sistemi**: `scripts/log.py` iÃ§indeki bÃ¶lÃ¼m sonu loglarÄ± artÄ±k daha okunabilir olmasÄ± iÃ§in renklendirildi. BaÅŸarÄ± (success), irtifa hatalarÄ± (low_agl, high_altitude) ve zaman aÅŸÄ±mÄ± (timeout) durumlarÄ± farklÄ± ANSI renkleriyle terminale basÄ±lÄ±yor.
> > - **Rapor taslaÄŸÄ±**: `docs/rapor/` dizinine proje raporu taslak Word belgesi eklendi.
>
> # v2.0 sÃ¼rÃ¼m ailesi
>
> > ## v2.0 - Ä°rtifa hatasÄ± (height_error) bazlÄ± state tanÄ±mÄ±
> >
> > - **Major State GÃ¼ncellemesi**: State tanÄ±mÄ±ndaki `target_h` (mutlak hedef yÃ¼ksekliÄŸi) Ã§Ä±karÄ±larak yerine `height_error` (hedef_yÃ¼ksekliÄŸi - mevcut_irtifa) eklendi. Bu deÄŸiÅŸiklik hem Unity (`env.cs`) hem de Python (`env.py`) tarafÄ±nda eÅŸzamanlÄ± olarak uygulandÄ±.
> > - **Normalizasyon ve Loglama**: `env.py` Ã¼zerindeki normalizasyon katmanÄ± yeni state yapÄ±sÄ±na gÃ¶re gÃ¼ncellendi. `log.py` ve `test.py` Ã¼zerindeki tÃ¼m loglama mekanizmalarÄ± (CSV ve Console) `height_error` bilgisini iÃ§erecek ÅŸekilde revize edildi.
> > - **GeliÅŸmiÅŸ BÃ¶lÃ¼m Analizi**: BÃ¶lÃ¼m sonu loglarÄ±na `final_height_error` metriÄŸi eklenerek eÄŸitimin baÅŸarÄ±sÄ± daha detaylÄ± izlenebilir hale getirildi.
> > 
> > ## v2.0.1 - Ä°rtifa sÄ±nÄ±rÄ± optimizasyonu ve sahne temizliÄŸi
> >
> > - **Ä°rtifa sÄ±nÄ±rÄ± optimizasyonu**: `scripts/env.py` iÃ§inde `MAX_ALTITUDE` eÅŸiÄŸi **150.0 -> 100.0** olarak dÃ¼ÅŸÃ¼rÃ¼ldÃ¼. Bu, roketin Ã§ok fazla yÃ¼kselmesini daha erken engelleyerek eÄŸitimin daha verimli alanlara odaklanmasÄ±nÄ± saÄŸlar.
> > - **Sahne temizliÄŸi**: `SampleScene.unity` iÃ§inde gereksiz AudioListener bileÅŸenleri devre dÄ±ÅŸÄ± bÄ±rakÄ±ldÄ± ve Ã§alÄ±ÅŸma ortamÄ± optimize edildi.
> > - **Dosya temizliÄŸi**: GeÃ§ici Word dosyalarÄ± ve eski log kayÄ±tlarÄ± temizlendi.
> >
> > ## v2.0.2 - GÃ¼venli irtifa artÄ±trÄ±mÄ±
> >
> > - **GÃ¼venli irtifa artÄ±rÄ±mÄ±**: `scripts/env.py` iÃ§inde `MIN_AGL` (minimum yerden yÃ¼kseklik) eÅŸiÄŸi **0.20 -> 0.40** olarak artÄ±rÄ±ldÄ±. Bu, rokete yerden daha gÃ¼venli bir mesafe bÄ±rakmasÄ± iÃ§in daha erken ceza verilmesini saÄŸlar ve Ã§arpÄ±ÅŸma riskini azaltÄ±r.
>
> > ## v2.0.3 - Debug Ã§izgileri ve model gÃ¼ncellemeleri
> >
> > - **GÃ¶rsel iyileÅŸtirmeler (Debug Lines)**: Unity sahnesindeki (`SampleScene.unity`) `LineRenderer` bileÅŸenlerinin `widthMultiplier` deÄŸeri **0.05 -> 0.3** olarak artÄ±rÄ±ldÄ±. Bu, takip edilen yÃ¶rÃ¼nge ve debug Ã§izgilerinin daha belirgin olmasÄ±nÄ± saÄŸlar.
> > - **Model gÃ¼ncellemeleri**: Yeni eÄŸitim verileriyle gÃ¼ncellenen modeller (`models/`) projeye dahil edildi.
>
> # v3.0 sÃ¼rÃ¼m ailesi
>
> > ## v3.0 - Ã–dÃ¼l Fonksiyonu ve State TanÄ±mÄ± Revizyonu
> >
> > - **State TanÄ±mÄ± GÃ¼ncellemesi**: State vektÃ¶rÃ¼ sonundaki `blend_w` (grounded flag) Ã§Ä±karÄ±larak yerine `time_remaining` (kalan sÃ¼re oranÄ±) eklendi. Bu, ajanÄ±n zaman kÄ±sÄ±tÄ±na gÃ¶re strateji deÄŸiÅŸtirmesine olanak tanÄ±yor.
> > - **Ã–dÃ¼l Fonksiyonu Overhaul**:
> >     - **Hizalama Ã–dÃ¼lÃ¼ (Alignment Bonus)**: Roket burnunun hedefe bakma derecesine gÃ¶re (`target_dir_z`) ek Ã¶dÃ¼l tanÄ±mlandÄ±.
> >     - **Takla CezasÄ± (Angular Velocity Penalty)**: Roketin kontrolsÃ¼z dÃ¶nmesini engellemek iÃ§in aÃ§Ä±sal hÄ±z bÃ¼yÃ¼klÃ¼ÄŸÃ¼ne baÄŸlÄ± ceza eklendi.
> >     - **Kapanma HÄ±zÄ± AÄŸÄ±rlÄ±ÄŸÄ±**: Hedefe yaklaÅŸma hÄ±zÄ± Ã¶dÃ¼lÃ¼ (`closing_rate`) 2.5 katÄ±na Ã§Ä±karÄ±ldÄ±.
> > - **EÄŸitim Stabilitesi**:
> >     - `MIN_AGL` eÅŸiÄŸi **0.25**'e Ã§ekilerek rampadan kalkÄ±ÅŸ sÄ±rasÄ±ndaki hatalÄ± sonlanmalar engellendi.
> >     - `LOW_AGL_GRACE_STEPS` **15**'e Ã§Ä±karÄ±larak kalkÄ±ÅŸ toleransÄ± artÄ±rÄ±ldÄ±.
> > - **Loglama ve Analiz**:
> >     - Konsol ve CSV loglarÄ±na `alignment` ve `ang_vel_mag` tanÄ±larÄ± eklendi.
> >     - `log.py` iÃ§indeki GAE lambda bug'Ä± dÃ¼zeltildi.
> > - **Model YÃ¶netimi**: Eski model ve state dosyalarÄ± `models/old-models/` dizinine taÅŸÄ±narak Ã§alÄ±ÅŸma alanÄ± temizlendi.
>
> > ## v3.1.0 - KaÃ§Ä±ÅŸ Terminali (Escape Logic) ve Renk GÃ¼ncellemesi
> >
> > - **KaÃ§Ä±ÅŸ Terminali (Escape Logic)**: Roketin hedeften kontrolsÃ¼zce uzaklaÅŸmasÄ±nÄ± engellemek iÃ§in yeni bir terminal koÅŸulu eklendi. BaÅŸlangÄ±Ã§ mesafesinin 1.5 katÄ±na Ã§Ä±kan roketler, 50 adÄ±m tolerans sonrasÄ± (`ESCAPE_GRACE_STEPS`) otomatik olarak durduruluyor.
> > - **Yeni Ceza**: KaÃ§Ä±ÅŸ durumu iÃ§in `-50.0` ceza puanÄ± (`ESCAPE_PENALTY`) tanÄ±mlandÄ±. Bu, deÄŸer fonksiyonunun hatalÄ± yÃ¼kselmesini (value function inflation) engeller.
> > - **Loglama GÃ¼ncellemesi**: `log.py` iÃ§inde `escaped` durumu iÃ§in turkuaz (`CYAN`) renk kodu eklendi, bÃ¶ylece konsol Ã§Ä±ktÄ±larÄ±nda kaÃ§Ä±ÅŸ terminali kolayca ayÄ±rt edilebiliyor.
>
> > ## v3.1.1 - Ã–dÃ¼l ve Ceza Parametre Ä°yileÅŸtirmeleri
> >
> > - **GÃ¼venlik SÄ±nÄ±rÄ± GÃ¼ncellemesi**: `MIN_AGL` (minimum yerden yÃ¼kseklik) eÅŸiÄŸi **0.25 -> 0.35** olarak artÄ±rÄ±ldÄ±. Bu, roketin yere daha gÃ¼venli bir mesafede kalmasÄ±nÄ± zorunlu kÄ±lar.
> > - **Ä°rtifa KÄ±sÄ±tlamasÄ±**: `MAX_ALTITUDE` (maksimum irtifa) **100.0 -> 95.0** olarak dÃ¼ÅŸÃ¼rÃ¼ldÃ¼.
> > - **BaÅŸarÄ± Ã–dÃ¼lÃ¼ ArtÄ±rÄ±mÄ±**: `SUCCESS_REWARD` (baÅŸarÄ± Ã¶dÃ¼lÃ¼) **200.0 -> 210.0** olarak gÃ¼ncellendi.
> > - **DÃ¼ÅŸÃ¼k Ä°rtifa CezasÄ±**: `LOW_ALTITUDE_PENALTY` (dÃ¼ÅŸÃ¼k irtifa cezasÄ±) **-70.0 -> -75.0** olarak artÄ±rÄ±ldÄ±.
>
> > ## v3.2.0 - BaÅŸlangÄ±Ã§ KoÅŸullarÄ± Stabilizasyonu
> >
> > - **Heading Offset KÄ±sÄ±tlamasÄ±**: Reset sÄ±rasÄ±nda roketin rastgele atanan baÅŸlangÄ±Ã§ yÃ¶nÃ¼ sapmasÄ± (heading offset) **Â±45 derece -> Â±5 derece** aralÄ±ÄŸÄ±na dÃ¼ÅŸÃ¼rÃ¼ldÃ¼. Bu, eÄŸitimin baÅŸlangÄ±Ã§ aÅŸamasÄ±nda daha kararlÄ± bir Ã¶ÄŸrenme sÃ¼reci saÄŸlar.
>
> > ## v3.3.0 - Performans ZarflarÄ±nÄ±n GeniÅŸletilmesi ve EÄŸitim Optimizasyonu
> >
> > - **Thrust ve Kontrol Kuvveti ArtÄ±rÄ±mÄ±**:
> >     - `MIN_THRUST` **600.0 -> 580.0**, `MAX_THRUST` **1000.0 -> 1050.0** olarak gÃ¼ncellendi.
> >     - `MAX_PITCH_FORCE` ve `MAX_YAW_FORCE` **1.5 -> 1.7** deÄŸerine Ã§Ä±karÄ±larak manevra kabiliyeti artÄ±rÄ±ldÄ±.
> > - **Ä°rtifa ve Ceza GÃ¼ncellemeleri**:
> >     - `MAX_ALTITUDE` **95.0 -> 100.0** olarak esnetildi.
> >     - `HIGH_ALTITUDE_PENALTY` (yÃ¼ksek irtifa cezasÄ±) **-80.0 -> -82.0** olarak gÃ¼ncellendi.
> > - **EÄŸitim ve Loglama AyarlarÄ±**:
> >     - `ROLLOUT_LEN` **1024 -> 1200** olarak artÄ±rÄ±ldÄ± (daha uzun veri toplama periyodu).
> >     - `SAVE_EVERY_UPDATES` **16 -> 20** olarak gÃ¼ncellendi.
> >     - `STEP_PRINT_EVERY` **50 -> 25** yapÄ±larak konsol takibi sÄ±klaÅŸtÄ±rÄ±ldÄ±.
>
> > ## v3.4.0 - Ä°rtifa Hizalama ve Yer YakÄ±nlÄ±k UyarÄ±sÄ± (Soft Floor)
> >
> > - **Yer YakÄ±nlÄ±k UyarÄ±sÄ± (Soft Floor)**: Roketin 5m altÄ±na indiÄŸi durumlarda terminale girmeden Ã¶nce sÃ¼rekli bir ceza sinyali eklendi (`SOFT_FLOOR = 5.0`). Bu, ajanÄ±n yere tehlikeli yaklaÅŸmasÄ±nÄ± erkenden fark etmesini saÄŸlar.
> > - **Ä°rtifa Hizalama Ã–dÃ¼lÃ¼ (Height Alignment)**: AjanÄ±n hedef irtifaya (target altitude) sadÄ±k kalmasÄ±nÄ± teÅŸvik etmek iÃ§in `height_error` tabanlÄ± yeni bir Ã¶dÃ¼l eklendi (`HEIGHT_ALIGN_GAIN = 0.020`).
> > - **KaÃ§Ä±ÅŸ Terminali Hassasiyeti**: `ESCAPE_MULTIPLIER` **1.5 -> 1.4** seviyesine dÃ¼ÅŸÃ¼rÃ¼lerek hedeften uzaklaÅŸma tespiti daha hassas hale getirildi.
> > - **Ã–dÃ¼l AÄŸÄ±rlÄ±klarÄ± Ä°yileÅŸtirmesi**:
> >     - `DISTANCE_GAIN` **0.30 -> 0.35** ve `CLOSING_RATE_GAIN` **0.010 -> 0.017** olarak artÄ±rÄ±ldÄ±.
> >     - `ALIGNMENT_GAIN` **0.04 -> 0.045** seviyesine Ã§Ä±karÄ±ldÄ±.
> >     - `STEP_PENALTY` ve `ANG_VEL_PENALTY` deÄŸerlerinde kÃ¼Ã§Ã¼k yumuÅŸatmalar yapÄ±ldÄ±.
>
> > ## v3.4.1 - Ä°rtifa Hizalama Hassasiyeti ArtÄ±rÄ±mÄ±
> >
> > - **Ä°rtifa Hizalama Hassasiyeti**: `HEIGHT_ALIGN_GAIN` deÄŸeri **0.020 -> 0.035** olarak artÄ±rÄ±ldÄ± ve ceza mantÄ±ÄŸÄ± (`reward -= gain * error`) stabilize edildi. Bu, roketin hedef irtifaya Ã§ok daha sÄ±kÄ± tutunmasÄ±nÄ± saÄŸlar.
>
> > ## v3.4.2 - Ã–dÃ¼l Ä°nce AyarÄ± ve Analiz AraÃ§larÄ±
> >
> > - **Ä°rtifa Hizalama Dengelenmesi**: `HEIGHT_ALIGN_GAIN` deÄŸeri **0.035 -> 0.015** seviyesine Ã§ekilerek Ã¶dÃ¼l fonksiyonu daha dengeli hale getirildi. Bu, ajanÄ±n irtifa hatasÄ±na aÅŸÄ±rÄ± odaklanÄ±p ana hedefi (mesafe) ihmal etmesini Ã¶nler.
> > - **Yeni Analiz Scripti (`docs/analiz.py`)**: `step_log.csv` verilerini Pandas ile hÄ±zlÄ±ca analiz etmek iÃ§in temel bir script eklendi.
> > - **Reward Test OrtamÄ± (`scripts/reward_test.py`)**: TCP baÄŸlantÄ±sÄ± gerektirmeden `calculate_reward` mantÄ±ÄŸÄ±nÄ± farklÄ± senaryolarla test etmeyi saÄŸlayan kapsamlÄ± bir unit-test benzeri script geliÅŸtirildi.
>
> # v4.0 - Curriculum Learning (MÃ¼fredatlÄ± Ã–ÄŸrenme)
>
> > ## v4.0.0 - MÃ¼fredat Temelli EÄŸitimin BaÅŸlatÄ±lmasÄ± (AdÄ±m 1)
> >
> > - **Curriculum Learning (CL) GeÃ§iÅŸi**: EÄŸitimin daha saÄŸlÄ±klÄ± ve dengeli ilerlemesi iÃ§in aÅŸamalÄ± mÃ¼fredat modeline geÃ§ildi.
> > - **Hareketsiz Hedef (Stationary Target)**: Ä°lk eÄŸitim aÅŸamasÄ±nda hedefin hareketi tamamen devre dÄ±ÅŸÄ± bÄ±rakÄ±ldÄ± (`TARGET_VELOCITY = 0.0`). Hedef, roketin tam tepesinde sabit bekleyecek ÅŸekilde konumlandÄ±rÄ±ldÄ±.
> > - **Lokasyon Sabitleme**: Hedefin baÅŸlangÄ±Ã§ konumu (px, pz) **(300, 300) -> (0, 0)** olarak gÃ¼ncellenerek eÄŸitimin en basit senaryodan baÅŸlamasÄ± saÄŸlandÄ±.
> > - **Temiz BaÅŸlangÄ±Ã§**: CL sÃ¼recinin saÄŸlÄ±klÄ± takibi iÃ§in eski log ve model dosyalarÄ± temizlendi. Yeni mÃ¼fredata uygun modeller bu sÃ¼rÃ¼mden itibaren kaydedilecek.
>
> > ## v4.0.1 - MÃ¼fredat Temelli Ã–ÄŸrenme - AdÄ±m 2: Stabilizasyon
> >
> > - **BaÅŸlangÄ±Ã§ Oryantasyonu Sabitleme**: `env.py` iÃ§indeki `reset` fonksiyonunda `calculate_new_loc` devre dÄ±ÅŸÄ± bÄ±rakÄ±larak `px, pz, ry, rz = 0,0,0,0` olarak sabitlendi. Bu, ajanÄ±n her bÃ¶lÃ¼me tam olarak aynÄ± konum ve yÃ¶nelimle baÅŸlamasÄ±nÄ± saÄŸlar.
> > - **EÄŸitim KararlÄ±lÄ±ÄŸÄ±**: RastgeleliÄŸin (randomness) azaltÄ±lmasÄ±yla ajanÄ±n temel hareketleri ve dengeyi daha hÄ±zlÄ± Ã¶ÄŸrenmesi hedeflenmektedir.
>
> # v5.0 - Yeni State TanÄ±mÄ± ve MÃ¼fredat GeliÅŸimi
>
> > ## v5.0.0 - Yeni State TanÄ±mÄ± ve GeliÅŸmiÅŸ Loglama
> >
> > - **Major State GÃ¼ncellemesi**: State vektÃ¶rÃ¼nden `closing_rate` Ã§Ä±karÄ±larak yerine `look_angle_rad` (bakÄ±ÅŸ aÃ§Ä±sÄ± - radyan) eklendi. Bu, ajanÄ±n hedefe olan yÃ¶nelimini daha hassas algÄ±lamasÄ±nÄ± saÄŸlar.
> > - **State Normalizasyonu**: Yeni eklenen bakÄ±ÅŸ aÃ§Ä±sÄ± iÃ§in `LOOK_ANGLE_SCALE = np.pi` tanÄ±mlandÄ± ve [0, 1] aralÄ±ÄŸÄ±na normalize edildi.
> > - **GeliÅŸmiÅŸ Loglama**: `log.py` gÃ¼ncellenerek `step_log.csv` ve `episode_log.csv` dosyalarÄ±na `look_angle_rad` ve `look_angle_deg` verileri eklendi.
> > - **MÃ¼fredat Takibi**: Curriculum Learning Step 2 (Sabit BaÅŸlangÄ±Ã§) devam ederken yeni state yapÄ±sÄ±yla eÄŸitim kararlÄ±lÄ±ÄŸÄ± hedefleniyor.
>
> > ## v5.0.0a - Reward Fonksiyonu ve Terminal Åart Ä°yileÅŸtirmeleri
> >
> > - **AÃ§Ä± OdaklÄ± Ã–dÃ¼l (Angle Reward)**: `look_angle_rad` Ã¼zerinden hesaplanan `ANGLE_GAIN` Ã¶dÃ¼lÃ¼ eklendi. Burun hedefe baktÄ±kÃ§a Ã¶dÃ¼l artar, ters yÃ¶ne dÃ¶ndÃ¼kÃ§e ceza verilir.
> > - **YÃ¼ksek Sapma Terminali (Bad Angle Terminal)**: Roketin hedeften 135 dereceden fazla saptÄ±ÄŸÄ± durumlar iÃ§in `bad_angle` terminali ve `-60` puanlÄ±k ceza tanÄ±mlandÄ±.
> > - **Ä°rtifa Hizalama Revizyonu**: Ä°rtifa Ã¶dÃ¼lÃ¼ (`HEIGHT_ALIGN_GAIN`) artÄ±k lineer ceza yerine, 50m hata payÄ± iÃ§erisinde pozitif bir Ã§arpan olarak hesaplanÄ±yor.
> > - **Dengeleme**: `DISTANCE_GAIN` deÄŸeri **0.35 -> 0.15** seviyesine Ã§ekilerek aÃ§Ä±sal Ã¶dÃ¼llerle uyumlu hale getirildi.
>
> > ## v5.0.1 - Ã–dÃ¼l ve Terminal ÅartÄ± RefakatÃ§Ä± DÃ¼zenlemeleri
> >
> > - **Terminal ÅartÄ± KaldÄ±rÄ±ldÄ±**: `bad_angle` terminal ÅŸartÄ± `env.py` dosyasÄ±ndan kaldÄ±rÄ±larak ajanÄ±n aÅŸÄ±rÄ± yÃ¶nelmelerde de Ã¶ÄŸrenmeye devam etmesi saÄŸlandÄ±.
> > - **BakÄ±ÅŸ AÃ§Ä±sÄ± HesaplamasÄ± Ä°yileÅŸtirildi (Unity)**: `env.cs` iÃ§erisinde bakÄ±ÅŸ aÃ§Ä±sÄ± (`look_angle_rad`) artÄ±k `Mathf.Acos` kullanÄ±larak daha hassas ve kararlÄ± bir ÅŸekilde hesaplanÄ±yor.
>
> > ## v5.0.2 - Ã–dÃ¼l Ã–lÃ§eklendirme ve BaÅŸarÄ± Metrikleri
> >
> > - **Reward Ã–lÃ§eklendirme (Scale-up)**: `DISTANCE_GAIN` ve `ANGLE_GAIN` gibi temel Ã¶dÃ¼l katsayÄ±larÄ± artÄ±rÄ±larak ajanÄ±n daha gÃ¼Ã§lÃ¼ sinyallerle eÄŸitilmesi saÄŸlandÄ±.
> > - **BaÅŸarÄ± OranÄ± Takibi (Success Rate)**: `train.py` ve `log.py` gÃ¼ncellenerek eÄŸitim sÃ¼resince toplam episode ve baÅŸarÄ± sayÄ±sÄ± (success rate) anlÄ±k olarak takip edilmeye baÅŸlandÄ±.
> > - **Dinamik Konsol Ã‡Ä±ktÄ±sÄ±**: EÄŸitim sÄ±rasÄ±nda konsola yazdÄ±rÄ±lan metrikler daha detaylÄ± hale getirilerek ilerleme gÃ¶rÃ¼nÃ¼rlÃ¼ÄŸÃ¼ artÄ±rÄ±ldÄ±.

> > ### Faz 1 - TamamlandÄ±
> > - Modeller ve loglar ilk kez commit edildi; scripts deÄŸiÅŸmedi.
> > - **BaÅŸlangÄ±Ã§ konfigÃ¼rasyonu** (`env.py` v5.0.2 ile aynÄ±):
> >   - `TARGET_VELOCITY = 0.0` (hedef sabit)
> >   - `reset`: `px, pz, ry, rz = 0, 0, 0, 0` (sabit baÅŸlangÄ±Ã§)
> >   - `calculate_new_loc()` iÃ§inde `px = 0 * np.cos(theta)`, `pz = 0 * np.sin(theta)` (efektif sabit konum)
> >   - `ANGLE_GAIN = 0.22`, `DISTANCE_GAIN = 0.15`
> > - BÃ¼yÃ¼k log dosyalarÄ± 40MB parÃ§alara bÃ¶lÃ¼nerek GitHub'a yedeklendi.
>
> > ### Faz 2 - TamamlandÄ±
> > - Faz 2 mÃ¼fredatlÄ± eÄŸitimi (Curriculum Learning) tamamlandÄ±.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 1 â†’ Faz 2, git diff ile):
> >   - `calculate_new_loc()`: `px`/`pz` artÄ±k `0 * np.cos(theta)` / `0 * np.sin(theta)` yerine `np.random.randint(0,3) * np.cos(theta)` / `np.random.randint(0,3) * np.sin(theta)` (0â€“2 birim, yakÄ±n alan)
> >   - `reset`: `px, pz, ry, rz = 0,0,0,0` â†’ `px, pz, ry, rz = calculate_new_loc()` (dinamik konum ve rz kuzeye yÃ¶nelik)
>
> > ### Faz 3 - TamamlandÄ±
> > - Faz 3 final eÄŸitimi ve stabilizasyon tamamlandÄ±.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 2 â†’ Faz 3, git diff ile):
> >   - BaÅŸlangÄ±Ã§ mesafe Ã§arpanÄ±: `np.random.randint(0,3)` â†’ `np.random.randint(1,5.5)` (1â€“4 birim, daha geniÅŸ alan)
> > - TÃ¼m modeller ve loglar GitHub'a yedeklendi.
>
> > ### Faz 4 - TamamlandÄ±
> > - Faz 4 eÄŸitimi tamamlandÄ±.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 3 â†’ Faz 4):
> >   - BaÅŸlangÄ±Ã§ mesafe Ã§arpanÄ±: `np.random.randint(1,5.5)` â†’ `np.random.randint(2,7)` (2â€“6 birim, daha geniÅŸ alan)
>
> > ### Faz 5 - TamamlandÄ±
> > - Faz 5 eÄŸitimi tamamlandÄ±.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 4 â†’ Faz 5):
> >   - BaÅŸlangÄ±Ã§ mesafe Ã§arpanÄ±: `np.random.randint(2,7)` â†’ `np.random.randint(3,10)` (3â€“9 birim, daha geniÅŸ alan)
>
> > ### Faz 6 - TamamlandÄ±
> > - Faz 6 eÄŸitimi tamamlandÄ±.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 5 â†’ Faz 6):
> >   - BaÅŸlangÄ±Ã§ mesafe Ã§arpanÄ±: `np.random.randint(3,10)` â†’ `np.random.randint(4,11)` (4â€“10 birim, daha geniÅŸ alan)
>
> > ### Faz 7 - TamamlandÄ±
> > - Faz 7 eÄŸitimi tamamlandÄ±.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 6 â†’ Faz 7):
> >   - BaÅŸlangÄ±Ã§ mesafe Ã§arpanÄ±: `np.random.randint(4,11)` â†’ `np.random.randint(7,13)` (7â€“12 birim, daha geniÅŸ alan)
> >   - Ã–dÃ¼l ve ceza ayarlarÄ±: `ANGLE_GAIN = 0.22 â†’ 0.30`, `SUCCESS_REWARD = 210.0 â†’ 250.0`, `HIGH_ALTITUDE_PENALTY = -82.0 â†’ -85.0`, `ESCAPE_PENALTY = -50.0 â†’ -60.0`
> > - **Log yÃ¶netimi**: `logs/step_log.csv` Faz 7 iÃ§in `logs/step_log_faz7.zip` olarak sÄ±kÄ±ÅŸtÄ±rÄ±ldÄ± ve aktif dosya sÄ±fÄ±rlandÄ± (bÃ¼yÃ¼k dosya uyarÄ±larÄ±nÄ± azaltmak iÃ§in).

> > ### Faz 8 - TamamlandÄ±
> > - Faz 8 eÄŸitimi tamamlandÄ±.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 7 â†’ Faz 8):
> >   - BaÅŸlangÄ±Ã§ mesafe Ã§arpanÄ±: `np.random.randint(5.5,12.5)` â†’ `np.random.randint(7,13)` (yaklaÅŸÄ±k 6â€“12 birimden 7â€“12 birime, daha uzak minimum mesafe)

> > ### Faz 9 - TamamlandÄ±
> > - Faz 9 eÄŸitimi tamamlandÄ±.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 8 â†’ Faz 9):
> >   - BaÅŸlangÄ±Ã§ mesafe Ã§arpanÄ±: `np.random.randint(7,13)` â†’ `np.random.randint(9,16)` (9â€“15 birim, hedef baÅŸlangÄ±Ã§ mesafesi belirgin ÅŸekilde bÃ¼yÃ¼dÃ¼)
> >   - Ã–dÃ¼l ve ceza ayarlarÄ±:
> >     - `STEP_PENALTY = -0.018 â†’ -0.022` (adÄ±m baÅŸÄ±na ceza biraz artÄ±rÄ±ldÄ±)
> >     - `DISTANCE_GAIN = 0.15 â†’ 0.17`, `ANGLE_GAIN = 0.30 â†’ 0.40`
> >     - `ANG_VEL_PENALTY = 0.004 â†’ 0.005`
> >     - `ESCAPE_PENALTY = -60.0 â†’ -70.0`, `ESCAPE_GRACE_STEPS = 50 â†’ 55`
> >     - `HEIGHT_ALIGN_GAIN = 0.015 â†’ 0.020`

> > ### Faz 10 - BaÅŸarÄ±sÄ±z (TamamlandÄ±)
> > - Faz 10 eÄŸitimi **tamamlandÄ± ancak hedeflenen baÅŸarÄ± seviyesine ulaÅŸamadÄ±**.
> > - **env.py deÄŸiÅŸiklikleri** (Faz 9 â†’ Faz 10):
> >   - BaÅŸlangÄ±Ã§ mesafe Ã§arpanÄ±: `np.random.randint(9,16)` â†’ `np.random.randint(10.5,20)` (yaklaÅŸÄ±k 11â€“19 birim; Ã§ok uzak baÅŸlangÄ±Ã§ menzili)
> >   - Maksimum adÄ±m sayÄ±sÄ±: `max_step = 1300` â†’ `max_step = 255` (epizot sÃ¼resi ciddi biÃ§imde kÄ±saltÄ±ldÄ±)
> >   - Ã–dÃ¼l/ceza parametreleri:
> >     - `STEP_PENALTY = -0.022 â†’ -0.030` (her adÄ±m iÃ§in daha sert ceza)
> >     - `HIGH_ALTITUDE_PENALTY = -85.0 â†’ -90.0`
> >     - `TIMEOUT_PENALTY = -60.0 â†’ -90.0`
> >     - `HEIGHT_ALIGN_GAIN = 0.020 â†’ 0.025`
> >   - KaÃ§Ä±ÅŸ (escape) mantÄ±ÄŸÄ±: ESCAPE terminal bloÄŸu yoruma alÄ±narak devre dÄ±ÅŸÄ± bÄ±rakÄ±ldÄ± (kaÃ§Ä±ÅŸ durumlarÄ± artÄ±k terminal olmuyor).
> > - **BaÅŸarÄ± oranÄ± (success rate)**: **%54.34** â€” Ã¶nceki fazlara kÄ±yasla belirgin dÃ¼ÅŸÃ¼ÅŸ; bu nedenle Faz 10 **baÅŸarÄ±sÄ±z** olarak iÅŸaretlendi ve bir Ã¶nceki faz (Faz 9) kalÄ±cÄ± referans olarak korunuyor.
