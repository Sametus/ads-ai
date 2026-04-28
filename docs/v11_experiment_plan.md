# V11 Deney Plani

V11'in amaci reward katsayisi kurcalamak degil, once problemin fiziksel olarak
cozulebilir oldugunu kanitlamaktir. Bu nedenle ilk adim klasik gudum testiyle
baslar.

## 1. V11.0 - Klasik Gudum Saglik Testi

- Dosya: `scripts/pn_guidance_test.py`
- Yontem: PN (Proportional Navigation / oransal gudum)
- Amac: Roket, RL olmadan hedefi vurabiliyor mu?
- Basarili olursa yorum: Unity sahnesi, action uygulamasi ve kuvvetler hedefi vurmak icin yeterli.
- Basarisiz olursa yorum: Sorun PPO veya reward degil; once fizik, kuvvet, sahne veya action uygulamasi incelenmeli.

## 1.1. V11.0.1 - Detayli PN Testleri

- PN test scripti artik radius araligini komut satirindan alabilir.
- Nihai senaryo icin `300m` sabit radius dogrudan denenebilir.
- `blend`, `pn` ve `pursuit` modlari vardir.
- `step_delay` ile Unity sahnesinde vurma davranisi yavas izlenebilir.
- Episode ozeti ayri CSV dosyasina yazilir; en yakin mesafe ve o andaki theta takip edilir.

## 1.2. V11.0.2 - Unity Action / Irtifa Guvenligi Duzeltmesi

- Thrust artik `rocketPoint.forward` yonunden uygulanir.
- Dusuk irtifada clock-12 yani yukari toparlama komutu korunur.
- PN testine `--altitude-guard` eklendi.
- PN test thrust varsayilani once `1400` yapildi; V11.0.3'te guard yumusatilirken `1200` seviyesine indirildi. Bu sadece klasik saglik testi icindir, PPO egitim thrust araligini degistirmez.
- Amac: Klasik gudum hedefe donerken roketin yere gomulmesini engelleyip fiziksel vurulabilirligi test etmek.

## 1.3. V11.0.3 - Guard Yumusatma

- Ilk guard denemesi kalkista asiri yukari komut verdi ve `high_altitude` terminaline girdi.
- Guard artik sadece roket asagi hizlaniyorsa veya grace sonrasi kritik alcak irtifadaysa calisir.
- PN test thrust varsayilani `1200` seviyesine indirildi.
- `--terminal-max-altitude` opsiyonu eklendi; bu sadece PN testinde terminal tavanini gecici esnetir.

## 1.4. V11.0.4 - Unity Action Axis Audit

- PN testindeki drift davranisi nedeniyle yeni adim dogrudan "vuruyor mu?" sorusu degildir.
- Once Unity action kanallarinin gercek fizik tepkisi olculur.
- Dosya: `scripts/action_axis_test.py`
- Test: `thrust_only`, `clock_12`, `clock_6`, `clock_3`, `clock_9` sabit komutlari uygulanir.
- Beklenti: `clock_12` olculen clock-12 burun donusunu pozitif, `clock_6` negatif; `clock_3` pozitif, `clock_9` negatif yapmalidir.
- `Env.cs` telemetry alanlari genisletildi: thrust vektoru, istenen clock donusu, command turn, torque command, raw/net action ve rocketPoint/body eksen dot degerleri loglanir.
- Scene view icin renkli debug ray'leri eklendi: cyan burun/itki, yesil clock-12, sari clock-3, beyaz hedef, magenta istenen donus, kirmizi tork.
- Bu adimdan gecmeden PN/BC/RL tarafinda yeni reward denemesi yapilmayacak.

## 1.5. V11.0.5 - Roll Kontrol Onceligi Duzeltmesi

