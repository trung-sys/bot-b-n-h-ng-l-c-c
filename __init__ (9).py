from __future__ import annotations

import sqlite3

from app.db.repositories.base import BaseRepository


class CatalogRepository(BaseRepository):
    def add_category(self, name: str, con: sqlite3.Connection | None = None) -> int:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute("INSERT INTO categories(name, is_active) VALUES(?, 1)", (name,))
            return int(cursor.lastrowid)

    def edit_category(self, category_id: int, name: str, con: sqlite3.Connection | None = None) -> None:
        with self.connection(con, write=True) as connection:
            connection.execute("UPDATE categories SET name=? WHERE id=?", (name, category_id))

    def deactivate_category(self, category_id: int, con: sqlite3.Connection | None = None) -> None:
        with self.connection(con, write=True) as connection:
            connection.execute("UPDATE categories SET is_active=0 WHERE id=?", (category_id,))

    def list_active_categories(self, con: sqlite3.Connection | None = None) -> list[sqlite3.Row]:
        with self.connection(con) as connection:
            return connection.execute(
                "SELECT id, name FROM categories WHERE is_active=1 ORDER BY id DESC"
            ).fetchall()

    def add_product(
        self,
        category_id: int,
        name: str,
        price: int,
        stock: int,
        deliver_text: str,
        con: sqlite3.Connection | None = None,
    ) -> int:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute(
                """
                INSERT INTO products(category_id, name, price, stock, deliver_text, is_active)
                VALUES(?, ?, ?, ?, ?, 1)
                """,
                (category_id, name, price, stock, deliver_text),
            )
            return int(cursor.lastrowid)

    def edit_product(
        self,
        product_id: int,
        name: str,
        price: int,
        stock: int,
        deliver_text: str,
        con: sqlite3.Connection | None = None,
    ) -> None:
        with self.connection(con, write=True) as connection:
            connection.execute(
                """
                UPDATE products
                SET name=?, price=?, stock=?, deliver_text=?
                WHERE id=?
                """,
                (name, price, stock, deliver_text, product_id),
            )

    def deactivate_product(self, product_id: int, con: sqlite3.Connection | None = None) -> None:
        with self.connection(con, write=True) as connection:
            connection.execute("UPDATE products SET is_active=0 WHERE id=?", (product_id,))

    def list_products_by_category(self, category_id: int, con: sqlite3.Connection | None = None) -> list[sqlite3.Row]:
        with self.connection(con) as connection:
            return connection.execute(
                """
                SELECT id, category_id, name, price, stock, deliver_text
                FROM products
                WHERE is_active=1 AND category_id=?
                ORDER BY id DESC
                """,
                (category_id,),
            ).fetchall()

    def get_product(self, product_id: int, active_only: bool = True, con: sqlite3.Connection | None = None) -> sqlite3.Row | None:
        query = "SELECT * FROM products WHERE id=?"
        if active_only:
            query += " AND is_active=1"
        with self.connection(con) as connection:
            return connection.execute(query, (product_id,)).fetchone()

    def decrement_stock_if_available(
        self,
        product_id: int,
        quantity: int = 1,
        con: sqlite3.Connection | None = None,
    ) -> bool:
        with self.connection(con, write=True) as connection:
            cursor = connection.execute(
                """
                UPDATE products
                SET stock = stock - ?
                WHERE id=? AND is_active=1 AND COALESCE(stock, 0) >= ?
                """,
                (quantity, product_id, quantity),
            )
            return cursor.rowcount > 0

