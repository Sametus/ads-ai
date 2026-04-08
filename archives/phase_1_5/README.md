# Phase 1.5 Archive

Bu klasor, V8 guidance/action hattiyla kosulan Phase 1.5 egitim penceresinin dondurulmus arsividir.

## Icerik

- `models/ppo_model_up1380.keras`
- `models/ppo_state_up1380.pkl.gz`
- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/phase_1_5_success_rate.png`
- `logs/phase_1_5_success_episode_rug.png`
- `logs/phase_1_5_reset_outcome_polar.png`
- `logs/phase_1_5_reset_radius_distribution.png`
- `logs/phase_1_5_reset_radius_phase_plan.png`
- `logs/step_log.csv.gz.part001` ... `logs/step_log.csv.gz.part005`

## Kisa Ozet

- Secilen devam modeli: `up1380`
- Arsivlenen log kapsami: `update 1384`e kadar
- Toplam episode: `1291`
- Success sayisi: `1015`
- Genel success rate: `%78.621`
- Guncel rolling 100 success rate: `%88.000`
- Guncel rolling 200 success rate: `%91.000`
- Guncel rolling 300 success rate: `%91.000`
- En iyi rolling 100 success rate: `%95.000` (`episode 1053-1152`)
- En iyi rolling 200 success rate: `%92.500` (`episode 988-1187`)
- En iyi rolling 300 success rate: `%91.667` (`episode 899-1198`)
- Ortalama success episode uzunlugu: `134.983`

Done reason dagilimi:

- `success`: `1015`
- `wrong_way`: `204`
- `high_altitude`: `56`
- `timeout`: `15`
- `low_agl`: `1`

## Kisa Analiz

- Phase 1.5 kosusu, onceki `62-82 radius` bandinin artik guclu sekilde ogrenildigini gosterdi. Son `200-300` episode koridorunda success rate `%91` bandina oturdu.
- Yari-cap bazli analizde `60-70` bandi `%93-%96`, `70-75` bandi `%88`, `75-80` bandi `%60`, `80-85` bandi ise `%23` success verdi. Bu, bir sonraki fazin zorlugu yukari kaydirirken `80+` bolgesine tek adimda atlamamanin daha dengeli oldugunu gosteriyor.
- `up1380` checkpoint'i, son guclu koridorun icinde kaldigi ve `up1384`e kadar performans halen yuksek seyretdigi icin handoff modeli olarak secildi.
- Bir sonraki faz icin onerilen gecis: `spawn_radius_min = 71`, `spawn_radius_max = 81`, heading araligi ayni, reward ailesi ayni.

## Step Log Parcalari

Step log tek dosya olarak buyudugu icin `gzip` ile sikistirildi ve 5 parcaya bolundu.

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
