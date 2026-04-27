# V11 Roll / Axis Root Cause Audit

Tarih: 2026-04-27
Aktif takip surumu: v11.0.9

Bu not, PN / reward / PPO denemelerine devam etmeden once Unity sahnesindeki
roket roll davranisinin kok nedenini kaybetmemek icin yazildi.

## 1. Son Axis Test Ozeti

Komut:

```powershell
C:\Users\husey\miniconda3\envs\rl_codes\python.exe scripts\action_axis_test.py --episodes-per-command 1 --steps 120 --step-delay 0.02
```

Son loglar:

- `logs/action_axis_test.csv`
- `logs/action_axis_test_summary.csv`

Ozet bulgular:

- `thrust_only`: roll yok. Bu, sadece thrust ekseninin roll yaratmadigini gosteriyor.
- `clock_6`: beklenen negatif clock-12 donusu temiz. Roll yok.
- `clock_3`: clock-3 isareti dogru ama kalkista roll buyuyor.
- `clock_9`: clock-9 isareti dogru ama kalkista ters isaretli roll buyuyor.
- `clock_12`: saf dik kalkista sign testini gecemiyor.
- `clock_12_after_clock_6`: once egilip sonra clock-12 verilince sign testini geciyor.

En onemli yorum:

- `clock_12` ters degil; dik kalkista gravity-up ile roket burnu ayni hatta oldugu icin clock-12 yonu tekillesiyor.
- Asil roll problemi `clock_3/clock_9` yatay komutlarinda ortaya cikiyor.

Son sayisal durum:

- V11.0.8 sonrasi `torque_local_z` artik `+-3` bandinda sinirli.
- Buna ragmen `clock_3/clock_9` ilk 30 step icinde roll rate yaklasik `3.8 rad/s` seviyesine cikabiliyor.
- Bu, yalnizca "z torkunu biraz kisalim" ile cozulmeyecek bir fizik/inertia problemi oldugunu gosteriyor.

## 2. Env.cs Incelemesi

Ilgili bolumler:

- `ReadAction`: Unity action formati `[thrust, clock_12, clock_6, clock_3, clock_9]`.
- `ApplyAction`: thrust `rocketPoint.forward` yonunde uygulanir.
- `BuildClockFrame`: gravity-up roket burnuna dik duzleme projekte edilir.
- `ComputeRollErrorRad`: roketin `rocketPoint.up` eksenini gravity-up referansina hizalamaya calisir.
- `AddRelativeTorque`: local x/y pitch-yaw, local z roll torku olarak uygulanir.

Kritik kod yolu:

```text
clock command -> desiredClockTurnWorld
desiredClockTurnWorld -> commandTurnWorld = Cross(clockForward, desiredClockTurn)
commandTurnWorld -> local x/y torque
rollError + angularVelocity.z -> local z torque
local torque -> AddRelativeTorque
```

Riskli nokta:

- Roll stabilizer, steering komutu varken bile local z torku uretiyor.
- Bu z torku V11.0.8 ile fiziksel olarak `+-3` bandina sinirlandi.
- Fakat roketin roll inertia'si cok dusuk oldugu icin `3` bile fazla kalabiliyor.

State/reward tarafinda roll:

- `turn_rate_roll`, state vektorune giriyor.
- Reward icinde `reward_roll_penalty` var.
- Ancak bu ceza, fiziksel roll patlamasini engellemez; sadece modelin sonradan ogrenmesini bekler.
- Sim tarafindaki roll davranisi temizlenmeden reward ile duzeltmeye calismak yanlis siralama.

## 3. Unity Scene / Env - env Durumu

Kontrol edilen dosyalar:

- `ads_ai/Assets/Scripts/Env.cs`
- `ads_ai/Assets/Scripts/Env.cs.meta`
- `ads_ai/Assets/Scenes/SampleScene.unity`
- `scripts/env.py`

Sonuc:

- `Env.cs.meta` GUID: `d19c1d16f08a9c349a8073e10bf05485`
- `SampleScene.unity` CombatManager component script GUID ayni.
- `m_EditorClassIdentifier`: `Assembly-CSharp::Env`
- Unity tarafindaki script class adi `Env`.
- Python tarafindaki dosya `scripts/env.py`; bu Unity component degildir.

