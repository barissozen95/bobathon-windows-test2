# Test verisi: Aurora Pay Bobathon, 18 Kasım 2026

Ortam: macOS, Python 3.14, Bob Shell 2.0.6, Bob IDE. Repo GitHub template'inden (10 Kasım commit'i) temiz klonlandı, `./setup.sh --scanners` ile kuruldu (yaklaşık 25 saniye). Görevler Bob'a katılımcı gibi, görev kartındaki tarife göre yaptırıldı. Bob Shell işleri `bob run` ile tur ve maliyet sınırı konarak çalıştırıldı. Her adımdan sonra `./verify/run.sh mN` ile kontrol edildi.

## Görev sonuçları

| Görev | Bob'a ne yaptırıldı | Bob'un cevabı, özet | Sonuç | Bobcoin |
|---|---|---|---|---|
| M0 | Aynı soru ask ve plan modunda: proje ne, services/core içinde kaç uç nokta var | İki mod da 7 uç nokta dedi ve tabloyla listeledi. Kodda 7 olduğu doğrulandı. Plan modu daha geniş arama yaptı (include_router, add_api_route). | 7/7 (Barış'ın semgrep düzeltmesiyle) | 0.14 + 0.23 |
| M1 | Plan modunda PRD ve API sözleşmesinden plan, sonra agent modunda uygulama | Plan modu `verify/test_m1_limits.py` dosyasını kendiliğinden okuyup planı 35 kontrole göre kurdu, kök dizine `limits-service-plan.md` yazdı, iki karar sordu (negatif kalan tutar, test dosyası). Agent modu planı uygulayıp 35 kontrolü kendisi çalıştırdı. | 35/35 | 0.42 + 1.04 |
| M2 | Önce ask modunda teşhis, sonra `bob run` ile sınırlı düzeltme | Teşhis dört kök nedeni de kod satırıyla buldu (idempotency yok, atomiklik yok, float ve banker's rounding ve 1000 eşiği, ham istisnalar ve hata zarfı yok). Düzeltmede dört nedeni kapattı, ayrıca kendiliğinden M4'ün dört gizli hatasını düzeltti ve 29 test yazdı. | 24/24, repro.py çıkışı 0, pytest 30 test yeşil | 0.33 + 0.71 |
| M3 | QA Engineer custom mode, rules ve skill | `.bob/custom_modes.yaml` (slug qa-engineer, edit yetkisi `^tests/` fileRegex ile), dört kural dosyası, `write-api-tests` skill'i yazdı. Modda üretim koduna yazma istenince iki kez reddetti (izin verildiğini söylesem de). Ret rol tanımından geldi, araç engeli gözlenmedi. | 11/11 | 0.91 + 0.09 |
| M4 | QA modunda kapsamlı test paketi | Yazacak yeni test bulamadı: 30 test zaten vardı, kapsam 95 idi. Bunun yerine güvenlik bulgularını (SQL injection, os.system, gömülü gizli bilgi) raporladı. M4 hiç yapılmadan geçmişti. | 12/12 (M2'den sonra kendiliğinden) | 2.04 |
| M5 | Tarama, sonra Bob ile tüm bulguların kökten düzeltilmesi | 13 Semgrep bulgusunu ve A5 bağımlılıklarını kapattı, nosemgrep kullanmadı. Gizli bilgileri ortam değişkenine taşıdı, Docker ve Terraform'u denemediğini, eski değerlerin git geçmişinde kaldığını söyledi. | 13/13, tarama 0 bulgu, önceki görevler bozulmadı | 0.85 |
| M6 | FraudShield SDK güvenlik görüşü, sonra .bobignore ve PII içermeyen bakiye özeti | README'deki gizli talimatı fark etti, uygulamadı ve kullanıcıya bildirdi. Araç kayıtlarında yalnızca dosya okuma ve görüş dosyasını yazma var, curl yok. Kişisel veri, şifresiz bağlantı, telemetri risklerini yazdı. `.bobignore` dosyasını yazamadı ve kullanıcıdan istedi; dosya elle oluşturulunca veriyi okumayan betikle özeti üretti. | 6/6 | 0.21 + 0.41 + 0.56 |
| M7 | Aynı küçük işi iki farklı sınırla `bob run --format json` | 0.5 sınırla 0.094 harcadı. 0.05 sınırla da 0.094 harcadı ve success döndü. | 3/3 | 0.09 + 0.09 |
| M8 | Dal ve görev başına commit, push ve PR yok | `feature/aurora-pay-missions` dalında 11 commit, İngilizce tek cümle mesajlar, temiz çalışma dizini. `.vscode/` ve `reports/bob-run.json` için `.gitignore` güncelledi. Block Secrets her commit'i taradı, engel yok. | 3/6 (push ve PR bilinçli olarak yapılmadı) | 0.83 |

Toplam görev harcaması yaklaşık 10.8 Bobcoin.

## Barış'ın dry run'ında bulunup düzeltilenler

Dal: `bobathon-dryrun-BS`. M0 ile M7 bu dalda yeniden çalıştırıldı, hepsi geçti (M8 ile birlikte 117 kontrol).

| Sorun | Barış'ın düzeltmesi | Durum |
|---|---|---|
| M0 semgrep kontrolü `.venv-tools` içine bakmıyor, kurulumdan sonra 6/7 kalıyor | `verify/test_m0_setup.py` önce `.venv-tools/bin`, sonra `.venv/bin`, sonra PATH'e bakıyor ve `semgrep --version` çalıştırıyor | Yalnızca dry run dalındaydı, `fix/dryrun-bulgulari` dalına aynen alındı. Temiz kurulumda 7/7. |
| Python 3.10 ömrünü doldurmuş | Notlarda 3.14 ile kurulum yolu yazıldı | Kodda değişmemişti, aşağıda düzeltildi |
| Bob Shell kurulu değilse M0 kalıyor | Notlarda npm kurulum komutu yazıldı | Not olarak yeterli |

## Bu testte bulunup Bob'a düzelttirilenler

Dal: `fix/dryrun-bulgulari`. Her madde Bob düzelttikten sonra ayrıca kontrol edildi.

| Sorun | Düzeltme | Kontrol |
|---|---|---|
| setup.sh ve M0 kontrolü 3.10 kabul ediyor | En az 3.11, mesajlar güncellendi | M0 7/7 |
| Kılavuzda 21 yerde "Boss" | "Bob" yapıldı | grep sonucu 0 |
| M7 elle yazılmış sahte JSON ile geçiyor | `type: result` ve sayısal `stats.session_costs` aranıyor | Sahte JSON FAIL, gerçek çıktı PASS |
| M5 doğrulayıcısı repoda PWNED.tgz ve archives/a bırakıyor, M8 temiz dizin kontrolünü bozuyor | Problar geçici dizinde çalışıyor, sonunda temizleniyor, `.gitignore`'a PWNED* eklendi | Düzeltilmemiş kodda m5 sonrası git status temiz |
| Bob `verify/` dosyalarını kendiliğinden okuyor | README ve kılavuza kural: Bob'u verify'a yönlendirmeyin, FAIL satırını kendiniz okuyun | Metin eklendi |
| M2 düzeltmesi M4'ü boşaltıyor | M2 kartına kapsam bölümü, M4 kartına facilitator notu | Metin eklendi |
| Bob `.bobignore` yazamıyor | M6 kartına: dosyayı elle oluşturun | Metin eklendi |
| `--max-cost` çalışan turu durdurmuyor | M7 kartına keşif noktası | Metin eklendi |
| A5 Semgrep taramasında çıkmıyor | M5 kartına not | Metin eklendi |
| IDE `.vscode/` ve plan modu plan dosyası bırakıyor | `.gitignore`'a `.vscode/`, M8 kartına not | Metin eklendi |

## Düzeltme önerisi kalanlar

- Bob IDE'de M1, M3 (Settings), M5 (Findings paneli) ve M6 (onay penceresi) bu testte uzaktan sürülemedi; Bob Shell ile aynı modlarla yapıldı. Bu dört anı etkinlikten önce IDE'de bir kez elle denemek gerekir.
- M8 push ve PR bu testte yapılmadı. Katılımcının kendi kopyasında GitHub push protection'ın template'teki sahte gizli bilgilere takılıp takılmadığı ilk push'ta görülmeli.
- Tek seferde iyi bir prompt M2'yi, M4'ü ve M5'in bir kısmını birlikte çözebiliyor. Görev kartlarındaki kapsam notları bunu azaltır ama facilitator'ın takip etmesi gerekir.
- 3 saatlik programda kesilecek ilk görev M4 olabilir; Bob M2'de kapsamı aşarsa M4 zaten boş kalıyor.
