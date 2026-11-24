# aurora-pay - Mimari

Her servis aynı dört katmanla yazılır. Bağımlılık yönü **yalnızca içe doğrudur**:

```
api  ──►  application  ──►  domain
              │
              └──►  infrastructure  ──►  domain
```

| Katman | Sorumluluk | Bilmediği şeyler |
|---|---|---|
| `domain/` | İş kuralları, varlıklar, domain hataları (ücret politikası, limit kuralları) | FastAPI, HTTP, depolama |
| `application/` | Use-case'ler: doğrula, sonra yaz; kilit, idempotency, atomiklik | HTTP şemaları, yanıt biçimi |
| `infrastructure/` | Depolama ve dış kaynaklar: in-memory store, SQLite transfer log, arşiv | HTTP |
| `api/` | FastAPI app (`create_app`), router'lar, istek şemaları, girdi ayrıştırma | İş kuralı |

Ortak yapı taşları `services/shared/` altındadır:

- `shared/errors.py`: `AppError` tabanı, handbook **hata zarfı** ve `install_error_handlers(app, logger)`. Her servis aynı zarfı kullanır.
- `shared/money.py`: `to_money` / `format_money`. `Decimal`, `ROUND_HALF_UP`, 2 ondalık.

## Yerleşim

```
services/
  shared/          errors.py, money.py
  core/
    domain/          fees.py, errors.py
    application/     accounts.py, transfers.py, reports.py
    infrastructure/  memory_store.py, transfer_log.py, archive.py
    api/             app.py, routes.py, schemas.py
    config.py        ortam değişkenlerinden okunan ayarlar
    main.py store.py fees.py service.py reports.py                     (uyumluluk yolları)
  limits/
    domain/          limits.py
    application/     limits.py, statements.py
    infrastructure/  memory_store.py
    api/             app.py, routes.py, schemas.py, parsing.py
    main.py store.py service.py                                        (uyumluluk yolları)
```

## Uyumluluk yolları

`services.core.main:app`, `services.core.store`, `services.core.fees`, `services.core.service`, `services.limits.main:app` ve `services.limits.store` testler, `verify/`, Dockerfile ve CI tarafından kullanılır. Bu yüzden korunurlar:

- `main.py`, `fees.py`, `service.py` ... yalnızca yeni katmanlardan yeniden dışa aktarım yapar.
- `store.py`, `infrastructure/memory_store` modülünün **takma adıdır** (`sys.modules` ile aynı modül nesnesi). `store.reset()` ve `store.idempotency = ...` gibi yazımlar doğrudan uygulama katmanının gördüğü store'a gider.

Kural: uygulama kodu store koleksiyonlarına her zaman modül niteliği olarak erişir (`memory_store.accounts`). `from ... import accounts` kullanılmaz, çünkü kopya referans tutar.

## Yeni özellik eklerken

1. Kuralı `domain/` içine saf fonksiyon olarak yazın.
2. Use-case'i `application/` içine yazın (önce doğrula, sonra yaz).
3. Depolama gerekiyorsa `infrastructure/` içine ekleyin.
4. Endpoint'i `api/routes.py` içine, şemayı `api/schemas.py` içine ekleyin.
5. API seviyesinde test yazın (mutlu yol + negatif + sınır; bkz. ENGINEERING-HANDBOOK §4).