- Ilk axis audit sonucunda `clock_12` kanali beklenen yukari donus tepkisini net veremedi.
- Ayni loglarda aktif steering sirasinda roll duzeltmesinin `torque_local_z` kanalini cok buyuk degerlere tasidigi goruldu.
- Roll kontrolu kaldirilmadi; sadece aktif manevra komutu varken ve clock frame dik konumdayken ikincil seviyeye indirildi.
- Yeni parametreler: `activeSteeringRollScale=0.35`, `rollValidityFloor=0.15`.
- Beklenen etki: roll baskisi korunur, fakat pitch/yaw manevrasi roll stabilizer tarafindan ezilmez.

## 1.6. V11.0.6 - Aşamali Clock-12 Audit

- V11.0.5 tekrari roll baskisinin azaldigini fakat `clock_12` isaretinin hala temiz cikmadigini gosterdi.
- Yorum: roket dik kalkista gravity-up ile ayni eksende oldugu icin clock-12 yonu geometrik olarak tekillesiyor.
- `scripts/action_axis_test.py` icine `clock_12_after_clock_6` komutu eklendi.
- Bu komut once `60` step `clock_6` ile roketi egiyor, sonra `clock_12` verip toparlama isaretini olcuyor.
- Beklenen etki: saf dik-kalkis tekilligi ile gercek clock-12 toparlama yetenegi birbirinden ayrilacak.

## 1.7. V11.0.7 - Roll Saturation Clamp

- V11.0.6 testinde staged clock-12 isareti temiz cikti, fakat bazi kanallarda anlik roll rate cok buyudu.
- Kok neden: roll duzeltmesi olcekleniyordu ama son limit hala tam `maxRollCorrection` oldugu icin `torque_local_z` `±34` saturasyonuna vurabiliyordu.
- Duzeltme: aktif steering sirasinda roll correction limiti de dinamik olarak kucultuldu.
- Yeni telemetry: `roll_correction_limit`.
- Beklenen etki: roll baskisi korunur, fakat aktif manevra sirasinda buyuk z-tork darbeleri engellenir.

## 1.8. V11.0.8 - Fiziksel Roll Tork Limiti

- V11.0.7 testinde command seviyesi kisilse bile fizik motoruna giden `torque_local_z` hala buyuk kalabildi.
- Kok neden: command clamp sonrasi `rollTorqueScale * torqueScale` carpanlari z-torku tekrar buyutuyordu.
- Duzeltme: `AddRelativeTorque` oncesinde son fiziksel z-torku `maxRollTorqueCommand=3.0` ile sinirlandi.
- Yeni telemetry: `roll_torque_limit`.
- Beklenen etki: kalkis aninda buyuk roll impulse'lari azalir; pitch/yaw torklari aynen kalir.

## 1.9. V11.0.9 - Roll Rate Projection

- V11.0.8 sonrasi z-tork limiti calisti ama roketin dusuk roll inertia'si nedeniyle roll rate yine buyuyebildi.
- Karar: roll bu projede ogrenilecek ayri bir hedef degil; roket roll-free kabul edilecek.
- `Env.cs` icine `suppressRollRate=1` ve `rollRateSuppressBlend=1` eklendi.
- Her `Physics.Simulate()` sonrasi roketin kendi forward ekseni etrafindaki angular velocity bileseni temizlenir.
- Roll correction z-torku projection aktifken sifirlanir.
- Yeni telemetry: `suppressed_roll_rate`.
- Beklenen etki: `clock_3/clock_9` kalkisinda `turn_rate_roll` ve `rocket_turn_clock_signed_z` yaklasik sifira inmeli.

## 1.16. V11.0.16 - Acceleration PN Baseline

- Kaynak incelemesine gore PN once yanal ivme komutu uretir, sonra autopilot bu ivmeyi takip eder.
- Eski `blend/pn/pursuit` modlari PN yonunu clock komutuna cevirdigi icin ivme buyuklugunu ve fizik limitini kaybediyordu.
- `scripts/pn_guidance_test.py --mode accel` yeni saglik testidir.
- Varsayilan fizik kabulu: `rocket_mass=50kg`, `thrust=700N`, `gravity_comp=0.95`, `lateral_accel_fraction=0.85`.
- Basari kriteri: Bu mod klasik kontrolle en az bir success uretebilmeli. Uretemezse sonraki odak PPO/reward degil, Unity actuator/fizik modelidir.

