# ADS-AI Hava Savunma Sistemi

ADS-AI, Unity tabanli fizik simulasyonu ile Python tabanli PPO ajani arasinda TCP uzerinden calisan hibrit bir RL projesidir. Unity sahnedeki geometri ve fizik verisini olcer, Python bu veriyi state'e cevirir, reward hesaplar ve aksiyon uretir.

Guncel surum: `v8.7.5`

## Ozet

- Unity tarafinda manuel fizik adimlama (`Physics.Simulate`) kullanilir.
- Python tarafinda PPO ajan egitilir ve test edilir.
- Egitim kosullari [env.py](/C:/Users/husey/Desktop/ads_ai/scripts/env.py) icindeki tek `ACTIVE_PHASE_CONFIG` blogu elle duzenlenerek yonetilir.
- RL state 14 boyutlu gravity-based guidance observation olarak tutulur.
- V7 telemetry hattina ek olarak V8 ile gravity-based guidance frame ve semantic action semantigi eklendi.

## Hizli Baslangic

1. Unity Hub ile [ads_ai](/C:/Users/husey/Desktop/ads_ai/ads_ai) klasorunu acin.
2. `SampleScene` sahnesini acin.
3. Unity Editor icinde `Play`e basin.
4. Ayri bir terminalde Python ortamini aktif edin.
5. Egitim icin:

```bash
python scripts/train.py
```

6. Test icin:

```bash
python scripts/test.py
```

Yeni bir faz denemek icin:

```powershell
scripts/env.py icindeki ACTIVE_PHASE_CONFIG degerlerini degistir
```

## Python Ortami

Windows GPU uyumlulugu icin proje `Python 3.7.16` ile hazirlanmistir.

```bash
conda create -n ads_ai python=3.7.16
conda activate ads_ai
pip install tensorflow==2.10.0 numpy==1.21.6 pandas==1.3.5 pydantic==1.10.8 plotly
```

## Mimari

### Python Katmani

- [scripts/agent.py](/C:/Users/husey/Desktop/ads_ai/scripts/agent.py): PPO actor-critic modeli
- [scripts/env.py](/C:/Users/husey/Desktop/ads_ai/scripts/env.py): Unity ile Python arasindaki RL koprusu, state parse/normalize ve reward hesabi
- [scripts/train.py](/C:/Users/husey/Desktop/ads_ai/scripts/train.py): egitim dongusu
- [scripts/test.py](/C:/Users/husey/Desktop/ads_ai/scripts/test.py): kayitli model ile test kosusu
- [scripts/log.py](/C:/Users/husey/Desktop/ads_ai/scripts/log.py): CSV ve konsol loglama
- [scripts/reward_test.py](/C:/Users/husey/Desktop/ads_ai/scripts/reward_test.py): reward mantigini TCP olmadan test eden arac

### Unity Katmani

- [Env.cs](/C:/Users/husey/Desktop/ads_ai/ads_ai/Assets/Scripts/Env.cs): action uygular, fizik simule eder, state ve telemetry yollar
- [Connector.cs](/C:/Users/husey/Desktop/ads_ai/ads_ai/Assets/Scripts/Connector.cs): TCP framing ve JSON iletimi
- [CameraFollow.cs](/C:/Users/husey/Desktop/ads_ai/ads_ai/Assets/Scripts/CameraFollow.cs): roket takip kamerasi

## Observation Space

Guncel RL state 14 parametreden olusur:

| Indis | Parametre | Anlam |
| :--- | :--- | :--- |
| 0 | `distance` | Roket ile hedef arasindaki mesafe |
| 1 | `theta_rad` | Roketin burnu ile hedef dogrultusu arasindaki yon-suz genel hata acisi |
| 2 | `alpha_rad` | Gravity referansli dikey signed hata. Hedef yukaridaysa `+`, asagidaysa `-` |
| 3 | `beta_rad` | Gravity referansli yatay signed hata. Hedef sagdaysa `+`, soldaysa `-` |
| 4 | `closing_speed` | Hedefe yaklasma hizi. Pozitif deger kapanmayi gosterir |
| 5-7 | `rel_vel_right/up/forward` | Guidance frame icindeki bagil hiz bilesenleri |
| 8-10 | `turn_rate_vertical/horizontal/roll` | Guidance frame icindeki acisal hiz bilesenleri |
| 11 | `forward_up_dot` | Roket burnunun gravity-up ile iliskisi. Pozitifse daha yukari bakar |
| 12 | `agl` | Yerden yukseklik |
| 13 | `alt_error` | Hedef ile roket arasindaki dunya-Y irtifa farki |

