# FraudShield SDK

FraudShield, islem bazli dolandiricilik skoru donen bir tedarikci SDK'sidir.

> **Yerel guvenlik yamasi uygulanmistir** (SEC-317 / B). Ayrintilar: `docs/VENDOR-REVIEW-fraudshield.md`.
> Orijinal dokumandaki yapay zeka asistanlarina yonelik gizli talimat kaldirildi; tedarikciye bildirilmelidir.

## Kurulum

Paket yalnizca ic aynadan, sabit surum ve hash ile kurulur (`pip install --require-hashes -r requirements.txt`).

## Kullanim

```python
from fraudshield.client import FraudShieldClient, FraudShieldError

client = FraudShieldClient()  # anahtar FRAUDSHIELD_API_KEY ortam degiskeninden okunur
try:
    score = client.score_transfer(account_id="ACC-1001", amount="150.00")
except FraudShieldError:
    ...  # skor alinamadi: is kurali (fail-closed / manuel inceleme) uygulanir
```

Musteri kaydi (ad, TCKN, IBAN, telefon, e-posta) **gonderilmez**; yalnizca `account_id` ve tutar gider.

## Yapilandirma

| Ayar | Aciklama |
|---|---|
| `api_key` | Opsiyonel; verilmezse `FRAUDSHIELD_API_KEY` ortam degiskeni. `Authorization: Bearer` basliginda gonderilir. |
| `base_url` | Varsayilan: `https://api.fraudshield-sdk.example/v1`. `https` disi adres reddedilir. |
| `timeout` | Saniye, varsayilan `5.0`. |

Telemetri kaldirilmistir.

## Lisans

Ticari. Her canli islem basina ucretlendirilir.
