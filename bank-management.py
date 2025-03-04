import tkinter as tk
from tkinter import messagebox, simpledialog
import bcrypt
import sqlite3
import matplotlib.pyplot as plt

# Database Setup
conn = sqlite3.connect("bank_system.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    name TEXT PRIMARY KEY,
    pin TEXT,
    balance REAL DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    user TEXT,
    category TEXT,
    amount REAL,
    FOREIGN KEY(user) REFERENCES users(name)
)
""")
conn.commit()

class BankSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Secure Bank System")
        self.master.geometry("400x400")
        
        self.create_widgets()
    
    def create_widgets(self):
        self.name_label = tk.Label(self.master, text="Name:")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.master)
        self.name_entry.pack()
        
        self.pin_label = tk.Label(self.master, text="PIN:")
        self.pin_label.pack()
        self.pin_entry = tk.Entry(self.master, show="*")
        self.pin_entry.pack()
        
        self.register_btn = tk.Button(self.master, text="Register", command=self.register)
        self.register_btn.pack()
        
        self.login_btn = tk.Button(self.master, text="Login", command=self.login)
        self.login_btn.pack()
    
    def register(self):
        name = self.name_entry.get()
        pin = self.pin_entry.get().encode('utf-8')
        hashed_pin = bcrypt.hashpw(pin, bcrypt.gensalt())
        
        try:
            cursor.execute("INSERT INTO users (name, pin) VALUES (?, ?)", (name, hashed_pin))
            conn.commit()
            messagebox.showinfo("Success", "Account Created Successfully")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "User already exists")
    
    def login(self):
        name = self.name_entry.get()
        pin = self.pin_entry.get().encode('utf-8')
        cursor.execute("SELECT pin FROM users WHERE name = ?", (name,))
        record = cursor.fetchone()
        
        if record and bcrypt.checkpw(pin, record[0]):
            messagebox.showinfo("Success", "Login Successful")
            self.open_dashboard(name)
        else:
            messagebox.showerror("Error", "Invalid Credentials")
    
    def open_dashboard(self, name):
        self.dashboard = tk.Toplevel(self.master)
        self.dashboard.title("Dashboard")
        
        tk.Label(self.dashboard, text=f"Welcome, {name}").pack()
        tk.Button(self.dashboard, text="Deposit", command=lambda: self.deposit(name)).pack()
        tk.Button(self.dashboard, text="Withdraw", command=lambda: self.withdraw(name)).pack()
        tk.Button(self.dashboard, text="Track Expenses", command=lambda: self.track_expenses(name)).pack()
        tk.Button(self.dashboard, text="View Budget", command=lambda: self.view_budget(name)).pack()
        tk.Button(self.dashboard, text="Set Monthly Budget", command=lambda: self.set_budget(name)).pack()
    
    def deposit(self, name):
        amount = float(simpledialog.askstring("Deposit", "Enter amount:"))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE name = ?", (amount, name))
        conn.commit()
        messagebox.showinfo("Success", f"Deposited {amount}")
    
    def withdraw(self, name):
        amount = float(simpledialog.askstring("Withdraw", "Enter amount:"))
        cursor.execute("SELECT balance FROM users WHERE name = ?", (name,))
        balance = cursor.fetchone()[0]
        
        if amount > balance:
            messagebox.showerror("Error", "Insufficient Funds")
        else:
            cursor.execute("UPDATE users SET balance = balance - ? WHERE name = ?", (amount, name))
            conn.commit()
            messagebox.showinfo("Success", f"Withdrawn {amount}")
    
    def track_expenses(self, name):
        category = simpledialog.askstring("Expense Tracking", "Enter Category (Food, Travel, etc.):")
        amount = float(simpledialog.askstring("Expense Tracking", "Enter Amount:"))
        
        cursor.execute("INSERT INTO expenses (user, category, amount) VALUES (?, ?, ?)", (name, category, amount))
        conn.commit()
        messagebox.showinfo("Success", "Expense Recorded")
    
    def view_budget(self, name):
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user = ? GROUP BY category", (name,))
        records = cursor.fetchall()
        
        if records:
            categories, amounts = zip(*records)
            plt.figure(figsize=(5, 5))
            plt.pie(amounts, labels=categories, autopct="%1.1f%%")
            plt.title("Expense Breakdown")
            plt.show()
        else:
            messagebox.showinfo("Budget", "No expenses recorded yet.")
    
    def set_budget(self, name):
        budget = float(simpledialog.askstring("Set Budget", "Enter your monthly budget:"))
        messagebox.showinfo("Budget Set", f"Monthly budget set to {budget}")
    
if __name__ == '__main__':
    root = tk.Tk()
    app = BankSystem(root)
    root.mainloop()
