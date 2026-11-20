# M0 - İlk gün: kurulum, servisi tanıma ve "Merhaba Bob"

**Süre:** 20 dk | **Bob özelliği:** Mod seçici, `@` bağlamı

> **Komutlar hakkında:** Her komut kendi kutusundadır (GitHub'da sağ üstteki düğmeyle kopyalanır).
> macOS/Linux'ta `python3`, Windows'ta `py` yazın. Etkileşimli, işletim sistemine göre seçmeli sürüm için
> [`KATILIMCI-KILAVUZU.html`](../KATILIMCI-KILAVUZU.html) dosyasını tarayıcıda açın.

## Durum

Aurora Bank'ın Instant Pay ekibine bu sabah katıldınız. İlk iş: repoyu kurun, servisi çalışırken görün ve Bob'un projeyi nasıl gördüğünü anlayın.

## Teslim edilecekler

- Kendi GitHub hesabınızdaki kopya klonlandı ve kurulum tamamlandı
- `verify m0` tüm kontrollerde **PASS**
- Servis arayüzde çalışıyor; demo hesapları oluşturdunuz ve bir transfer denediniz
- Endpoint sayısını Bob'un söylediğiyle kodda karşılaştırdınız (beklenen: **7**)
- `feature/<kısa-ad>` dalı açıldı

## Adım 1 - Ön koşul kontrolü

Dört komut da hata vermeden çalışmalı. Eksik olan varsa [README'deki ön koşullara](../README.md#ön-koşullar) bakın.

macOS/Linux:

```bash
python3 --version
```

Windows (PowerShell):

```powershell
py --version
```

```bash
git --version
```

```bash
bob --version
```

`BOB_API_KEY` tanımlı mı? macOS/Linux:

```bash
echo "${BOB_API_KEY:+BOB_API_KEY tanımlı}"
```

Windows (PowerShell):

```powershell
if ($env:BOB_API_KEY) { "BOB_API_KEY tanımlı" }
```

## Adım 2 - Kendi kopyanızı oluşturun ve klonlayın

1. GitHub'da template repo sayfasında **Use this template → Create a new repository** ile **kendi hesabınızda** bir kopya oluşturun.
2. Bob IDE'de komut paletini açın (`Ctrl/Cmd + Shift + P`), **Git: Clone** yazın, **Clone Git Repository** → **Clone from GitHub** (veya *Clone from URL*) seçin ve kendi kopyanızı seçin.
3. Klasör açılırken **"Yes, I trust the authors"** (Trust) seçeneğini onaylayın. Onaylamazsanız Restricted Mode açık kalır ve Bob'un araçları kısıtlanır.

> **Boş klasör açmayın, doğrudan klonlayın.** Aksi hâlde `origin` olmaz ve M8'de takılırsınız.
> Klonladığınız repo template'in kendisi değil, **sizin hesabınızdaki** kopya olmalı.

Komut satırı ile:

```bash
git clone https://github.com/<kullanici-adin>/<repo-adi>.git
```

```bash
cd <repo-adi>
```

Bob Shell'i her zaman klasörün **içinden** başlatın.

## Adım 3 - Kurulum

`setup.py` iki şey yapar: `.venv` sanal ortamını oluşturup `requirements-dev.txt` paketlerini kurar; `--scanners` ile Semgrep'i ayrı bir `.venv-tools` klasörüne yükler.
Repodaki kodu değiştirmez; sanal ortamı elle etkinleştirmeniz gerekmez.

```bash
python3 setup.py --scanners
```

Windows'ta `py setup.py --scanners`. Semgrep Windows'ta kurulamayabilir; kurulum uyarı verir ama durmaz (M5 taramasını WSL'de ya da CI'da çalıştırın).

## Adım 4 - Doğrulama

M0'da doğrulama kurulumdan hemen sonra gelir, çünkü sonraki görevlerin hepsi buna dayanır. Sonucu doğrulamak için aşağıdaki komutu kullanabilirsiniz:

```bash
python3 verify/run.py m0
```

## Adım 5 - Servisi ayağa kaldırın ve tanıyın

Aurora Pay tarayıcı arayüzünü başlatın (Bob'un yaptığı değişiklikleri sonraki görevlerde burada izleyeceksiniz):

```bash
python3 ui/server.py
```

Tarayıcıda <http://127.0.0.1:8080> adresini açın:

1. *Hesaplar ve transfer* sekmesinde **Demo hesapları ekle (A ve B)** düğmesine basın.
2. A'dan B'ye bir transfer gönderin; bakiyeleri izleyin.
3. Bu servisin ne yaptığını, hangi dosyanın neyi yönettiğini not edin.

Durdurmak için `Ctrl+C`. Servis kod değişince kendini yeniler.

## Adım 6 - Bob'a sorun

Yeni bir terminalde ya da IDE sohbetinde Bob'a projeyi **kendi cümlelerinizle** anlattırın ve `docs/` ile karşılaştırın. Aynı soruyu **iki farklı modda** sorup farkı not alın. Bob'a `services/core`'u açıklatın.

Bob endpoint sayısını söylediğinde kodda kendiniz sayın (endpointler `@app.` dekoratörleriyle tanımlı). macOS/Linux:

```bash
grep -c "@app\." services/core/main.py
```

Windows (PowerShell):

```powershell
(Select-String -Path services/core/main.py -Pattern "@app\.").Count
```

**İpucu:** Bob'a "kaç satır" diye sorarsanız tahmin yürütebilir; kendiniz sayın. macOS/Linux:

```bash
wc -l services/core/*.py
```

Windows (PowerShell):

```powershell
Get-ChildItem services/core/*.py | ForEach-Object { "{0} {1}" -f (Get-Content $_).Count, $_.Name }
```

## Adım 7 - Çalışma dalını açın

```bash
git switch -c feature/<kısa-ad>
```

Her görev bittiğinde bir commit atın (M8'de en az 3 anlamlı commit gerekir):

```bash
git add -A
```

```bash
git commit -m "Add limits service from PRD"
```

## Keşif noktaları

- Sohbet kutusunun yanındaki **mod seçici**: her mod neye izin veriyor?
- Sohbet alanına `@` yazınca ne oluyor?
- Bonus: Bob sohbetinde `/init` komutunu deneyin; ürettiği bilgiyi projeyle karşılaştırın.

## İpucu

- **İpucu 1:** FAIL satırını okuyun. Bob'un cevabını sadece dinlemeyin, kodda sayarak doğrulayın.
- **İpucu 2:** Kurulum sorunlarının çoğu `setup.py` çalışmadan `verify` çalıştırmaktan çıkar. Klasör Bob'da açık değilse `@` listesi boş görünür; "Trust" onaylanmadıysa araçlar kısıtlıdır.
- **Eğitmenden yardım:** İpucu 2 yetmediyse eğitmeni çağırın.
