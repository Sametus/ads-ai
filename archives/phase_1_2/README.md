# Phase 1.2 Archive

Bu klasor, Phase 1.2 egitim kosusunun dondurulmus arsividir.

## Icerik

- `models/ppo_model_up520.keras`
- `models/ppo_state_up520.pkl.gz`
- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/success_rate_phase1_2.png`
- `logs/step_log.csv.gz.part001`
- `logs/step_log.csv.gz.part002`
- `logs/step_log.csv.gz.part003`
- `logs/step_log.csv.gz.part004`
- `logs/step_log.csv.gz.part005`
- `logs/step_log.csv.gz.part006`
- `logs/step_log.csv.gz.part007`

## Kisa Ozet

- Secilen devam modeli: `up520`
- Toplam episode: `1621`
- Success sayisi: `308`
- Genel success rate: `%19.001`
- En iyi kümülatif success rate: `%27.957` (`episode 930`, `update 529`)
- En iyi rolling 200 success rate: `%35.500` (`episode 724-923`, `update 489-527`)
- Ortalama baslangic mesafesi: `79.348`
- Ortalama final mesafesi: `103.672`
- Ortalama episode return: `-54.827`

Done reason dagilimi:

- `high_altitude`: `1051`
- `success`: `308`
- `low_agl`: `191`
- `timeout`: `52`
- `collision`: `19`

## Kisa Analiz

- Peak koridorda (`episode 724-923`) success rate `%35.5`'e cikti ve mean return `+7.23` oldu.
- Ayni koridorda step ortalama reward `+0.0317`, mean closing speed `+3.31` ve pozitif closing orani `%63.2` idi.
- Son 200 episode'a gelindiginde success rate `%4.5`'e dustu; mean return `-108.60`, mean closing speed `-7.43` ve last-50-step look angle `109.85` dereceye bozuldu.
- Update log'da peak sonrasi `kl` ve `clip_frac` belirgin arttigi icin Phase 1.2 son bolumunde policy drift / asiri guncelleme izi goruluyor.

## Phase 1.3 Yonelimi

- Warm-start noktasi olarak `up520` kullanilmali.
- Faz 1.3'te oncelik zorluk artirmak degil, peak davranisi stabilize etmek olmali.
- Baslangic menzili `80-90` fiili mesafe bandini koruyacak sekilde hafif yukari kaydirilmali; `70-80` bandi belirgin zayif kaldi.
- Reward ailesi korunup optimizer tarafinda daha korumaci ayarlar dusunulmeli: daha dusuk entropy / daha dusuk ogrenme hizi / en iyi checkpoint secimi.

## Step Log Parcalari

Step log tek dosya olarak cok buyudugu icin `gzip` ile sikistirildi ve 7 parcaya bolundu.

Parcalari tek dosyada birlestirmek icin PowerShell:

```powershell
$out = 'step_log.csv.gz'
$parts = Get-ChildItem .\logs\step_log.csv.gz.part* | Sort-Object Name
$stream = [System.IO.File]::Create($out)
try {
    foreach ($part in $parts) {
        $bytes = [System.IO.File]::ReadAllBytes($part.FullName)
        $stream.Write($bytes, 0, $bytes.Length)
    }
}
finally {
    $stream.Dispose()
}
```

Ardindan `gzip` acilarak orijinal `step_log.csv` elde edilebilir.
