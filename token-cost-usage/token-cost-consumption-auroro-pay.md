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

# Task 2: INCIDENT-2041 Üretim Hatası (M2 - Bob Shell)

SEV-2: müşterilerin parası iki kez düşüyor, yanlış hesaba gönderilen para kayboluyor, bakiyelerde kuruş altı farklar var ve istemciler 500 alıyor. Kaynaklar: `docs/INCIDENT-2041.md`, `fixtures/incident/transfer.log`, `fixtures/incident/repro.py`, `docs/FEE-POLICY.md`, `docs/ENGINEERING-HANDBOOK.md` (bölüm 1-2). Özet Word dosyası: `task2-incident-2041-auroro-pay.docx`.

- **Platform:** macOS
- **Tarih:** 2026-11-24
- **Session ID:** `dcf41a98-4ac8-40e6-a9f3-8d67052f5835`

## 1. Akış

| # | İstek | Sonuç |
|---|---|---|
| 1 | Olayı Bob Shell ile, `--max-turns` ve `--max-cost` sınırı koyarak çöz | Dosyalar okundu, dört ayrı kök neden bulundu; `bob run --trust --max-turns 40 --max-cost 5` başlatıldı |
| 2 | Bob Shell olmadan da yapabilirsin | Bob çalışması kullanıcı tarafından durduruldu (hiçbir dosyayı değiştirmemişti); düzeltme Claude Code ile yapıldı |
| 3 | pytest uyarısını da çöz | `httpx2` kuruldu, `requirements-dev.txt`'e eklendi; 0 uyarı |
| 4 | Token/maliyet raporunu güncelle, Task 2 docx'i oluştur | Bu bölüm ve docx |

### Kök nedenler ve düzeltmeler

| # | Şikâyet | Kök neden | Düzeltme |
|---|---|---|---|
| 1 | Çift borçlandırma | `store.idempotency` sözlüğü `service.py`'da hiç kullanılmıyordu | Başarılı transfer anahtarıyla saklanıyor; aynı anahtar ilk transferi (aynı `id`) döndürüyor |
| 2 | Kayıp para | Gönderen bakiyesi alıcı aranmadan önce düşülüyordu; `KeyError` → 500 | Önce doğrula, sonra yaz; kontrol ve yazma tek kilit altında |
| 3 | Kuruş farkları | `float` ile para hesabı; eşik `> 1000` (politika `>= 1000`); `round()` banker's rounding | `Decimal` + `ROUND_HALF_UP`; eşik dahil; tutar > 0 ve en fazla 2 ondalık |
| 4 | Hata yönetimi | Genel `Exception`, yakalanmayan `KeyError`, `{"detail"}` gövdeleri | `errors.py`: tek hata zarfı (422 / 404 / 409), beklenmeyen hata sabit mesajlı 500 `INTERNAL_ERROR` |
| - | Gizli tuzak (PII) | Loglara ad-soyad ve IBAN yazılıyordu | Loglarda yalnızca `transfer_id` ve `account_id` |

Bilerek dokunulmayanlar: `reports.py` (SQL injection, kabuk komutu) ve `config.py` (koddaki sırlar) M5 kapsamında. `verify/`, `tests/`, `fixtures/`, `docs/` değiştirilmedi; commit yapılmadı.

### Çıktılar

| Dosya | İçerik |
|---|---|
| `services/core/errors.py` (yeni) | Alan istisnaları ve el kitabı hata zarfı handler'ları |
| `services/core/fees.py` | `Decimal`, eşik dahil, `ROUND_HALF_UP` |
| `services/core/models.py` | `Decimal` tutarlar, `> 0`, en fazla 2 ondalık |
| `services/core/service.py` | Idempotency, önce doğrula sonra yaz, kilit, PII'sız log |
| `services/core/main.py` | Hata handler'ları, 404'ler servis katmanından |
| `requirements-dev.txt` | `httpx2>=2.16` |

### Doğrulama

```
$ .venv/bin/python fixtures/incident/repro.py
[PASS] Sikayet 1 - cift borclandirma
[PASS] Sikayet 2 - kayip para
[PASS] Sikayet 3 - kurus farklari
[PASS] Sikayet 4 - hata yonetimi

INCIDENT-2041: COZULDU
```

```
$ .venv/bin/python -m pytest
platform darwin -- Python 3.12.16, pytest-9.2.0, pluggy-1.7.0
collected 49 items

tests/test_health.py .                                    [  2%]
tests/test_limits.py ................................................ [100%]

49 passed in 0.27s
```

