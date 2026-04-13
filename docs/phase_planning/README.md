# Phase Planning

Bu klasor runtime tarafinda kullanilmaz. Amac, biten fazlarin analiz grafiklerini ve radius curriculum icin offline reward grid-search ciktilarini saklamaktir.

## Curriculum Reward Grid

Her faz radius bandi icin ayri reward parametresi aramak istendiginde bu komut kullanilir. Bu arac `105-120` bandindan baslayip `500m` max radiusa kadar faz merdiveni kurar ve her faz icin ayri reward/grid sonucu uretir:

```powershell
C:\Python310\python.exe scripts\curriculum_reward_grid_search.py --max-radius 500 --seconds-per-phase 720 --device cuda --candidates-per-round 65536 --batch-size 2048 --label v8_7_4_radius500_reward_grid
```

Kisa dogrulama icin:

```powershell
C:\Python310\python.exe scripts\curriculum_reward_grid_search.py --seconds-per-phase 1 --device cpu --candidates-per-round 512 --batch-size 128 --label quick_check
```

## Ciktilar

- `curriculum_phase_plan_*.csv`: `500m`ye kadar planlanan radius fazlari.
- `curriculum_reward_best_per_phase_*.csv`: her faz icin en iyi reward/guard parametreleri.
- `curriculum_reward_candidates_*.csv`: her faz icin saklanan en iyi adaylar.
- `curriculum_reward_summary_*.txt`: faz planini ve reward tablosunu tek yerde ozetler.
- `phase_*/`: biten fazlarin summary, diagnostics CSV ve karar grafiklerini tasir.

## Yorumlama

- Curriculum ciktisi gelecek radiuslar icin offline ekstrapolasyondur.
- Her yeni fazdan sonra taze Unity loglari incelenmeden tablonun bir sonraki satiri otomatik uygulanmaz.
- Sadece siradaki faz satiri kullanilir; daha ileri radiuslara atlanmaz.
