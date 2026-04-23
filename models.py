from __future__ import annotations

import sqlite3

from app.db.repositories.base import BaseRepository


class CouponsRepository(BaseRepository):
    def upsert_coupon(
        self,
        code: str,
        discount_amount: int,
        discount_percent: int,
        apply_product_id: int | None,
        min_order: int,
        max_uses: int,
        con: sqlite3.Connection | None = None,
    ) -> None:
        with self.connection(con, write=True) as connection:
            connection.execute(
                """
                INSERT INTO coupons(code, discount_amount, discount_percent, apply_product_id, min_order, is_active, max_uses, used_count)
                VALUES(?, ?, ?, ?, ?, 1, ?, 0)
                ON CONFLICT(code) DO UPDATE SET
                    discount_amount=excluded.discount_amount,
                    discount_percent=excluded.discount_percent,
                    apply_product_id=excluded.apply_product_id,
                    min_order=excluded.min_order,
                    max_uses=excluded.max_uses,
                    is_active=1
                """,
                (code, discount_amount, discount_percent, apply_product_id, min_order, max_uses),
            )

    def deactivate_coupon(self, code: str, con: sqlite3.Connection | None = None) -> None:
        with self.connection(con, write=True) as connection:
            connection.execute("UPDATE coupons SET is_active=0 WHERE code=?", (code,))

    def get_coupon(self, code: str, active_only: bool = True, con: sqlite3.Connection | None = None) -> sqlite3.Row | None:
        query = "SELECT * FROM coupons WHERE code=?"
        if active_only:
            query += " AND is_active=1"
        with self.connection(con) as connection:
            return connection.execute(query, (code,)).fetchone()

    def reserve_use(self, code: str, con: sqlite3.Connection | None = None) -> bool:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute(
                """
                UPDATE coupons
                SET used_count = used_count + 1
                WHERE code=? AND is_active=1 AND (max_uses=0 OR used_count < max_uses)
                """,
                (code,),
            )
            return cursor.rowcount > 0

