# ADS-AI Hava Savunma Sistemi

ADS-AI, Unity tabanli fizik simulasyonu ile Python tabanli PPO ajani arasinda TCP uzerinden calisan hibrit bir RL projesidir. Unity sahnedeki geometri ve fizik verisini olcer, Python bu veriyi state'e cevirir, reward hesaplar ve aksiyon uretir.

Guncel surum: `v7.3.0`

## Ozet

- Unity tarafinda manuel fizik adimlama (`Physics.Simulate`) kullanilir.
- Python tarafinda PPO ajan egitilir ve test edilir.
- Curriculum fazlari `ADS_AI_PHASE` ile secilir.
- RL state 14 boyutlu sade bir guidance observation olarak tutulur.
- V7 ile birlikte Unity'den gelen genis telemetry paketi, Python reward/action verileriyle birlestirilerek tek bir step CSV dosyasina yazilir.

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

Faz secmek icin:

```powershell
$env:ADS_AI_PHASE="1"
python scripts/train.py
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

- [env.cs](/C:/Users/husey/Desktop/ads_ai/ads_ai/Assets/Scripts/env.cs): action uygular, fizik simule eder, state ve telemetry yollar
- [Connector.cs](/C:/Users/husey/Desktop/ads_ai/ads_ai/Assets/Scripts/Connector.cs): TCP framing ve JSON iletimi
- [CameraFollow.cs](/C:/Users/husey/Desktop/ads_ai/ads_ai/Assets/Scripts/CameraFollow.cs): roket takip kamerasi

## Observation Space

Guncel RL state 14 parametreden olusur:

| Indis | Parametre | Anlam |
| :--- | :--- | :--- |
| 0 | `distance` | Roket ile hedef arasindaki mesafe |
| 1 | `look_angle_rad` | Roketin ileri bakis yonu ile hedef dogrultusu arasindaki aci |
| 2 | `closing_speed` | Hedefe yaklasma hizi. Pozitif deger kapanmayi gosterir |
| 3-5 | `rel_vel_x/y/z` | Hedefin rokete gore bagil hizi |
| 6-8 | `roc_ang_vel_x/y/z` | Roketin acisal hizlari |
| 9-11 | `g_x/y/z` | Yercekim vektorunun secili frame'deki bilesenleri |
| 12 | `agl` | Yerden yukseklik |
| 13 | `alt_error` | Hedef ile roket arasindaki dunya-Y irtifa farki |

`grounded_flag` state vektorune dahil degildir. Reward ve terminal mantigi icin ham sinyal olarak tasinir.

## Reward Yapisi

Reward ailesi su sinyalleri birlikte kullanir:

- Mesafe ilerlemesi: `prev_distance - distance`
- Bakis hizalamasi: `alignment = cos(look_angle_rad)`
- Pozitif kapanma hizi: `closing_speed`
- Acisal hiz cezasi: `roc_ang_vel`
- Irtifa hizalama: `alt_error`
- Terminal katkilar: `success`, `collision`, `low_agl`, `high_altitude`, `timeout`

Reward breakdown alanlari step CSV icinde ayri kolonlar olarak saklanir. Boylece toplam reward sonradan offline olarak yeniden analiz edilebilir.

## Faz Yapisi

Faz secimi `ADS_AI_PHASE` environment variable ile yapilir.

- Faz 1: yakin menzil, dar heading sapmasi, `max_step=500`
- Faz 2: orta menzil, daha genis heading sapmasi, `max_step=700`
- Faz 3: daha zor intercept kosullari, `max_step=900`

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

## V7 Telemetry Loglama

V7 ile birlikte Unity paketi iki parca halinde gelir:

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

V7, telemetry agirlikli gozlemlenebilirlik surumudur. Ana hedef, egitim sirasinda ortaya cikan guidance ve reward sorunlarini step bazinda offline inceleyebilmek ve sonraki reward retune islerini veri temelli hale getirmektir.
