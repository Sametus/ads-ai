# Phase 1.6 Archive

Bu klasor, V8 guidance/action hattiyla kosulan Phase 1.6 egitim penceresinin dondurulmus arsividir.

## Icerik

- `models/ppo_model_up1460.keras`
- `models/ppo_state_up1460.pkl.gz`
- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/phase_1_6_success_rate.png`
- `logs/phase_1_6_success_rug.png`
- `logs/phase_1_6_reset_outcome_polar.png`
- `logs/phase_1_6_reset_radius_distribution.png`
- `logs/phase_1_6_reset_radius_phase_plan.png`
- `logs/step_log.csv.gz.part001` ... `logs/step_log.csv.gz.part002`

## Kisa Ozet

- Secilen devam modeli: `up1460`
- Arsivlenen log kapsami: `update 1462`ye kadar
- Toplam episode satiri: `637`
- Success sayisi: `600`
- Genel success rate: `%94.192`
- Guncel rolling 100 success rate: `%94.000`
- Guncel rolling 200 success rate: `%95.000`
- Guncel rolling 300 success rate: `%94.000`
- En iyi rolling 100 success rate: `%100.000`
- En iyi rolling 200 success rate: `%98.500`
- En iyi rolling 300 success rate: `%97.333`

Done reason dagilimi:

- `success`: `600`
- `wrong_way`: `31`
- `high_altitude`: `6`

## Kisa Analiz

- Phase 1.6 kosusu, `71-81 radius` bandinin artik guclu sekilde ogrenildigini gosterdi. Son `100-300` episode koridorunda success rate `%94-%95` bandina oturdu.
- Log icinde episode kimligi bir kez sifirlanip yeniden baslasa da grafikler ham `episode_id` yerine log sirasi uzerinden cizildi; bu nedenle success yogunlugu ve rolling pencereler faz genelini dogru temsil eder.
- Yari-cap bazli analizde `70-75` bandi `%99.6`, `75-80` bandi `%93.4`, `80-85` bandi `%63.9` success verdi. Bu nedenle bir sonraki faz icin en dogal gecis `75-85 radius` bandina kaymaktir.
- `up1460` checkpoint'i son guclu koridorun icinde kaldigi ve `update 1462` sonuna kadar performans dusmeden devam ettigi icin handoff modeli olarak secildi.

## Step Log Parcalari

Step log tek dosya olarak buyudugu icin `gzip` ile sikistirildi ve 2 parcaya bolundu.

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
