from __future__ import annotations

import re
import urllib.parse

from app.config.settings import CODERENT_BANK_CODES


NAPID_RE = re.compile(r"\bNapid\s+(\d+)\b", re.IGNORECASE)


def build_vietqr_image_url(
    bank_id: str,
    account_no: str,
    template: str,
    amount: int,
    add_info: str,
    account_name: str,
) -> str:
    base = f"https://img.vietqr.io/image/{bank_id}-{account_no}-{template}.png"
    query = urllib.parse.urlencode(
        {
            "amount": str(max(0, int(amount))),
            "addInfo": add_info,
            "accountName": account_name or "",
        },
        safe="",
    )
    return f"{base}?{query}"


def build_coderent_history_url(bank_name: str, token: str, base_url: str) -> str:
    bank_code = CODERENT_BANK_CODES.get(bank_name)
    if not bank_code:
        raise ValueError(f"Bank API chưa hỗ trợ: {bank_name}")
    cleaned_base = base_url.rstrip("/")
    return f"{cleaned_base}/api/{bank_code}/historyv2/{token}"