## 1.17. V11.0.17 - Velocity Path Correction

- 300m accel testinde theta iyi olmasina ragmen roket 20-28m disaridan gecti.
- Bu, burun hizalamasinin yeterli olmadigini; hiz vektorunun da onleme hattina cekilmesi gerektigini gosterdi.
- Accel mode artik `desired_velocity - rocket_vel` farkindan ek ivme istegi uretir.
- Yeni parametreler: `velocity_track_gain=0.25`, `velocity_accel_fraction=0.65`, `loft_weight=0.20`, `loft_agl=45`.
- `--max-steps` artik env terminalini de gunceller; 300m testleri 700 stepte yanlislikla kesilmez.
- Beklenen etki: 300m testinde miss distance azalacak; roket hedefi sadece takip etmek yerine trajectory hattini da kesise yaklastiracak.

## 1.18. V11.0.18 - Direct Guidance Baseline

- Clock/torque zinciri hala 300m hedefi temiz vuramadigi icin dogrudan dunya ivmesi baseline'i eklendi.
- Direct action paketi: `[-7777, accel_x, accel_y, accel_z, look_x, look_y, look_z]`.
- Unity direct mode'da normal thrust/clock action yolunu bypass eder, `ForceMode.Acceleration` uygular.
- Roket burnu hedefe kilitlenir ve angular velocity sifirlanir; bu testte roll dinamikleri bilincli olarak devre disidir.
- Basari yorumu: Direct mode vurup clock/torque mode vuramazsa action uygulama mimarisi RL icin fazla dolaylidir. Sonraki RL action tasarimi direct acceleration veya desired-velocity komutuna yaklastirilmalidir.

## 2. V11.1 - Klasik Gudum Verisi Toplama

- PN basarili olursa ayni script daha fazla episode ile calistirilir.
- Ucuslar `logs/pn_guidance_test.csv` icinde saklanir.
- Bu veri, modelin hangi durumda hangi yone donmesi gerektigini anlamak icin kullanilir.

## 6. V12.0.0 - RL Direct Acceleration

- Direct baseline hedefi vurdugu icin RL action seti direct acceleration olarak yenilendi.
- Yeni action: `accel_right`, `accel_up`, `accel_forward`.
- Yeni state: hedef yonu, relative velocity, rocket velocity, distance, closing, theta, AGL ve altitude error.
- PPO korunur; once action/state sade mimarisinin egitilebilirligi test edilir.
- Bu calisirsa sonraki algoritma adimi SAC veya TD3 olur. SAC kesif icin, TD3 deterministic continuous control icin adaydir.

## 3. V11.2 - Ogretili Baslangic

- Model tamamen rastgele baslatilmaz.
- PN verisinden hafif davranis kopyalama yapilir.
- Sonra PPO yeniden devreye girer ve kendi deneme-yanilmasi ile ince ayar yapar.

## 4. V12.0 - PPO Disi Algoritma Denemesi

- Ilk aday: SAC.
- Gerekce: Gecmis deneyleri tekrar kullanabildigi icin nadir basari gelen zor ortamlarda PPO'dan daha verimli olabilir.
- Muhtemel action yapisi: `thrust`, `clock_12_axis`, `clock_3_axis`.

## 5. V12.1 - Reward Shaping Revizyonu

- Reward en son tekrar ele alinacak.
- Ana sinyaller: mesafe kapanmasi, hedefe bakma acisi, gorus cizgisi hareketinin azalmasi.
- Terminal cezalar sade tutulacak.

## Takip Kurali

Her degisiklikte:

- Kod icinde kisa aciklama yorumu olacak.
- Kullaniciya sade teknik aciklama verilecek.
- `CHANGELOG.md` icinde dosya, parametre, gerekce ve beklenen etki yazilacak.
