# Aurora Pay Bobathon

Aurora Bank'ın Instant Pay ekibine katıldınız. Dokuz kısa görev (mission) var. Her görev **tek bir probleme** odaklanır,
**1-2 hamlede** çözülür ve **tek bir Bob özelliğini** gösterir. Hazır prompt yok: durumu okuyun, hedefi anlayın, Bob'a kendiniz yönlendirin.

Her görevin sonunda sonucu kendiniz doğrularsınız:

```bash
./verify/run.sh m1      # tek görev
./verify/run.sh all     # hepsi (özet tablo)
```

## Akış

| # | Görev | Senaryo türü | Bob özelliği | Süre |
|---|---|---|---|---|
| [M0](missions/M0-hazirlik.md) | Hazırlık | Temel kullanım | Mod seçici, `@` bağlamı | 10 dk |
| [M1](missions/M1-dokumandan-koda.md) | Dokümandan koda | Document-to-code | Plan / Agent, todo listesi | 25 dk |
| [M2](missions/M2-uretim-hatasi.md) | Üretim hatası | Bug fix, hata yönetimi | **Bob Shell / CLI** | 20 dk |
| [M3](missions/M3-kendi-custom-mode.md) | Kendi custom mode'um | Takım standardı | **Custom Mode + Rules + Skills** | 20 dk |
| [M4](missions/M4-kapsamli-test.md) | Kapsamlı test | Unit test | M3'teki mod ve skill'in değeri | 25 dk |
| [M5](missions/M5-bob-findings.md) | Güvenlik bulguları | Security | **Bob Findings**, Fix with Bob | 20 dk |
| [M6](missions/M6-bob-guvenlik-farklari.md) | Tuzağa düşmeyen asistan | Security | **Güvenlik farkları**: prompt injection, `.bobignore` | 20 dk |
| [M7](missions/M7-bobcoin-analytics.md) | Harcamayı görün | Ölçüm | **Bobcoin, Bob Admin, Bobalytics** | 15 dk |
| [M8](missions/M8-github-teslim.md) | GitHub'a teslim | Teslimat | Bob ile **commit, push, PR** | 15 dk |

Toplam: yaklaşık 170 dk. Süre kısıtlıysa kesilebilecek sıra: M1, M4 (bonus), M0.
Bağımlılıklar: M4, M3'ün modunu kullanır. M8, önceki işlerin commit'lenmesini bekler. Diğerleri bağımsızdır.

## Kurulum

```bash
./setup.sh --scanners
./verify/run.sh m0
```

## Kural: Bob'u `verify/` klasörüne yönlendirmeyin

Bob `verify/` içindeki kontrol dosyalarını kendiliğinden okuyabilir ve planını oradan çıkarabilir. Bu, görevi çözmek değil, kontrolü geçmek olur.
Bob'a `verify/` klasörünü göstermeyin. FAIL satırını **kendiniz** okuyun ve Bob'u PRD'deki ilgili cümleyle yönlendirin.

## Klasörler

| Yol | İçerik |
|---|---|
| `missions/` | Görev kartları |
| `docs/` | PRD, API sözleşmesi, olay kaydı, güvenlik bileti, mühendislik el kitabı |
| `fixtures/` | Olay logu ve yeniden üretme betiği, tedarikçi SDK, müşteri verisi |
| `services/core/` | Üzerinde çalışılan servis |
| `deploy/` | Dockerfile, Terraform, worker bağımlılıkları |
| `verify/` | Otomatik kabul kontrolleri |
