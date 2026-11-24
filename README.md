# Aurora Pay Bobathon

Aurora Bank'ın Instant Pay ekibine katıldınız. Dokuz kısa görev (M0-M8) var. Her görev **tek bir probleme** odaklanır, **birkaç adımda** çözülür ve **tek bir Bob özelliğini** gösterir.
Durumu okuyun, hedefi anlayın ve Bob'a kendi cümlelerinizle yön verin.

> **Etkileşimli kılavuz:** [`KATILIMCI-KILAVUZU.html`](KATILIMCI-KILAVUZU.html) dosyasını tarayıcıda açın. İşletim sisteminizi (Windows, macOS, Linux) seçer, komutları ona göre gösterir ve her komutu **Kopyala** düğmesiyle alır.
> Bu README ve [`missions/`](missions/) kartlarında her komut kendi kutusundadır; macOS/Linux'ta `python3`, Windows'ta `py` yazın.

Her görevin sonunda sonucu doğrulamak için aşağıdaki komutu kullanabilirsiniz (`m1` yerine görev numarasını yazın):

```bash
python3 verify/run.py m1
```

Tüm görevleri tek seferde görmek için:

```bash
python3 verify/run.py all
```

## Akış

| # | Görev | Senaryo türü | Bob özelliği | Süre |
|---|---|---|---|---|
| [M0](missions/M0-hazirlik.md) | İlk gün: kurulum ve servisi tanıma | Temel kullanım | Mod seçici, `@` bağlamı | 20 dk |
| [M1](missions/M1-dokumandan-koda.md) | Dokümandan koda | Document-to-code | Plan / Agent, todo listesi | 25 dk |
| [M2](missions/M2-uretim-hatasi.md) | Üretim hatası | Bug fix, hata yönetimi | **Bob Shell / CLI** | 20 dk |
| [M3](missions/M3-kendi-custom-mode.md) | Kendi custom mode'um | Takım standardı | **Custom Mode + Rules + Skills** | 20 dk |
| [M4](missions/M4-kapsamli-test.md) | Kapsamlı test | Unit test | M3'teki mod ve skill'in değeri | 25 dk |
| [M5](missions/M5-bob-findings.md) | Güvenlik bulguları | Security | **Bob Findings**, Fix with Bob | 20 dk |
| [M6](missions/M6-bob-guvenlik-farklari.md) | Tuzağa düşmeyen asistan | Security | **Güvenlik farkları**: prompt injection, `.bobignore` | 20 dk |
| [M7](missions/M7-bobcoin-analytics.md) | Harcamayı görün | Ölçüm | **Bobcoin, Bob Admin, Bobalytics** | 15 dk |
| [M8](missions/M8-github-teslim.md) | GitHub'a teslim | Teslimat | Bob ile **commit, push, PR** | 15 dk |

Toplam görev süresi: **180 dk**. Bağımlılıklar: M4, M3'ün modunu kullanır. M8, önceki işlerin commit'lenmesini bekler. Diğerleri bağımsızdır.

Her görev kartı aynı yapıdadır: **Durum**, **Teslim edilecekler**, numaralı **Adımlar** (son adım her zaman **Doğrulama**), **Keşif noktaları** ve **İpucu** (İpucu 1, İpucu 2, Eğitmenden yardım).

## Program (4 saat)

| Saat | İçerik | Süre |
|---|---|---|
| 08:30 | Ön kontrol: kurulum ve `verify m0` (programa dahil değil) | - |
| 09:00 | Açılış | 10 dk |
| 09:10 | M0 İlk gün | 20 dk |
| 09:30 | M1 Dokümandan koda | 25 dk |
| 09:55 | M2 Üretim hatası | 20 dk |
| 10:15 | Mola | 15 dk |
| 10:30 | M3 Kendi custom mode'um | 20 dk |
| 10:50 | M4 Kapsamlı test | 25 dk |
| 11:15 | M5 Güvenlik bulguları | 20 dk |
| 11:35 | Mola | 15 dk |
| 11:50 | M6 Tuzağa düşmeyen asistan | 20 dk |
| 12:10 | M7 Harcamayı görün | 15 dk |
| 12:25 | M8 GitHub'a teslim | 15 dk |
| 12:40 | Kapanış | 20 dk |
| 13:00 | Bitiş | - |

### B planı: 3 saatlik çekirdek program (7 görev)

Süre daralırsa **M1 ve M4** çıkarılır; kalan yedi görev **M0, M2, M3, M5, M6, M7, M8** yaklaşık 130 dk görev süresi eder. **M3 ve M6 her durumda çekirdekte kalır.**

Süre daha da daralırsa kesme sırası:

1. M7'nin portal kısmı (yalnızca `bob-run.json` ölçümü kalır)
2. M4
3. M1
4. M8'de CI'ın bitmesini beklemek

## Ön koşullar

