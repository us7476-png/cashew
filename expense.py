import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

FILE_NAME = "expenses.csv"

# --- Ensure CSV file exists with headers ---
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Category", "Amount", "Description"])

# --- Functions ---
def add_expense():
    category = category_var.get()
    amount = amount_var.get()
    description = desc_var.get()

    if not amount:
        messagebox.showerror("Error", "Amount is required", parent=root)
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Enter a valid number for amount", parent=root)
        return

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(FILE_NAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, amount, description])

    messagebox.showinfo("Success", "Expense added successfully!", parent=root)
    amount_var.set("")
    desc_var.set("")
    view_expenses()

def view_expenses(filter_func=None):
    for row in tree.get_children():
        tree.delete(row)

    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

        if len(rows) <= 1:
            return

        for i, row in enumerate(rows[1:]):  # skip header
            if filter_func is None or filter_func(row):
                tree.insert("", "end", values=row, tags=('oddrow',) if i % 2 else ('evenrow',))

def total_by_category():
    totals = {}
    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

        if len(rows) <= 1:
            messagebox.showinfo("Info", "No expenses recorded yet.", parent=root)
            return

        for row in rows[1:]:
            category, amount = row[1], float(row[2])
            totals[category] = totals.get(category, 0) + amount

    msg = "\n".join([f"{cat}: ₹{amt:,.2f}" for cat, amt in totals.items()])
    messagebox.showinfo("Total by Category", msg, parent=root)

def search_expenses():
    query = search_var.get().lower()
    if not query:
        view_expenses()
        return

    def filter_func(row):
        return (query in row[0].lower() or
                query in row[1].lower() or
                query in row[3].lower())

    view_expenses(filter_func)

def monthly_total():
    month = month_var.get().strip()
    if not month or len(month) != 7 or month.count('-') != 1:
        messagebox.showerror("Error", "Enter month in valid YYYY-MM format (e.g., 2025-10)", parent=root)
        return

    total = 0
    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

        if len(rows) <= 1:
            messagebox.showinfo("Info", "No expenses recorded yet.", parent=root)
            return

        for row in rows[1:]:
            date_str, _, amt, _ = row
            if date_str.startswith(month):
                total += float(amt)

    messagebox.showinfo("Monthly Total", f"Total expense for {month}: ₹{total:,.2f}", parent=root)

# --- GUI Setup ---
root = tk.Tk()
root.title("💰 Aesthetic Expense Tracker")
root.state('zoomed')  # Open maximized
root.configure(bg="#E6E6FA")  # Light Lavender Purple background

# --- Styling ---
style = ttk.Style(root)
style.theme_use('clam')

# Colors
PRIMARY_COLOR = "#8A2BE2"      # Purple for buttons
BG_COLOR = "#E6E6FA"           # Light lavender background
TEXT_COLOR = "#4B0082"         # Deep indigo for text

style.configure('.', font=('Segoe UI', 10))
style.configure('TButton', font=('Segoe UI', 10, 'bold'),
                background=PRIMARY_COLOR, foreground="white")
style.map('TButton', background=[('active', '#6A0DAD')])
style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR)
style.configure('TFrame', background=BG_COLOR)
style.configure('Treeview', background="white", fieldbackground="white", font=('Segoe UI', 10))
style.configure("Treeview.Heading", font=('Segoe UI', 11, 'bold'), background=PRIMARY_COLOR, foreground="white")

# --- Variables ---
category_var = tk.StringVar(value="Food")
amount_var = tk.StringVar()
desc_var = tk.StringVar()
month_var = tk.StringVar()
search_var = tk.StringVar()

# --- Main Frame (responsive layout) ---
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main_frame = ttk.Frame(root, padding=10)
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.columnconfigure((0, 1, 2), weight=1)
main_frame.rowconfigure(1, weight=1)

# --- Input Section ---
input_frame = ttk.LabelFrame(main_frame, text="Add Expense", padding=10)
input_frame.grid(row=0, column=0, sticky='nwe', padx=10, pady=10)
input_frame.columnconfigure(1, weight=1)

ttk.Label(input_frame, text="Category:").grid(row=0, column=0, sticky='w')
ttk.Combobox(input_frame, textvariable=category_var,
             values=["Food", "Travel", "Shopping", "Bills", "Health", "Education", "Other"]).grid(row=0, column=1, padx=5, pady=5, sticky='we')

ttk.Label(input_frame, text="Amount (₹):").grid(row=1, column=0, sticky='w')
ttk.Entry(input_frame, textvariable=amount_var).grid(row=1, column=1, padx=5, pady=5, sticky='we')

ttk.Label(input_frame, text="Description:").grid(row=2, column=0, sticky='w')
ttk.Entry(input_frame, textvariable=desc_var).grid(row=2, column=1, padx=5, pady=5, sticky='we')

ttk.Button(input_frame, text="➕ Add Expense", command=add_expense).grid(row=3, column=0, columnspan=2, pady=10, sticky='we')

# --- Reports Section ---
analysis_frame = ttk.LabelFrame(main_frame, text="Reports", padding=10)
analysis_frame.grid(row=0, column=1, sticky='nwe', padx=10, pady=10)
analysis_frame.columnconfigure(0, weight=1)

ttk.Button(analysis_frame, text="📊 Totals by Category", command=total_by_category).grid(row=0, column=0, pady=5, sticky='we')
ttk.Label(analysis_frame, text="Month (YYYY-MM):").grid(row=1, column=0, sticky='w', pady=(10, 0))
ttk.Entry(analysis_frame, textvariable=month_var).grid(row=2, column=0, pady=5, sticky='we')
ttk.Button(analysis_frame, text="💹 Monthly Total", command=monthly_total).grid(row=3, column=0, pady=5, sticky='we')

# --- Search Section ---
search_frame = ttk.LabelFrame(main_frame, text="Search", padding=10)
search_frame.grid(row=0, column=2, sticky='nwe', padx=10, pady=10)
search_frame.columnconfigure(0, weight=1)

ttk.Entry(search_frame, textvariable=search_var).grid(row=0, column=0, padx=5, pady=5, sticky='we')
ttk.Button(search_frame, text="🔍 Search", command=search_expenses).grid(row=1, column=0, pady=5, sticky='we')
ttk.Button(search_frame, text="🔄 Clear / Refresh", command=lambda: [search_var.set(""), view_expenses()]).grid(row=2, column=0, pady=5, sticky='we')

# --- Expense Table ---
table_frame = ttk.Frame(main_frame, padding=10)
table_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)
table_frame.columnconfigure(0, weight=1)
table_frame.rowconfigure(0, weight=1)

cols = ("Date", "Category", "Amount", "Description")
tree = ttk.Treeview(table_frame, columns=cols, show="headings")

for col in cols:
    tree.heading(col, text=col)
    tree.column(col, anchor='center', stretch=True)

tree.grid(row=0, column=0, sticky='nsew')

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky='ns')

# --- Load Data ---
view_expenses()

root.mainloop()