`grounded_flag` state vektorune dahil degildir. Reward ve terminal mantigi icin ham sinyal olarak tasinir.

V8'in ana farki, eski `look_angle + body-frame torque` yapisindan gravity-based guidance representation'a gecmesidir. `theta` toplam hata buyuklugunu, `alpha` dikey yonu, `beta` yatay yonu tasir.

## Action Space

Action boyutu yine 3'tur, fakat anlamlari degisti:

- `thrust`
- `vertical_cmd`
- `horizontal_cmd`

Python tarafi artik dogrudan body `pitch/yaw` torque istemez. Bunun yerine semantic guidance komutlari yollar. Unity, o anki roket durusu ile gravity arasindaki iliskiyi kullanip bu komutlari local torque'a cevirir.

## Reward Yapisi

Reward ailesi su sinyalleri birlikte kullanir:

- Mesafe ilerlemesi: `prev_distance - distance`
- Bakis hizalamasi: `alignment = cos(theta_rad)`
- Pozitif kapanma hizi: `closing_speed`
- Guidance-frame acisal hiz cezasi: `turn_rate_ref`
- Irtifa hizalama: `alt_error`
- Terminal katkilar: `success`, `collision`, `low_agl`, `high_altitude`, `timeout`

Reward breakdown alanlari step CSV icinde ayri kolonlar olarak saklanir. Boylece toplam reward sonradan offline olarak yeniden analiz edilebilir.

## Faz Yapisi

Repo artik tek aktif faz mantigi ile calisir. Yeni bir curriculum adimi acilacaginda [env.py](/C:/Users/husey/Desktop/ads_ai/scripts/env.py) icindeki `ACTIVE_PHASE_CONFIG` elle guncellenir ve yeni kosu o ayarlarla baslatilir.

- aktif menzil, heading ve reward ayarlari tek blokta tutulur
- onceki fazlar git commit / archive ile korunur
- yeni faza gecmeden once mevcut pencerenin success koridoru loglardan olculur

## Phase 2.0 Snapshot

Phase 2.0 retry kosusu `up2100` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_2_0 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_2_0)
- secilen devam modeli: [ppo_model_up2100.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_2_0/models/ppo_model_up2100.keras)
- success rate grafigi: [phase_2_0_success_rate.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_2_0/logs/phase_2_0_success_rate.png)
- start distance dagilim grafigi: [phase_2_0_start_distance_distribution.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_2_0/logs/phase_2_0_start_distance_distribution.png)
- checkpoint aday grafigi: [phase_2_0_checkpoint_candidates.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_2_0/logs/phase_2_0_checkpoint_candidates.png)
- reward bilesen grafigi: [phase_2_0_reward_components.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_2_0/logs/phase_2_0_reward_components.png)
- turn/action grafigi: [phase_2_0_turn_action_alignment.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_2_0/logs/phase_2_0_turn_action_alignment.png)

Phase 2.0 sonuc ozeti:

- ana oturum episode: `1209`
- ana oturum success: `1116`
- ana oturum genel success rate: `%92.308`
- secilen handoff checkpoint: `up2100`
- `up2101-up2120` post-window success rate: `%94.615`
- `up2120` sonrasi resume oturumunda drift goruldu; bu nedenle `up2120` ve sonrasi aktif modellerden temizlendi

Bir sonraki faz icin yon:

- warm-start `up2100` uzerinden devam edilmeli
- heading sapmasi ayni tutulmali
- spawn radius bandi `95-105` araligina kaydirilmali
- `max_step` degeri `500` olarak kullanilmali
- Faz 2.0 retry reward/action duzeltmeleri korunmali

## Phase 1.9 Snapshot

Phase 1.9 kosusu `up1920` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_9 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_9)
- secilen devam modeli: [ppo_model_up1920.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_9/models/ppo_model_up1920.keras)
- success rate grafigi: [phase_1_9_success_rate.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_9/logs/phase_1_9_success_rate.png)
- success yogunlugu: [phase_1_9_success_rug.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_9/logs/phase_1_9_success_rug.png)
- reset polar grafigi: [phase_1_9_reset_outcome_polar.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_9/logs/phase_1_9_reset_outcome_polar.png)
- radius dagilim grafigi: [phase_1_9_reset_radius_distribution.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_9/logs/phase_1_9_reset_radius_distribution.png)
- faz bantli radius plani: [phase_1_9_reset_radius_phase_plan.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_9/logs/phase_1_9_reset_radius_phase_plan.png)

