"""DRAFT internal client for the FraudShield HTTP API (SEC-317 / B, recommendation #7).

Not wired into services/: this is a reference implementation for the fraud team to
review before any integration decision. It depends only on the standard library,
not on the vendor SDK package.

Rules enforced (docs/ENGINEERING-HANDBOOK.md, docs/VENDOR-REVIEW-fraudshield.md):
- HTTPS only; API key from the environment, sent in the Authorization header
- only technical identifiers leave the bank (account_id, transfer_id, amount); no PII
- amounts are Decimal, rounded ROUND_HALF_UP to 2 places
- explicit timeout, bounded retries on transient errors, no telemetry
- fail-closed: if no score can be obtained, the decision is REVIEW, never APPROVE
- logs contain only transfer_id / account_id, never the key or customer data
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Callable
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

API_KEY_ENV = "FRAUDSHIELD_API_KEY"
BASE_URL_ENV = "FRAUDSHIELD_BASE_URL"
DEFAULT_BASE_URL = "https://api.fraudshield-sdk.example/v1"
CENT = Decimal("0.01")
RETRYABLE_STATUS = {429, 502, 503, 504}

APPROVE, REVIEW, DECLINE = "APPROVE", "REVIEW", "DECLINE"


@dataclass(frozen=True)
class FraudDecision:
    decision: str
    risk: Decimal | None
    reason: str


class FraudScoreClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 3.0,
        max_attempts: int = 2,
        review_threshold: Decimal = Decimal("0.50"),
        decline_threshold: Decimal = Decimal("0.90"),
        opener: Callable = urllib.request.urlopen,
    ):
        key = api_key or os.environ.get(API_KEY_ENV)
        if not key:
            raise ValueError(f"{API_KEY_ENV} is not set")
        url = (base_url or os.environ.get(BASE_URL_ENV) or DEFAULT_BASE_URL).rstrip("/")
        if urlparse(url).scheme != "https":
            raise ValueError("FraudShield base URL must use https")
        if timeout <= 0 or max_attempts < 1:
            raise ValueError("timeout must be > 0 and max_attempts >= 1")
        if not Decimal("0") <= review_threshold <= decline_threshold <= Decimal("1"):
            raise ValueError("thresholds must satisfy 0 <= review <= decline <= 1")
        self._api_key = key
        self._url = f"{url}/score"
        self._timeout = timeout
        self._max_attempts = max_attempts
        self._review = review_threshold
        self._decline = decline_threshold
        self._open = opener

    def __repr__(self) -> str:
        return f"FraudScoreClient(url={self._url!r})"

    def assess(self, transfer_id: str, account_id: str, amount: str | Decimal) -> FraudDecision:
        try:
            value = Decimal(str(amount)).quantize(CENT, rounding=ROUND_HALF_UP)
        except InvalidOperation as exc:
            raise ValueError("invalid amount") from exc
        if not value.is_finite() or value <= 0:
            raise ValueError("amount must be positive")

        body = json.dumps({"transfer_id": transfer_id, "account_id": account_id, "amount": str(value)}).encode()
        risk = self._score(transfer_id, body)
        if risk is None:
            return FraudDecision(REVIEW, None, "score unavailable (fail-closed)")
        if risk >= self._decline:
            return FraudDecision(DECLINE, risk, "risk above decline threshold")
        if risk >= self._review:
            return FraudDecision(REVIEW, risk, "risk above review threshold")
        return FraudDecision(APPROVE, risk, "risk below review threshold")

    def _score(self, transfer_id: str, body: bytes) -> Decimal | None:
        for attempt in range(1, self._max_attempts + 1):
            request = urllib.request.Request(
                self._url,
                data=body,
                method="POST",
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            )
            try:
                with self._open(request, timeout=self._timeout) as response:
                    risk = Decimal(str(json.loads(response.read())["risk"]))
                if not risk.is_finite() or not Decimal("0") <= risk <= Decimal("1"):
                    raise ValueError("risk out of range")
                return risk
            except urllib.error.HTTPError as exc:
                retryable = exc.code in RETRYABLE_STATUS
                logger.warning("fraud score http error transfer_id=%s status=%s attempt=%s", transfer_id, exc.code, attempt)
            except (urllib.error.URLError, TimeoutError) as exc:
                retryable = True
                logger.warning("fraud score unreachable transfer_id=%s error=%s attempt=%s", transfer_id, type(exc).__name__, attempt)
            except (ValueError, KeyError, TypeError, InvalidOperation):
                retryable = False
                logger.warning("fraud score invalid response transfer_id=%s attempt=%s", transfer_id, attempt)
            if not retryable or attempt == self._max_attempts:
                return None
            time.sleep(0.2 * attempt)
        return None
