# PRD - Aurora Limits & Statements Servisi

**Ürün sahibi:** Instant Pay ekibi | **Durum:** Onaylandı | **Hedef:** İlk canlı sürüm (v1)

## 1. Neden?

Aurora Instant Pay canlıya çıkarken regülatör ve risk ekibi iki şeyi zorunlu tuttu:

1. Her müşteri için **günlük** ve **işlem başına** transfer limiti uygulanmalı.
2. Müşteri, belirli bir tarih aralığında **onaylanmış** işlemlerinin dökümünü (statement) alabilmeli.

Bu iki ihtiyaç `aurora-pay-core`'dan bağımsız, küçük bir servis olarak yazılacak: **Limits & Statements**.
Henüz hiç kod yoktur. Bu doküman ve `API-SPEC-limits.yaml` tek kaynaktır.

## 2. Kapsam

- İçeride: limit tanımlama/sorgulama, işlem yetkilendirme (limit kontrolü + kullanım kaydı), statement.
- Dışarıda: kimlik doğrulama, kalıcı veritabanı, para birimi dönüşümü. v1 **tek para birimi (TRY)** ve **bellek içi (in-memory)** depolama kullanır.

## 3. Kavramlar

| Terim | Anlam |
|---|---|
| `customer_id` | `C` + 6 rakam. Örn. `C004217`. Başka biçim geçersizdir. |
| `daily_limit` | Bir takvim günü (`occurred_on`) içinde onaylanabilecek toplam tutar. |
| `per_transfer_limit` | Tek bir işlemde onaylanabilecek en yüksek tutar. |
| Kullanım | Bir günde **onaylanmış** işlemlerin toplamı. Reddedilen işlemler kullanıma yazılmaz. |

## 4. İş kuralları

1. Müşteri için limit tanımlanmamışsa **varsayılan** değerler geçerlidir: `daily_limit = 10000.00`, `per_transfer_limit = 5000.00`.
2. Limit tanımlarken `per_transfer_limit` en fazla `daily_limit` kadar olabilir. Her iki değer de sıfırdan büyük olmalıdır.
3. Limitler **dahildir**: tutar tam olarak limite eşitse işlem onaylanır.
4. Bir işlem şu iki koşulu da sağlıyorsa onaylanır:
   - `amount <= per_transfer_limit`
   - `o günün kullanımı + amount <= daily_limit`
5. Reddedilirse sebep kodu döner. İki koşul da ihlal edilmişse **`PER_TRANSFER_LIMIT_EXCEEDED`** öncelikli sebeptir. Diğeri `DAILY_LIMIT_EXCEEDED`.
6. Onaylanan işlem kullanıma eklenir ve statement'a yazılır. Reddedilen işlem **hiçbir yere** yazılmaz.
7. Kullanım günler arasında bağımsızdır: 14 Mart'taki kullanım, 15 Mart'ın limitini etkilemez.
8. Limit değişikliği geçmiş kullanımı silmez ve sıfırlamaz.
9. Statement; `from` ve `to` tarihlerini **dahil** eder, kayıtlar `occurred_on`'a göre artan sırada, aynı günde ise onay sırasına göredir.
10. `from > to` geçersizdir. Hiç işlemi olmayan müşteri için statement boş döner (hata değil).

## 5. Biçim kuralları

- Para tutarları API'de **string** olarak taşınır ve yanıtta **her zaman tam 2 ondalıkla** döner (`"1500.00"`). Hesaplamada `float` kullanılmaz.
- Tarihler `YYYY-MM-DD` biçimindedir.
- Tüm hatalar tek bir **hata zarfı** ile döner:

```json
{"error": {"code": "VALIDATION_ERROR", "message": "okunabilir açıklama"}}
```

  Geçersiz girdi her zaman **HTTP 422** ve `VALIDATION_ERROR` kodudur (FastAPI'nin varsayılan `{"detail": ...}` biçimi **kullanılmaz**).
- İş kuralı sonucu olan "reddedildi" durumu hata değildir: HTTP 200 ve `allowed: false` döner.

## 6. Kabul kriterleri

- `API-SPEC-limits.yaml`'daki tüm uç noktalar çalışır.
- Yukarıdaki iş kuralları örnek senaryolarla doğrulanabilir.
- Servis `services/limits/main.py` içinde, `app` adlı bir FastAPI uygulaması olarak sunulur.

## 7. Örnek senaryo

Müşteri `C004217`: `daily_limit = 5000.00`, `per_transfer_limit = 2000.00`.

| Sıra | Tarih | Tutar | Sonuç | Kalan günlük |
|---|---|---|---|---|
| 1 | 2025-03-14 | 1500.00 | onay | 3500.00 |
| 2 | 2025-03-14 | 2500.00 | red `PER_TRANSFER_LIMIT_EXCEEDED` | 3500.00 |
| 3 | 2025-03-14 | 2000.00 | onay | 1500.00 |
| 4 | 2025-03-14 | 1600.00 | red `DAILY_LIMIT_EXCEEDED` | 1500.00 |
| 5 | 2025-03-15 | 1600.00 | onay | 3400.00 |
