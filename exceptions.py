from __future__ import annotations

import sqlite3

from app.db.repositories.base import BaseRepository
from app.utils.time import timestamp


class OrdersRepository(BaseRepository):
    def create_order(
        self,
        user_id: int,
        product_id: int,
        price: int,
        discount: int,
        final_price: int,
        coupon_code: str | None,
        status: str,
        deliver_text_snapshot: str,
        con: sqlite3.Connection | None = None,
    ) -> int:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute(
                """
                INSERT INTO orders(user_id, product_id, price, discount, final_price, coupon_code, status, created_at, deliver_text_snapshot)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, product_id, price, discount, final_price, coupon_code, status, timestamp(), deliver_text_snapshot),
            )
            return int(cursor.lastrowid)

    def list_orders(self, user_id: int, limit: int, con: sqlite3.Connection | None = None) -> list[sqlite3.Row]:
        with self.connection(con) as connection:
            return connection.execute(
                """
                SELECT o.id, o.final_price, o.discount, o.status, o.created_at, o.coupon_code, p.name AS product_name
                FROM orders o
                LEFT JOIN products p ON p.id=o.product_id
                WHERE o.user_id=?
                ORDER BY o.id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()


class DepositsRepository(BaseRepository):
    def create_deposit(
        self,
        user_id: int,
        amount: int,
        description: str,
        transaction_id: str,
        status: str,
        source: str,
        pending_id: int | None = None,
        con: sqlite3.Connection | None = None,
    ) -> int:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute(
                """
                INSERT INTO deposits(user_id, amount, description, trans_id, status, created_at, source, pending_id)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, amount, description, transaction_id, status, timestamp(), source, pending_id),
            )
            return int(cursor.lastrowid)

    def get_deposit_by_transaction_id(self, transaction_id: str, con: sqlite3.Connection | None = None) -> sqlite3.Row | None:
        with self.connection(con) as connection:
            return connection.execute("SELECT * FROM deposits WHERE trans_id=?", (transaction_id,)).fetchone()

    def insert_bank_seen_if_new(self, transaction_id: str, con: sqlite3.Connection | None = None) -> bool:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO bank_seen(transaction_id, seen_at) VALUES(?, ?)",
                (transaction_id, timestamp()),
            )
            return cursor.rowcount > 0

    def create_pending_deposit(
        self,
        user_id: int,
        amount: int,
        qr_url: str,
        add_info: str,
        created_at: str,
        expires_at: str,
        con: sqlite3.Connection | None = None,
    ) -> int:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute(
                """
                INSERT INTO pending_deposits(user_id, amount, qr_url, add_info, status, created_at, expires_at)
                VALUES(?, ?, ?, ?, 'PENDING', ?, ?)
                """,
                (user_id, amount, qr_url, add_info, created_at, expires_at),
            )
            return int(cursor.lastrowid)

    def get_pending_deposit(self, pending_id: int, con: sqlite3.Connection | None = None) -> sqlite3.Row | None:
        with self.connection(con) as connection:
            return connection.execute(
                "SELECT * FROM pending_deposits WHERE id=?",
                (pending_id,),
            ).fetchone()

    def find_latest_pending_for_credit(
        self,
        user_id: int,
        amount: int,
        add_info: str,
        con: sqlite3.Connection | None = None,
    ) -> sqlite3.Row | None:
        with self.connection(con) as connection:
            return connection.execute(
                """
                SELECT *
                FROM pending_deposits
                WHERE user_id=? AND amount=? AND add_info=? AND status IN ('PENDING', 'EXPIRED', 'APPROVED_MANUAL')
                ORDER BY
                    CASE status
                        WHEN 'PENDING' THEN 0
                        WHEN 'APPROVED_MANUAL' THEN 1
                        WHEN 'EXPIRED' THEN 2
                        ELSE 3
                    END,
                    id DESC
                LIMIT 1
                """,
                (user_id, amount, add_info),
            ).fetchone()

    def update_pending_status(
        self,
        pending_id: int,
        status: str,
        matched_transaction_id: str | None = None,
        resolution_note: str = "",
        con: sqlite3.Connection | None = None,
    ) -> None:
        with self.connection(con, write=True) as connection:
            connection.execute(
                """
                UPDATE pending_deposits
                SET status=?,
                    matched_transaction_id=COALESCE(?, matched_transaction_id),
                    resolved_at=?,
                    resolution_note=?
                WHERE id=?
                """,
                (status, matched_transaction_id, timestamp(), resolution_note, pending_id),
            )

    def expire_pending(self, cutoff_ts: str, con: sqlite3.Connection | None = None) -> int:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute(
                """
                UPDATE pending_deposits
                SET status='EXPIRED', resolved_at=?, resolution_note='Expired by cleanup job'
                WHERE status='PENDING' AND expires_at <= ?
                """,
                (timestamp(), cutoff_ts),
            )
            return cursor.rowcount
