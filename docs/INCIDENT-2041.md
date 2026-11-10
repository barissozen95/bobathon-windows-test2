# INCIDENT-2041 - Çift borçlandırma ve kayıp para

**Önem:** SEV-2 | **Durum:** Açık | **Atanan:** Siz | **Servis:** `services/core` (Aurora Core)

## Özet

Bu sabah Müşteri Deneyimi ve Mutabakat ekipleri aynı anda dört şikâyet iletti. Hepsi `POST /transfers` ile ilgili.

## Şikâyetler

| # | Bildiren | Gözlem |
|---|---|---|
| 1 | Müşteri Deneyimi | Mobil uygulama, ağ geçidi zaman aşımına uğrayınca isteği **aynı `Idempotency-Key` ile** yeniden gönderiyor. Müşteriler tutarın **iki kez** düşüldüğünü söylüyor. |
| 2 | Müşteri Deneyimi | Yanlış IBAN/hesap yazan müşterilerin hesabından para düşüyor ama alıcıya geçmiyor. Ekranda "Internal Server Error" görünüyor. |
| 3 | Mutabakat | Günlük mutabakatta bakiyeler kuruş altı farklarla tutmuyor (`99.00000000000006`). Ayrıca bazı ücretler politika dokümanından **1 kuruş** düşük hesaplanıyor. |
| 4 | Mobil ekip | Yetersiz bakiye, negatif tutar ve bilinmeyen hesap durumlarında istemci düzgün bir hata alamıyor, sunucu 500 dönüyor. |

## Ek bilgi

- Örnek sunucu logu: [`fixtures/incident/transfer.log`](../fixtures/incident/transfer.log)
- Sorunu yerelde yeniden üretmek için: `python fixtures/incident/repro.py` (düzelince `0` ile çıkar, bozukken `1`)
- Para kuralları: [`FEE-POLICY.md`](FEE-POLICY.md)

## Beklenen sonuç

Dört şikâyetin kök nedenini bulun, düzeltin ve düzelttiğinizi gösterin. Yeni bir hata sınıfı (ör. başka bir bozuk istek) çıkarsa
sunucu 500 dönmemeli, istemci anlaşılır bir hata almalıdır.

> Not: Bu iş için acele var ama **yeni bir regresyon istemiyoruz**.