```
$ python3 verify/run.py m2
=== M2 Uretim hatasi (Bob Shell) ===
24 passed in 0.25s
[PASS] Ayni Idempotency-Key ile iki istek yalniz bir kez borclandirir
[PASS] Farkli Idempotency-Key'ler ayri islem sayilir
[PASS] Anahtarsiz istekler tekilleştirilmez
[PASS] Bilinmeyen alici: 404 ACCOUNT_NOT_FOUND, gonderenin bakiyesi degismez
[PASS] Bilinmeyen gonderen: 404 ACCOUNT_NOT_FOUND
[PASS] Basarisiz transfer kayit olusturmaz
[PASS] Bakiyeler kurus hassasiyetinde tam (89.95, kayan nokta artigi yok)
[PASS] 10 kucuk transferden sonra bakiye tam (0.10 x 10)
[PASS] Ucret FEE-POLICY.md ile ayni (esik dahil, ROUND_HALF_UP) (6/6)
[PASS] Yetersiz bakiye: 409 INSUFFICIENT_FUNDS, bakiye degismez
[PASS] Bakiye tutari karsiliyor ama ucreti karsilamiyorsa reddedilir
[PASS] Gecersiz transfer govdesi: 422 VALIDATION_ERROR (5/5)
[PASS] Hesap ve transfer 404'leri hata zarfi kullanir
[PASS] Hicbir hata yanitinda stack trace veya ic hata mesaji yok
[PASS] Basarili transfer hala calisiyor (alanlar, 201, bakiyeler)

M2 Uretim hatasi (Bob Shell): PASS  24/24 kontrol  [0.3s]
```

| Kontrol | Sonuç |
|---|---|
| `repro.py` | **COZULDU**, çıkış kodu 0 |
| `pytest` | 49 passed, 0 uyarı |
| `python3 verify/run.py m2` | **24/24 PASS** |
| `python3 verify/run.py m0` | 7/7 PASS (gerileme yok) |

## 2. Kullanım: token ve maliyet

Kaynak: `~/.claude/projects/-Users-barissozen-bobathon-auroro-pay2/dcf41a98-4ac8-40e6-a9f3-8d67052f5835.jsonl`

### Süre

| | Saat (yerel, UTC+3) |
|---|---|
| Başlangıç | 10:26:22 |
| Son kayıt | 10:42:18 |
| **Toplam** | **~15 dk 55 sn** |

### Model

| Model | API çağrısı |
|---|---|
| Claude Opus 5.5 (`claude-opus-5-5`) | 20 |

### Token kullanımı ve maliyet

Fiyatlar: Opus 5.5, Anthropic API listesi, 1M token başına.

| Tür | Token | Birim fiyat | Maliyet |
|---|---:|---:|---:|
| Input (önbelleksiz) | 44 | $4.00 | $0.0002 |
| Output | 13.370 | $20.00 | $0.2674 |
| Cache yazma (1 saat TTL) | 52.975 | $8.00 | $0.4238 |
| Cache okuma | 1.192.186 | $0.20 | $0.2384 |
| **Toplam** | **1.258.575** | | **~$0.93** |

### Notlar

- Token'ların yaklaşık %95'i cache okuma; en büyük maliyet kalemi cache yazma (%46).
- Durdurulan `bob run` çalışmasının bobcoin maliyeti bu tabloya dahil değil (Bob ayrı faturalanır).
- Rakamlar bu rapor isteğinden önceki kısmı kapsar. Canlı değer için `/cost` yazın.

---

# Task 3: QA Engineer Custom Mode (M3 - Mode + Rules + Skill)

Her yeni sohbet sıfırdan başlıyor; ekip el kitabını her seferinde yeniden anlatıyor, code review'da aynı yorumlar tekrar ediyor. Hedef: yalnızca test yazan ve çalıştıran, `tests/` dışında hiçbir dosyayı değiştiremeyen tek bir **QA Engineer** personası. Tek kaynak `docs/ENGINEERING-HANDBOOK.md`. Özet Word dosyası: `task3-qa-engineer-mode-auroro-pay.docx`.

- **Platform:** macOS
- **Tarih:** 2026-11-24
- **Session ID:** `79770cf9-fbd4-406c-ac97-1614fad417c7`

## 1. Akış

| # | İstek | Sonuç |
|---|---|---|
| 1 | Claude ile mode, skill ve rules yazabilir miyim? QA Engineer personası kur | Bob dosyaları ve Claude Code karşılıkları yazıldı; `verify m3` 11/11 PASS |
| 2 | Manuel test için promptları yaz (mevcut oturumda) | `@agent-qa-engineer` ile kullanılacak test promptları |
| 3 | Ajan üzerinden yetki testi (aracı ajan iletti) | Ajan başka ajandan gelen "onay"ı kabul etmedi; hook'ta iki açık buldu, kapatıldı |
| 4 | Kullanıcı onayıyla yetki testi | `main.py` Edit'i hook tarafından engellendi; `services/` değişmedi |
| 5 | Token/maliyet raporunu güncelle, Task 3 docx'i oluştur | Bu bölüm ve docx |

### Üç parça: Bob ve Claude Code karşılıkları