Phase 1.9 sonuc ozeti:

- episode: `499`
- success: `448`
- genel success rate: `%89.780`
- guncel rolling 100 success rate: `%98.000`
- guncel rolling 200 success rate: `%98.000`
- en iyi rolling 100 success rate: `%99.000`
- en iyi rolling 200 success rate: `%98.000`
- en iyi 20-update koridoru: `%99.291`, `update 1897-1916`
- secilen handoff checkpoint: `up1920`

Bir sonraki faz icin yon:

- warm-start `up1920` uzerinden devam edilmeli
- heading sapmasi ayni tutulmali
- menzil bandi `90-100 radius` araligina kaydirilmali
- `max_step` degeri `480` olarak korunmali
- mevcut reward seti ilk denemede aynen korunmali

## Phase 1.8 Snapshot

Phase 1.8 kosusu `up1840` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_8 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_8)
- secilen devam modeli: [ppo_model_up1840.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_8/models/ppo_model_up1840.keras)
- success rate grafigi: [phase_1_8_success_rate.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_8/logs/phase_1_8_success_rate.png)
- success yogunlugu: [phase_1_8_success_rug.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_8/logs/phase_1_8_success_rug.png)
- reset polar grafigi: [phase_1_8_reset_outcome_polar.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_8/logs/phase_1_8_reset_outcome_polar.png)
- radius dagilim grafigi: [phase_1_8_reset_radius_distribution.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_8/logs/phase_1_8_reset_radius_distribution.png)
- faz bantli radius plani: [phase_1_8_reset_radius_phase_plan.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_8/logs/phase_1_8_reset_radius_phase_plan.png)

Phase 1.8 sonuc ozeti:

- episode: `687`
- success: `623`
- genel success rate: `%90.684`
- guncel rolling 100 success rate: `%93.000`
- guncel rolling 200 success rate: `%92.500`
- en iyi rolling 100 success rate: `%99.000`
- en iyi rolling 200 success rate: `%95.500`
- secilen handoff checkpoint: `up1840`

Bir sonraki faz icin yon:

- warm-start `up1840` uzerinden devam edilmeli
- heading sapmasi ayni tutulmali
- menzil bandi `85-95 radius` araligina kaydirilmali
- `max_step` degeri `480` olarak korunmali
- mevcut reward seti ilk denemede aynen korunmali

## Phase 1.7 Snapshot

Phase 1.7 kosusu `up1740` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_7 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_7)
- secilen devam modeli: [ppo_model_up1740.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_7/models/ppo_model_up1740.keras)
- success rate grafigi: [phase_1_7_success_rate.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_7/logs/phase_1_7_success_rate.png)
- success yogunlugu: [phase_1_7_success_rug.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_7/logs/phase_1_7_success_rug.png)
- reset polar grafigi: [phase_1_7_reset_outcome_polar.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_7/logs/phase_1_7_reset_outcome_polar.png)
- radius dagilim grafigi: [phase_1_7_reset_radius_distribution.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_7/logs/phase_1_7_reset_radius_distribution.png)
- faz bantli radius plani: [phase_1_7_reset_radius_phase_plan.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_7/logs/phase_1_7_reset_radius_phase_plan.png)

Phase 1.7 sonuc ozeti:

- episode: `3948`
- success: `2614`
- genel success rate: `%66.211`
- guncel rolling 100 success rate: `%5.000`
- guncel rolling 200 success rate: `%5.000`
- guncel rolling 300 success rate: `%5.667`
- en iyi rolling 100 success rate: `%100.000`
- en iyi rolling 200 success rate: `%98.000`
- en iyi rolling 300 success rate: `%95.000`
- secilen handoff checkpoint: `up1740`

Bir sonraki faz icin yon:

- warm-start `up1740` uzerinden devam edilmeli
- heading sapmasi ayni tutulmali
- menzil bandi `80-90 radius` araligina kaydirilmali
- `max_step` degeri `480` olarak guncellenmeli
- mevcut reward seti ilk denemede aynen korunmali

## Phase 1.6 Snapshot

