---
name: api-test-writing
description: Use when writing, extending or reviewing tests for aurora-pay endpoints, or when turning a bug report into a failing test. Encodes the handbook test standard (TestClient, store.reset, happy/negative/boundary).
---
# API test yazma prosedürü (Aurora Pay)

Kaynak: `docs/ENGINEERING-HANDBOOK.md` bölüm 4. Yalnızca `tests/` altına yaz.

## 1. Davranışı çıkar
- İlgili PRD / API spec / incident dokümanını ve endpoint'i oku (`docs/`, `services/*/main.py`).
- Her özellik için bir tablo çıkar: **mutlu yol (happy path)**, **negatif durum** (hata zarfı + HTTP kodu), **sınır değeri (boundary)** (ör. tam eşik `1000.00`, `0`, `0.01`, limitin bir kuruş üstü).

## 2. Dosya iskeleti
```python
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from services.core import store
from services.core.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()
```
- Testler **API seviyesinde**: yalnız `TestClient` ile endpoint çağır; iç fonksiyonlara bağlı test yazma.
- Store her testten önce `store.reset()` ile sıfırlanır (autouse fixture zorunlu).

## 3. Her test
- İsim: `test_<davranış>_<koşul>` (ör. `test_transfer_rejects_amount_zero`).
- Arrange / Act / Assert bölümlerini yorumla ayır.
- Tutarları `Decimal(str(value))` ile karşılaştır; `float` eşitliği kullanma.
- Negatif testlerde tam zarfı doğrula: `status_code` + `body["error"]["code"]`, ve `"detail"` anahtarının **olmadığını**.
- Para hareketi hatalarında bakiyelerin değişmediğini (atomiklik) ayrıca doğrula.
- Idempotency: aynı `Idempotency-Key` ile ikinci istek aynı yanıtı döner, yeni işlem oluşmaz.
- Loglarda PII yok: `caplog` ile ad/IBAN/e-posta geçmediğini kontrol et.

## 4. Çalıştır ve ölç
```bash
python3 -m pytest -q
python3 -m pytest -q --cov=services/core --cov-report=term-missing   # eşik: %85 satır
```

## 5. Raporla
- Kapsanan davranışlar (mutlu / negatif / sınır) listesi ve kapsam yüzdesi.
- Başarısız test = muhtemel üretim hatası: dosya, satır, beklenen vs gerçek. Üretim kodunu **düzeltme**.
