"""Flask web application and JSON API for G&R RestoManage."""

from __future__ import annotations

import os
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from functools import wraps
from typing import Any, Callable

from flask import Flask, Response, jsonify, render_template, request, session

from backend import RestoManageBackend


app = Flask(__name__)
app.secret_key = os.getenv("RESTOMANAGE_SECRET", "local-demo-key-change-before-deployment")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
db = RestoManageBackend()


def _serialize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


def json_response(payload: Any, status: int = 200):
    return jsonify(_serialize(payload)), status


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any):
        if not session.get("user"):
            return json_response({"error": "Sign in required."}, 401)
        return view(*args, **kwargs)
    return wrapped


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    @login_required
    def wrapped(*args: Any, **kwargs: Any):
        if session["user"].get("role") != "admin":
            return json_response({"error": "Administrator access required."}, 403)
        return view(*args, **kwargs)
    return wrapped


def payload() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("A JSON object is required.")
    return data


def required_text(data: dict[str, Any], key: str, label: str | None = None) -> str:
    value = str(data.get(key, "")).strip()
    if not value:
        raise ValueError(f"{label or key.replace('_', ' ').title()} is required.")
    return value


def positive_int(value: Any, label: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a whole number.") from None
    if result <= 0:
        raise ValueError(f"{label} must be greater than zero.")
    return result


def handle_error(error: Exception, status: int = 400):
    return json_response({"error": str(error)}, status)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/auth/login")
def login():
    try:
        data = payload()
        username = required_text(data, "username", "Username")
        password = required_text(data, "password", "Password")
        user = db.authenticate(username, password)
        if not user:
            return json_response({"error": "Invalid credentials or inactive account."}, 401)
        session.clear()
        session["user"] = {"user_id": user["user_id"], "username": user["username"],
            "role": user["role"], "employee_id": user["employee_id"],
            "first_name": user.get("first_name"), "last_name": user.get("last_name")}
        return json_response({"user": session["user"]})
    except ValueError as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


@app.post("/api/auth/logout")
def logout():
    session.clear()
    return json_response({"ok": True})


@app.get("/api/auth/me")
def current_user():
    return json_response({"user": session.get("user")})


@app.get("/api/dashboard")
@login_required
def dashboard():
    try:
        return json_response(db.dashboard_data())
    except Exception as error:
        return handle_error(error, 503)


@app.get("/api/menu")
@login_required
def menu_list():
    try:
        raw_category = request.args.get("category_id")
        category_id = positive_int(raw_category, "Category") if raw_category else None
        items = db.menu_items(category_id, request.args.get("q", "").strip(),
                              request.args.get("available") == "true")
        return json_response({"items": items, "categories": db.categories()})
    except Exception as error:
        return handle_error(error)


@app.post("/api/menu")
@admin_required
def menu_create():
    try:
        data = payload()
        item_name = required_text(data, "item_name", "Item name")
        category_id = positive_int(data.get("category_id"), "Category")
        price = Decimal(str(data.get("price", "")))
        if not price.is_finite() or price < 0:
            raise ValueError("Price must be a non-negative amount.")
        item_id = db.save_menu_item(None, (category_id, item_name, data.get("description") or None, price))
        return json_response({"item_id": item_id}, 201)
    except (ValueError, InvalidOperation) as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


@app.patch("/api/menu/<int:item_id>")
@admin_required
def menu_update(item_id: int):
    try:
        data = payload()
        if "status" in data:
            if data["status"] not in ("Available", "Unavailable"):
                raise ValueError("Status must be Available or Unavailable.")
            db.set_menu_status(item_id, data["status"])
        else:
            item_name = required_text(data, "item_name", "Item name")
            category_id = positive_int(data.get("category_id"), "Category")
            price = Decimal(str(data.get("price", "")))
            if not price.is_finite() or price < 0:
                raise ValueError("Price must be a non-negative amount.")
            db.save_menu_item(item_id, (category_id, item_name, data.get("description") or None, price))
        return json_response({"ok": True})
    except (ValueError, InvalidOperation) as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


@app.get("/api/customers")
@login_required
def customers_list():
    try:
        return json_response({"customers": db.customers()})
    except Exception as error:
        return handle_error(error, 503)


@app.post("/api/customers")
@login_required
def customer_create():
    return customer_save(None)


@app.patch("/api/customers/<int:customer_id>")
@login_required
def customer_update(customer_id: int):
    return customer_save(customer_id)


def customer_save(customer_id: int | None):
    try:
        data = payload()
        first = required_text(data, "first_name", "First name")
        last = required_text(data, "last_name", "Last name")
        db.save_customer(customer_id, (first, last, str(data.get("phone", "")).strip() or None))
        return json_response({"ok": True}, 201 if customer_id is None else 200)
    except ValueError as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


@app.get("/api/orders")
@login_required
def orders_list():
    try:
        status = request.args.get("status", "All orders")
        if status not in ("All orders", "Pending", "Completed", "Cancelled"):
            raise ValueError("Unknown order status.")
        return json_response({"orders": db.orders(status)})
    except Exception as error:
        return handle_error(error, 503 if not isinstance(error, ValueError) else 400)


@app.post("/api/orders")
@login_required
def order_create():
    try:
        data = payload()
        if not session["user"].get("employee_id"):
            raise ValueError("This account is not linked to an employee.")
        method = data.get("payment_method")
        if method not in ("Cash", "GCash", "Card"):
            raise ValueError("Choose Cash, GCash, or Card.")
        items = data.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError("Add at least one item to the order.")
        cart: dict[int, dict[str, Any]] = {}
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Invalid order item.")
            item_id = positive_int(item.get("item_id"), "Menu item")
            quantity = positive_int(item.get("quantity"), "Quantity")
            cart[item_id] = {"quantity": quantity}
        customer_id = positive_int(data["customer_id"], "Customer") if data.get("customer_id") else None
        table_id = positive_int(data["table_id"], "Table") if data.get("table_id") else None
        tendered = Decimal(str(data.get("tendered", "")))
        if not tendered.is_finite() or tendered < 0:
            raise ValueError("Enter a valid amount received.")
        order_id, total = db.checkout(session["user"]["employee_id"], customer_id,
                                      table_id, cart, method, tendered)
        return json_response({"order_id": order_id, "total": total,
                              "change": tendered - total}, 201)
    except (ValueError, InvalidOperation) as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


@app.patch("/api/orders/<int:order_id>/complete")
@login_required
def order_complete(order_id: int):
    try:
        db.complete_order(order_id)
        return json_response({"ok": True})
    except Exception as error:
        return handle_error(error)


@app.get("/api/tables")
@login_required
def tables_list():
    try:
        return json_response({"tables": db.tables()})
    except Exception as error:
        return handle_error(error, 503)


@app.post("/api/tables")
@admin_required
def table_create():
    return table_save(None)


@app.patch("/api/tables/<int:table_id>")
@admin_required
def table_update(table_id: int):
    return table_save(table_id)


def table_save(table_id: int | None):
    try:
        data = payload()
        number = required_text(data, "table_number", "Table number")
        capacity = positive_int(data["capacity"], "Capacity") if data.get("capacity") else None
        db.save_table(table_id, number, capacity)
        return json_response({"ok": True}, 201 if table_id is None else 200)
    except ValueError as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


@app.get("/api/employees")
@admin_required
def employees_list():
    try:
        return json_response({"employees": db.employees()})
    except Exception as error:
        return handle_error(error, 503)


@app.post("/api/employees")
@admin_required
def employee_create():
    return employee_save(None)


@app.patch("/api/employees/<int:employee_id>")
@admin_required
def employee_update(employee_id: int):
    return employee_save(employee_id)


def employee_save(employee_id: int | None):
    try:
        data = payload()
        values = (required_text(data, "first_name", "First name"),
                  required_text(data, "last_name", "Last name"),
                  str(data.get("phone", "")).strip() or None,
                  str(data.get("address", "")).strip() or None,
                  required_text(data, "position", "Position"),
                  str(data.get("date_hired", "")).strip() or None)
        db.save_employee(employee_id, values)
        return json_response({"ok": True}, 201 if employee_id is None else 200)
    except ValueError as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


@app.patch("/api/employees/<int:employee_id>/status")
@admin_required
def employee_status(employee_id: int):
    try:
        status = payload().get("status")
        if status not in ("Active", "Inactive"):
            raise ValueError("Status must be Active or Inactive.")
        db.set_employee_status(employee_id, status)
        return json_response({"ok": True})
    except ValueError as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


def parse_attendance_time(value: Any) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.strptime(str(value), "%I:%M %p")
    except ValueError:
        raise ValueError("Choose a time between 8:00 AM and 8:00 PM.") from None
    if parsed.hour < 8 or parsed.hour > 20 or (parsed.hour == 20 and parsed.minute > 0):
        raise ValueError("Choose a time between 8:00 AM and 8:00 PM.")
    return parsed.strftime("%H:%M:%S")


@app.get("/api/attendance")
@admin_required
def attendance_list():
    try:
        return json_response({"attendance": db.attendance(), "employees": db.employees(False)})
    except Exception as error:
        return handle_error(error, 503)


@app.post("/api/attendance")
@admin_required
def attendance_create():
    return attendance_save(None)


@app.patch("/api/attendance/<int:attendance_id>")
@admin_required
def attendance_update(attendance_id: int):
    return attendance_save(attendance_id)


def attendance_save(attendance_id: int | None):
    try:
        data = payload()
        employee_id = positive_int(data.get("employee_id"), "Employee")
        status = data.get("status")
        if status not in ("Present", "Late", "Absent"):
            raise ValueError("Choose Present, Late, or Absent.")
        db.save_attendance(attendance_id, employee_id,
            parse_attendance_time(data.get("time_in")),
            parse_attendance_time(data.get("time_out")), status)
        return json_response({"ok": True}, 201 if attendance_id is None else 200)
    except ValueError as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


@app.get("/api/expenses")
@admin_required
def expenses_list():
    try:
        total, expenses = db.expenses()
        return json_response({"total": total, "expenses": expenses})
    except Exception as error:
        return handle_error(error, 503)


@app.post("/api/expenses")
@admin_required
def expense_create():
    try:
        data = payload()
        name = required_text(data, "expense_name", "Expense name")
        amount = Decimal(str(data.get("amount", "")))
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        db.add_expense(session["user"].get("employee_id"), name,
                       str(data.get("description", "")).strip() or None, amount)
        return json_response({"ok": True}, 201)
    except (ValueError, InvalidOperation) as error:
        return handle_error(error)
    except Exception as error:
        return handle_error(error, 503)


if __name__ == "__main__":
    app.run(host=os.getenv("RESTOMANAGE_HOST", "127.0.0.1"),
            port=int(os.getenv("RESTOMANAGE_PORT", "5000")), debug=False)