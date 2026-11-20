# M5 - Bob Findings: bulguları görün, Bob'a düzelttirin

**Süre:** 20 dk | **Bob özelliği:** **Bob Findings** paneli, **Fix with Bob**, `.devsecignore`

> macOS/Linux'ta `python3`, Windows'ta `py` yazın.

## Durum

Canlıya çıkış öncesi pentest sonuçları geldi: [`docs/SECURITY-TICKET-317.md`](../docs/SECURITY-TICKET-317.md) bölüm A.
**Tüm maddeler kapanmadan** canlıya çıkış onayı yok. Bulgular kodda ve altyapı dosyalarında:

| # | Bulgu | Nerede |
|---|---|---|
| A1 | Koda gömülü gizli bilgiler | `services/core/` |
| A2 | SQL injection | `services/core/` |
| A3 | Komut enjeksiyonu ve yol gezintisi | `services/core/` |
| A4 | Docker ve Terraform hataları | `deploy/` |
| A5 | Zafiyetli bağımlılıklar | `deploy/worker/` |

## Teslim edilecekler

- Bulgular listelendi ve riske göre sıralandı (Findings paneli veya `scan.py --verbose`)
- A1-A4 kapandı: `scan.py` **0 bulgu** veriyor
- A5 (bağımlılıklar) ayrıca kontrol edildi ve kapandı
- İşlev kontrolü geçti
- `verify m5` tüm kontrollerde PASS

## Adım 1 - Bulguları görün

**Bob Findings** panelini açın (DevSecOps paketi kuruluysa tarama sürekli çalışır, değilse komut paletinden başlatın). **Panel başlangıçta boş görünebilir**; taramanın bitmesini bekleyin ya da elle başlatın. Bulguları listeleyin ve risklerine göre sıralayın.

Panel yoksa aynı bulguları Semgrep ile görün (başlangıçta 13 bulgu beklenir):

```bash
python3 scripts/scan.py --verbose
```

## Adım 2 - Düzelttirin

Bir bulguyu seçip **Fix with Bob** deyin. Bob, bulgu ayrıntılarıyla dolu bir görev başlatır. Sonra kalan bulguları toplu seçerek kapatın.

> **Yasak:** `# nosemgrep` ile susturmak yok. Gerçek bir yanlış pozitif için doğru yol `.bob/.devsecignore` dosyasıdır. Kaynakları silerek de "çözemezsiniz".

## Adım 3 - A5 bağımlılıklarını ayrıca kontrol edin

**Semgrep bağımlılıkları taramaz.** `scan.py` 0 bulgu dese bile A5 açık olabilir. A5, `deploy/worker/requirements.txt` içindeki zafiyetli sürümlerin yükseltilmesiyle kapanır ve yalnızca `verify m5` ile doğrulanır. Bob'a bağımlılıkları da yükselttirdiğinizden emin olun.

## Adım 4 - İşlev kontrolü

Güvenlik düzeltmesi geçerli girdiyi bozmamalı. Bu betik üç şeyi dener: geçerli arşiv adı `{'exit_code': 0}` döndürmeli, geçersiz adlar (komut enjeksiyonu, yol gezintisi) `422` ile reddedilmeli, SQL injection denemesi `[]` döndürmeli.
Geçersiz ad denemeleri geçici bir dizinde çalışır, repoda dosya bırakmaz. macOS/Linux:

```bash
.venv/bin/python scripts/m5_islev_kontrolu.py
```

Windows (PowerShell):

```powershell
.venv\Scripts\python scripts/m5_islev_kontrolu.py
```

## Adım 5 - Doğrulama

Sonucu doğrulamak için aşağıdaki komutları kullanabilirsiniz. Doğrulayıcı komut enjeksiyonunu izole bir geçici dizinde dener; repoda dosya bırakmaz, elle temizlik gerekmez.

```bash
python3 scripts/scan.py
```

```bash
python3 verify/run.py m5
```

Arayüzde (`python3 ui/server.py`) *Raporlar* sekmesindeki *Enjeksiyon dene* ve *Yol gezintisi dene* düğmeleri düzeltmenizi canlı gösterir.

> Windows'ta Semgrep kurulamadıysa taramayı WSL'de ya da PR üzerindeki CI'da çalıştırın.

## Keşif noktaları

- Bulguları bulmak ile düzeltmek aynı araç mı? Findings paneli hangi kısmı yapıyor, Bob hangisini?
- Bob düzeltirken kodu mu siliyor, yoksa kökten mi çözüyor? (Doğrulayıcı kaynakların silinmesini kabul etmez.)
- Gizli bilgiyi ortam değişkenine taşıdığınızda eski değer Git geçmişinde kalır mı?

## İpucu

- **İpucu 1:** Önce bulguların hepsini görün, sonra düzeltin. Düzeltme geçerli girdiyle işlevi bozmamalı.
- **İpucu 2:** A1: `services/core/config.py` (eski değerler Dockerfile ve Terraform dahil hiçbir yerde kalmasın). A2 ve A3: `services/core/reports.py`. A4: `deploy/Dockerfile` ve `deploy/terraform/main.tf` (el kitabı bölüm 5). A5: `deploy/worker/requirements.txt`.
- **Eğitmenden yardım:** İpucu 2 yetmediyse eğitmeni çağırın.
