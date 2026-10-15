"""Tkinter presentation layer for G&R RestoManage."""

from __future__ import annotations

import tkinter as tk
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk
from typing import Any, Callable

from backend import RestoManageBackend


PALETTES = {
    "light": {"BG":"#f8f4fb","PANEL":"#ffffff","INK":"#35263f","MUTED":"#887b93",
        "ACCENT":"#9b6cc0","NAV":"#52365f","PINK":"#f1c8df","LINE":"#e9dff0",
        "RED":"#b94d73","SOFT":"#f0e7f5","NAV_TEXT":"#f5eefa","NAV_MUTED":"#d1bddc",
        "FREE":"#e9f3ec","BUSY":"#f7e8ee","GOOD":"#568268","GRID":"#e9e1ed"},
    "dark": {"BG":"#211a28","PANEL":"#30263a","INK":"#f6edf9","MUTED":"#b9a9c3",
        "ACCENT":"#c49cdd","NAV":"#493553","PINK":"#edb8d4","LINE":"#493d53",
        "RED":"#ed9eba","SOFT":"#3a2e45","NAV_TEXT":"#f6edf9","NAV_MUTED":"#ceb8da",
        "FREE":"#30483d","BUSY":"#513746","GOOD":"#9bc6a9","GRID":"#4a3d54"},
}
FONT = "Segoe UI"


def money(value: Any) -> str:
    return f"PHP {Decimal(str(value or 0)):,.2f}"


class OrderingApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.db = RestoManageBackend()
        self.user: dict[str, Any] | None = None
        self.cart: dict[int, dict[str, Any]] = {}
        self.theme = "light"
        self.colors = PALETTES[self.theme]
        self.current_page: Callable[[], None] = self.dashboard
        self.root.title("G&R RestoManage | Ordering Management System")
        self.root.geometry("1360x860")
        self.root.minsize(1120, 720)
        self.root.configure(bg=self.colors["BG"])
        self._style()
        self.show_login()

    def _style(self) -> None:
        c = self.colors
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=c["BG"])
        style.configure("TLabel", background=c["BG"], foreground=c["INK"], font=(FONT, 10))
        style.configure("Muted.TLabel", foreground=c["MUTED"], font=(FONT, 9))
        style.configure("Title.TLabel", font=(FONT, 22, "bold"), foreground=c["INK"])
        style.configure("TButton", font=(FONT, 9, "bold"), padding=(11, 8))
        style.configure("Accent.TButton", background=c["ACCENT"], foreground="white")
        style.map("Accent.TButton", background=[("active", c["NAV"])])
        style.configure("Nav.TButton", background=c["NAV"], foreground=c["NAV_TEXT"],
                        anchor="w", padding=(16, 11))
        style.map("Nav.TButton", background=[("active", c["ACCENT"])])
        style.configure("Treeview", background=c["PANEL"], fieldbackground=c["PANEL"],
                        foreground=c["INK"], rowheight=33, borderwidth=0, font=(FONT, 9))
        style.configure("Treeview.Heading", background=c["SOFT"], foreground=c["MUTED"],
                        font=(FONT, 8, "bold"), relief="flat", padding=(8, 8))
        style.map("Treeview", background=[("selected", c["PINK"])], foreground=[("selected", c["INK"])])
        style.configure("TEntry", padding=8, fieldbackground=c["PANEL"], foreground=c["INK"])
        style.configure("TCombobox", padding=7, fieldbackground=c["PANEL"], foreground=c["INK"])

    def _clear(self, widget: tk.Widget) -> None:
        for child in widget.winfo_children():
            child.destroy()

    def show_login(self) -> None:
        self._clear(self.root)
        c = self.colors
        shell = tk.Frame(self.root, bg=c["NAV"])
        shell.pack(fill="both", expand=True)
        brand = tk.Frame(shell, bg=c["NAV"], padx=70)
        brand.pack(side="left", fill="both", expand=True)
        tk.Label(brand, text="G&R\nRestoManage", bg=c["NAV"], fg=c["NAV_TEXT"],
                 font=(FONT, 37, "bold"), justify="left").pack(anchor="w", pady=(170, 14))
        tk.Label(brand, text="Ordering Management System", bg=c["NAV"], fg=c["NAV_MUTED"],
                 font=(FONT, 15)).pack(anchor="w")
        tk.Frame(brand, bg=c["PINK"], height=5, width=90).pack(anchor="w", pady=28)
        panel = tk.Frame(shell, bg=c["BG"], padx=70)
        panel.pack(side="right", fill="both", expand=True)
        form = tk.Frame(panel, bg=c["BG"], width=370)
        form.place(relx=.5, rely=.5, anchor="center")
        tk.Label(form, text="Welcome back", bg=c["BG"], fg=c["INK"], font=(FONT, 25, "bold")).pack(anchor="w")
        tk.Label(form, text="Sign in to manage today’s service.", bg=c["BG"], fg=c["MUTED"]).pack(anchor="w", pady=(7, 28))
        tk.Label(form, text="USERNAME", bg=c["BG"], fg=c["MUTED"], font=(FONT, 8, "bold")).pack(anchor="w")
        self.username_entry = ttk.Entry(form)
        self.username_entry.pack(fill="x", pady=(7, 18))
        tk.Label(form, text="PASSWORD", bg=c["BG"], fg=c["MUTED"], font=(FONT, 8, "bold")).pack(anchor="w")
        self.password_entry = ttk.Entry(form, show="*")
        self.password_entry.pack(fill="x", pady=(7, 22))
        ttk.Button(form, text="Sign in", style="Accent.TButton", command=self.login).pack(fill="x")
        self.username_entry.bind("<Return>", lambda _event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda _event: self.login())
        self.username_entry.focus_set()

    def login(self) -> None:
        username, password = self.username_entry.get().strip(), self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Sign in", "Enter your username and password.")
            return
        try:
            self.user = self.db.authenticate(username, password)
        except Exception as error:
            self._error(error)
            return
        if not self.user:
            messagebox.showerror("Sign in failed", "The credentials are invalid or the account is inactive.")
            return
        self.show_shell()

    def show_shell(self) -> None:
        self._clear(self.root)
        c = self.colors
        shell = tk.Frame(self.root, bg=c["BG"])
        shell.pack(fill="both", expand=True)
        nav = tk.Frame(shell, bg=c["NAV"], width=220)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)
        tk.Label(nav, text="G&R RestoManage", bg=c["NAV"], fg=c["NAV_TEXT"],
                 font=(FONT, 14, "bold")).pack(anchor="w", padx=19, pady=(24, 4))
        tk.Label(nav, text="ORDERING MANAGEMENT", bg=c["NAV"], fg=c["NAV_MUTED"],
                 font=(FONT, 8, "bold")).pack(anchor="w", padx=19, pady=(0, 22))
        self.content = tk.Frame(shell, bg=c["BG"])
        self.content.pack(side="left", fill="both", expand=True)
        sections = [
            ("OVERVIEW", [("Dashboard", self.dashboard), ("Point of sale", self.pos), ("Orders", self.orders)]),
            ("CATALOG", [("Menu", self.menu), ("Customers", self.customers), ("Tables", self.tables)]),
        ]
        if self.user["role"] == "admin":
            sections.append(("OPERATIONS", [("Employees", self.employees),
                ("Attendance", self.attendance), ("Expenses", self.expenses)]))
        for heading, entries in sections:
            tk.Label(nav, text=heading, bg=c["NAV"], fg=c["NAV_MUTED"],
                     font=(FONT, 8, "bold")).pack(anchor="w", padx=19, pady=(9, 6))
            for title, callback in entries:
                ttk.Button(nav, text=title, style="Nav.TButton",
                           command=lambda page=callback: self.navigate(page)).pack(fill="x", padx=8, pady=1)
        tk.Frame(nav, bg=c["LINE"], height=1).pack(fill="x", padx=16, pady=(16, 10))
        full_name = " ".join(filter(None, (self.user.get("first_name"), self.user.get("last_name")))) or self.user["username"]
        tk.Label(nav, text=full_name, bg=c["NAV"], fg=c["NAV_TEXT"], font=(FONT, 9, "bold")).pack(anchor="w", padx=19)
        tk.Label(nav, text=self.user["role"].title(), bg=c["NAV"], fg=c["NAV_MUTED"], font=(FONT, 9)).pack(anchor="w", padx=19, pady=(2, 9))
        ttk.Button(nav, text="Use dark theme" if self.theme == "light" else "Use light theme",
                   style="Nav.TButton", command=self.toggle_theme).pack(fill="x", padx=8, pady=2)
        ttk.Button(nav, text="Sign out", style="Nav.TButton", command=self.show_login).pack(fill="x", padx=8, pady=2)
        self.navigate(self.current_page)

    def navigate(self, page: Callable[[], None]) -> None:
        self.current_page = page
        page()

    def toggle_theme(self) -> None:
        self.theme = "dark" if self.theme == "light" else "light"
        self.colors = PALETTES[self.theme]
        self.root.configure(bg=self.colors["BG"])
        self._style()
        self.show_shell()

    def _heading(self, title: str, subtitle: str, action: tuple[str, Callable[[], None]] | None = None) -> None:
        c = self.colors
        bar = tk.Frame(self.content, bg=c["BG"])
        bar.pack(fill="x", padx=27, pady=(22, 16))
        text = tk.Frame(bar, bg=c["BG"])
        text.pack(side="left")
        ttk.Label(text, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(text, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(3, 0))
        if action:
            ttk.Button(bar, text=action[0], style="Accent.TButton", command=action[1]).pack(side="right")

    def _body(self) -> tk.Frame:
        body = tk.Frame(self.content, bg=self.colors["BG"])
        body.pack(fill="both", expand=True, padx=27, pady=(0, 22))
        return body

    def _panel(self, parent: tk.Widget, **kwargs: Any) -> tk.Frame:
        return tk.Frame(parent, bg=self.colors["PANEL"], highlightbackground=self.colors["LINE"],
                        highlightthickness=1, **kwargs)

    def _tree(self, parent: tk.Widget, columns: list[tuple[str, str, int]]) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=[item[0] for item in columns], show="headings")
        for key, label, width in columns:
            tree.heading(key, text=label)
            tree.column(key, width=width, anchor="w", stretch=True)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        return tree

    def _error(self, error: Exception) -> None:
        messagebox.showerror("Unable to complete action", str(error))

    def dashboard(self) -> None:
        self._heading("Good service starts here", f"Restaurant overview · {date.today():%A, %B %d, %Y}",
                      ("+  New order", lambda: self.navigate(self.pos)))
        body = self._body()
        try:
            data = self.db.dashboard_data()
        except Exception as error:
            self._error(error)
            return
        metric = data["metrics"]
        row = tk.Frame(body, bg=self.colors["BG"])
        row.pack(fill="x")
        stats = [("SALES TODAY", money(metric["sales_today"])),
                 ("OPEN ORDERS", metric["open_orders"]), ("AVAILABLE TABLES", metric["available_tables"]),
                 ("ACTIVE MENU ITEMS", metric["active_items"])]
        for index, (label, value) in enumerate(stats):
            card = self._panel(row, padx=14, pady=11)
            card.pack(side="left", fill="x", expand=True, padx=(0, 9 if index < 3 else 0))
            tk.Label(card, text=label, bg=self.colors["PANEL"], fg=self.colors["MUTED"],
                     font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(card, text=str(value), bg=self.colors["PANEL"], fg=self.colors["INK"],
                     font=(FONT, 17, "bold")).pack(anchor="w", pady=(5, 0))
        chart_row = tk.Frame(body, bg=self.colors["BG"])
        chart_row.pack(fill="x", pady=(12, 12))
        line_panel = self._chart_panel(chart_row, "Sales and expenses · 6 months")
        line_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))
        visit_panel = self._chart_panel(chart_row, "Customer visits · 6 months")
        visit_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))
        attendance_panel = self._chart_panel(chart_row, "Attendance · this month")
        attendance_panel.pack(side="left", fill="both", expand=True)
        months = self._month_labels()
        keys = [key for key, _label in months]
        sales = {row["month_key"]: float(row["amount"]) for row in data["sales"]}
        expenses = {row["month_key"]: float(row["amount"]) for row in data["expenses"]}
        visits = {row["month_key"]: int(row["visits"]) for row in data["visits"]}
        self._line_chart(line_panel, [label for _key, label in months],
                         [sales.get(key, 0) for key in keys], [expenses.get(key, 0) for key in keys])
        self._bar_chart(visit_panel, [label for _key, label in months], [visits.get(key, 0) for key in keys])
        self._pie_chart(attendance_panel, data["attendance"])
        panel = self._panel(body)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Recent orders", bg=self.colors["PANEL"], fg=self.colors["INK"],
                 font=(FONT, 11, "bold")).pack(anchor="w", padx=14, pady=(10, 0))
        tree = self._tree(panel, [("id","ORDER",72),("date","DATE & TIME",155),
            ("customer","CUSTOMER",190),("status","STATUS",105),("total","TOTAL",115)])
        for order in data["recent"]:
            tree.insert("", "end", values=(f"#{order['order_id']:04d}",order["order_date"],order["customer"],
                order["order_status"],money(order["total_amount"])))

    def _chart_panel(self, parent: tk.Widget, title: str) -> tk.Frame:
        panel = self._panel(parent, height=236)
        panel.pack_propagate(False)
        tk.Label(panel, text=title, bg=self.colors["PANEL"], fg=self.colors["INK"],
                 font=(FONT, 9, "bold")).pack(anchor="w", padx=11, pady=(10, 0))
        panel.chart = tk.Canvas(panel, bg=self.colors["PANEL"], highlightthickness=0, height=198)
        panel.chart.pack(fill="both", expand=True, padx=5, pady=2)
        return panel

    @staticmethod
    def _month_labels() -> list[tuple[str, str]]:
        today = date.today()
        index = today.year * 12 + today.month - 1 - 5
        months = []
        for offset in range(6):
            year, month_zero = divmod(index + offset, 12)
            month = month_zero + 1
            months.append((f"{year:04d}-{month:02d}", date(year, month, 1).strftime("%b")))
        return months

    def _line_chart(self, panel: tk.Frame, labels: list[str], sales: list[float], expenses: list[float]) -> None:
        canvas = panel.chart
        c = self.colors
        def draw(_event: Any = None) -> None:
            canvas.delete("all")
            width, height = max(canvas.winfo_width(), 260), max(canvas.winfo_height(), 150)
            left, right, top, bottom = 42, width - 12, 24, height - 29
            maximum = max(sales + expenses + [1])
            for step in range(4):
                y = bottom - (bottom - top) * step / 3
                canvas.create_line(left,y,right,y,fill=c["GRID"])
                canvas.create_text(left-4,y,text=f"{maximum*step/3/1000:.0f}k",anchor="e",fill=c["MUTED"],font=(FONT,7))
            for name, values, color in (("Sales",sales,c["ACCENT"]),("Expenses",expenses,c["RED"])):
                points = []
                for idx,value in enumerate(values):
                    x = left + (right-left) * idx / max(len(values)-1,1)
                    y = bottom - (bottom-top) * value / maximum
                    points.extend((x,y))
                    canvas.create_oval(x-3,y-3,x+3,y+3,fill=color,outline=color)
                if len(points) >= 4:
                    canvas.create_line(*points,fill=color,width=2,smooth=True)
            for idx,label in enumerate(labels):
                x = left + (right-left) * idx / max(len(labels)-1,1)
                canvas.create_text(x,bottom+12,text=label,fill=c["MUTED"],font=(FONT,7))
            canvas.create_line(left+4,10,left+16,10,fill=c["ACCENT"],width=2)
            canvas.create_text(left+20,10,text="Sales",anchor="w",fill=c["MUTED"],font=(FONT,7))
            canvas.create_line(left+67,10,left+79,10,fill=c["RED"],width=2)
            canvas.create_text(left+83,10,text="Expenses",anchor="w",fill=c["MUTED"],font=(FONT,7))
        canvas.bind("<Configure>", draw)
        canvas.after(40, draw)

    def _bar_chart(self, panel: tk.Frame, labels: list[str], values: list[int]) -> None:
        canvas = panel.chart
        c = self.colors
        def draw(_event: Any = None) -> None:
            canvas.delete("all")
            width, height = max(canvas.winfo_width(), 240), max(canvas.winfo_height(), 150)
            left, right, top, bottom = 24, width - 9, 18, height - 29
            maximum = max(values + [1])
            for step in range(3):
                y = bottom - (bottom-top)*step/2
                canvas.create_line(left,y,right,y,fill=c["GRID"])
            slot = (right-left)/max(len(values),1)
            for index,value in enumerate(values):
                bar_height = (bottom-top)*value/maximum
                x1 = left+slot*index+slot*.2
                x2 = left+slot*(index+1)-slot*.2
                canvas.create_rectangle(x1,bottom-bar_height,x2,bottom,fill=c["ACCENT"],outline="")
                canvas.create_text((x1+x2)/2,bottom-bar_height-7,text=str(value),fill=c["INK"],font=(FONT,7))
                canvas.create_text((x1+x2)/2,bottom+12,text=labels[index],fill=c["MUTED"],font=(FONT,7))
        canvas.bind("<Configure>", draw)
        canvas.after(40, draw)

    def _pie_chart(self, panel: tk.Frame, records: list[dict[str, Any]]) -> None:
        canvas = panel.chart
        c = self.colors
        def draw(_event: Any = None) -> None:
            canvas.delete("all")
            width, height = max(canvas.winfo_width(), 230), max(canvas.winfo_height(), 150)
            center_x, center_y = width*.38, height*.51
            radius = min(width*.27,height*.35)
            colors = {"Present":c["ACCENT"],"Late":c["PINK"],"Absent":c["RED"]}
            values = {row["status"]:int(row["total"]) for row in records}
            total = sum(values.values())
            if not total:
                canvas.create_text(width/2,height/2,text="No attendance records",fill=c["MUTED"],font=(FONT,8))
                return
            start = 90
            for label in ("Present","Late","Absent"):
                value = values.get(label,0)
                if value:
                    extent = -360*value/total
                    canvas.create_arc(center_x-radius,center_y-radius,center_x+radius,center_y+radius,
                        start=start,extent=extent,fill=colors[label],outline=c["PANEL"],width=2,style="pieslice")
                    start += extent
            for index,label in enumerate(("Present","Late","Absent")):
                y = height*.27+index*24
                canvas.create_rectangle(width*.68,y-5,width*.68+9,y+4,fill=colors[label],outline="")
                canvas.create_text(width*.68+14,y,text=f"{label}  {values.get(label,0)}",anchor="w",
                    fill=c["MUTED"],font=(FONT,7))
        canvas.bind("<Configure>", draw)
        canvas.after(40, draw)

    def pos(self) -> None:
        self.current_page = self.pos
        self._clear(self.content)
        self._heading("Point of sale", "Build a ticket, review totals, then confirm payment.")
        body = self._body()
        left = tk.Frame(body, bg=self.colors["BG"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))
        right = self._panel(body, width=370)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        control = self._panel(left, padx=10, pady=10)
        control.pack(fill="x", pady=(0,10))
        self.menu_search = tk.StringVar()
        search = ttk.Entry(control, textvariable=self.menu_search)
        search.pack(side="left", fill="x", expand=True, padx=(0,8))
        search.insert(0,"Search menu")
        self.category_filter = ttk.Combobox(control,state="readonly",width=18)
        self.category_filter.pack(side="right")
        catalog = self._panel(left)
        catalog.pack(fill="both",expand=True)
        self.pos_tree = self._tree(catalog,[("id","ID",54),("name","ITEM",220),("category","CATEGORY",130),("price","PRICE",105)])
        self.pos_tree.bind("<Double-1>",lambda _event:self.add_to_cart())
        ttk.Button(control,text="Add selected",style="Accent.TButton",command=self.add_to_cart).pack(side="right",padx=(0,8))
        self.menu_search.trace_add("write",lambda *_args:self.load_pos_menu())
        self.category_filter.bind("<<ComboboxSelected>>",lambda _event:self.load_pos_menu())
        tk.Label(right,text="Current order",bg=self.colors["PANEL"],fg=self.colors["INK"],font=(FONT,14,"bold")).pack(anchor="w",padx=14,pady=(13,2))
        self.cart_tree = ttk.Treeview(right,columns=("item","qty","total"),show="headings",height=8)
        for key,label,width in (("item","ITEM",165),("qty","QTY",40),("total","TOTAL",90)):
            self.cart_tree.heading(key,text=label); self.cart_tree.column(key,width=width,anchor="w" if key=="item" else "center")
        self.cart_tree.pack(fill="both",expand=True,padx=7,pady=5)
        actions = tk.Frame(right,bg=self.colors["PANEL"]); actions.pack(fill="x",padx=12,pady=4)
        ttk.Button(actions,text="-",width=4,command=lambda:self.adjust_cart(-1)).pack(side="left")
        ttk.Button(actions,text="+",width=4,command=lambda:self.adjust_cart(1)).pack(side="left",padx=4)
        ttk.Button(actions,text="Remove",command=self.remove_cart_item).pack(side="right")
        self.cart_total_label=tk.Label(right,text="PHP 0.00",bg=self.colors["PANEL"],fg=self.colors["INK"],font=(FONT,19,"bold"))
        self.cart_total_label.pack(anchor="e",padx=14,pady=5)
        fields=tk.Frame(right,bg=self.colors["PANEL"]); fields.pack(fill="x",padx=14)
        self.customer_combo=ttk.Combobox(fields,state="readonly"); self.customer_combo.pack(fill="x",pady=3)
        self.table_combo=ttk.Combobox(fields,state="readonly"); self.table_combo.pack(fill="x",pady=3)
        self.payment_combo=ttk.Combobox(fields,state="readonly",values=("Cash","GCash","Card")); self.payment_combo.set("Cash"); self.payment_combo.pack(fill="x",pady=3)
        tk.Label(fields,text="Cash received",bg=self.colors["PANEL"],fg=self.colors["MUTED"],font=(FONT,8)).pack(anchor="w",pady=(4,0))
        self.tender_entry=ttk.Entry(fields); self.tender_entry.pack(fill="x")
        self.payment_combo.bind("<<ComboboxSelected>>",lambda _event:self.update_tender())
        bottom=tk.Frame(right,bg=self.colors["PANEL"]); bottom.pack(fill="x",padx=14,pady=12)
        ttk.Button(bottom,text="Clear order",command=self.clear_cart).pack(side="left")
        ttk.Button(bottom,text="Review checkout",style="Accent.TButton",command=self.review_checkout).pack(side="right")
        self.category_names={}
        try:
            categories=self.db.categories(); self.category_names={r["category_name"]:r["category_id"] for r in categories}
            self.category_filter["values"]=["All categories",*self.category_names]; self.category_filter.set("All categories")
            customers=self.db.customers()
            self.customer_choices={"Walk-in customer":None}
            self.customer_choices.update({f"{r['first_name']} {r['last_name']} · #{r['customer_id']}":r["customer_id"] for r in customers})
            self.customer_combo["values"]=list(self.customer_choices); self.customer_combo.set("Walk-in customer")
            tables=self.db.tables(); available=[r for r in tables if r["status"]=="Available"]
            self.table_choices={"Takeaway / no table":None}; self.table_choices.update({r["table_number"]:r["table_id"] for r in available})
            self.table_combo["values"]=list(self.table_choices); self.table_combo.set("Takeaway / no table")
            self.load_pos_menu()
        except Exception as error: self._error(error)
        self.refresh_cart()

    def load_pos_menu(self) -> None:
        if not hasattr(self,"pos_tree") or not self.pos_tree.winfo_exists(): return
        try:
            selected=self.category_filter.get(); category_id=self.category_names.get(selected)
            search=self.menu_search.get().strip()
            if search=="Search menu": search=""
            rows=self.db.menu_items(category_id,search,True)
            self.pos_tree.delete(*self.pos_tree.get_children())
            for row in rows:
                self.pos_tree.insert("","end",iid=str(row["item_id"]),values=(row["item_id"],row["item_name"],row["category_name"],money(row["price"])))
        except Exception as error: self._error(error)

    def add_to_cart(self) -> None:
        selected=self.pos_tree.selection()
        if not selected: messagebox.showinfo("Point of sale","Select an item first."); return
        item_id=int(selected[0]); values=self.pos_tree.item(selected[0],"values")
        if item_id in self.cart: self.cart[item_id]["quantity"]+=1
        else: self.cart[item_id]={"name":values[1],"price":Decimal(str(values[3]).replace("PHP ","").replace(",","")),"quantity":1}
        self.refresh_cart()

    def refresh_cart(self) -> None:
        if not hasattr(self,"cart_tree") or not self.cart_tree.winfo_exists(): return
        self.cart_tree.delete(*self.cart_tree.get_children())
        for item_id,item in self.cart.items():
            self.cart_tree.insert("","end",iid=str(item_id),values=(item["name"],item["quantity"],money(item["price"]*item["quantity"])))
        total=sum((i["price"]*i["quantity"] for i in self.cart.values()),Decimal("0.00"))
        self.cart_total_label.configure(text=money(total)); self.update_tender()

    def update_tender(self) -> None:
        if not hasattr(self,"tender_entry") or not self.tender_entry.winfo_exists(): return
        total=sum((i["price"]*i["quantity"] for i in self.cart.values()),Decimal("0.00")); text=str(total)
        current=self.tender_entry.get()
        if self.payment_combo.get()!="Cash" or not current or current==getattr(self,"suggested_tender",None):
            self.tender_entry.delete(0,"end")
            if total: self.tender_entry.insert(0,text)
        self.suggested_tender=text

    def adjust_cart(self, delta: int) -> None:
        selected=self.cart_tree.selection()
        if not selected:return
        item_id=int(selected[0]); self.cart[item_id]["quantity"]+=delta
        if self.cart[item_id]["quantity"]<1:del self.cart[item_id]
        self.refresh_cart()

    def remove_cart_item(self) -> None:
        selected=self.cart_tree.selection()
        if selected:self.cart.pop(int(selected[0]),None); self.refresh_cart()

    def clear_cart(self) -> None:
        if self.cart and not messagebox.askyesno("Clear order","Remove all items from this unsaved order?"):return
        self.cart.clear(); self.refresh_cart()

    def review_checkout(self) -> None:
        if not self.cart: messagebox.showwarning("Checkout","Add at least one item first."); return
        try: tendered=Decimal(self.tender_entry.get().strip())
        except InvalidOperation: messagebox.showwarning("Checkout","Enter a valid amount received."); return
        total=sum((i["price"]*i["quantity"] for i in self.cart.values()),Decimal("0.00"))
        if tendered<total: messagebox.showwarning("Checkout",f"Payment must be at least {money(total)}."); return
        dialog=self._dialog("Review order",480,520)
        tk.Label(dialog,text="Order summary",bg=self.colors["PANEL"],fg=self.colors["INK"],font=(FONT,14,"bold")).pack(anchor="w",padx=22,pady=(12,8))
        summary=tk.Frame(dialog,bg=self.colors["PANEL"]);summary.pack(fill="both",expand=True,padx=22)
        for item in self.cart.values():
            tk.Label(summary,text=f"{item['quantity']} × {item['name']}",bg=self.colors["PANEL"],fg=self.colors["INK"]).pack(anchor="w",pady=3)
        total_label=f"Total: {money(total)}"
        customer=self.customer_combo.get(); table=self.table_combo.get(); method=self.payment_combo.get()
        tendered=total if method!="Cash" else tendered
        for text in (total_label,f"Customer: {customer}",f"Table: {table}",f"Payment: {method}",f"Received: {money(tendered)}",f"Change: {money(tendered-total)}"):
            tk.Label(dialog,text=text,bg=self.colors["PANEL"],fg=self.colors["INK"],font=(FONT,9,"bold")).pack(anchor="w",padx=22,pady=2)
        buttons=tk.Frame(dialog,bg=self.colors["PANEL"]);buttons.pack(fill="x",padx=22,pady=16)
        ttk.Button(buttons,text="Back",command=dialog.destroy).pack(side="left")
        ttk.Button(buttons,text="Confirm checkout",style="Accent.TButton",
            command=lambda:self.commit_checkout(dialog,tendered)).pack(side="right")

    def commit_checkout(self, dialog: tk.Toplevel, tendered: Decimal) -> None:
        if not self.user or not self.user.get("employee_id"):
            messagebox.showerror("Checkout","This account is not linked to an employee.",parent=dialog);return
        try:
            order_id,total=self.db.checkout(self.user["employee_id"],self.customer_choices[self.customer_combo.get()],
                self.table_choices[self.table_combo.get()],self.cart,self.payment_combo.get(),tendered)
        except Exception as error:
            messagebox.showerror("Checkout",str(error),parent=dialog);return
        change=tendered-total;self.cart.clear();dialog.destroy()
        messagebox.showinfo("Order recorded",f"Order #{order_id:04d} saved.\nTotal: {money(total)}\nChange: {money(change)}")
        self.navigate(self.pos)

    def orders(self) -> None:
        self.current_page=self.orders;self._clear(self.content)
        self._heading("Orders","Review service activity and complete open tickets.",("+  New order",lambda:self.navigate(self.pos)))
        body=self._body();tools=tk.Frame(body,bg=self.colors["BG"]);tools.pack(fill="x",pady=(0,8))
        ttk.Button(tools,text="Complete selected",style="Accent.TButton",command=self.complete_order).pack(side="left")
        self.order_filter=ttk.Combobox(tools,state="readonly",values=("All orders","Pending","Completed","Cancelled"),width=18)
        self.order_filter.set("All orders");self.order_filter.pack(side="right")
        self.order_filter.bind("<<ComboboxSelected>>",lambda _event:self.load_orders())
        panel=self._panel(body);panel.pack(fill="both",expand=True)
        self.orders_tree=self._tree(panel,[("id","ORDER",80),("date","DATE & TIME",155),("customer","CUSTOMER",175),
            ("employee","STAFF",145),("table","TABLE",85),("status","STATUS",105),("total","TOTAL",110)])
        self.load_orders()

    def load_orders(self) -> None:
        try:rows=self.db.orders(self.order_filter.get())
        except Exception as error:self._error(error);return
        self.orders_tree.delete(*self.orders_tree.get_children())
        for row in rows:self.orders_tree.insert("","end",iid=str(row["order_id"]),values=(f"#{row['order_id']:04d}",row["order_date"],row["customer"],row["employee"],row["table_number"],row["order_status"],money(row["total_amount"])))

    def complete_order(self) -> None:
        selected=self.orders_tree.selection()
        if not selected:messagebox.showinfo("Orders","Select an order first.");return
        try:self.db.complete_order(int(selected[0]));self.load_orders()
        except Exception as error:self._error(error)

    def menu(self) -> None:
        self.current_page=self.menu;self._clear(self.content)
        self._heading("Menu","Items are listed by database ID in ascending order.",("+  Add menu item",self.menu_dialog))
        body=self._body();tools=tk.Frame(body,bg=self.colors["BG"]);tools.pack(fill="x",pady=(0,8))
        ttk.Button(tools,text="Edit selected",command=self.edit_menu_item).pack(side="left")
        ttk.Button(tools,text="Toggle availability",command=self.toggle_menu_item).pack(side="left",padx=7)
        panel=self._panel(body);panel.pack(fill="both",expand=True)
        self.menu_tree=self._tree(panel,[("id","ID",60),("name","ITEM",235),("category","CATEGORY",150),
            ("price","PRICE",110),("status","STATUS",110),("description","DESCRIPTION",280)])
        self.load_menu()

    def load_menu(self) -> None:
        try:rows=self.db.menu_items()
        except Exception as error:self._error(error);return
        self.menu_tree.delete(*self.menu_tree.get_children())
        for row in rows:self.menu_tree.insert("","end",iid=str(row["item_id"]),values=(row["item_id"],row["item_name"],row["category_name"],money(row["price"]),row["status"],row["description"] or ""))

    def menu_dialog(self, item_id: int | None = None) -> None:
        try:
            data=self.db.menu_item(item_id) if item_id else None
            categories=self.db.categories()
        except Exception as error:self._error(error);return
        if not categories:messagebox.showerror("Menu","Add menu categories to the database first.");return
        dialog=self._dialog("Edit menu item" if data else "Add menu item",480,440)
        fields=self._form_fields(dialog,[("Item name",data["item_name"] if data else ""),("Description",data["description"] if data else ""),("Price",str(data["price"]) if data else "")])
        category_map={r["category_name"]:r["category_id"] for r in categories}
        category=self._combo_field(dialog,"Category",list(category_map))
        if data:category.set(next(name for name,key in category_map.items() if key==data["category_id"]))
        def save() -> None:
            try:
                name,description,price_text=(entry.get().strip() for entry in fields);price=Decimal(price_text)
                if not name or price<0:raise ValueError("Enter an item name and a non-negative price.")
                self.db.save_menu_item(item_id,(category_map[category.get()],name,description or None,price))
                dialog.destroy();self.load_menu()
            except (InvalidOperation,ValueError) as error:messagebox.showwarning("Menu item",str(error),parent=dialog)
            except Exception as error:self._error(error)
        ttk.Button(dialog,text="Save item",style="Accent.TButton",command=save).pack(fill="x",padx=22,pady=18)

    def edit_menu_item(self) -> None:
        selected=self.menu_tree.selection()
        if selected:self.menu_dialog(int(selected[0]))
        else:messagebox.showinfo("Menu","Select a menu item first.")

    def toggle_menu_item(self) -> None:
        selected=self.menu_tree.selection()
        if not selected:messagebox.showinfo("Menu","Select a menu item first.");return
        row=self.menu_tree.item(selected[0],"values")
        try:self.db.set_menu_status(int(selected[0]),"Unavailable" if row[4]=="Available" else "Available");self.load_menu()
        except Exception as error:self._error(error)

    def customers(self) -> None:
        self.current_page=self.customers;self._clear(self.content)
        self._heading("Customers","Guest details for returning visits.",("+  Add customer",self.customer_dialog))
        body=self._body();panel=self._panel(body);panel.pack(fill="both",expand=True)
        self.customer_tree=self._tree(panel,[("id","ID",70),("name","CUSTOMER",250),("phone","PHONE",200)])
        ttk.Button(body,text="Edit selected",command=self.edit_customer).pack(anchor="w",pady=(8,0));self.load_customers()

    def load_customers(self) -> None:
        try:rows=self.db.customers()
        except Exception as error:self._error(error);return
        self.customer_tree.delete(*self.customer_tree.get_children())
        for row in rows:self.customer_tree.insert("","end",iid=str(row["customer_id"]),values=(row["customer_id"],f"{row['first_name']} {row['last_name']}",row["phone"] or "-"))

    def customer_dialog(self, customer_id: int | None = None) -> None:
        try:data=self.db.customer(customer_id) if customer_id else None
        except Exception as error:self._error(error);return
        dialog=self._dialog("Edit customer" if data else "Add customer",460,400)
        fields=self._form_fields(dialog,[("First name",data["first_name"] if data else ""),("Last name",data["last_name"] if data else ""),("Phone",data["phone"] if data else "")])
        def save() -> None:
            first,last,phone=(entry.get().strip() for entry in fields)
            if not first or not last:messagebox.showwarning("Customer","First and last name are required.",parent=dialog);return
            try:self.db.save_customer(customer_id,(first,last,phone or None));dialog.destroy();self.load_customers()
            except Exception as error:self._error(error)
        ttk.Button(dialog,text="Save customer",style="Accent.TButton",command=save).pack(fill="x",padx=22,pady=18)

    def edit_customer(self) -> None:
        selected=self.customer_tree.selection()
        if selected:self.customer_dialog(int(selected[0]))
        else:messagebox.showinfo("Customers","Select a customer first.")

    def tables(self) -> None:
        self.current_page=self.tables;self._clear(self.content)
        self._heading("Dining tables","Edit table numbers and capacity; availability follows active orders.",("+  Add table",self.table_dialog))
        body=self._body();tools=tk.Frame(body,bg=self.colors["BG"]);tools.pack(fill="x",pady=(0,8))
        ttk.Button(tools,text="Edit selected",command=self.edit_table).pack(side="left")
        panel=self._panel(body);panel.pack(fill="both",expand=True)
        self.table_tree=self._tree(panel,[("number","TABLE",150),("capacity","CAPACITY",120),("status","STATUS",120),("open","OPEN ORDERS",120)])
        self.load_tables()

    def load_tables(self) -> None:
        try:rows=self.db.tables()
        except Exception as error:self._error(error);return
        self.table_tree.delete(*self.table_tree.get_children())
        for row in rows:self.table_tree.insert("","end",iid=str(row["table_id"]),values=(row["table_number"],row["capacity"] or "-",row["status"],row["open_orders"]))

    def table_dialog(self, table_id: int | None = None) -> None:
        row=None
        if table_id:
            try:row=self.db.table(table_id)
            except Exception as error:self._error(error);return
        dialog=self._dialog("Edit table" if row else "Add table",450,350)
        fields=self._form_fields(dialog,[("Table number",row["table_number"] if row else ""),("Capacity",str(row["capacity"] or "") if row else "")])
        def save() -> None:
            number,capacity_text=(entry.get().strip() for entry in fields)
            if not number:messagebox.showwarning("Table","Table number is required.",parent=dialog);return
            try:
                capacity=int(capacity_text) if capacity_text else None
                if capacity is not None and capacity<1:raise ValueError("Capacity must be at least one.")
                self.db.save_table(table_id,number,capacity);dialog.destroy();self.load_tables()
            except ValueError as error:messagebox.showwarning("Table",str(error),parent=dialog)
            except Exception as error:self._error(error)
        ttk.Button(dialog,text="Save table",style="Accent.TButton",command=save).pack(fill="x",padx=22,pady=18)

    def edit_table(self) -> None:
        selected=self.table_tree.selection()
        if selected:self.table_dialog(int(selected[0]))
        else:messagebox.showinfo("Tables","Select a table first.")

    def employees(self) -> None:
        self.current_page=self.employees;self._clear(self.content)
        self._heading("Employees","Edit staff records or archive former employees.",("+  Add employee",self.employee_dialog))
        body=self._body();tools=tk.Frame(body,bg=self.colors["BG"]);tools.pack(fill="x",pady=(0,8))
        ttk.Button(tools,text="Edit selected",command=self.edit_employee).pack(side="left")
        ttk.Button(tools,text="Archive / restore",command=self.toggle_employee_status).pack(side="left",padx=7)
        self.employee_filter=ttk.Combobox(tools,state="readonly",values=("All employees","Active","Archived"),width=17)
        self.employee_filter.set("All employees");self.employee_filter.pack(side="right")
        self.employee_filter.bind("<<ComboboxSelected>>",lambda _event:self.load_employees())
        panel=self._panel(body);panel.pack(fill="both",expand=True)
        self.employee_tree=self._tree(panel,[("id","ID",50),("name","EMPLOYEE",180),("position","POSITION",135),
            ("phone","PHONE",130),("hired","DATE HIRED",110),("status","STATUS",90)])
        self.load_employees()

    def load_employees(self) -> None:
        try:rows=self.db.employees(self.employee_filter.get()!="Active")
        except Exception as error:self._error(error);return
        selected=self.employee_filter.get()
        if selected=="Archived":rows=[r for r in rows if r["status"]=="Inactive"]
        self.employee_tree.delete(*self.employee_tree.get_children())
        for row in rows:self.employee_tree.insert("","end",iid=str(row["employee_id"]),values=(row["employee_id"],f"{row['first_name']} {row['last_name']}",row["position"],row["phone"] or "-",row["date_hired"] or "-",row["status"]))

    def employee_dialog(self, employee_id: int | None = None) -> None:
        try:row=self.db.employee(employee_id) if employee_id else None
        except Exception as error:self._error(error);return
        dialog=self._dialog("Edit employee" if row else "Add employee",490,620)
        fields=self._form_fields(dialog,[("First name",row["first_name"] if row else ""),("Last name",row["last_name"] if row else ""),
            ("Phone",row["phone"] if row else ""),("Address",row["address"] if row else ""),("Position",row["position"] if row else "Staff"),
            ("Date hired (YYYY-MM-DD)",str(row["date_hired"]) if row and row["date_hired"] else date.today().isoformat())])
        def save() -> None:
            first,last,phone,address,position,hired=(entry.get().strip() for entry in fields)
            if not first or not last or not position:messagebox.showwarning("Employee","Name and position are required.",parent=dialog);return
            try:self.db.save_employee(employee_id,(first,last,phone or None,address or None,position,hired or None));dialog.destroy();self.load_employees()
            except Exception as error:self._error(error)
        ttk.Button(dialog,text="Save employee",style="Accent.TButton",command=save).pack(fill="x",padx=22,pady=18)

    def edit_employee(self) -> None:
        selected=self.employee_tree.selection()
        if selected:self.employee_dialog(int(selected[0]))
        else:messagebox.showinfo("Employees","Select an employee first.")

    def toggle_employee_status(self) -> None:
        selected=self.employee_tree.selection()
        if not selected:messagebox.showinfo("Employees","Select an employee first.");return
        values=self.employee_tree.item(selected[0],"values"); employee_id=int(selected[0]);current=values[5]
        target="Inactive" if current=="Active" else "Active"
        action="archive" if target=="Inactive" else "restore"
        if not messagebox.askyesno("Employee",f"{action.title()} {values[1]}? Historical orders and attendance will remain."):return
        try:self.db.set_employee_status(employee_id,target);self.load_employees()
        except Exception as error:self._error(error)

    def attendance(self) -> None:
        self.current_page=self.attendance;self._clear(self.content)
        self._heading("Attendance",f"Staff register · {date.today():%B %d, %Y}",("+  Record attendance",self.attendance_dialog))
        body=self._body();tools=tk.Frame(body,bg=self.colors["BG"]);tools.pack(fill="x",pady=(0,8))
        ttk.Button(tools,text="Edit selected",command=self.edit_attendance).pack(side="left")
        panel=self._panel(body);panel.pack(fill="both",expand=True)
        self.attendance_tree=self._tree(panel,[("employee","EMPLOYEE",200),("date","DATE",110),("in","TIME IN",110),("out","TIME OUT",110),("status","STATUS",100)])
        self.load_attendance()

    def load_attendance(self) -> None:
        try:rows=self.db.attendance()
        except Exception as error:self._error(error);return
        self.attendance_tree.delete(*self.attendance_tree.get_children())
        for row in rows:self.attendance_tree.insert("","end",iid=str(row["attendance_id"]),values=(row["employee"],row["attendance_date"],row["time_in"] or "-",row["time_out"] or "-",row["status"]))

    @staticmethod
    def time_options() -> list[str]:
        return [datetime.strptime(f"{hour:02d}:{minute:02d}","%H:%M").strftime("%I:%M %p")
                for total_minutes in range(480,1201,30)
                for hour,minute in [divmod(total_minutes,60)]]

    def attendance_dialog(self, attendance_id: int | None = None) -> None:
        try:
            record=self.db.attendance_record(attendance_id) if attendance_id else None
            employees=self.db.employees()
        except Exception as error:self._error(error);return
        employee_map={f"{r['first_name']} {r['last_name']} · #{r['employee_id']}":r["employee_id"] for r in employees}
        if not employee_map:messagebox.showinfo("Attendance","Add an employee first.");return
        dialog=self._dialog("Edit attendance" if record else "Record attendance",470,470)
        employee=self._combo_field(dialog,"Employee",list(employee_map))
        if record:
            employee.set(next((name for name,value in employee_map.items() if value==record["employee_id"]),""))
        no_time="No time"
        times=[no_time,*self.time_options()]
        time_in=self._combo_field(dialog,"Time in (8:00 AM to 8:00 PM)",times)
        time_out=self._combo_field(dialog,"Time out (8:00 AM to 8:00 PM)",times)
        if record:
            time_in.set(record["time_in"] or no_time);time_out.set(record["time_out"] or no_time)
        else:time_in.set("09:00 AM");time_out.set(no_time)
        status=self._combo_field(dialog,"Status",["Present","Late","Absent"])
        status.set(record["status"] if record else "Present")
        def to_sql(value: str) -> str | None:
            return None if value==no_time else datetime.strptime(value,"%I:%M %p").strftime("%H:%M:%S")
        def save() -> None:
            try:
                self.db.save_attendance(attendance_id,employee_map[employee.get()],to_sql(time_in.get()),to_sql(time_out.get()),status.get())
                dialog.destroy();self.load_attendance()
            except Exception as error:self._error(error)
        ttk.Button(dialog,text="Save attendance",style="Accent.TButton",command=save).pack(fill="x",padx=22,pady=18)

    def edit_attendance(self) -> None:
        selected=self.attendance_tree.selection()
        if selected:self.attendance_dialog(int(selected[0]))
        else:messagebox.showinfo("Attendance","Select an attendance record first.")

    def expenses(self) -> None:
        self.current_page=self.expenses;self._clear(self.content)
        self._heading("Expenses","Track operating costs recorded by the team.",("+  Record expense",self.expense_dialog))
        body=self._body()
        try:total,rows=self.db.expenses()
        except Exception as error:self._error(error);return
        tk.Label(body,text=f"MONTH-TO-DATE EXPENSES   {money(total)}",bg=self.colors["BG"],fg=self.colors["ACCENT"],font=(FONT,10,"bold")).pack(anchor="w",pady=(0,10))
        panel=self._panel(body);panel.pack(fill="both",expand=True)
        tree=self._tree(panel,[("id","ID",55),("date","DATE",155),("name","EXPENSE",170),("description","DESCRIPTION",245),("employee","RECORDED BY",155),("amount","AMOUNT",110)])
        for row in rows:tree.insert("","end",values=(row["expense_id"],row["expense_date"],row["expense_name"],row["description"] or "-",row["employee"],money(row["amount"])) )

    def expense_dialog(self) -> None:
        dialog=self._dialog("Record expense",460,420)
        choices=["Food supplies","Utilities","Rent","Salaries","Transportation","Maintenance","Equipment","Other"]
        name=self._combo_field(dialog,"Expense name",choices,state="normal")
        name.set(choices[0])
        description=self._entry_field(dialog,"Description","")
        amount=self._entry_field(dialog,"Amount","")
        def save() -> None:
            expense_name=name.get().strip();detail=description.get().strip()
            try:
                value=Decimal(amount.get().strip())
                if not expense_name or value<=0:raise ValueError("Enter an expense name and an amount greater than zero.")
                self.db.add_expense(self.user.get("employee_id"),expense_name,detail or None,value)
                dialog.destroy();self.navigate(self.expenses)
            except (InvalidOperation,ValueError) as error:messagebox.showwarning("Expense",str(error),parent=dialog)
            except Exception as error:self._error(error)
        ttk.Button(dialog,text="Save expense",style="Accent.TButton",command=save).pack(fill="x",padx=22,pady=18)

    def _dialog(self,title: str,width: int=450,height: int=580) -> tk.Toplevel:
        dialog=tk.Toplevel(self.root);dialog.title(title);dialog.configure(bg=self.colors["PANEL"])
        dialog.transient(self.root);dialog.grab_set();dialog.resizable(False,False)
        dialog.geometry(f"{width}x{height}")
        tk.Label(dialog,text=title,bg=self.colors["PANEL"],fg=self.colors["INK"],font=(FONT,16,"bold")).pack(anchor="w",padx=22,pady=(18,8))
        return dialog

    def _form_fields(self,parent: tk.Widget,labels: list[tuple[str,str]]) -> list[ttk.Entry]:
        entries=[]
        for label,value in labels:
            tk.Label(parent,text=label,bg=self.colors["PANEL"],fg=self.colors["MUTED"],font=(FONT,8,"bold")).pack(anchor="w",padx=22,pady=(8,3))
            entry=ttk.Entry(parent);entry.pack(fill="x",padx=22);entry.insert(0,value or "");entries.append(entry)
        return entries

    def _entry_field(self,parent: tk.Widget,label: str,value: str) -> ttk.Entry:
        tk.Label(parent,text=label,bg=self.colors["PANEL"],fg=self.colors["MUTED"],font=(FONT,8,"bold")).pack(anchor="w",padx=22,pady=(8,3))
        entry=ttk.Entry(parent);entry.pack(fill="x",padx=22);entry.insert(0,value);return entry

    def _combo_field(self,parent: tk.Widget,label: str,values: list[str],state: str="readonly") -> ttk.Combobox:
        tk.Label(parent,text=label,bg=self.colors["PANEL"],fg=self.colors["MUTED"],font=(FONT,8,"bold")).pack(anchor="w",padx=22,pady=(8,3))
        combo=ttk.Combobox(parent,state=state,values=values);combo.pack(fill="x",padx=22)
        if values:combo.set(values[0])
        return combo