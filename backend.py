"""Database access and business operations for G&R RestoManage."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import date
from decimal import Decimal
from typing import Any

from db import Database


class RestoManageBackend:
    """Restaurant workflows and business rules, backed by the low-level Database."""

    def __init__(self, database: Database | None = None):
        self.database = database or Database()

    def connection(self):
        return self.database.connection()

    def rows(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        return self.database.rows(sql, params)

    def row(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        return self.database.row(sql, params)

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        return self.database.execute(sql, params)

    def authenticate(self, username: str, password: str) -> dict[str, Any] | None:
        user = self.row(
            "SELECT u.user_id,u.username,u.password,u.role,u.employee_id,"
            "e.first_name,e.last_name,e.status employee_status "
            "FROM users u LEFT JOIN employees e ON e.employee_id=u.employee_id "
            "WHERE u.username=%s", (username,),
        )
        if not user or not self._verify_password(password, user["password"]):
            return None
        if user["employee_status"] == "Inactive":
            return None
        if not user["password"].startswith("pbkdf2_sha256$"):
            self.execute("UPDATE users SET password=%s WHERE user_id=%s",
                         (self._hash_password(password), user["user_id"]))
        return user

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
        return "pbkdf2_sha256${}${}".format(
            base64.urlsafe_b64encode(salt).decode(),
            base64.urlsafe_b64encode(digest).decode(),
        )

    @staticmethod
    def _verify_password(password: str, stored: str) -> bool:
        if not stored.startswith("pbkdf2_sha256$"):
            return hmac.compare_digest(password, stored)
        try:
            _, salt_text, digest_text = stored.split("$", 2)
            salt = base64.urlsafe_b64decode(salt_text.encode())
            expected = base64.urlsafe_b64decode(digest_text.encode())
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def money(value: Any) -> str:
        return f"PHP {Decimal(str(value or 0)):,.2f}"

    def dashboard_data(self) -> dict[str, Any]:
        today = date.today()
        month_index = today.year * 12 + today.month - 1 - 5
        start_year, start_month_index = divmod(month_index, 12)
        start_month = date(start_year, start_month_index + 1, 1)
        next_index = today.year * 12 + today.month
        next_year, next_month_index = divmod(next_index, 12)
        next_month = date(next_year, next_month_index + 1, 1)
        metrics = self.row(
            "SELECT (SELECT COALESCE(SUM(amount_paid),0) FROM payments "
            "WHERE payment_status='Paid' AND DATE(payment_date)=CURDATE()) sales_today, "
            "(SELECT COUNT(*) FROM orders WHERE order_status='Pending') open_orders, "
            "(SELECT COUNT(*) FROM restaurant_tables WHERE status='Available') available_tables, "
            "(SELECT COUNT(*) FROM menu_items WHERE status='Available') active_items"
        ) or {}
        sales = self.rows("SELECT DATE_FORMAT(payment_date,'%Y-%m') month_key,SUM(amount_paid) amount "
            "FROM payments WHERE payment_status='Paid' AND payment_date >= %s AND payment_date < %s "
            "GROUP BY DATE_FORMAT(payment_date,'%Y-%m')", (start_month,next_month))
        expenses = self.rows("SELECT DATE_FORMAT(expense_date,'%Y-%m') month_key,SUM(amount) amount "
            "FROM expenses WHERE expense_date >= %s AND expense_date < %s "
            "GROUP BY DATE_FORMAT(expense_date,'%Y-%m')", (start_month,next_month))
        visits = self.rows("SELECT DATE_FORMAT(order_date,'%Y-%m') month_key,COUNT(*) visits "
            "FROM orders WHERE order_date >= %s AND order_date < %s "
            "GROUP BY DATE_FORMAT(order_date,'%Y-%m')", (start_month,next_month))
        attendance = self.rows("SELECT status,COUNT(*) total FROM attendance "
            "WHERE attendance_date >= %s AND attendance_date < %s GROUP BY status",
            (today.replace(day=1),next_month))
        recent = self.rows("SELECT o.order_id,o.order_date,o.order_status,o.total_amount,"
            "COALESCE(CONCAT(c.first_name,' ',c.last_name),'Walk-in') customer "
            "FROM orders o LEFT JOIN customers c ON c.customer_id=o.customer_id "
            "ORDER BY o.order_date DESC LIMIT 6")
        return {"metrics":metrics,"sales":sales,"expenses":expenses,
                "visits":visits,"attendance":attendance,"recent":recent}

    def menu_items(self, category_id: int | None = None, search: str = "",
                   available_only: bool = False) -> list[dict[str, Any]]:
        sql = "SELECT m.item_id,m.item_name,m.description,m.price,m.status,m.category_id,c.category_name "
        sql += "FROM menu_items m JOIN menu_categories c ON c.category_id=m.category_id WHERE 1=1"
        params: list[Any] = []
        if available_only:
            sql += " AND m.status='Available'"
        if category_id is not None:
            sql += " AND m.category_id=%s"
            params.append(category_id)
        if search:
            sql += " AND m.item_name LIKE %s"
            params.append(f"%{search}%")
        return self.rows(sql + " ORDER BY m.item_id", tuple(params))

    def categories(self) -> list[dict[str, Any]]:
        return self.rows("SELECT category_id,category_name FROM menu_categories ORDER BY category_name")

    def menu_item(self, item_id: int) -> dict[str, Any] | None:
        return self.row("SELECT * FROM menu_items WHERE item_id=%s", (item_id,))

    def save_menu_item(self, item_id: int | None, values: tuple[Any, ...]) -> int:
        if item_id:
            self.execute("UPDATE menu_items SET category_id=%s,item_name=%s,description=%s,price=%s WHERE item_id=%s",
                         (*values,item_id))
            return item_id
        return self.execute("INSERT INTO menu_items (category_id,item_name,description,price) VALUES (%s,%s,%s,%s)", values)

    def set_menu_status(self, item_id: int, status: str) -> None:
        self.execute("UPDATE menu_items SET status=%s WHERE item_id=%s", (status,item_id))

    def customers(self) -> list[dict[str, Any]]:
        return self.rows("SELECT customer_id,first_name,last_name,phone FROM customers ORDER BY last_name,first_name")

    def customer(self, customer_id: int) -> dict[str, Any] | None:
        return self.row("SELECT * FROM customers WHERE customer_id=%s", (customer_id,))

    def save_customer(self, customer_id: int | None, values: tuple[Any, ...]) -> None:
        if customer_id:
            self.execute("UPDATE customers SET first_name=%s,last_name=%s,phone=%s WHERE customer_id=%s",
                         (*values,customer_id))
        else:
            self.execute("INSERT INTO customers (first_name,last_name,phone) VALUES (%s,%s,%s)", values)

    def orders(self, status: str = "All orders") -> list[dict[str, Any]]:
        sql = "SELECT o.order_id,o.order_date,o.order_status,o.total_amount,"
        sql += "COALESCE(CONCAT(c.first_name,' ',c.last_name),'Walk-in') customer,"
        sql += "CONCAT(e.first_name,' ',e.last_name) employee,COALESCE(t.table_number,'-') table_number "
        sql += "FROM orders o LEFT JOIN customers c ON c.customer_id=o.customer_id "
        sql += "JOIN employees e ON e.employee_id=o.employee_id LEFT JOIN restaurant_tables t ON t.table_id=o.table_id"
        params: tuple[Any, ...] = ()
        if status != "All orders":
            sql += " WHERE o.order_status=%s"
            params = (status,)
        return self.rows(sql + " ORDER BY o.order_date DESC", params)

    def complete_order(self, order_id: int) -> None:
        connection = self.connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT table_id,order_status FROM orders WHERE order_id=%s FOR UPDATE", (order_id,))
            row = cursor.fetchone()
            if not row or row[1] != "Pending":
                raise ValueError("Only pending orders can be completed.")
            cursor.execute("UPDATE orders SET order_status='Completed' WHERE order_id=%s", (order_id,))
            if row[0] is not None:
                cursor.execute("UPDATE restaurant_tables SET status='Available' WHERE table_id=%s", (row[0],))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def tables(self) -> list[dict[str, Any]]:
        return self.rows("SELECT t.table_id,t.table_number,t.capacity,t.status,"
            "(SELECT COUNT(*) FROM orders o WHERE o.table_id=t.table_id AND o.order_status='Pending') open_orders "
            "FROM restaurant_tables t ORDER BY t.table_number")

    def table(self, table_id: int) -> dict[str, Any] | None:
        return self.row("SELECT table_number,capacity FROM restaurant_tables WHERE table_id=%s", (table_id,))

    def save_table(self, table_id: int | None, table_number: str, capacity: int | None) -> None:
        if table_id:
            self.execute("UPDATE restaurant_tables SET table_number=%s,capacity=%s WHERE table_id=%s",
                         (table_number,capacity,table_id))
        else:
            self.execute("INSERT INTO restaurant_tables (table_number,capacity) VALUES (%s,%s)", (table_number,capacity))

    def employees(self, include_archived: bool = True) -> list[dict[str, Any]]:
        sql = "SELECT employee_id,first_name,last_name,phone,address,position,date_hired,status FROM employees"
        if not include_archived:
            sql += " WHERE status='Active'"
        return self.rows(sql + " ORDER BY employee_id")

    def employee(self, employee_id: int) -> dict[str, Any] | None:
        return self.row("SELECT * FROM employees WHERE employee_id=%s", (employee_id,))

    def save_employee(self, employee_id: int | None, values: tuple[Any, ...]) -> None:
        if employee_id:
            self.execute("UPDATE employees SET first_name=%s,last_name=%s,phone=%s,address=%s,position=%s,date_hired=%s WHERE employee_id=%s",
                         (*values,employee_id))
        else:
            self.execute("INSERT INTO employees (first_name,last_name,phone,address,position,date_hired) VALUES (%s,%s,%s,%s,%s,%s)", values)

    def set_employee_status(self, employee_id: int, status: str) -> None:
        self.execute("UPDATE employees SET status=%s WHERE employee_id=%s", (status,employee_id))

    def attendance(self) -> list[dict[str, Any]]:
        return self.rows("SELECT a.attendance_id,a.employee_id,CONCAT(e.first_name,' ',e.last_name) employee,"
            "a.attendance_date,DATE_FORMAT(a.time_in,'%h:%i %p') time_in,"
            "DATE_FORMAT(a.time_out,'%h:%i %p') time_out,a.status FROM attendance a "
            "JOIN employees e ON e.employee_id=a.employee_id ORDER BY a.attendance_date DESC,a.attendance_id DESC")

    def attendance_record(self, attendance_id: int) -> dict[str, Any] | None:
        return self.row("SELECT attendance_id,employee_id,attendance_date,"
            "DATE_FORMAT(time_in,'%h:%i %p') time_in,DATE_FORMAT(time_out,'%h:%i %p') time_out,status "
            "FROM attendance WHERE attendance_id=%s", (attendance_id,))

    def save_attendance(self, attendance_id: int | None, employee_id: int,
                        time_in: str | None, time_out: str | None, status: str) -> None:
        if attendance_id:
            self.execute("UPDATE attendance SET employee_id=%s,time_in=%s,time_out=%s,status=%s WHERE attendance_id=%s",
                         (employee_id,time_in,time_out,status,attendance_id))
        else:
            self.execute("INSERT INTO attendance (employee_id,attendance_date,time_in,time_out,status) "
                         "VALUES (%s,CURDATE(),%s,%s,%s)", (employee_id,time_in,time_out,status))

    def expenses(self) -> tuple[Any, list[dict[str, Any]]]:
        summary = self.row("SELECT COALESCE(SUM(amount),0) total FROM expenses "
            "WHERE YEAR(expense_date)=YEAR(CURDATE()) AND MONTH(expense_date)=MONTH(CURDATE())") or {"total":0}
        rows = self.rows("SELECT x.expense_id,x.expense_date,x.expense_name,x.description,x.amount,"
            "COALESCE(CONCAT(e.first_name,' ',e.last_name),'-') employee FROM expenses x "
            "LEFT JOIN employees e ON e.employee_id=x.employee_id ORDER BY x.expense_date DESC")
        return summary["total"], rows

    def add_expense(self, employee_id: int | None, name: str, description: str | None,
                    amount: Decimal) -> None:
        self.execute("INSERT INTO expenses (employee_id,expense_name,description,amount) VALUES (%s,%s,%s,%s)",
                     (employee_id,name,description,amount))

    def checkout(self, employee_id: int, customer_id: int | None, table_id: int | None,
                 cart: dict[int, dict[str, Any]], payment_method: str,
                 tendered: Decimal) -> tuple[int, Decimal]:
        connection = self.connection()
        try:
            cursor = connection.cursor()
            if table_id is not None:
                cursor.execute("SELECT status FROM restaurant_tables WHERE table_id=%s FOR UPDATE", (table_id,))
                table = cursor.fetchone()
                if not table or table[0] != "Available":
                    raise ValueError("That table is no longer available. Choose another table.")
            total = Decimal("0.00")
            items = []
            for item_id, entry in cart.items():
                cursor.execute("SELECT price FROM menu_items WHERE item_id=%s AND status='Available' FOR UPDATE", (item_id,))
                item = cursor.fetchone()
                if not item:
                    raise ValueError("A selected menu item is no longer available. Refresh the order.")
                price = Decimal(str(item[0]))
                quantity = entry["quantity"]
                subtotal = price * quantity
                total += subtotal
                items.append((item_id,quantity,price,subtotal))
            if tendered < total:
                raise ValueError(f"The current total is {self.money(total)}. Enter enough payment to continue.")
            cursor.execute("INSERT INTO orders (customer_id,employee_id,table_id,total_amount,order_status) "
                "VALUES (%s,%s,%s,%s,'Pending')", (customer_id,employee_id,table_id,total))
            order_id = cursor.lastrowid
            for item_id,quantity,price,subtotal in items:
                cursor.execute("INSERT INTO order_items (order_id,item_id,quantity,unit_price,subtotal) "
                    "VALUES (%s,%s,%s,%s,%s)", (order_id,item_id,quantity,price,subtotal))
            cursor.execute("INSERT INTO payments (order_id,payment_method,amount_paid,payment_status) "
                "VALUES (%s,%s,%s,'Paid')", (order_id,payment_method,total))
            if table_id is not None:
                cursor.execute("UPDATE restaurant_tables SET status='Occupied' WHERE table_id=%s", (table_id,))
            connection.commit()
            return order_id,total
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()