Yorum:

- `Env.cs` ile `scripts/env.py` farkli seylerdir.
- Unity component icin onemli olan `Env.cs` dosyasi icindeki `public class Env : MonoBehaviour`.
- Mevcut scene baglantisi saglam oldugu icin her kod guncellemesinde CombatManager'a tekrar surukle-birak gerekmez.
- Tekrar surukle-birak ancak su durumlarda gerekir:
  - Unity compile error varsa ve component "Missing Script" olduysa.
  - Dosya adi / class adi uyumsuzsa.
  - Script GUID/meta dosyasi bozulduysa.
  - Yanlis scene acildiysa.

Dikkat:

- `Assets/_Recovery/0.unity` dosyasi da var. Aktif calisilan scene `Assets/Scenes/SampleScene.unity` olmali.

## 4. Roket Yapisinin Incelenmesi

Roket asset:

- FBX: `ads_ai/Assets/Models/Rocket/lod_basic_pbr.fbx`
- GUID: `ede1cf4fbd7be2542986ef97a9d32b46`
- Import globalScale: `0.4`
- FBX import `addColliders: 0`

Scene'de roket:

- Rocket FBX prefab instance olarak sahneye eklenmis.
- Rigidbody ve BoxCollider scene override olarak root GameObject'e eklenmis.
- RocketPoint sonradan child object olarak eklenmis.

RocketPoint:

- local rotation identity.
- local position `{x:0, y:0.0725, z:0.3776}`.
- parent rocket transform.
- Loglarda `rocket_point_body_forward_dot`, `up_dot`, `right_dot` yaklasik `1.0`.

Yorum:

- RocketPoint ile roket body eksenleri cakisiyor.
- Thrust ekseni ve state/debug ekseni buyuk ihtimalle ayni.
- Roll sorunu eksen uyumsuzlugundan cok fizik/inertia ve roll controller kaynakli gorunuyor.

Rigidbody:

- mass: `50`
- angular damping: `0.05`
- constraints: `0`
- use gravity: `1`
- collision detection: `2`
- implicit center of mass: `1`
- implicit inertia tensor: `1`

Collider:

- BoxCollider size: `{x:0.15, y:0.15, z:0.76}`
- Center: `{x:0, y:0.06, z:0}`

Basit inertia hesabi:

```text
mass = 50
box = 0.15 x 0.15 x 0.76
pitch/yaw inertia yaklasik = 2.50 kg*m^2
roll inertia yaklasik      = 0.1875 kg*m^2
oran                       = 13.3x
```

Yani ayni tork:

- pitch/yaw ekseninde yavas etki eder.
- roll ekseninde yaklasik 13 kat daha hizli acisal ivme uretir.

Bu, "neden kucuk roll torku bile takla/roll gibi gorunuyor?" sorusunun en guclu cevabi.

## 5. Uzman Onerilerinde Roll Var Mi?

Uzman goruslerinde roll kelimesi dogrudan ana baslik degildi.

Ancak uzmanin asil siralamasi suydu:

1. Once klasik PN baseline ile sim fiziksel olarak cozulebilir mi bak.
2. PN bile cozemiyorsa sorun RL/reward degil, sim/action tarafindadir.
3. Sonra imitation/pretraining veya PPO disi algoritmalara gec.
4. Reward shaping en son yeniden ele alinmali.

Bizim mevcut bulgumuz bu siralamayi destekliyor:

- PN/pursuit davranisi drift/roll/irtifa sorununa takildi.
- Axis testleri action kanallarinin tam temiz olmadigini gosterdi.
- O halde once roket fizik/action otoritesi stabilize edilmeli.

Uzmanin "actor tanh doygunlugu" notu su an ikinci planda:

- Policy henuz asil sorun degil.
- Model dogru action verse bile Unity tarafindaki roll/fizik yan etkisi davranisi bozabilir.

## 6. Kok Neden Adaylari

En guclu adaylar:

1. Roll inertia cok dusuk.
   - BoxCollider uzun ve ince oldugu icin local z roll ekseni cok kolay hizlaniyor.
2. Roll stabilizer tork tabanli.
   - Gravity-up referansina roll hizalamaya calisirken aktif steering sirasinda z torku uretiyor.
