import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import bcrypt
import mysql.connector

# Database Setup
conn = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword",
    database="bank_system"
)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    name VARCHAR(255) PRIMARY KEY,
    pin VARCHAR(255),
    balance FLOAT DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    user VARCHAR(255),
    category VARCHAR(255),
    amount FLOAT,
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
            cursor.execute("INSERT INTO users (name, pin) VALUES (%s, %s)", (name, hashed_pin))
            conn.commit()
            messagebox.showinfo("Success", "Account Created Successfully")
        except mysql.connector.errors.IntegrityError:
            messagebox.showerror("Error", "User already exists")
    
    def login(self):
        name = self.name_entry.get()
        pin = self.pin_entry.get().encode('utf-8')
        cursor.execute("SELECT pin FROM users WHERE name = %s", (name,))
        record = cursor.fetchone()
        
        if record and bcrypt.checkpw(pin, record[0].encode('utf-8')):
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
        tk.Button(self.dashboard, text="View Expenses", command=lambda: self.view_expenses(name)).pack()
        tk.Button(self.dashboard, text="Set Monthly Budget", command=lambda: self.set_budget(name)).pack()
    
    def deposit(self, name):
        try:
            amount = float(simpledialog.askstring("Deposit", "Enter amount:"))
            cursor.execute("UPDATE users SET balance = balance + %s WHERE name = %s", (amount, name))
            conn.commit()
            messagebox.showinfo("Success", f"Deposited {amount}")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered")
    
    def withdraw(self, name):
        try:
            amount = float(simpledialog.askstring("Withdraw", "Enter amount:"))
            cursor.execute("SELECT balance FROM users WHERE name = %s", (name,))
            balance = cursor.fetchone()[0]
            
            if amount > balance:
                messagebox.showerror("Error", "Insufficient Funds")
            else:
                cursor.execute("UPDATE users SET balance = balance - %s WHERE name = %s", (amount, name))
                conn.commit()
                messagebox.showinfo("Success", f"Withdrawn {amount}")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered")
    
    def track_expenses(self, name):
        try:
            category = simpledialog.askstring("Expense Tracking", "Enter Category (Food, Travel, etc.):")
            amount = float(simpledialog.askstring("Expense Tracking", "Enter Amount:"))
            
            cursor.execute("INSERT INTO expenses (user, category, amount) VALUES (%s, %s, %s)", (name, category, amount))
            conn.commit()
            messagebox.showinfo("Success", "Expense Recorded")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered")
    
    def view_expenses(self, name):
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user = %s GROUP BY category", (name,))
        records = cursor.fetchall()
        
        if records:
            self.expenses_window = tk.Toplevel(self.master)
            self.expenses_window.title("Expenses")
            self.expenses_window.geometry("300x250")

            tree = ttk.Treeview(self.expenses_window, columns=("Category", "Amount"), show='headings')
            tree.heading("Category", text="Category")
            tree.heading("Amount", text="Total Amount")
            tree.pack(fill=tk.BOTH, expand=True)

            for record in records:
                tree.insert("", tk.END, values=record)
        else:
            messagebox.showinfo("Expenses", "No expenses recorded yet.")
    
    def set_budget(self, name):
        try:
            budget = float(simpledialog.askstring("Set Budget", "Enter your monthly budget:"))
            messagebox.showinfo("Budget Set", f"Monthly budget set to {budget}")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered")
    
if __name__ == '__main__':
    root = tk.Tk()
    app = BankSystem(root)
    root.mainloop()