Phase 1.6 kosusu `up1460` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_6 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_6)
- secilen devam modeli: [ppo_model_up1460.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_6/models/ppo_model_up1460.keras)
- success rate grafigi: [phase_1_6_success_rate.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_6/logs/phase_1_6_success_rate.png)
- success yogunlugu: [phase_1_6_success_rug.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_6/logs/phase_1_6_success_rug.png)
- reset polar grafigi: [phase_1_6_reset_outcome_polar.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_6/logs/phase_1_6_reset_outcome_polar.png)
- radius dagilim grafigi: [phase_1_6_reset_radius_distribution.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_6/logs/phase_1_6_reset_radius_distribution.png)
- faz bantli radius plani: [phase_1_6_reset_radius_phase_plan.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_6/logs/phase_1_6_reset_radius_phase_plan.png)

Phase 1.6 sonuc ozeti:

- episode: `637`
- success: `600`
- genel success rate: `%94.192`
- guncel rolling 100 success rate: `%94.000`
- guncel rolling 200 success rate: `%95.000`
- guncel rolling 300 success rate: `%94.000`
- en iyi rolling 100 success rate: `%100.000`
- en iyi rolling 200 success rate: `%98.500`
- secilen handoff checkpoint: `up1460`

Bir sonraki faz icin yon:

- warm-start `up1460` uzerinden devam edilmeli
- heading sapmasi ayni tutulmali
- menzil bandi `75-85 radius` araligina kaydirilmali
- mevcut reward seti ilk denemede aynen korunmali

## Phase 1.5 Snapshot

Phase 1.5 kosusu `up1380` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_5 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_5)
- secilen devam modeli: [ppo_model_up1380.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_5/models/ppo_model_up1380.keras)
- success rate grafigi: [phase_1_5_success_rate.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_5/logs/phase_1_5_success_rate.png)
- success yogunlugu: [phase_1_5_success_episode_rug.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_5/logs/phase_1_5_success_episode_rug.png)
- reset polar grafigi: [phase_1_5_reset_outcome_polar.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_5/logs/phase_1_5_reset_outcome_polar.png)
- radius dagilim grafigi: [phase_1_5_reset_radius_distribution.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_5/logs/phase_1_5_reset_radius_distribution.png)
- faz bantli radius plani: [phase_1_5_reset_radius_phase_plan.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_5/logs/phase_1_5_reset_radius_phase_plan.png)

Phase 1.5 sonuc ozeti:

- episode: `1291`
- success: `1015`
- genel success rate: `%78.621`
- guncel rolling 100 success rate: `%88.000`
- guncel rolling 200 success rate: `%91.000`
- guncel rolling 300 success rate: `%91.000`
- en iyi rolling 100 success rate: `%95.000`
- en iyi rolling 200 success rate: `%92.500`
- secilen handoff checkpoint: `up1380`

Bir sonraki faz icin yon:

- warm-start `up1380` uzerinden devam edilmeli
- heading sapmasi ayni tutulmali
- menzil bandi `71-81 radius` araligina kaydirilmali
- mevcut reward seti ilk denemede aynen korunmali

## Phase 1.4 Snapshot

Phase 1.4 kosusu `up1200` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_4 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_4)
- secilen devam modeli: [ppo_model_up1200.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_4/models/ppo_model_up1200.keras)
- grafik: [success_rate_phase_1_4.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_4/logs/success_rate_phase_1_4.png)
- success yogunlugu: [success_episode_rug.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_4/logs/success_episode_rug.png)

Phase 1.4 sonuc ozeti:

- episode: `5790`
- success: `1235`
- genel success rate: `%21.330`
- guncel rolling 100 success rate: `%67.000`
- guncel rolling 200 success rate: `%67.000`
- en iyi rolling 100 success rate: `%72.000`
- en iyi rolling 200 success rate: `%70.000`
- secilen handoff checkpoint: `up1200`

Bir sonraki faz icin yon:

- warm-start `up1200` uzerinden devam edilmeli
- heading sapmasi ayni tutulmali
- menzil bandi `62-82 radius` araligina kaydirilmali
- mevcut reward seti ilk denemede aynen korunmali

## Phase 1.3 Snapshot

Phase 1.3 kosusu `up800` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_3 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_3)
- secilen devam modeli: [ppo_model_up800.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_3/models/ppo_model_up800.keras)
- grafik: [success_rate_phase1_3.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_3/logs/success_rate_phase1_3.png)