3. Angular damping cok dusuk.
   - `0.05`, roll hizini hizli sonumlemiyor.
4. Constraints kapali.
   - Rigidbody constraints `0`, roll tamamen serbest.
5. Reward roll'u cezalandiriyor ama fiziksel problemi engellemiyor.

Daha zayif adaylar:

- RocketPoint/body eksen uyumsuzlugu: loglarda dot degerleri `1.0`; zayif aday.
- Thrust ekseni yanlisligi: thrust-only roll uretmedi; zayif aday.
- Env.cs / env.py karisikligi: Unity component GUID ve class dogru; zayif aday.

## 7. Onerilen Teknik Karar

Bir sonraki kod degisikligi kucuk parametre kisma olmamali.

Once su iki yoldan biri secilmeli:

### Yol A: Roll'u fiziksel olarak kilitle / projekte et

Amac:

- Roket roll yapmiyor varsayimini simde garanti etmek.

Basit runtime mantigi:

```csharp
Vector3 rollAngularVelocity = Vector3.Project(rocketRb.angularVelocity, rocketPoint.forward);
rocketRb.angularVelocity -= rollAngularVelocity;
```

Bu, her step sonunda roketin forward ekseni etrafindaki roll rate'i temizler.

Artisi:

- Roll problemi kokten biter.
- Clock frame daha kararlı olur.
- RL state/action daha anlamli hale gelir.

Eksisi:

- Tam fiziksel serbestlik degil; bilincli stabilizasyon varsayimi olur.

### Yol B: Inertia tensor'u manuel ayarla

Amac:

- Roll eksenini fiziksel olarak daha agir yap.

Ornek fikir:

```csharp
rocketRb.inertiaTensor = new Vector3(2.5f, 2.5f, 15f);
rocketRb.inertiaTensorRotation = Quaternion.identity;
```

Artisi:

- Roll tamamen kilitlenmez.
- Daha fizik benzeri bir stabilizasyon hissi verir.

Eksisi:

- Degerleri tekrar test etmek gerekir.
- Unity implicit tensor ile karismamasi icin runtime'da net uygulanmali.

### Benim tercih ettigim sira

1. Once Yol A ile local roll rate projection test edilmeli.
2. Axis test temizlenirse PN/autopilot baseline'a geri donulmeli.
3. Sonra gerekirse Yol B daha fiziksel alternatif olarak denenmeli.

Gerekce:

- Bu projenin amaci roll kontrol ogretmek degil, hedefe yonelme/interception.
- Roll serbestligi state/action uzayini gereksiz zorlastiriyor.
- Kullanici tasariminda da "roket roll yapmiyor" varsayimi daha once konusuldu.

## 9. Uygulanan Karar: V11.0.9

V11.0.9 ile Yol A uygulandi.

Degisenler:

- `Env.cs`: `suppressRollRate=true`, `rollRateSuppressBlend=1.0`.
- `Env.cs`: her `Physics.Simulate()` sonrasi `SuppressRollRate()` calisir.
- `Env.cs`: projection aktifken roll stabilizer z-torku sifirlanir.
- `SampleScene.unity`: Env component serialize alanlari senkronlandi.
- `scripts/env.py`: `suppressed_roll_rate` telemetry alani eklendi.
- `scripts/action_axis_test.py`: `suppressed_roll_rate` step loguna ve `mean_suppressed_roll_rate` summary alanina eklendi.

Beklenen axis test sonucu:

- `clock_3/clock_9` kalkisinda `measured_roll_rate` belirgin sekilde sifira yakin kalmali.
- `suppressed_roll_rate` buyukse bu, projection'in gercekten roll bilesenini temizledigini gosterir.
- `clock_12_after_clock_6` sign_ok `1` kalmali.

## 8. Devam Etmeden Once Kontrol Listesi

- `clock_3/clock_9` kalkis roll rate `~3.8 rad/s` seviyesinden belirgin dusmeli.
- `clock_12_after_clock_6` sign_ok `1` kalmali.
- `clock_6` sign_ok `1` kalmali.
- `rocket_point_body_*_dot` degerleri `~1.0` kalmali.
- `thrust_only` roll uretmemeli.
- PN testi ancak bu axis audit temizlendikten sonra tekrar kosulmali.
