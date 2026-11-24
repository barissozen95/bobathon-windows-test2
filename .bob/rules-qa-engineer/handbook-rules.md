# Aurora Pay - Bağlayıcı kurallar (özet)

Tek kaynak: `docs/ENGINEERING-HANDBOOK.md`. Bu dosya onun özetidir; çelişki olursa el kitabı geçerlidir.
Test yazarken bu kurallar **doğrulanacak davranıştır**: testler bu kuralları ihlal eden kodu yakalamalıdır.

## Para
- Tutarlar `decimal.Decimal` ile tutulur. **`float` ile para hesabı yasaktır** (testlerde de beklenen değerleri `Decimal("99.00")` gibi yaz).
- Yuvarlama `ROUND_HALF_UP`, 2 ondalık. Yanıttaki tutar kuruş hassasiyetinde tam olmalı (`99.00`, `99.00000000000006` değil).
- Ücret kuralları: `docs/FEE-POLICY.md`.

## Hata zarfı (error envelope)
- Tüm hatalar: `{"error": {"code": "<CODE>", "message": "<mesaj>"}}`. Çıplak `{"detail": ...}`, stack trace, iç mesaj asla dönmez.
- 422 `VALIDATION_ERROR` (eksik alan, tutar <= 0, tip hatası, aynı hesaba transfer)
- 404 `ACCOUNT_NOT_FOUND`, 404 `TRANSFER_NOT_FOUND`
- 409 `ACCOUNT_ALREADY_EXISTS`, 409 `INSUFFICIENT_FUNDS`
- 500 `INTERNAL_ERROR`, mesaj sabit: "Beklenmeyen bir hata oluştu"
- Para hareketi atomiktir: hata sonrası hiçbir bakiye değişmemiş olmalı.
- `Idempotency-Key` ile gelen ikinci istek yeni işlem oluşturmaz, ilk yanıtı döner.

## Loglama
- Kişisel veri (PII) loglanmaz: ad-soyad, IBAN, TCKN, telefon, e-posta, kart no.
- Log'da yalnız teknik kimlik: `account_id`, `transfer_id`. `print` değil `logging`.
- Testte `caplog` ile log satırlarında PII olmadığını doğrula.

## Güvenlik
- Gizli bilgi (secret, API anahtarı, parola/password, JWT sırrı) kodda/repoda bulunmaz; ortam değişkeninden okunur. Testlerde gerçek secret kullanma, `monkeypatch.setenv` kullan.
- SQL her zaman parametreli (parameterized) sorgu ile çalışır; kullanıcı girdisi SQL'e birleştirilmez.
- Kullanıcı girdisiyle shell komutu çalıştırılmaz; `..` yol gezintisi reddedilir.

## QA modunun sınırı
- Yalnızca `tests/` altındaki dosyalar düzenlenir. Üretim kodunda hata bulursan düzeltme: başarısız testi yaz, raporla.
