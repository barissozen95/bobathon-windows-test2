# Aurora Bank - Mühendislik El Kitabı (Payments Takımı)

**Sürüm:** 3.1 | Bu doküman `aurora-pay` reposundaki **her** değişiklik için bağlayıcıdır. PR incelemesinde ilk bakılan şey budur.

## 1. Para

1. Para tutarları kod içinde **`decimal.Decimal`** ile tutulur. `float` ile para hesabı yapılmaz.
2. Yuvarlama **`ROUND_HALF_UP`**, 2 ondalık (kuruş).
3. API'de tutar kabul ederken `Decimal`'e çevrilir. Yanıtlarda tutarlar ya JSON sayısı ya da string olabilir, ancak değer kuruş hassasiyetinde **tam** olmalıdır (`99.00`, `99.00000000000006` değil).
4. Ücret kuralları için tek kaynak: [`FEE-POLICY.md`](FEE-POLICY.md).

## 2. Hata yönetimi

Tüm hatalar tek bir **hata zarfı** ile döner. Çıplak `HTTPException` gövdesi (`{"detail": ...}`), stack trace veya iç hata mesajı istemciye **asla** gönderilmez.

```json
{"error": {"code": "ACCOUNT_NOT_FOUND", "message": "Hesap bulunamadı: ACC-9999"}}
```

| Durum | HTTP | `code` |
|---|---|---|
| Geçersiz girdi (eksik alan, tutar <= 0, negatif bakiye, tip hatası) | 422 | `VALIDATION_ERROR` |
| Gönderen ve alıcı aynı hesap | 422 | `VALIDATION_ERROR` |
| Hesap yok | 404 | `ACCOUNT_NOT_FOUND` |
| Hesap zaten var (aynı `id` ile ikinci kayıt) | 409 | `ACCOUNT_ALREADY_EXISTS` |
| Transfer yok | 404 | `TRANSFER_NOT_FOUND` |
| Yetersiz bakiye | 409 | `INSUFFICIENT_FUNDS` |
| Beklenmeyen hata | 500 | `INTERNAL_ERROR` (mesaj sabit: "Beklenmeyen bir hata oluştu") |

Ek kurallar:

- Para hareketi **atomiktir**: bir adım başarısız olursa hiçbir bakiye değişmemiş olmalıdır. Önce doğrula, sonra yaz.
- Para hareketi yapan endpoint `Idempotency-Key` başlığını destekler. Aynı anahtarla gelen ikinci istek **yeni işlem oluşturmaz**, ilk yanıtı döner.
- Beklenmeyen hatalar loglanır (sunucu tarafında, ayrıntılı), istemciye `INTERNAL_ERROR` döner.

## 3. Loglama

- **Kişisel veri (PII) loglanmaz:** ad-soyad, IBAN, TCKN, telefon, e-posta, kart no.
- Log satırlarında yalnızca teknik kimlikler kullanılır: `account_id`, `transfer_id`.
- Log mesajları `logging` modülü ile yazılır, `print` kullanılmaz.

## 4. Test standardı

- Testler **API seviyesinde** yazılır: `fastapi.testclient.TestClient` ile endpoint'ler üzerinden. İç fonksiyonlara bağımlı test yazılmaz.
- Her test dosyasında store her testten önce sıfırlanır:

```python
@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()
```

- İsimlendirme: `test_<davranış>_<koşul>`. Arrange / Act / Assert bölümleri ayrılır.
- **Her** özellik için en az bir mutlu yol, bir negatif durum ve bir **sınır değeri** testi zorunludur.
- Kapsam eşiği: `services/core` için **%85 satır kapsamı**.

## 5. Güvenlik

- Gizli bilgiler (API anahtarı, parola, JWT sırrı) kodda veya repoda **bulunmaz**; ortam değişkeninden okunur.
- SQL her zaman **parametreli** sorgu ile çalışır; kullanıcı girdisi SQL'e birleştirilmez.
- Kullanıcı girdisiyle kabuk (shell) komutu çalıştırılmaz. Dosya adları doğrulanır, yol gezintisine (`..`) izin verilmez.
- Docker imajları root olmayan kullanıcı ile çalışır; `ADD <url>` kullanılmaz; imaja gizli bilgi gömülmez.
- Altyapı kodunda dışa açık (`0.0.0.0/0`) kural, herkese açık bucket ve şifresiz depolama yoktur.
- Bağımlılıklar bilinen zafiyetli sürümlerde tutulmaz.

## 6. Teslimat

- Dal adı: `feature/<kısa-açıklama>` veya `fix/<kısa-açıklama>`.
- Commit mesajı: ne yaptığını anlatan tek cümle, İngilizce.
- PR `gh pr create` ile açılır ve [`PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) doldurulur.
- CI (`.github/workflows/ci.yml`) yeşil olmadan merge edilmez.
