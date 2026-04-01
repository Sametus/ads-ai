# ADS-AI Hava Savunma Sistemi

ADS-AI, Unity tabanli fizik simulasyonu ile Python tabanli PPO ajani arasinda TCP uzerinden calisan hibrit bir RL projesidir. Sistem, roketin hedefe gore geometrik durumu Unity tarafinda olcup Python tarafinda normalize ederek karar verir.

Guncel surum: `v6.0.0`

## Proje Ozeti

- Unity tarafinda manuel fizik adimlama (`Physics.Simulate`) kullanilir.
- Python tarafinda PPO ajanı egitilir ve test edilir.
- Egitim, curriculum learning mantigiyla giderek zorlasan reset senaryolari uzerinden ilerler.
- V6 ile observation yapisi guidance-first tasarima gecmistir; tekrar eden feature'lar yerine LOS acilari, kapanma hizi, acisal hiz ve irtifa farki gibi daha dogrudan guidance sinyalleri kullanilir.

## Hizli Baslangic

1. Unity Hub ile `ads_ai/` klasorunu acin.
2. `SampleScene` sahnesini acin.
3. Unity Editor icinde `Play`e basin.
4. Ayrı bir terminalde Python ortamini aktif edin.
5. Egitim icin:

```bash
python scripts/train.py
```

6. Test icin:

```bash
python scripts/test.py
```

## Python Ortami

Windows GPU uyumlulugu icin proje `Python 3.7.16` ile hazirlanmistir.

```bash
conda create -n ads_ai python=3.7.16
conda activate ads_ai
pip install tensorflow==2.10.0 numpy==1.21.6 pandas==1.3.5 pydantic==1.10.8 plotly
```

## Mimari

### Python Katmani (`scripts/`)

- `agent.py`: PPO actor-critic modeli.
- `env.py`: Unity ile Python arasindaki RL koprusu, state parse/normalize ve reward hesaplari.
- `train.py`: egitim dongusu.
- `test.py`: kayitli model ile deterministik/stokastik test.
- `log.py`: CSV ve konsol loglama.
- `reward_test.py`: reward mantigini TCP olmadan test eden senaryo dosyasi.

### Unity Katmani (`ads_ai/Assets/Scripts/`)

- `Env.cs`: sahne state'ini toplar, action uygular, fizik simule eder ve Python'a observation yollar.
- `Connector.cs`: TCP framing ve JSON iletimi.
- `CameraFollow.cs`: roket takip kamerası.

## Teknik Parametreler

### Durum Uzayi (Observation Space - 18 Parametre)

V6 observation yapisi guidance-first mantigina gore tasarlanmistir. State vektoru:

| Indis | Parametre | Aciklama |
| :--- | :--- | :--- |
| **0-1** | `los_yaw_sin`, `los_yaw_cos` | Hedefin roket burun eksenine gore yatay LOS hatasi. |
| **2-3** | `los_pitch_sin`, `los_pitch_cos` | Hedefin dikey LOS hatasi. |
| **4** | `distance` | Hedefe kalan mutlak mesafe. |
| **5** | `closing_speed` | Roketin hedefe yaklasma/uzaklasma hizi. Pozitif deger kapanmayi ifade eder. |
| **6-8** | `rel_vel_x, y, z` | Hedefin rokete gore bagil hizi. |
| **9-11** | `roc_ang_vel_x, y, z` | Roketin acisal hizi. |
| **12-14** | `g_x, g_y, g_z` | Yercekim vektorunun local frame izdüsümü. |
| **15** | `agl` | Yerden yukseklik (raycast tabanli). |
| **16** | `alt_error` | Hedef ile roket arasindaki dunya-Y irtifa farki. |
| **17** | `time_remaining` | Episode icinde kalan sure orani. |

### Aksiyon Uzayi

- `thrust`: surekli itki kuvveti.
- `pitch_f`: pitch torku.
- `yaw_f`: yaw torku.

### Reward Yapisi

Reward ailesi V6'da korunmus, ancak yeni guidance feature'lari ile tekrar kurulmustur:

- LOS alignment odulu: `alignment = los_yaw_cos * los_pitch_cos`
- Mesafe ilerleme odulu: `prev_distance - distance`
- Pozitif kapanma hizi odulu: `closing_speed`
- Acisal hiz cezasi: `roc_ang_vel`
- Irtifa hizalama odulu: `abs(alt_error)`
- Terminal kosullar: `success`, `collision`, `low_agl`, `high_altitude`, `timeout`

## Curriculum Learning Notu

Bu surumde curriculum faz mesafeleri ve `TARGET_VELOCITY = 0.0` davranisi korunmustur. V6'nin amaci moving-target final senaryosuna gecmeden once observation/reward tabanini yeniden kurmaktir.

Bir sonraki buyuk adimda hedefin:

- merkezden cok daha uzakta baslamasi,
- merkeze gore belli bir sapma ile yonlenmesi,
- sabit hizla hareket etmesi

gibi zorlayici final senaryolar icin ayni kod tabani uzerinden daha guvenilir egitim kurulmasi hedeflenmektedir.

## Log ve Model Politikasi

V6 ile repo kokundeki `logs/` ve `models/` ciktilari varsayilan olarak git disina alinmistir. Egitim ve test scriptleri bu klasorleri ihtiyac halinde yeniden olusturur.

## Analiz

Episode log uzerinden kümülatif basari orani grafigi icin:

```bash
python docs/analiz.py
```

## Durum

Proje halen aktif gelisim asamasindadir. V6, observation kontratini kirdigi icin onceki modeller ile geriye donuk uyum hedeflemez; yeni egitimler `v6.0.0` state yapisi ile yeniden alinmalidir.
