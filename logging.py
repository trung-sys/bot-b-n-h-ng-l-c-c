from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from app.config.settings import AppSettings
from app.domain.models import DepositResult
from app.payments.bank_client import BankApiError, CoderentBankClient
from app.services.deposit_service import DepositService


class BankPoller:
    def __init__(
        self,
        settings: AppSettings,
        client: CoderentBankClient,
        deposit_service: DepositService,
        on_credit: Callable[[DepositResult], None] | None = None,
    ) -> None:
        self.settings = settings
        self.client = client
        self.deposit_service = deposit_service
        self.on_credit = on_credit
        self.logger = logging.getLogger("telegram_shop_pro.payments.bank_poller")
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="bank-poller", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)
        self._thread = None

    def _run(self) -> None:
        self.logger.info("Bank poller started.")
        while not self._stop_event.is_set():
            try:
                self.poll_once()
            except Exception:
                self.logger.exception("Bank poll loop crashed.")
            self._stop_event.wait(max(5, int(self.settings.poll_interval_seconds)))
        self.logger.info("Bank poller stopped.")

    def poll_once(self) -> None:
        expired_count = self.deposit_service.cleanup_expired_pending()
        if expired_count:
            self.logger.info("Expired %s pending deposits.", expired_count)

        transactions = self.client.fetch_transactions(
            bank_name=self.settings.bank_api_name,
            token=self.settings.bank_api_token,
            base_url=self.settings.bank_api_base_url,
        )
        self.logger.info("Fetched %s bank transactions.", len(transactions))

        for transaction in transactions:
            try:
                result = self.deposit_service.credit_from_bank_transaction(transaction)
            except Exception:
                self.logger.exception(
                    "Failed to process bank transaction %s.",
                    transaction.transaction_id or "<missing-id>",
                )
                continue

            if result.success and not result.already_processed:
                self.logger.info(
                    "Deposit credited from bank transaction %s for user %s amount %s.",
                    result.transaction_id,
                    result.user_id,
                    result.amount,
                )
                if self.on_credit:
                    self.on_credit(result)
            elif result.message and result.already_processed and result.user_id:
                self.logger.info(
                    "Bank transaction %s skipped: %s",
                    result.transaction_id,
                    result.message,
                )

