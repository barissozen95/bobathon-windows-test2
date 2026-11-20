# M2 - Üretim hatası (Bob Shell / CLI)

**Süre:** 20 dk | **Bob özelliği:** **Bob Shell / CLI** (`bob chat`, `bob run`)

> macOS/Linux'ta `python3`, Windows'ta `py` yazın. `.venv` içindeki Python: macOS/Linux `.venv/bin/python`, Windows `.venv\Scripts\python`.

## Durum

SEV-2 açık: müşterilerin parası **iki kez** düşüyor, bazı transferlerde para alıcıya **hiç ulaşmıyor**, bakiyelerde kuruş altı farklar var ve istemciler düzgün bir hata alamıyor.

- [`docs/INCIDENT-2041.md`](../docs/INCIDENT-2041.md): olay kaydı
- [`fixtures/incident/transfer.log`](../fixtures/incident/transfer.log): sunucu logu
- [`fixtures/incident/repro.py`](../fixtures/incident/repro.py): sorunu yeniden üretir (bozukken `1`, düzelince `0` ile çıkar)
- [`docs/FEE-POLICY.md`](../docs/FEE-POLICY.md) ve [`docs/ENGINEERING-HANDBOOK.md`](../docs/ENGINEERING-HANDBOOK.md) bölüm 1-2

Bu görevi IDE sohbetinde değil, **terminalde Bob Shell ile** yürütün.

> **Kapsam: yalnızca bu 4 şikâyet.** Bob `verify/` klasörünü okuyabilir ve M4'ün gizli hatalarını da düzeltmeye kalkabilir; istemediğinizi ona açıkça söyleyin.

## Teslim edilecekler

- Dört şikâyetin her biri için kök neden bulundu ve `repro.py` çıktısıyla eşleştirildi
- `repro.py` çıkış kodu `0`
- `verify m2`: **24 kontrolün tamamı** PASS
- `pytest` hâlâ yeşil

## Adım 1 - Teşhis (etkileşimli, düzeltme yasak)

**İki pencere, iki iş.** Terminal 1'de repo kökünden Bob Shell'i başlatın:

```bash
bob chat
```

Bob'a olay kaydını ve logu gösterip **kök nedenleri** bulmasını isteyin. **Düzeltmesini açıkça yasaklayın.**

> **API anahtarı hatası:** `bob chat` kimlik/anahtar hatası verirse `BOB_API_KEY` bu terminalde tanımlı değildir. macOS/Linux:
>
> ```bash
> export BOB_API_KEY="<anahtarınız>"
> ```
>
> Windows (PowerShell):
>
> ```powershell
> $env:BOB_API_KEY="<anahtarınız>"
> ```

Terminal 2'de olayı yeniden üretin. macOS/Linux:

```bash
.venv/bin/python fixtures/incident/repro.py
```

Windows (PowerShell):

```powershell
.venv\Scripts\python fixtures/incident/repro.py
```

Çıkış kodunu görmek için hemen ardından. macOS/Linux:

```bash
echo $?
```

Windows (PowerShell):

```powershell
echo $LASTEXITCODE
```

Bob'un bulduğu her nedeni `repro.py` çıktısıyla eşleştirin: kaç şikâyet kapandı, kaçı açık?

## Adım 2 - Düzeltme (tek seferlik, fren takılı)

Aynı işi bu kez `bob run` ile, **tur ve maliyet sınırı koyarak** yaptırın:

```bash
bob run --max-turns <n> --max-cost <bobcoin> "<görev tanımınız>"
```

```bash
bob run --help
```

> **Tehlike:** `bob run` tüm araçları **önceden onaylı** çalıştırır; komut başına onay istemez. `--max-turns` ve `--max-cost` sizin frenizdir.

## Adım 3 - Doğrulama

Sonucu doğrulamak için aşağıdaki komutları sırayla kullanabilirsiniz. macOS/Linux:

```bash
.venv/bin/python fixtures/incident/repro.py
```

```bash
.venv/bin/python -m pytest
```

Windows (PowerShell):

```powershell
.venv\Scripts\python fixtures/incident/repro.py
```

```powershell
.venv\Scripts\python -m pytest
```

```bash
python3 verify/run.py m2
```

Arayüzdeki *Değişiklik kontrolü* sekmesinde (`python3 ui/server.py`) çift borçlandırma ve 500 hataları da canlı görülür.

## Keşif noktaları

- `bob chat` ile `bob run` arasındaki fark nedir?
- `--max-turns` ve `--max-cost` ile çalışmayı sınırlayabiliyor musunuz?
- Bob terminalde komut çalıştırmadan önce ne soruyor? Hangi komutlara izin vermek mantıklı, hangilerine asla?
- Bob log dosyasını kendisi mi buldu, siz mi gösterdiniz? Sonuç farkı oldu mu?

## İpucu

- **İpucu 1:** Dört şikâyet = dört ayrı neden. "Tek hata" diye düşünüyorsanız teşhisi yeniden isteyin.
- **İpucu 2:** Hepsi `services/core/` altında: çift borçlandırma (`store.py` içindeki `idempotency` sözlüğü `service.py`'da kullanılıyor mu?), kaybolan para (bakiye düşüşü ile alıcı aramasının sırası: önce doğrula, sonra yaz), kuruş farkları (`fees.py` ve `models.py` sayı türü, ücret eşiği), 500 hataları (genel `Exception`; el kitabı bölüm 2'deki hata zarfı), gizli tuzak (logdaki ad-soyad ve IBAN).
- **Eğitmenden yardım:** İpucu 2 yetmediyse eğitmeni çağırın.