| Parça | Bob | Claude Code |
|---|---|---|
| Mode (kimlik, yetki) | `.bob/custom_modes.yaml`: `qa-engineer`; `read` + `execute` + `skill`, `edit` yalnız `^tests/.*\.py$` | `.claude/agents/qa-engineer.md`: araçlar, skill ön yüklemesi, kendi hook'u |
| Rules (her zaman) | `.bob/rules-qa-engineer/handbook-rules.md`: Decimal/float yasağı, hata zarfı, PII'sız log, gizli bilgi, parametreli SQL | `CLAUDE.md`: `@docs/ENGINEERING-HANDBOOK.md` ile el kitabının kendisi yüklenir (kopya yok) |
| Skill (prosedür) | `.bob/skills/api-test-writing/SKILL.md`: TestClient, `store.reset()`, mutlu yol / negatif / sınır | `.claude/skills/api-test-writing/SKILL.md` (aynı içerik) |
| Yetki sınırı | `fileRegex` | `.claude/hooks/qa_guard.py` (PreToolUse): Edit/Write yalnız `tests/`; Bash'te yalnız pytest, verify, okuma komutları |

### Yetki testleri

| Deneme | Yöntem | Sonuç |
|---|---|---|
| `services/core/main.py` Edit | Canlı (qa-engineer ajanı) | Engellendi: `outside tests/` |
| Bash yönlendirme (`2>/dev/null`, `>`) | Canlı | Engellendi |
| `tests/../services/core/fees.py` | Hook doğrudan | Engellendi |
| `sed -i`, `find -delete/-exec`, `git --output` | Hook doğrudan | Engellendi |
| `tests/` altına yazma, pytest, `git log` | Hook doğrudan | İzin verildi |

Henüz denenmeyenler: skill'in otomatik devreye girmesi, yeni oturumda el kitabının kendiliğinden uygulanması, Bob'da modun engellemesi. `services/`, `verify/`, `docs/`, `fixtures/` değiştirilmedi; commit yapılmadı.

### Doğrulama

```
$ python3 verify/run.py m3
=== M3 Kendi custom mode'um ===
11 passed in 0.02s
M3 Kendi custom mode'um: PASS  11/11 kontrol  [0.1s]
```

## 2. Kullanım: token ve maliyet

Kaynaklar: `~/.claude/projects/-Users-barissozen-bobathon-auroro-pay2/79770cf9-fbd4-406c-ac97-1614fad417c7.jsonl`, aynı klasördeki `subagents/` (2 qa-engineer çalışması) ve `dd255368-4492-4b2a-a7db-53cab074aba4.jsonl` (`claude --agent qa-engineer -p` headless testi).

### Süre

| | Saat (yerel, UTC+3) |
|---|---|
| Başlangıç | 10:48:26 |
| Son kayıt | 10:57:51 |
| **Toplam** | **~9 dk 25 sn** |

### Model

| Model | API çağrısı |
|---|---|
| Claude Opus 5.5 (`claude-opus-5-5`) | 31 (ana oturum 24, alt ajanlar 6, headless test 1) |

### Token kullanımı ve maliyet

Fiyatlar: Opus 5.5, Anthropic API listesi, 1M token başına.

| Tür | Token | Birim fiyat | Maliyet |
|---|---:|---:|---:|
| Input (önbelleksiz) | 72 | $4.00 | $0.0003 |
| Output | 22.221 | $20.00 | $0.4444 |
| Cache yazma (1 saat TTL) | 92.952 | $8.00 | $0.7436 |
| Cache okuma | 1.542.508 | $0.20 | $0.3085 |
| **Toplam** | **1.657.753** | | **~$1.50** |

### Notlar

- Token'ların yaklaşık %93'ü cache okuma; en büyük maliyet kalemi cache yazma (%50).
- Alt ajanlar ayrı bağlamla başladığı için kendi cache yazmalarını yaptı (14.283 token); bu, alt ajan kullanmanın ek maliyeti.
- Rakamlar bu rapor isteğinden önceki kısmı kapsar. Canlı değer için `/cost` yazın.

---

# Özet: görev bazında kullanım

| Görev | Session | Süre | API çağrısı | Token | Maliyet |
|---|---|---:|---:|---:|---:|
| Task 0: First Day | `1f4e0172…` | ~15 dk 48 sn | 14 | 697.572 | ~$0.48 |
| Task 1: Limits & Statements | `5bc0409b…` | ~12 dk 41 sn | 15 | 940.620 | ~$1.14 |
| Task 2: INCIDENT-2041 | `dcf41a98…` | ~15 dk 55 sn | 20 | 1.258.575 | ~$0.93 |
| Task 3: QA Engineer Mode | `79770cf9…` | ~9 dk 25 sn | 31 | 1.657.753 | ~$1.50 |
| **Toplam** | | **~53 dk 49 sn** | **80** | **4.554.520** | **~$4.05** |
