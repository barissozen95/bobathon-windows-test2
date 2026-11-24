# Task 1 - Limits & Statements Servisi: Uygulama Planı

**Kaynaklar:** `docs/PRD-limits.md`, `docs/API-SPEC-limits.yaml`, `docs/ENGINEERING-HANDBOOK.md`
**Durum:** Onay bekliyor. Onay gelmeden kod yazılmaz.

## 1. Hedef

`services/core`'dan bağımsız, küçük bir FastAPI servisi:
- müşteri bazlı **günlük** ve **işlem başına** transfer limiti,
- **onaylanmış** işlemler için tarih aralığına göre döküm (statement).

Depolama bellek içi, para birimi tek (TRY). Kimlik doğrulama ve kalıcı veritabanı kapsam dışı.

## 2. Kısıtlar

- Servis `services/limits/main.py` içinde `app` adlı FastAPI uygulaması olacak.
- `services/core`'a dokunulmayacak, oradan import yapılmayacak.
- Yeni bağımlılık eklenmeyecek (fastapi, pydantic ve uvicorn zaten mevcut).

## 3. Dosya yapısı

| Dosya | Sorumluluk |
|---|---|
| `services/limits/__init__.py` | Paket tanımı |
| `services/limits/store.py` | Bellek içi depolar (`limits`, `usage[(customer_id, gün)]`, `entries[customer_id]`), bir kilit ve `reset()` |
| `services/limits/service.py` | İş kuralları (PRD §4): varsayılan limitler, limit tanımlama, yetkilendirme, statement |
| `services/limits/main.py` | HTTP katmanı: endpoint'ler, girdi ayrıştırma ve doğrulama, hata zarfı, yanıt biçimi |
| `tests/test_limits.py` | `TestClient` ile API seviyesinde testler |

## 4. Endpoint'ler (API-SPEC)

| Metot | Yol | Davranış |
|---|---|---|
| PUT | `/limits/{customer_id}` | Limitleri tanımlar veya günceller, `source: custom` döner |
| GET | `/limits/{customer_id}` | Limitleri getirir. Tanımlı değilse varsayılanları `source: default` ile döner |
| POST | `/limits/{customer_id}/authorize` | Kararı döner (onay ve red, ikisi de HTTP 200). Onaylanan işlem kullanıma ve statement'a yazılır |
| GET | `/statements/{customer_id}?from=&to=` | Onaylanmış işlemler, toplam ve aralık bilgisi |
| GET | `/health` | Sağlık kontrolü (ek, spesifikasyonda yok) |

## 5. PRD §4 iş kuralları ve karşılıkları

| # | Kural | Planlanan uygulama |
|---|---|---|
| 1 | Varsayılan limitler 10000.00 / 5000.00 | `DEFAULT_LIMITS` sabiti. Store'da kayıt yoksa bu kullanılır, `source=default` |
| 2 | İki limit de > 0 ve `per_transfer <= daily` | `set_limits` içinde kontrol edilir, ihlal olursa 422 |
| 3 | Limitler dahildir | Karşılaştırmalar `<=` ile yapılır (aşım için `>`) |
| 4 | Onay için iki koşul birlikte sağlanmalı | `amount <= per_transfer` **ve** `kullanım + amount <= daily` |
| 5 | İki ihlal birden varsa `PER_TRANSFER_LIMIT_EXCEEDED` öncelikli | Önce işlem başına limit kontrol edilir, sonra günlük limit |
| 6 | Reddedilen işlem hiçbir yere yazılmaz | Yazma yalnızca karar onay olduğunda yapılır |
| 7 | Kullanım günler arasında bağımsız | Kullanım anahtarı `(customer_id, occurred_on)` |
| 8 | Limit değişikliği kullanımı silmez | `set_limits` yalnızca limit kaydını değiştirir, `usage`'a dokunmaz |
| 9 | Statement uçları dahil, tarihe göre artan, aynı günde onay sırasına göre | `from <= gün <= to` filtresi, ardından kararlı (stable) sıralama |
| 10 | `from > to` geçersiz, işlemi olmayan müşteri için boş liste | `from > to` 422 döner. İşlem yoksa `entries: []`, `total: "0.00"` |

