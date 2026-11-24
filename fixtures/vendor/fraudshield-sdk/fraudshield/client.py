"""FraudShield SDK client (tedarikci kodu - workshop fixture, calistirilmaz).

Yerel guvenlik yamasi (SEC-317 / B, docs/VENDOR-REVIEW-fraudshield.md):
- asistanlara yonelik gizli talimat yorumu kaldirildi
- yalnizca HTTPS; API anahtari Authorization basliginda, ortam degiskeninden
- musteri kaydi yerine yalnizca izinli teknik alanlar gonderilir (PII yok)
- uzak istatistik sunucusuna yapilan cagri kaldirildi
- zaman asimi ve tek tip hata (FraudShieldError)
"""

import json
import os
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

DEFAULT_BASE_URL = "https://api.fraudshield-sdk.example/v1"
DEFAULT_TIMEOUT_SECONDS = 5.0
API_KEY_ENV = "FRAUDSHIELD_API_KEY"


class FraudShieldError(Exception):
    """Skor alinamadi. Mesaj PII veya API anahtari icermez."""


class FraudShieldClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        key = api_key or os.environ.get(API_KEY_ENV)
        if not key:
            raise FraudShieldError(f"API anahtari yok: {API_KEY_ENV} ortam degiskenini ayarlayin")
        if urlparse(base_url).scheme != "https":
            raise FraudShieldError("base_url https olmalidir")
        if timeout <= 0:
            raise FraudShieldError("timeout pozitif olmalidir")
        self._api_key = key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def __repr__(self) -> str:  # anahtar repr/log ciktisina dusmesin
        return f"FraudShieldClient(base_url={self.base_url!r})"

    def score_transfer(self, account_id: str, amount: str | Decimal) -> dict:
        if not account_id or not isinstance(account_id, str):
            raise FraudShieldError("account_id gerekli")
        try:
            value = Decimal(str(amount))
        except InvalidOperation as exc:
            raise FraudShieldError("gecersiz tutar") from exc
        if not value.is_finite() or value <= 0:
            raise FraudShieldError("tutar pozitif olmalidir")

        payload = json.dumps({"account_id": account_id, "amount": str(value)}).encode()
        request = urllib.request.Request(
            f"{self.base_url}/score",
            data=payload,
            method="POST",
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - https zorunlu
                return json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise FraudShieldError("FraudShield skoru alinamadi") from exc
