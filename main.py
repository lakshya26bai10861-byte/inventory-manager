"""
main.py
--------
The main window. Run with: python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from database import create_tables
from auth import register_user, login_user
from products import (
    create_product, list_products, remove_product,
    sell_product, list_sales, CATEGORIES,
)
from analytics import (
    get_stock_summary, get_low_stock_items,
    get_sales_summary, get_category_breakdown,
)


BG         = "#f4f6fb"
PRIMARY    = "#3949ab"
PRIMARY_D  = "#283593"
TEXT       = "#1f2937"
MUTED      = "#6b7280"
DANGER     = "#dc2626"
SUCCESS    = "#16a34a"
WARNING    = "#f59e0b"


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Manager")
        self.root.geometry("1000x650")
        self.root.configure(bg=BG)

        self.current_user = None
        self.show_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ------- LOGIN SCREEN -------
    def show_login_screen(self):
        self.clear_window()

        tk.Label(self.root, text="Inventory Manager",
                 font=("Segoe UI", 26, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(70, 5))

        tk.Label(self.root, text="Track stock. Sell smart.",
                 font=("Segoe UI", 12), bg=BG, fg=MUTED).pack(pady=(0, 30))

        card = tk.Frame(self.root, bg="white", padx=40, pady=30)
        card.pack()

        tk.Label(card, text="Username", font=("Segoe UI", 10, "bold"),
                 bg="white", fg=TEXT).pack(anchor="w")
        self.username_entry = tk.Entry(card, width=30, font=("Segoe UI", 11))
        self.username_entry.pack(pady=(5, 15), ipady=6)

        tk.Label(card, text="Password", font=("Segoe UI", 10, "bold"),
                 bg="white", fg=TEXT).pack(anchor="w")
        self.password_entry = tk.Entry(card, width=30,
                                       font=("Segoe UI", 11), show="*")
        self.password_entry.pack(pady=(5, 20), ipady=6)

        tk.Button(card, text="Login", bg=PRIMARY, fg="white",
                  font=("Segoe UI", 11, "bold"), width=25,
                  relief="flat", cursor="hand2",
                  command=self.handle_login).pack(pady=5, ipady=6)

        tk.Button(card, text="Create New Account",
                  bg="white", fg=PRIMARY,
                  font=("Segoe UI", 10, "bold"), width=25,
                  relief="flat", cursor="hand2",
                  command=self.handle_register).pack(pady=5, ipady=4)

    def handle_login(self):
        user, msg = login_user(self.username_entry.get().strip(),
                                self.password_entry.get().strip())
        if user:
            self.current_user = user
            self.show_dashboard()
        else:
            messagebox.showerror("Login failed", msg)

    def handle_register(self):
        ok, msg = register_user(self.username_entry.get().strip(),
                                 self.password_entry.get().strip())
        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Oops", msg)

    # ------- DASHBOARD -------
    def show_dashboard(self):
        self.clear_window()

        topbar = tk.Frame(self.root, bg=PRIMARY, height=60)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text=f"Hi, {self.current_user['username']}",
                 font=("Segoe UI", 14, "bold"),
                 bg=PRIMARY, fg="white").pack(side="left", padx=20)

        tk.Button(topbar, text="Logout", bg=PRIMARY_D, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.logout
                  ).pack(side="right", padx=20, pady=12, ipadx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_products = tk.Frame(self.notebook, bg=BG)
        self.tab_sales = tk.Frame(self.notebook, bg=BG)
        self.tab_analytics = tk.Frame(self.notebook, bg=BG)

        self.notebook.add(self.tab_products, text="  Products  ")
        self.notebook.add(self.tab_sales, text="  Sell  ")
        self.notebook.add(self.tab_analytics, text="  Analytics  ")

        self._build_products_tab()
        self._build_sales_tab()
        self._build_analytics_tab()

    # ------- PRODUCTS TAB -------
    def _build_products_tab(self):
        add_frame = tk.LabelFrame(self.tab_products, text=" Add Product ",
                                   font=("Segoe UI", 11, "bold"),
                                   bg=BG, fg=TEXT, padx=15, pady=10)
        add_frame.pack(fill="x", padx=10, pady=10)

        row = tk.Frame(add_frame, bg=BG)
        row.pack(fill="x")

        self.name_entry    = self._entry(row, "Name", 0)
        self.price_entry   = self._entry(row, "Price", 1)
        self.qty_entry     = self._entry(row, "Quantity", 2)
        self.reorder_entry = self._entry(row, "Reorder Level", 3)

        tk.Label(row, text="Category", font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=TEXT).grid(row=0, column=8, padx=5, sticky="w")
        self.cat_var = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(row, textvariable=self.cat_var, values=CATEGORIES,
                     width=14, state="readonly").grid(row=1, column=8, padx=5)

        tk.Button(row, text="Add", bg=SUCCESS, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.handle_add_product
                  ).grid(row=1, column=9, padx=10, ipadx=15)

        list_frame = tk.LabelFrame(self.tab_products, text=" Products in Stock ",
                                    font=("Segoe UI", 11, "bold"),
                                    bg=BG, fg=TEXT, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("ID", "Name", "Category", "Price", "Qty", "Status")
        self.product_table = ttk.Treeview(list_frame, columns=cols,
                                           show="headings", height=8)
        for c in cols:
            self.product_table.heading(c, text=c)
            self.product_table.column(c, width=120, anchor="center")
        self.product_table.column("ID", width=40)
        self.product_table.column("Name", width=180)
        self.product_table.pack(fill="both", expand=True)

        btn_row = tk.Frame(list_frame, bg=BG)
        btn_row.pack(pady=8)

        tk.Button(btn_row, text="Delete Selected", bg=DANGER, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.handle_delete_product
                  ).pack(side="left", padx=5, ipadx=10)

        tk.Button(btn_row, text="Refresh", bg=PRIMARY_D, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.refresh_products
                  ).pack(side="left", padx=5, ipadx=10)

        self.refresh_products()

    def _entry(self, parent, label, col):
        tk.Label(parent, text=label, font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=TEXT).grid(row=0, column=col, padx=5, sticky="w")
        e = tk.Entry(parent, width=15, font=("Segoe UI", 10))
        e.grid(row=1, column=col, padx=5)
        return e

    def handle_add_product(self):
        ok, msg = create_product(
            self.name_entry.get(), self.cat_var.get(),
            self.price_entry.get(), self.qty_entry.get(),
            self.reorder_entry.get() or "5",
        )
        if ok:
            messagebox.showinfo("Done", msg)
            for e in [self.name_entry, self.price_entry,
                      self.qty_entry, self.reorder_entry]:
                e.delete(0, tk.END)
            self.refresh_products()
            self.refresh_product_dropdown()
        else:
            messagebox.showerror("Error", msg)

    def refresh_products(self):
        for row in self.product_table.get_children():
            self.product_table.delete(row)

        for p in list_products():
            if p["quantity"] == 0:
                status = "Out"
            elif p["quantity"] <= p["reorder_level"]:
                status = "Low"
            else:
                status = "OK"

            self.product_table.insert("", "end", values=(
                p["id"], p["name"], p["category"],
                f"Rs.{p['price']:.2f}", p["quantity"], status
            ))

    def handle_delete_product(self):
        sel = self.product_table.selection()
        if not sel:
            messagebox.showwarning("Nothing selected", "Click a product first.")
            return
        if messagebox.askyesno("Confirm", "Delete this product?"):
            pid = self.product_table.item(sel[0])["values"][0]
            remove_product(pid)
            self.refresh_products()
            self.refresh_product_dropdown()

    # ------- SALES TAB -------
    def _build_sales_tab(self):
        sell_frame = tk.LabelFrame(self.tab_sales, text=" Record a Sale ",
                                    font=("Segoe UI", 11, "bold"),
                                    bg=BG, fg=TEXT, padx=15, pady=10)
        sell_frame.pack(fill="x", padx=10, pady=10)

        row = tk.Frame(sell_frame, bg=BG)
        row.pack(fill="x")

        tk.Label(row, text="Product", font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=TEXT).grid(row=0, column=0, padx=5, sticky="w")
        self.product_var = tk.StringVar()
        self.product_dropdown = ttk.Combobox(row, textvariable=self.product_var,
                                              width=28, state="readonly")
        self.product_dropdown.grid(row=1, column=0, padx=5)

        tk.Label(row, text="Quantity", font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=TEXT).grid(row=0, column=1, padx=5, sticky="w")
        self.sale_qty_entry = tk.Entry(row, width=12, font=("Segoe UI", 10))
        self.sale_qty_entry.grid(row=1, column=1, padx=5)

        tk.Label(row, text="Date (YYYY-MM-DD)", font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=TEXT).grid(row=0, column=2, padx=5, sticky="w")
        self.sale_date_entry = tk.Entry(row, width=15, font=("Segoe UI", 10))
        self.sale_date_entry.insert(0, str(date.today()))
        self.sale_date_entry.grid(row=1, column=2, padx=5)

        tk.Button(row, text="Sell", bg=SUCCESS, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.handle_sell
                  ).grid(row=1, column=3, padx=10, ipadx=15)

        list_frame = tk.LabelFrame(self.tab_sales, text=" Sales History ",
                                    font=("Segoe UI", 11, "bold"),
                                    bg=BG, fg=TEXT, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("ID", "Product", "Qty", "Total", "Date")
        self.sales_table = ttk.Treeview(list_frame, columns=cols,
                                         show="headings", height=10)
        for c in cols:
            self.sales_table.heading(c, text=c)
            self.sales_table.column(c, width=130, anchor="center")
        self.sales_table.column("ID", width=40)
        self.sales_table.column("Product", width=200)
        self.sales_table.pack(fill="both", expand=True)

        self.refresh_product_dropdown()
        self.refresh_sales()

    def refresh_product_dropdown(self):
        products = list_products()
        self.product_map = {}
        display = []
        for p in products:
            label = f"{p['name']} (Rs.{p['price']:.2f}) - stock: {p['quantity']}"
            display.append(label)
            self.product_map[label] = p["id"]

        self.product_dropdown["values"] = display
        if display and not self.product_var.get():
            self.product_var.set(display[0])

    def handle_sell(self):
        label = self.product_var.get()
        if not label or label not in self.product_map:
            messagebox.showerror("Error", "Please select a product.")
            return

        pid = self.product_map[label]
        ok, msg = sell_product(pid, self.sale_qty_entry.get(),
                                self.sale_date_entry.get())
        if ok:
            messagebox.showinfo("Sale recorded", msg)
            self.sale_qty_entry.delete(0, tk.END)
            self.refresh_products()
            self.refresh_product_dropdown()
            self.refresh_sales()
        else:
            messagebox.showerror("Error", msg)

    def refresh_sales(self):
        for row in self.sales_table.get_children():
            self.sales_table.delete(row)
        for s in list_sales():
            self.sales_table.insert("", "end", values=(
                s["id"], s["product_name"], s["quantity"],
                f"Rs.{s['total_price']:.2f}", s["sale_date"]
            ))

    # ------- ANALYTICS TAB -------
    def _build_analytics_tab(self):
        tk.Button(self.tab_analytics, text="Refresh Analytics",
                  bg=PRIMARY, fg="white", font=("Segoe UI", 11, "bold"),
                  relief="flat", cursor="hand2",
                  command=self.render_analytics
                  ).pack(pady=15, ipadx=20, ipady=6)

        self.analytics_container = tk.Frame(self.tab_analytics, bg=BG)
        self.analytics_container.pack(fill="both", expand=True, padx=15, pady=5)
        self.render_analytics()

    def render_analytics(self):
        for widget in self.analytics_container.winfo_children():
            widget.destroy()

        products = list_products()
        sales = list_sales()
        stock = get_stock_summary(products)
        sales_sum = get_sales_summary(sales)
        low_stock = get_low_stock_items(products)
        breakdown = get_category_breakdown(products)

        stats_row = tk.Frame(self.analytics_container, bg=BG)
        stats_row.pack(fill="x", pady=10)

        self._stat_card(stats_row, "Total Products",
                        str(stock["total_products"]), PRIMARY)
        self._stat_card(stats_row, "Stock Value",
                        f"Rs.{stock['total_value']:.2f}", SUCCESS)
        self._stat_card(stats_row, "Low Stock",
                        str(stock["low_stock"]), WARNING)
        self._stat_card(stats_row, "Total Sales",
                        str(sales_sum["total_sales"]), PRIMARY_D)

        if low_stock:
            warn_frame = tk.LabelFrame(self.analytics_container,
                                        text=" Low Stock Alerts ",
                                        font=("Segoe UI", 11, "bold"),
                                        bg=BG, fg=DANGER, padx=10, pady=10)
            warn_frame.pack(fill="x", pady=10)
            for p in low_stock:
                tk.Label(warn_frame,
                         text=f"- {p['name']} - only {p['quantity']} left "
                              f"(reorder at {p['reorder_level']})",
                         font=("Segoe UI", 10), bg=BG, fg=DANGER,
                         anchor="w").pack(fill="x")

        cat_frame = tk.LabelFrame(self.analytics_container,
                                   text=" Stock by Category ",
                                   font=("Segoe UI", 11, "bold"),
                                   bg=BG, fg=TEXT, padx=10, pady=10)
        cat_frame.pack(fill="x", pady=10)

        if not breakdown:
            tk.Label(cat_frame, text="No products yet.",
                     bg=BG, fg=MUTED).pack(anchor="w")
        else:
            for cat, data in breakdown.items():
                tk.Label(cat_frame,
                         text=f"- {cat}: {data['count']} product(s) - "
                              f"value Rs.{data['value']:.2f}",
                         font=("Segoe UI", 10), bg=BG, fg=TEXT,
                         anchor="w").pack(fill="x")

        sales_frame = tk.LabelFrame(self.analytics_container,
                                     text=" Sales Summary ",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=BG, fg=TEXT, padx=10, pady=10)
        sales_frame.pack(fill="x", pady=10)

        for line in [
            f"Total revenue: Rs.{sales_sum['total_revenue']:.2f}",
            f"Average sale value: Rs.{sales_sum['average_sale']:.2f}",
        ]:
            tk.Label(sales_frame, text=line, font=("Segoe UI", 10),
                     bg=BG, fg=TEXT, anchor="w").pack(fill="x")

    def _stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", padx=15, pady=12,
                        highlightbackground=color, highlightthickness=2)
        card.pack(side="left", padx=6, fill="y")
        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"),
                 bg="white", fg=MUTED).pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 16, "bold"),
                 bg="white", fg=color).pack(anchor="w")

    def logout(self):
        self.current_user = None
        self.show_login_screen()


# -------- START --------
if __name__ == "__main__":
    create_tables()
    root = tk.Tk()
    InventoryApp(root)
    root.mainloop()