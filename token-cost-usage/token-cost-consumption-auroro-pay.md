# Task 0: First Day (İlk Gün)

macOS'ta M0 kurulumunu baştan sona nasıl tamamladığımın kısa özeti. Kurulum sırasında Claude Code'a sorduğum sorular ve bu session'ın token/maliyet kullanımı da aşağıda.

- **Platform:** macOS (Apple Silicon, Homebrew kurulu)
- **Tarih:** 2026-11-24
- **Session ID:** `1f4e0172-1203-4265-bb5a-8b84d9d36a8a`

## 1. Kurulum adımları (macOS)

### 1.1 İlk deneme: Python sürüm hatası

```bash
python3 setup.py --scanners
```

```
HATA: Python 3.11 veya üzeri gerekli, bulunan: 3.9.
```

macOS ile gelen `python3` 3.9 sürümünde. Proje 3.11 veya üzerini istiyor; kodda `str | None` gibi yeni sözdizimi kullanılıyor.

### 1.2 Yeni Python kurulumu

```bash
brew install python@3.12
/opt/homebrew/bin/python3.12 --version
```

### 1.3 Kurulumu yeni Python ile çalıştırma

```bash
/opt/homebrew/bin/python3.12 setup.py --scanners
```

Alternatif olarak `PYTHON=/opt/homebrew/bin/python3.12 ./setup.sh --scanners` de kullanılabilir.

Bu adım iki sanal ortam oluşturur:
- `.venv`: proje bağımlılıkları (fastapi, uvicorn, pydantic, pytest...)
- `.venv-tools`: Semgrep (M5 için)

> İpucu: Daha önce 3.9 ile oluşturulmuş bir `.venv` varsa önce silin (`rm -rf .venv .venv-tools`), sonra kurulumu tekrar çalıştırın.

### 1.4 Doğrulama

```bash
python3 verify/run.py m0
```

```
=== M0 Kurulum ===
7 passed in 7.11s
[PASS] Python 3.11 veya uzeri
[PASS] Bagimliliklar kurulu (fastapi, pytest, httpx, yaml)
[PASS] Aurora Core uygulamasi ayaga kalkiyor (/health)
[PASS] Gorev dosyalari yerinde (docs, fixtures, deploy)
[PASS] Git kurulu ve klasor bir git deposu
[PASS] semgrep kurulu (M5 icin)
[PASS] Bob Shell (bob komutu) kurulu (M2 icin)

M0 Kurulum: PASS  7/7 kontrol  [7.3s]
```

Bu çıktı eğitmene gönderilir.

## 2. Claude Code'a sorulan sorular

| # | Soru | Kısa cevap |
|---|---|---|
| 1 | `setup.py` "Python 3.11 gerekli" hatası veriyor, nasıl çözerim? | `brew install python@3.12`, ardından kurulumu `/opt/homebrew/bin/python3.12` ile çalıştır. |
| 2 | Bu uygulama hakkında bilgi verir misin? | Bob'u öğretmek için hazırlanmış 4 saatlik bir atölye. Senaryo: Aurora Bank'ta FastAPI ile yazılmış bir bankacılık servisi. M0–M8 arası 9 görev var, her biri bir Bob özelliğini gösteriyor. |
| 3 | `services/core` içinde kaç endpoint, kaç satır kod var? | 7 endpoint (hepsi `main.py` içinde). 201 satır; boş satır ve yorumlar hariç ~148. |
| 4 | Repoda toplam kaç satır kod var? | Toplam 5.917 satır; kod ~3.000. Python 2.302 satır, bunun 1.497'si `verify/` testleri. |
| 5 | Bu session'da kaç token, ne kadar süre, hangi model kullanıldı? | Aşağıdaki "Kullanım" bölümü. |
| 6 | Maliyeti de ekleyip bir dosyada tut. | Bu dosya. |

### Endpoint'ler (`services/core/main.py`)

| Metot | Yol |
|---|---|
| GET | `/health` |
| POST | `/accounts` |
| GET | `/accounts/{account_id}` |
| POST | `/transfers` |
| GET | `/transfers/{transfer_id}` |
| GET | `/reports/transfers` |
| POST | `/reports/archive` |

## 3. Kullanım: token ve maliyet

Kaynak: `~/.claude/projects/-Users-barissozen-bobathon-auroro-pay2/1f4e0172-1203-4265-bb5a-8b84d9d36a8a.jsonl`

### Süre

| | Saat (yerel, UTC+3) |
|---|---|
| Başlangıç | 09:38:23 |
| Son kayıt | 09:54:11 |
| **Toplam** | **~15 dk 48 sn** |

### Model

| Model | API çağrısı |
|---|---|
| Claude Opus 5.5 (`claude-opus-5-5`) | 14 |

### Token kullanımı ve maliyet

Fiyatlar: Opus 5.5, Anthropic API listesi, 1M token başına.

| Tür | Token | Birim fiyat | Maliyet |
|---|---:|---:|---:|
| Input (önbelleksiz) | 38 | $4.00 | $0.0002 |
| Output | 6.369 | $20.00 | $0.1274 |
| Cache yazma (1 saat TTL) | 27.456 | $8.00 | $0.2196 |
| Cache okuma | 663.709 | $0.20 | $0.1327 |
| **Toplam** | **697.572** | | **~$0.48** |

