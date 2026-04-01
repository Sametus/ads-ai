# Phase 1.1 Archive

Bu klasor, Phase 1.1 egitim kosusunun dondurulmus arsividir.

## Icerik

- `models/ppo_model_up340.keras`
- `models/ppo_state_up340.pkl.gz`
- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/success_rate_phase1_latest.png`
- `logs/step_log.csv.gz.part001`
- `logs/step_log.csv.gz.part002`
- `logs/step_log.csv.gz.part003`
- `logs/step_log.csv.gz.part004`

## Kisa Ozet

- En iyi warm-start modeli: `up340`
- Episode sayisi: `1640`
- Success sayisi: `161`
- Success rate: `%9.817`
- Ortalama baslangic mesafesi: `79.37`
- Ortalama final mesafesi: `121.783`
- Ortalama episode return: `-78.912`

Done reason dagilimi:

- `high_altitude`: `1200`
- `low_agl`: `235`
- `success`: `161`
- `timeout`: `15`
- `collision`: `29`

## Step Log Parcalari

Step log tek dosya olarak cok buyudugu icin `gzip` ile sikistirildi ve 4 parcaya bolundu.

Parcalari tek dosyada birlestirmek icin PowerShell:

```powershell
$out = 'step_log.csv.gz'
$parts = Get-ChildItem .\\logs\\step_log.csv.gz.part* | Sort-Object Name
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
