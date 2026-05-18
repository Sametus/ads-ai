# ADS-AI Roket Güdüm Projesi

![ADS-AI final vuruş demosu](docs/ads_success_gif.gif)

## Kısa Özet

ADS-AI, Unity fizik simülasyonu içinde hareket eden bir roketin yaklaşan bir hava hedefine yönelmesini ve hedefe temas / yakın patlama bölgesine girmesini öğrenmesi için geliştirilmiş bir pekiştirmeli öğrenme projesidir. Unity sahne, fizik, çarpışma alanı ve telemetry üretir; Python tarafı bu veriden state vektörü çıkarır, SAC ajanını eğitir, ödül/terminal hesabını yapar ve Unity'ye action gönderir.

Güncel teslim noktası `v16.0.7_forward_speed_y100` fazıdır. Bu fazda PPO denemelerinden sonra SAC tabanlı, replay buffer kullanan, continuous action üreten ve finalde `step675000` checkpoint'iyle test edilen bir hat bırakılmıştır. Sonuç bir “tam kusursuz füze güdümü” iddiası değildir; fakat PPO dönemine göre ölçülebilir şekilde daha iyi, çalıştırılabilir ve raporlanabilir bir final prototiptir.

## İçindekiler

- [Güncel Durum](#güncel-durum)
- [Sayısal Özet](#sayısal-özet)
- [Kullanılan Disiplinler](#kullanılan-disiplinler)
- [Teknik Mimari](#teknik-mimari)
- [Genel Faz Akışı](#genel-faz-akışı)
- [PPO'dan SAC'a Geçiş](#ppodan-saca-geçiş)
- [SAC: Stokastik Train, Deterministik Test](#sac-stokastik-train-deterministik-test)
- [RL Tasarımı: State, Action, Reward](#rl-tasarımı-state-action-reward)
- [Matematiksel Gözlem: Alignment ve Açı](#matematiksel-gözlem-alignment-ve-açı)
- [Reward ve Terminal Mantığı](#reward-ve-terminal-mantığı)
- [Eğitim Grafikleri](#eğitim-grafikleri)
- [Arayüz ve Sahne Görüntüleri](#arayüz-ve-sahne-görüntüleri)
- [Çalıştırma](#çalıştırma)
- [Klasör Yapısı](#klasör-yapısı)
- [Uzman İncelemesi İçin Öncelikli Noktalar](#uzman-incelemesi-için-öncelikli-noktalar)

## Güncel Durum

Aktif final model:

```text
model_prefix: sac_v16_0_7_forward_speed_y100
selected_checkpoint: step 675000
selection_method: deterministic checkpoint sweep + Unity visual observation
validated_offsets: +3 and +5 valid intercept
visual_final_candidate: +5 offset
valid_intercept_rule: hit + closing >= -1.0 + theta <= 30 deg + alignment >= 0.866
target_y: 100 m
max_step: 1200
control_mode: direct_accel
```

Tüm run snapshot'ında success sinyali alınmış olsa da final seçim yalnızca ham success sayısına göre yapılmamıştır. Çünkü bazı checkpointlerde collider teması success üretse bile roketin hedefin altından ya da arkasından dolanarak vurduğu görülebilir. Bu yüzden final aday, ayrıca deterministik checkpoint sweep ile izlenmiştir. `step675000` checkpoint'i `-5, -3, +3, +5` offset testlerinde 4/4 hit vermiş; `+3` ve `+5` offsetlerinde `valid_intercept` koşulunu sağlamıştır. Unity gözleminde özellikle son test olan `+5` offset vuruşu daha temiz önden yaklaşma davranışı gösterdiği için final aday olarak seçilmiştir.

Seçilen checkpoint test özeti:

![Seçili SAC checkpoint testi](docs/readme_assets/v16_selected_checkpoint_test.png)

Final test komutu:

```powershell
conda activate rl_codes
python scripts/final_test.py
```

`final_test.py` Unity sahnesi açıkken seçilen `step675000` checkpoint'ini yükler ve kullanıcı durdurana kadar deterministik policy ile test episode'ları çalıştırır. Konsolda success, valid intercept, weak hit, missed intercept, timeout, episode uzunluğu, reward, theta, closing ve hit bilgisi kısa biçimde yazdırılır.

## Sayısal Özet

Bu sayılar repository içinde commitlenmiş güncel kaynak kodu ve `logs/episode_log.csv` snapshot'ı üzerinden yaklaşık olarak hesaplanmıştır. Boş satırlar ve yalnızca yorum olan satırlar “kod satırı” hesabına dahil edilmemiştir.

| Alan | Değer | Not |
|---|---:|---|
| Python script dosyası | 11 | `scripts/` altında aktif kalan dosyalar; geçici checkpoint sweep/test helper dosyaları kaldırılmıştır. |
| Python toplam satır | 4.705 | Boş satır ve yorum dahil. |
| Python yaklaşık kod satırı | 4.063 | Boş satır ve `#` yorumları hariç. |
| Python dosya başına ortalama | 428 satır | Yaklaşık kaynak büyüklüğü. |
| Unity C# script dosyası | 3 | `Env.cs`, `Connector.cs`, `CameraFollow.cs`. |
| Unity C# toplam satır | 2.193 | Boş satır ve yorum dahil. |
| Unity C# yaklaşık kod satırı | 1.789 | Boş satır ve `//` yorumları hariç. |
| Commitlenmiş episode sayısı | 1.209 | Güncel `episode_log.csv` içindeki `v16_0_7_phase_1_forward_speed_y100` kayıtları. |
| Commitlenmiş toplam environment step | 1.093.936 | Episode uzunluklarının toplamı. |
| Ortalama episode uzunluğu | 904,8 step | `total_step / episode_count`. |
| Commitlenmiş success sayısı | 295 | Ham terminal nedeni `success` olan episode sayısı. |
| Ham success oranı | %24,4 | Final seçim yalnızca bu değere göre yapılmamıştır; görsel ve valid intercept testi ayrıca kullanılmıştır. |

## Kullanılan Disiplinler

Bu çalışma tek bir makine öğrenmesi denemesinden çok, birkaç disiplinin birlikte çalıştığı küçük bir Ar-Ge prototipidir:

- `Pekiştirmeli öğrenme`: SAC ajanı state-action-reward döngüsüyle continuous control öğrenir.
- `Kontrol ve güdüm`: PN fikri, closing speed, line-of-sight, theta ve final approach gibi kavramlar davranışı yorumlamak için kullanılır.
- `Matematik`: Vektör projeksiyonu, dot product, cos(theta), normalizasyon, moving average ve reward bileşimi kullanılır.
- `Fizik simülasyonu`: Unity Rigidbody, yerçekimi, AGL raycast, hız, ivme ve trigger/collider davranışları modelin gerçek sahneyle temas ettiği yerdir.
- `Yazılım mühendisliği`: Unity C# runtime ile Python training hattı TCP/JSON üzerinden haberleşir; log, checkpoint, replay buffer ve analiz scriptleri izlenebilirlik sağlar.
- `Veri analizi ve görselleştirme`: CSV loglardan terminal dağılımı, rolling success, theta/distance ve SAC alpha/entropy grafikleri üretilir.

## Teknik Mimari

Sistem iki runtime arasında çalışır:

```text
Unity sahnesi
  -> Env.cs fizik adımı, hedef/roket telemetry, hit ellipsoid, aim point
  -> Connector.cs TCP server
  -> JSON state paketi

Python
  -> connector.py paketi okur
  -> env.py state normalizasyonu, reward, terminal, action dönüşümü
  -> sac_agent.py actor/critic/replay buffer
  -> train.py stochastic training veya final_test.py deterministik test
  -> action paketi Unity'ye geri gider
```

Unity tarafında hedef ve roket gerçek transform/Rigidbody üzerinden hareket eder. Python tarafı Unity'den gelen ham telemetry'yi doğrudan neural network'e vermek yerine anlamlı bir guidance frame'e dönüştürür. Bu ayrım önemliydi; çünkü önceki denemelerde koordinat ekseni, roll ve sağ-sol simetri problemleri modelin ne öğrenmesi gerektiğini belirsiz hale getiriyordu.

## Genel Faz Akışı

Proje tek hamlede bu noktaya gelmedi. Ana teknik geçiş şu şekildedir:

![Genel faz zaman çizgisi](docs/readme_assets/phase_timeline.png)

Kısa okuma:

- PPO ilk denemelerde küçük radius değerlerinde umut verdi, fakat büyük radius ve heading offset altında davranış genelleşmedi.
- PN / oransal güdüm fikri, problemin yalnızca reward değil aynı zamanda geometri ve simülasyon sağlığı problemi olduğunu gösteren referans olarak kullanıldı.
- SAC'a geçişin ana gerekçesi off-policy öğrenme, replay buffer ve continuous control için daha uygun keşif davranışıydı.
- V16.0.7'de hedef burnu çevresinde aim point, ellipsoid hit bölgesi, sağ-sol simetri, irtifa schedule ve ileri hız ayarları ile daha çalışır bir sonuç alındı.

## PPO'dan SAC'a Geçiş

PPO, on-policy bir algoritmadır. Yani her güncellemede son toplanan rollout verisini kullanır ve bu veri güncellemeden sonra büyük ölçüde eskir. Bu projede episode'lar pahalıdır; Unity fizik simülasyonu gerçek zamanlı çalıştığı için her transition değerlidir. Bu yüzden aynı deneyleri tekrar tekrar kullanabilen off-policy bir yöntem daha mantıklı hale geldi.

PPO'nun temel fikri policy oranını sınırlayarak çok sert güncellemeleri engellemektir:

![PPO formülü](docs/readme_assets/formula_ppo.png)

SAC ise replay buffer içindeki geçmiş deneyleri tekrar kullanır. Ayrıca entropy terimi sayesinde policy'nin eğitim sırasında aşırı erken tek davranışa çökmesini engellemeye çalışır:

![SAC formülü](docs/readme_assets/formula_sac.png)

SAC'ın bu projedeki avantajları:

- `Replay buffer`: Başarılı ve başarısız geçmiş deneyler yeniden kullanılabilir.
- `Actor-critic`: Actor action üretir, critic bu action'ın uzun vadeli değerini tahmin eder.
- `Twin Q`: İki critic kullanarak değer tahminindeki aşırı iyimserliği azaltır.
- `Entropy`: Eğitim sırasında rastlantısal keşfi teşvik eder.
- `Continuous action`: Roketin sağ-sol, yukarı-aşağı ve ileri ivme bileşenleri doğrudan sürekli değerlerle temsil edilir.

PN formülü de proje boyunca "klasik güdüm mantığı ne söyler?" sorusu için referans olarak kullanıldı:

![PN formülü](docs/readme_assets/formula_pn.png)

## SAC: Stokastik Train, Deterministik Test

SAC eğitim sırasında stokastik, yani rastlantısal action örnekler. Bu rastlantısallık hata değil, keşif mekanizmasıdır. Policy bir ortalama (`mu`) ve dağılım genişliği (`sigma`) üretir; eğitimde action bu dağılımdan örneklenir.

Test sırasında ise deterministik çalıştırılır. Yani gürültü kapatılır ve actor'ın ortalama action'ı kullanılır. Bu yüzden training ekranında roket daha oynak görünebilir; final testte aynı model daha sakin ve tekrarlanabilir davranır.

![SAC stokastik ve deterministik davranış](docs/readme_assets/sac_stochastic_vs_deterministic.png)

Pratik yorum:

- Eğitimde oynaklık kısmen normaldir.
- Deterministik test, modelin gerçekten öğrendiği merkezi davranışı gösterir.
- Başarılı bir checkpoint seçerken yalnızca son modeli ya da ham success sayısını değil, deterministik testteki gerçek yaklaşma geometrisini izlemek gerekir.

## RL Tasarımı: State, Action, Reward

Aktif kontrol modu `direct_accel` olarak ayarlanmıştır. Bu modda agent klasik “saat yönü torque” komutu üretmez; bunun yerine roket burnuna göre küçük yön sapmaları ve ileri ivme büyüklüğü üretir. Böylece modelin öğrendiği şey daha okunabilir hale gelir: hedefe ne kadar sağa/sola, ne kadar yukarı/aşağı kıracağı ve ne kadar ileri ivme kullanacağı.

### State Vektörü

Aktif state vektörü 16 sayısal bileşenden oluşur. Unity önce aim point'i belirler; sonra roket burnu ile aim point arasındaki göreli konum, göreli hız ve açı bilgilerini Python'a gönderir. Python da bu bilgileri guidance frame üzerinde normalize eder.

| State bileşeni | Nasıl hesaplanır | Ne anlatır |
|---|---|---|
| `distance` | `||aim_point - rocket_point||` | Roketin yöneldiği noktaya kalan mesafe. |
| `rel_dir_right/up/forward` | Göreli yön vektörünün guidance sağ/yukarı/ileri eksenlerine dot product projeksiyonu | Hedefin roketin referans çerçevesinde nerede göründüğü. |
| `rel_vel_right/up/forward` | Göreli hızın aynı eksenlere projeksiyonu | Hedefin sağ-sol, dikey ve ileri eksende roketten nasıl ayrıştığı. |
| `rocket_vel_right/up/forward` | Roket hızının guidance frame'e projeksiyonu | Roketin kendi hareket yönü ve enerjisi. |
| `closing_speed` | `-dot(relative_velocity, relative_direction)` | Pozitifse mesafe kapanıyor, negatifse hedef uzaklaşıyor. |
| `theta_rad` | `acos(dot(rocket_forward, rel_dir))` | Roket burnu ile aim point hattı arasındaki genel açı. |
| `agl` | Unity'de aşağı raycast ile ölçülen above-ground-level | Roketin yere göre yüksekliği. |
| `alt_error` | `aim_point.y - rocket_point.y` | Hedef/aim point irtifasına göre dikey hata. |
| `target_speed` | Unity hedef hızından gelir | Hedefin sabit hareket hızı. |
| `rocket_speed` | `||rocket_velocity||` | Roketin toplam hızı. |

Guidance frame şu fikirle kurulmuştur: `up` ekseni yerçekiminin tersidir, `forward` ekseni roket burnunun yatay düzleme projeksiyonudur, `right` ekseni ise `cross(up, forward)` ile çıkarılır. Böylece state, dünya koordinatlarına göre değil roketin sahnedeki yönlenmesine göre anlam kazanır.

### Action Vektörü

Actor network üç adet normalize action üretir:

```text
action = [aim_right, aim_up, forward_accel]
```

Bu değerlerin her biri önce `[-1, 1]` aralığında çıkar. Python tarafında `denormalize_direct_accel_action` bu üç değeri Unity'nin uygulayacağı ivme paketine dönüştürür.

| Action | Uygulama | Anlam |
|---|---|---|
| `aim_right` | `right_ref * action[0] * 0.75` | Roket burnunun sağ/sol yön sapması. |
| `aim_up` | `up_ref * action[1] * 2.15` | Roket burnunun yukarı/aşağı yön sapması. |
| `forward_accel` | `20 + ((action[2] + 1) / 2) * (55 - 20)` | 20-55 bandında ileri ivme büyüklüğü. |

Önemli nokta şudur: `aim_right` ve `aim_up` hedefe otomatik kilit değildir. Kod, hedef yönünü action'a doğrudan eklemez. Agent state içinde hedefin nerede olduğunu görür ve kendi action'ıyla roket burnunu oraya yaklaştırmayı öğrenir. Oluşan yön yaklaşık olarak şu şekilde kurulur:

```text
look_dir = normalize(rocket_forward + right_offset + up_offset)
accel_world = look_dir * forward_accel
```

Bu paket Unity'ye özel bir marker ile gönderilir. Unity tarafı bu world acceleration değerini roket Rigidbody'sine uygular ve görsel yönlenmeyi bu komuta göre günceller. Kalkışın ilk adımlarında yere bastırmayı azaltmak için küçük bir launch guard / up bias vardır; bu hedefe otomatik güdüm değil, rampadan güvenli ayrılma desteğidir.

### Reward ve Öğrenme Sinyali

Reward tasarımı özellikle karmaşık reward hacking riskinden dolayı birkaç ana sinyale indirgenmiştir:

- `step_penalty`: Uzun süre oyalanmayı pahalı yapar.
- `distance_progress`: Aim point'e yaklaşmayı ödüllendirir.
- `theta_progress`: Roket burnu ile aim point hattı arasındaki açının azalmasını ödüllendirir.
- `closing`: Hedefe gerçekten kapanma hızını destekler.
- `lateral_alignment`: Sağ-sol eksende kaçırma davranışını azaltmaya çalışır.
- `altitude_schedule`: Roketin alçakta bekleyip son anda tırmanmasını azaltmak için hedef irtifaya kademeli yaklaşma sinyali verir.
- `final_approach`: Yakın mesafede düşük açı ve pozitif kapanma davranışını birlikte değerlendirir.
- `terminal_reward`: Success, missed intercept, timeout, bad angle, low AGL gibi episode sonlarını ayrıştırır.

Final seçimde ham `success` tek başına yeterli kabul edilmemiştir. Bunun sebebi collider temasının bazen hedefin altından veya arkasından gelen zayıf vuruşları da success yapabilmesidir. Bu yüzden final model, deterministik testte `hit + closing >= -1.0 + theta <= 30° + alignment >= 0.866` koşuluna göre ayrıca değerlendirilmiştir.

## Matematiksel Gözlem: Alignment ve Açı

Projede uzun süre tartışılan ana konulardan biri alignment ödülünün açıyla ilişkisi oldu. Alignment şu şekilde tanımlanır:

```text
alignment = cos(theta)
```

Burada `theta`, roket burnu ile hedef görüş hattı arasındaki açıdır. Bu değer açının kendisi değildir; cosinus dönüşümünden geçmiş bir hizalanma skorudur.

![Alignment theta eğrisi](docs/readme_assets/alignment_theta_curve.png)

Bu grafik şunu anlatır:

- `theta = 0` iken alignment `1.0` olur, yani roket hedefe tam bakıyordur.
- `theta = 90` iken alignment `0` olur.
- `theta > 90` olduğunda alignment negatife düşer.
- `theta = 30` civarında alignment yaklaşık `0.866` olduğu için hedefe makul hizalanma kabul edilebilir.

Bir diğer önemli geometri problemi hedefin sabit irtifada yaklaşmasıdır. Hedef irtifası `h = 100 m`, yatay mesafe `x` kabul edilirse roketin görmesi gereken açı yaklaşık:

```text
theta(x) = atan(h / x)
|d theta / dx| = h / (x^2 + h^2)
```

![Sabit irtifa açı nonlineerliği](docs/readme_assets/theta_nonlinearity_fixed_altitude.png)

Bu grafik, neden roketin bazen alçak irtifada bekleyip son anda panik tırmanışına geçtiğini açıklar. Uzak mesafede hedefin açısı yavaş değişir; bu yüzden alignment sinyali "şimdilik sorun yok" gibi görünebilir. Hedef yaklaştıkça aynı yatay hareket çok daha büyük açı değişimi üretir. Bu nedenle yalnızca alignment'a güvenmek reward hacking riskini artırır; closing, final approach, step penalty ve irtifa schedule birlikte düşünülmelidir.

## Reward ve Terminal Mantığı

Güncel fazda reward karmaşık eski shaping denemelerine göre sade tutulmuştur. Ana amaç roketi şu davranışlara itmekti:

- Hedefe yaklaşmak.
- Görüş hattı açısını düşürmek.
- Hedefe göre doğru final yaklaşma geometrisini kurmak.
- Alçakta oyalanmayı azaltmak.
- Hedefin arkasına takılıp timeout ödülü toplamayı engellemek.

Temel bileşenler:

```text
step_penalty
distance_progress
theta_progress
lateral_alignment
altitude_schedule
closing
final_approach
terminal_reward
```

Başarı artık yalnızca basit mesafe hesabı gibi düşünülmez. Unity tarafındaki hedef hit alanı ve Python tarafındaki final telemetry birlikte okunur. V16'da hedef gövdesi etrafındaki ellipsoid hit bölgesi, "füze çok yakın patlayıp hasar verdi" yorumuna daha uygundur.

Terminal sebeplerinin son run snapshot'ındaki dağılımı:

![Terminal dağılımı](docs/readme_assets/v16_terminal_distribution.png)

Okuma:

- `success` artık rastgele ya da wrapper kaynaklı değildir; zero/random baseline mantığı bu yüzden geçmişte ayrıca test edildi.
- `missed_intercept` ve `timeout`, hedefe yaklaşsa da doğru zamanda vuramayan episode'ları ayırmak için önemlidir.
- `low_agl`, `bad_angle`, `wrong_way` gibi terminaller roketin öğrenme alanını gereksiz kaçışlardan temizlemek için kullanılmıştır.

## Eğitim Grafikleri

Rolling success grafiği, modelin dönem dönem ciddi şekilde iyileştiğini ama eğitimin monoton artmadığını gösterir:

![Rolling success](docs/readme_assets/v16_rolling_success.png)

Success scatter grafiği episode sırasına göre başarıların nerede yoğunlaştığını gösterir. Bu grafik aday checkpoint aralığını daraltmak için kullanışlıdır; final karar ise ayrıca deterministik sweep ve görsel gözlemle verilmiştir:

![Success scatter](docs/readme_assets/v16_success_scatter_by_episode.png)

Final distance ve theta trendi, roketin zamanla hedefe daha yakın bitirmeyi ve daha düşük açıyla yaklaşmayı öğrendiğini gösterir:

![Distance theta trend](docs/readme_assets/v16_distance_theta.png)

SAC update log grafiği alpha, entropy ve value loss davranışını gösterir:

![SAC alpha entropy](docs/readme_assets/sac_alpha_entropy.png)

Kısa yorum:

- Alpha azalırken policy daha az rastlantısal hale gelir.
- Entropy tamamen sıfırlanmaz; bu SAC'ın keşif baskısını koruduğunu gösterir.
- Value loss spike'ları, replay buffer içindeki yeni davranış bölgeleri ve reward değişimlerinin critic tarafından sindirildiği dönemleri işaret eder.

## Arayüz ve Sahne Görüntüleri

Unity runtime görünümü aşağıdaki çoklu kamera ekranında gösterilmiştir. Bu görüntü roket, hedef uçak, takip çizgileri ve sahnedeki test düzenini aynı anda okumak için kullanılır.

![Unity çoklu kamera runtime görünümü](docs/readme_assets/screenshots/unity_multi_camera_runtime.png)

Aim point ve hit ellipsoid sahne içinde ayrıca görselleştirilmiştir. Büyük yarı saydam elipsoid hedef etrafındaki yakın patlama / hasar bölgesini, küçük küre ise roketin yönelmesi beklenen aim point'i temsil eder.

![Aim point ve hit ellipsoid sahne görünümü](docs/readme_assets/screenshots/unity_aim_point_hit_ellipsoid.png)

## Çalıştırma

1. Unity projesini aç:

```text
ads_ai/
```

2. Unity sahnesinde Play'e bas.

3. Python ortamını aç:

```powershell
conda activate rl_codes
```

4. Final modeli test et:

```powershell
python scripts/final_test.py
```

5. Eğitimi devam ettirmek istersen:

```powershell
python scripts/train.py
```

6. Grafik üretmek istersen:

```powershell
python scripts/generate_readme_charts.py
python scripts/plot_success_scatter.py
python scripts/plot_sac_report.py
```

## Klasör Yapısı

```text
ads_ai/
  ads_ai/                       Unity projesi
    Assets/Scripts/Env.cs       Unity fizik, action uygulama ve telemetry
    Assets/Scripts/Connector.cs TCP/JSON iletişim katmanı
    Assets/Scenes/              Unity sahneleri

  scripts/                      Python RL kodları
    train.py                    Aktif SAC training döngüsü
    final_test.py               Final checkpoint test scripti
    sac_agent.py                SAC actor, critic, replay buffer ve checkpoint
    env.py                      Python Env wrapper, reward ve state/action dönüşümü
    settings.py                 Model prefix, SAC ayarları, GPU/port ayarları
    connector.py                Unity-Python TCP bağlantısı
    cuda_bootstrap.py           Windows/Conda CUDA DLL hazırlığı
    log.py                      CSV ve terminal logları
    generate_readme_charts.py   README grafiklerini Türkçe karakter desteğiyle üretir
    plot_success_scatter.py     Success scatter ve rolling success grafiği
    plot_sac_report.py          SAC eğitim rapor grafikleri

  docs/readme_assets/           README görselleri
  logs/                         Güncel eğitim logları
  models/                       Final SAC checkpoint dosyaları
  CHANGELOG.md                  Kronolojik geliştirme notları
  VERSION                       Aktif sürüm bilgisi
```

`archives/` ve `teacher_data/` klasörleri yerelden kaldırılmıştır. Eski fazlar, teacher/pretrain denemeleri ve audit scriptleri Git commit geçmişinde durur; final çalışma klasöründe yalnızca aktif teslim hattı bırakılmıştır.

## Uzman İncelemesi İçin Öncelikli Noktalar

Bir uzmanın özellikle şu dosyalara bakması yeterli olur:

```text
scripts/env.py
scripts/sac_agent.py
scripts/train.py
scripts/settings.py
ads_ai/Assets/Scripts/Env.cs
ads_ai/Assets/Scripts/Connector.cs
```

Kontrol edilmesi gereken ana başlıklar:

- `alignment = cos(theta)` sinyalinin tek başına reward hacking üretip üretmediği.
- Closing ve final approach bileşenlerinin timeout'a değil intercept'e yönlendirip yönlendirmediği.
- Aim point ile hit ellipsoid'in Unity sahnesindeki konumu.
- Sağ-sol offset simetrisi ve replay mirror davranışı.
- SAC alpha/entropy eğrisinin exploration'ı yeterli ama aşırı olmayacak düzeyde tutup tutmadığı.
- Final checkpoint seçiminin ham success yerine valid intercept ve görsel yaklaşma kalitesine göre doğru olup olmadığı.

## Kısa Sonuç

Proje artık yalnızca deneme kodlarından oluşan dağınık bir çalışma değildir. Unity sahnesi, Python SAC hattı, final test scripti, seçilmiş checkpoint ve rapor grafikleri ile çalıştırılabilir bir teslim paketidir. Final aday `step675000` checkpoint'idir; bu seçim rolling success değerinden çok deterministik checkpoint sweep, valid intercept ölçütü ve Unity görsel gözlemiyle yapılmıştır.

Kalan temel teknik risk, modelin tüm spawn ve offset koşullarında tamamen kararlı bir güdüm kanunu öğrenmiş olmamasıdır. Buna rağmen PPO dönemine kıyasla SAC ile replay buffer, entropy kontrollü keşif ve final checkpoint seçimi sayesinde ölçülebilir bir başarı penceresi elde edilmiştir.
