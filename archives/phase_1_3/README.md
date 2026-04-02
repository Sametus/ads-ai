# Phase 1.3 Archive

Bu klasor, Phase 1.3 egitim kosusunun dondurulmus arsividir.

## Icerik

- `models/ppo_model_up800.keras`
- `models/ppo_state_up800.pkl.gz`
- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/success_rate_phase1_3.png`
- `logs/step_log.csv.gz.part001`
- `logs/step_log.csv.gz.part002`
- `logs/step_log.csv.gz.part003`
- `logs/step_log.csv.gz.part004`
- `logs/step_log.csv.gz.part005`
- `logs/step_log.csv.gz.part006`

## Kisa Ozet

- Secilen devam modeli: `up800`
- Toplam episode: `1817`
- Success sayisi: `855`
- Genel success rate: `%47.056`
- En iyi rolling 100 success rate: `%67.000` (`episode 959-1058`, `update 689-703`)
- En iyi rolling 200 success rate: `%61.000` (`episode 878-1077`, `update 676-706`)
- `up800` penceresi success rate: `%59.677`
- Ortalama baslangic mesafesi: `84.458`
- Ortalama final mesafesi: `64.583`
- Ortalama episode return: `26.488`

Done reason dagilimi:

- `success`: `855`
- `high_altitude`: `833`
- `low_agl`: `112`
- `timeout`: `9`
- `collision`: `8`

## Kisa Analiz

- Phase 1.3, Phase 1.2'ye gore belirgin bir sicrama urettti ve peak koridorda rolling 200 success rate `%61` seviyesine kadar cikti.
- Reward ayrisma gucu cok guclu kaldi: success episode'larin shaping ortalamasi `+26.066`, failure shaping ortalamasi `-36.218` oldu.
- En verimli fiili baslangic mesafesi bandi `82.0-87.5` araliginda toplandi.
- `up800` sonrasi policy drift tekrar goruldu; `801-840` araliginda success rate `%22.86`'ya duserken `clip_frac` ve `kl` belirgin arttı.
- Bu nedenle bir sonraki adim ayni fazda daha uzun kalmak degil, `up800` uzerinden daha yumusak bir `Phase 2.1` gecisi olarak secildi.

## Step Log Parcalari

Step log tek dosya olarak cok buyudugu icin `gzip` ile sikistirildi ve 6 parcaya bolundu.

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