**Eşzamanlılık:** Yetkilendirmede okuma, kontrol ve yazma tek bir kilit altında yapılır. Böylece eşzamanlı iki istek birlikte günlük limiti aşamaz (el kitabındaki atomiklik kuralı).

## 6. Biçim ve doğrulama (PRD §5)

- **Para:** `decimal.Decimal`, `float` hiç kullanılmaz. Girdi `^[0-9]+(\.[0-9]{1,2})?$` desenine uyan bir **string** olmalı ve değeri > 0 olmalı. JSON'da sayı olarak gelen tutar 422 döner. Yanıtta tutar `quantize(0.01, ROUND_HALF_UP)` ile her zaman 2 ondalıklı yazılır.
- **Tarih:** Katı `YYYY-MM-DD` deseni ve `date.fromisoformat` birlikte kullanılır. `20250314` ve `2025-02-30` reddedilir.
- **customer_id:** `^C[0-9]{6}$` deseni. Bu doğrulama yalnızca HTTP katmanında yapılır.
- **Hata zarfı:** Hatalar `{"error": {"code", "message"}}` biçiminde döner. Bunun için şu handler'lar tanımlanır:
  - `RequestValidationError` (eksik alan, tip hatası, bozuk JSON) → 422 `VALIDATION_ERROR`
  - Servisteki iş doğrulama hataları → 422 `VALIDATION_ERROR`
  - Starlette `HTTPException` (bilinmeyen route) → 404 `NOT_FOUND`, 405 `METHOD_NOT_ALLOWED`
  - Beklenmeyen hata → 500 `INTERNAL_ERROR` (sabit mesaj, ayrıntı sunucu tarafında loglanır)
- **Statement'taki `from`:** Python'da ayrılmış sözcük olduğu için `Query(alias="from")` ile alınır. Yanıtta da JSON anahtarı `from` olarak yazılır.
- **Red bir hata değildir:** HTTP 200, `allowed: false` ve sebep kodu döner.

## 7. Test planı

- `TestClient` ile API seviyesinde testler. `autouse` fixture her testten önce `store.reset()` çağırır.
- Test adları `test_<davranış>_<koşul>` biçiminde olur. Her özellik için en az bir mutlu yol, bir negatif durum ve bir sınır değeri testi yazılır.
- PRD §7'deki örnek senaryo (5 adım) birebir test edilir.
- Sınır değerleri: limite tam eşit tutar, limiti 1 kuruş aşan tutar, `per_transfer == daily`, tek günlük statement aralığı.
- Hedef kapsam %85 ya da üzeri (`services/limits`).

## 8. Doğrulama

1. `pytest tests/test_limits.py --cov=services/limits`
2. `python3 verify/run.py m1`: 35/35 kontrolün tamamı PASS olmalı.
3. `semgrep --config security/semgrep-rules.yml services/limits`: bulgu olmamalı.

## 9. Kararlar (2026-11-24)

| Soru | Karar |
|---|---|
| Test kapsamı hedefi | `services/limits` için en az **%85** |
| `customer_id` doğrulaması | **Yalnızca HTTP katmanında** (`main.py`). Servis katmanı gelen id'nin geçerli olduğunu varsayar |
| JSON'daki `from` alanı | **Alias** ile karşılanır: `Query(alias="from")` (varsayılan, ayrıca sorulmadı) |
| Limit kullanılmış tutarın altına düşerse `remaining_daily` | **`"0.00"`**, negatif değer dönmez (API-SPEC'teki Money deseni de negatife izin vermiyor) |
| Daha önce yazılan kod | Silindi. Plan onaylandıktan sonra sıfırdan yazılacak |