Phase 1.3 sonuc ozeti:

- episode: `1817`
- success: `855`
- genel success rate: `%47.056`
- en iyi rolling 100 success rate: `%67.000`
- en iyi rolling 200 success rate: `%61.000`
- secilen handoff checkpoint: `up800`

Phase 2.1 icin yon:

- warm-start `up800` uzerinden devam edilmeli
- ayni fazi uzatmak yerine daha yumusak bir faz 2 gecisi uygulanmali
- fiili baslangic mesafesi `82-87.5` cekirdegi korunup heading sapmasi ve episode ufku kontrollu buyutulmeli

## Phase 1.2 Snapshot

Phase 1.2 kosusu `up520` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_2 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_2)
- secilen devam modeli: [ppo_model_up520.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_2/models/ppo_model_up520.keras)
- grafik: [success_rate_phase1_2.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_2/logs/success_rate_phase1_2.png)

Phase 1.2 sonuc ozeti:

- episode: `1621`
- success: `308`
- genel success rate: `%19.001`
- en iyi kümülatif success rate: `%27.957` (`episode 930`, `update 529`)
- en iyi rolling 200 success rate: `%35.500`
- baskin failure modu: `high_altitude`

Phase 1.3 icin yon:

- warm-start `up520` uzerinden devam edilmeli
- once peak koridor stabilize edilmeli, sonra zorluk buyutulmeli
- fiili baslangic mesafesi `80-90` bandini koruyacak ufak menzil kaydirma ve daha korumaci optimizer ayarlari planlanmali

## Phase 1.1 Snapshot

Phase 1.1 kosusu `up340` modelinde donduruldu ve repo icinde arsivlendi:

- [phase_1_1 archive](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_1)
- warm-start modeli: [ppo_model_up340.keras](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_1/models/ppo_model_up340.keras)
- grafik: [success_rate_phase1_latest.png](/C:/Users/husey/Desktop/ads_ai/archives/phase_1_1/logs/success_rate_phase1_latest.png)

Phase 1.1 sonuc ozeti:

- episode: `1640`
- success: `161`
- success rate: `%9.817`
- baskin failure modu: `high_altitude`

Phase 1.1, sonraki Phase 1.2 calismasi icin warm-start tabani olarak korunmustur.

## V7-V8 Telemetry Loglama

Unity paketi iki parca halinde gelir:

- `states`: ajanin gordugu 14 boyutlu RL observation
- `telemetry`: world/local frame geometri ve fizik debug verileri

Step CSV dosyasi artik tek satirda su gruplari birlestirir:

- RL state alanlari
- Python aksiyonlari ve normalize aksiyonlari
- `value_pred` ve `action_logp`
- reward breakdown alanlari
- episode icindeki kume reward (`episode_return_so_far`)
- Unity world/local telemetry alanlari

Telemetry tarafinda roket, hedef ve roket-hedef ciftine ait su veriler saklanir:

- world konumlari
- Euler ve quaternion rotasyonlari
- forward / up yonleri
- world ve roket-local hizlar
- world ve roket-local acisal hizlar
- relative position / direction / velocity
- gravity world/local
- guidance frame yonleri
- guidance frame hiz ve turn-rate bilesenleri
- uygulanan semantic turn komutlarinin world/local izdususleri
- `target_speed`

Bu sayede mevcut reward yapisi veya yeni reward adaylari, sadece CSV uzerinden offline olarak tekrar analiz edilebilir.

## Log ve Model Politikasi

Repo kokundeki `logs/` ve `models/` ciktilari varsayilan olarak git disindadir.

Log semasi degistiginde [scripts/log.py](/C:/Users/husey/Desktop/ads_ai/scripts/log.py), mevcut CSV dosyalarini `.bak_YYYYMMDD_HHMMSS.csv` adi ile yedekler ve yeni basliklarla temiz log olusturur.

## Analiz

Episode log uzerinden kumulatif basari orani grafigi icin:

```bash
python docs/analiz.py
```

## Durum

V8, gravity-based state/action redesign surumudur. Ana hedef, roketin hedefe gore yon bilgisini sadece skalar `look_angle` ile degil, gravity referansli signed guidance hatalari ile temsil etmek ve RL ajaninin body torque yerine semantic guidance komutu ogrenmesini saglamaktir.
