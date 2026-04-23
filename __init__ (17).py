from __future__ import annotations

import logging
from typing import Any

import requests

from app.domain.models import BankTransaction
from app.payments.vietqr import build_coderent_history_url
from app.utils.validation import parse_int


class BankApiError(RuntimeError):
    """Raised when the bank API cannot be consumed safely."""


class CoderentBankClient:
    def __init__(self, session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()
        self.logger = logging.getLogger("telegram_shop_pro.payments.bank_client")

    def fetch_transactions(self, bank_name: str, token: str, base_url: str) -> list[BankTransaction]:
        url = build_coderent_history_url(bank_name, token, base_url)
        try:
            response = self.session.get(url, timeout=25)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise BankApiError(f"Không gọi được bank API: {exc}") from exc
        except ValueError as exc:
            raise BankApiError("Bank API trả về JSON không hợp lệ.") from exc

        items = self._extract_transactions(payload)
        transactions: list[BankTransaction] = []
        for item in items:
            tx_id = str(item.get("transactionID") or item.get("transaction_id") or item.get("id") or "").strip()
            amount = parse_int(item.get("amount", 0), 0)
            description = str(item.get("description") or item.get("content") or "").strip()
            tx_type = str(item.get("type") or item.get("transactionType") or "").strip().upper()
            transactions.append(
                BankTransaction(
                    transaction_id=tx_id,
                    amount=amount,
                    description=description,
                    tx_type=tx_type,
                    raw_payload=item,
                )
            )
        return transactions

    def _extract_transactions(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            if isinstance(payload.get("transactions"), list):
                return [item for item in payload["transactions"] if isinstance(item, dict)]
            data = payload.get("data")
            if isinstance(data, dict):
                for key in ("transactions", "items", "history"):
                    if isinstance(data.get(key), list):
                        return [item for item in data[key] if isinstance(item, dict)]
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
        raise BankApiError("Không tìm thấy danh sách giao dịch hợp lệ trong bank API response.")

