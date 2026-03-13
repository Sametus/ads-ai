# v1.0 - İlk kararlı sürüm

- Unity ortamı ve sahne düzeni
- PPO eğitim scriptleri ve ayarları
- Rapor dokümanları ve 3D model dosyalarının `docs` altına taşınması
- JSON bağımlılıklarının projeye eklenmesi

# v1.1 - Fizik senkronizasyonu ve reward güncellemeleri

- Unity `Env` ortamında manuel fizik adımı (Physics.Simulate) ve güvenli reset akışı
- Raycast tabanlı AGL (yerden yükseklik) ve grounded flag ile iyileştirilmiş state tanımı
- Python `env.py` tarafında reward/terminal mantığının AGL ve grounded bilgisiyle güncellenmesi
- Ortam problemlerine yönelik detaylı `docs/deep_research/deep-research-report.md` teknik analizi eklendi

# v1.1.1 - Debug çizgileri ve görsel iyileştirme

- Unity `Env` içinde debug çizgilerinin fizik adımıyla senkron çalışacak şekilde güncellenmesi
- Roket ileri yön çizgisinin `rocket` yerine `rocketPoint` referansıyla çizilerek görsel tutarlılığın artırılması

**Kod düzeyi değişiklikler**

- `Env.Update` içindeki `UpdateDebugLines()` çağrısı kaldırıldı; debug çizgileri artık her aksiyon adımında `StepOnce()` içinde, fizik simülasyonu (`Physics.Simulate`) sonrasında güncelleniyor.
- `UpdateDebugLines()` fonksiyonunda ileri yön çizgisi hesabı `rocket.forward` yerine `rocketPoint.forward` kullanacak şekilde değiştirildi.