Programdan **önce** tamamlayın. Etkileşimli sürümü (işletim sistemine göre seçmeli) kılavuzun [Ön koşullar](KATILIMCI-KILAVUZU.html#onkosul) bölümündedir.

- **Python 3.11 veya üstü** ve **git**. Sürüm kontrolü: `python3 --version` (Windows: `py --version`), `git --version`.
- **Bob IDE** kurulu ve giriş yapılmış; IDE'de **GitHub oturumu** açık.
- **Bob Shell** kurulu; `bob --version` çalışıyor.
- **`BOB_API_KEY`** tanımlı. Anahtarın kapsamı **Inference** olmalı; "general" kapsamlı bir anahtarla komutlara ayrıca `--team-id` eklenir.
- **GitHub CLI** (`gh`) kurulu ve `gh auth login` yapılmış; kendi kopya reponuzda **GitHub Actions etkin**.
- Kurulumu bitirince `verify m0` çıktısını eğitmene gönderin.

Bob Shell kurulumu, macOS/Linux:

```bash
curl -fsSL https://bob.ibm.com/download/bobshell.sh | bash
```

Bob Shell kurulumu, Windows (PowerShell):

```powershell
powershell -ep Bypass "iwr https://bob.ibm.com/download/bobshell.ps1 -OutFile $env:TMP\bob.ps1; &$env:TMP\bob.ps1"
```

Alternatif (Node.js varsa):

```bash
npm install --registry=https://registry.npmjs.org/ --allow-scripts=@officecli/officecli -g @ibm/bob
```

API anahtarı (açık terminal için), macOS/Linux:

```bash
export BOB_API_KEY="<anahtarınız>"
```

API anahtarı (açık terminal için), Windows (PowerShell):

```powershell
$env:BOB_API_KEY="<anahtarınız>"
```

Windows'ta kalıcı yapmak için:

```powershell
[System.Environment]::SetEnvironmentVariable('BOB_API_KEY','<anahtarınız>','User')
```

## Kurulum

Repoyu **klonlayın** (boş klasör açmayın; M0'da adım adım anlatılıyor) ve kök dizinden çalıştırın:

```bash
python3 setup.py --scanners
```

```bash
python3 verify/run.py m0
```

`setup.py` `.venv` sanal ortamını oluşturup bağımlılıkları kurar, Semgrep'i ayrı bir `.venv-tools` klasörüne yükler; repodaki kodu değiştirmez. Sanal ortamı elle etkinleştirmeniz gerekmez. Windows'ta Semgrep kurulamayabilir; kurulum uyarı verir ama durmaz.

## Arayüz: değişiklikleri izleyin

Aurora Pay tarayıcı arayüzü, Bob'un yaptığı değişiklikleri gözlemlemeniz için vardır. Servisi başlatır ve <http://127.0.0.1:8080> adresinde sunar:

```bash
python3 ui/server.py
```

Hesap ve transfer, raporlar, limitler (M1) ve **Değişiklik kontrolü** sekmeleri vardır; Bob kodu değiştirdikçe servis kendini yeniler.

## Klasörler

| Yol | İçerik |
|---|---|
| `missions/` | Görev kartları |
| `docs/` | PRD, API sözleşmesi, olay kaydı, güvenlik bileti, mühendislik el kitabı |
| `fixtures/` | Olay logu ve yeniden üretme betiği, tedarikçi SDK, müşteri verisi |
| `services/core/` | Üzerinde çalışılan servis (katmanlar: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)) |
| `services/limits/` | M1'de sizin yazacağınız servis |
| `services/shared/` | Servislerin ortak hata zarfı ve para yardımcıları |
| `ui/` | Aurora Pay tarayıcı arayüzü |
| `deploy/` | Dockerfile, Terraform, worker bağımlılıkları |
| `verify/` | Otomatik doğrulama kontrolleri |
| `scripts/` | Güvenlik taraması ve M5 işlev kontrolü |

## Sorun giderme

| Belirti | Çözüm |
|---|---|
| `bob` komutu bulunamıyor | Bob Shell'i kurun, yeni bir terminal açın |
| Bob Shell API anahtarı hatası | `BOB_API_KEY` tanımlı mı, kapsamı Inference mı? |
| "Python 3.11+ gerekli" | Python'u güncelleyin, eski `.venv` varsa silip `setup.py`'yi yeniden çalıştırın |
| Push veya PR yetkisi hatası | IDE'de GitHub oturumu açın, `gh auth login` çalıştırın |
| Bob araçları kısıtlı (Restricted Mode) | Klasörü açarken "Trust"ı onaylayın; boş klasör değil, klonlanmış repo açın |
| CI hiç çalışmıyor | Repo sayfasında *Actions* sekmesinden workflow'ları etkinleştirin |
| Özel mod / skill görünmüyor | YAML'da ASCII dışı karakter ve `fileRegex`'i kontrol edin, `Developer: Reload Window` çalıştırın |
| `@` ile dosya görünmüyor / `.bobignore` | Dosya `.bobignore` kapsamında olabilir; Bob bu dosyayı yazamaz, kendiniz oluşturun |