### Notlar

- Token'ların yaklaşık %95'i cache okuma. Konuşma her mesajda modele yeniden gönderiliyor, ancak önbellekten okunduğu için input fiyatının yalnızca 1/20'si ödeniyor.
- En büyük maliyet kalemi cache yazma (%46). Claude Code 1 saatlik önbellek kullanıyor ve bu önbelleğin yazma fiyatı normal input fiyatının 2 katı.
- Maliyet API liste fiyatıyla hesaplanmış tahmini bir değerdir. Claude Pro/Max aboneliği ile kullanılıyorsa ayrıca ücret ödenmez; kullanım abonelik limitinden düşer.
- Rakamlar 6. soruya kadar olan kısmı kapsar. Canlı değer için Claude Code içinde `/cost` yazın.

---

# Task 1: Limits & Statements Servisi (M1 - Dokümandan koda)

Regülatör şartı: müşteri bazlı günlük ve işlem başına transfer limiti, ayrıca işlem dökümü (statement). Kaynak dokümanlar `docs/PRD-limits.md` ve `docs/API-SPEC-limits.yaml`. Özet Word dosyası: `task1-limits-statements-auroro-pay.docx`.

- **Platform:** macOS
- **Tarih:** 2026-11-24
- **Session ID:** `5bc0409b-171e-4417-ab02-944c12576fe4`

## 1. Akış

| # | İstek | Sonuç |
|---|---|---|
| 1 | Servisi PRD ve API-SPEC'e göre yaz | Servis plan yazılmadan kodlandı; `verify m1` 35/35 PASS |
| 2 | Önce `task1-plan.md` oluştur, soruları sor, onaysız ilerleme | Plan yazıldı, 4 soru soruldu, önceki kod silindi |
| 3 | Planı onayla | Servis ve testler plana göre sıfırdan yazıldı |
| 4 | Token/maliyet raporunu güncelle, Task 1 docx'i oluştur | Bu bölüm ve docx |

### Plan kararları

| Soru | Karar |
|---|---|
| Test kapsamı hedefi | En az %85 |
| `customer_id` doğrulaması | Yalnızca HTTP katmanında |
| JSON'daki `from` alanı | `Query(alias="from")` |
| Limit, kullanılmış tutarın altına düşürülürse `remaining_daily` | `"0.00"` (negatif değer dönmez) |

### Çıktılar

| Dosya | İçerik |
|---|---|
| `task1-plan.md` | Uygulama planı ve kararlar |
| `services/limits/store.py` | Bellek içi depolama, kilit, `reset()` |
| `services/limits/service.py` | PRD §4'teki 10 iş kuralı |
| `services/limits/main.py` | `app`, doğrulama, hata zarfı |
| `tests/test_limits.py` | API seviyesinde 48 test |

### Doğrulama

| Kontrol | Sonuç |
|---|---|
| `pytest tests/test_limits.py --cov=services/limits` | 48 passed, kapsam %98 |
| `python3 verify/run.py m1` | **35/35 PASS** |
| `semgrep` (`services/limits`) | 0 bulgu |

## 2. Kullanım: token ve maliyet

Kaynak: `~/.claude/projects/-Users-barissozen-bobathon-auroro-pay2/5bc0409b-171e-4417-ab02-944c12576fe4.jsonl`

### Süre

| | Saat (yerel, UTC+3) |
|---|---|
| Başlangıç | 10:04:36 |
| Son kayıt | 10:17:17 |
| **Toplam** | **~12 dk 41 sn** |

### Model

| Model | API çağrısı |
|---|---|
| Claude Opus 5.5 (`claude-opus-5-5`) | 15 |

### Token kullanımı ve maliyet

Fiyatlar: Opus 5.5, Anthropic API listesi, 1M token başına.

| Tür | Token | Birim fiyat | Maliyet |
|---|---:|---:|---:|
| Input (önbelleksiz) | 36 | $4.00 | $0.0001 |
| Output | 25.999 | $20.00 | $0.5200 |
| Cache yazma (1 saat TTL) | 56.614 | $8.00 | $0.4529 |
| Cache okuma | 857.971 | $0.20 | $0.1716 |
| **Toplam** | **940.620** | | **~$1.14** |

### Notlar

- Token'ların yaklaşık %91'i cache okuma.
- Task 0'dan farklı olarak en büyük maliyet kalemi output (%45). Sebep, bu görevde servis kodunun ve testlerin iki kez yazılması (önce plansız, sonra plana göre).
- Rakamlar bu rapor isteğinden önceki kısmı kapsar. Canlı değer için `/cost` yazın.

---

# Özet: görev bazında kullanım

| Görev | Session | Süre | API çağrısı | Token | Maliyet |
|---|---|---:|---:|---:|---:|
| Task 0: First Day | `1f4e0172…` | ~15 dk 48 sn | 14 | 697.572 | ~$0.48 |
| Task 1: Limits & Statements | `5bc0409b…` | ~12 dk 41 sn | 15 | 940.620 | ~$1.14 |
| **Toplam** | | **~28 dk 29 sn** | **29** | **1.638.192** | **~$1.62** |
