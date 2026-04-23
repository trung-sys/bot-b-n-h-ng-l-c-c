from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class CouponDecision:
    requested_code: str | None
    applied_code: str | None
    discount: int
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PurchaseResult:
    order_id: int
    user_id: int
    product_id: int
    product_name: str
    price: int
    discount: int
    final_price: int
    deliver_text: str
    applied_coupon: str | None
    balance_after: int
    referrer_id: int | None = None
    affiliate_earnings: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PendingDepositResult:
    pending_id: int
    user_id: int
    amount: int
    qr_url: str
    add_info: str
    expires_at: str


@dataclass(slots=True)
class DepositResult:
    success: bool
    user_id: int
    amount: int
    transaction_id: str
    description: str
    status: str
    source: str
    deposit_id: int | None = None
    pending_id: int | None = None
    already_processed: bool = False
    message: str = ""


@dataclass(slots=True)
class ReferralSummary:
    user_id: int
    percent: int
    referral_link: str
    total_earnings: int


@dataclass(slots=True)
class DashboardSummary:
    total_users: int = 0
    total_orders: int = 0
    total_revenue: int = 0
    total_deposits: int = 0
    total_commission: int = 0
    active_categories: int = 0
    active_products: int = 0
    pending_deposits: int = 0
    approved_deposits: int = 0


@dataclass(slots=True)
class ExportResult:
    path: Path
    row_count: int


@dataclass(slots=True)
class BankTransaction:
    transaction_id: str
    amount: int
    description: str
    tx_type: str
    raw_payload: dict[str, object]

