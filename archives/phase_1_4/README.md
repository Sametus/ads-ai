# Phase 1.4 Archive

Bu klasor, V8 guidance/action hattiyla kosulan Phase 1.4 egitim penceresinin dondurulmus arsividir.

## Icerik

- `models/ppo_model_up1200.keras`
- `models/ppo_state_up1200.pkl.gz`
- `logs/episode_log.csv`
- `logs/update_log.csv`
- `logs/success_rate_phase_1_4.png`
- `logs/success_episode_rug.png`
- `logs/success_episodes_scatter.png`
- `logs/success_count_by_steps_scatter.png`
- `logs/step_log.csv.gz.part001` ... `logs/step_log.csv.gz.part030`

## Kisa Ozet

- Secilen devam modeli: `up1200`
- Toplam episode: `5790`
- Success sayisi: `1235`
- Genel success rate: `%21.330`
- Guncel rolling 100 success rate: `%67.000`
- Guncel rolling 200 success rate: `%67.000`
- En iyi rolling 100 success rate: `%72.000` (`episode 561-660`, `update 1188-1201`)
- En iyi rolling 200 success rate: `%70.000` (`episode 424-623`, `update 1169-1196`)
- Ortalama success episode uzunlugu: `142.015`

Done reason dagilimi:

- `success`: `1235`
- `wrong_way`: `3444`
- `high_altitude`: `749`
- `low_agl`: `279`
- `timeout`: `82`
- `collision`: `1`

## Kisa Analiz

- Phase 1.4'te uzun sureli denemelerden sonra egitim belirgin sekilde toparlandi ve son `100-300` episode koridorunda success rate `%64-%67` bandina oturdu.
- Success episode'larin fiili baslangic mesafesi agirlikli olarak `75-90` bandinda toplandi; ozellikle son `200` episode icinde `75-80` bandi `%95.83`, `80-85` bandi `%100`, `85-90` bandi `%100` success verdi.
- Buna karsilik `70-75` bandi hala zayif kaldi (`%9.23`), bu da bir sonraki fazin asagiya degil yukariya dogru kaydirilmasi gerektigini gosterdir.
- Secilen `up1200` checkpoint'i, en iyi rolling 100 penceresine (`update 1188-1201`) dogrudan denk geldigi ve ayni zamanda son koridorun guclu performansini korudugu icin handoff noktasi olarak secildi.
- Bir sonraki faz icin onerilen gecis: `spawn_radius_min = 62`, `spawn_radius_max = 82`, heading araligi ayni, reward seti ayni.

## Step Log Parcalari

Step log tek dosya olarak cok buyudugu icin `gzip` ile sikistirildi ve 30 parcaya bolundu.

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
