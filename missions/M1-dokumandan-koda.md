# M1 - Dokümandan koda

**Süre:** 25 dk | **Bob özelliği:** Plan / Agent modları, `@` ile bağlam, todo listesi

> macOS/Linux'ta `python3`, Windows'ta `py` yazın.

## Durum

Regülatör, canlıya çıkmadan önce müşteri bazlı **transfer limitlerini** ve **işlem dökümünü** zorunlu kıldı.
Bu iş için henüz **tek satır kod yok**. Elinizde yalnızca ürün gereksinimi ve API sözleşmesi var:

- [`docs/PRD-limits.md`](../docs/PRD-limits.md): iş kuralları ve örnek senaryo
- [`docs/API-SPEC-limits.yaml`](../docs/API-SPEC-limits.yaml): endpointler ve şemalar

> **Bu görevde yeni bir servis yazıyorsunuz.** `services/limits`, `services/core`'dan bağımsız **yeni** bir servistir. Core'a dokunmayın, içe aktarmayın.

## Teslim edilecekler

- `services/limits/main.py` içinde `app` adlı bir FastAPI uygulaması
- `verify m1`: **35 kontrolün tamamı** PASS
- Yeni bağımlılık eklenmedi, `services/core`'a dokunulmadı

## Adım 1 - Önce anlayın (Plan modu)

PRD ve API sözleşmesini Bob'a **bağlam olarak** verin (`@docs/PRD-limits.md`), yapıştırmayın. Bob'dan bir uygulama planı isteyin ve açıkça yazın: *"Ben onaylayana kadar kod yazma."*

Planı okurken PRD bölüm 4'ü (10 madde) yanınızda açın ve her maddeyi plana karşı işaretleyin. Kapsamayan varsa kodlamadan önce Bob'a ekletin.

Bob plan modunda size soru soracaktır. Beklenen sorular ve örnek cevaplar:

| Bob'un sorusu | Örnek cevap |
|---|---|
| Test kapsamı hedefi nedir? | %85 kapsamı koruyalım. |
| `customer_id` nerede doğrulanmalı? | Yalnızca HTTP katmanında doğrulayalım. |
| `from` Python'da ayrılmış sözcük; JSON'daki `from` alanı nasıl karşılanmalı? | Alias yaklaşımını kullanalım. |

## Adım 2 - Sonra yazın (Agent modu)

Onayladığınız planı uygulatın. Todo listesini izleyin: Bob işi parçalara bölüyor mu, siz kontrol edebiliyor musunuz?

Servisi arayüzde görmek için (`services/limits/main.py` oluşunca *Limitler* sekmesi çalışır):

```bash
python3 ui/server.py
```

## Adım 3 - Doğrulama

Sonucu doğrulamak için aşağıdaki komutu kullanabilirsiniz:

```bash
python3 verify/run.py m1
```

FAIL satırının altındaki açıklama PRD'deki hangi kuralı kaçırdığınızı söyler. **Bob'un yazdığı kodun ilk seferde tüm kontrollerden geçmemesi normaldir**; hataları doğrulama çıktısıyla Bob'a geri verip düzelttirmek işin parçasıdır.

## Keşif noktaları

- Önce **anlamak** ile **yazmak** aynı mod olmak zorunda mı?
- Bob'un işi parçalara böldüğünü gösteren **todo listesi** sizin kontrol edebileceğiniz bir yer mi?

## İpucu

- **İpucu 1:** "Yaz" demeden önce planı onaylayın. PRD bölüm 4'ü plana karşı satır satır işaretleyin.
- **İpucu 2:** Çoğu FAIL şu dört yerden gelir: hata biçimi (`422` + `VALIDATION_ERROR` zarfı), reddedilen işlem hata değildir (HTTP `200`, `allowed: false`), para string gelir ve `"1500.00"` biçiminde döner (girişte `"5000"` ve `"2000.5"` de kabul edilir), sınırlar dahildir. PRD bölüm 7'deki örnek senaryoyu aynen çalıştırın.
- **Eğitmenden yardım:** İpucu 2 yetmediyse eğitmeni çağırın.
