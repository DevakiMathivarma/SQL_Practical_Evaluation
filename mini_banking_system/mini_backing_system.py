import mysql.connector
from datetime import datetime
from tabulate import tabulate
from colorama import init, Fore, Style
from decimal import Decimal, InvalidOperation
import getpass
import re

init(autoreset=True)

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2798",  # Change this to your MySQL password
    database="mini_banks"
)
cursor = conn.cursor()

# Utility: Fetch account details
def get_account(name):
    cursor.execute("SELECT account_id, balance, overdraft_limit, pin FROM accounts WHERE name = %s", (name,))
    return cursor.fetchone()

# Verify 4-digit PIN
def verify_pin(actual_pin):
    entered_pin = getpass.getpass("Enter your 4-digit PIN: ")
    if entered_pin != actual_pin:
        print(Fore.RED + "❌ Incorrect PIN.")
        return False
    return True

# Create Account
def create_account(name):
    try:
        aadhar = input("Enter 12-digit Aadhar number: ").strip()
        if not re.fullmatch(r"\d{12}", aadhar):
            print(Fore.RED + "❌ Invalid Aadhar number.")
            return

        acc_type = input("Enter account type (Savings/Current): ").strip().capitalize()
        if acc_type not in ["Savings", "Current"]:
            print(Fore.RED + "❌ Invalid account type.")
            return

        pin = getpass.getpass("Set a 4-digit numeric PIN: ")
        if not re.fullmatch(r"\d{4}", pin):
            print(Fore.RED + "❌ PIN must be exactly 4 digits.")
            return

        overdraft_limit = Decimal('500')
        cursor.execute(
            "INSERT INTO accounts (name, aadhar, account_type, overdraft_limit, pin) VALUES (%s, %s, %s, %s, %s)",
            (name, aadhar, acc_type, overdraft_limit, pin)
        )
        conn.commit()
        print(Fore.GREEN + f"✅ Account created for {name} with overdraft limit ₹{overdraft_limit:.2f}.")
    except mysql.connector.IntegrityError:
        print(Fore.RED + "❌ Account with this name already exists.")
    except InvalidOperation:
        print(Fore.RED + "❌ Invalid input.")

# Deposit
def deposit(name, amount):
    account = get_account(name)
    if not account:
        print(Fore.RED + "❌ Account not found.")
        return
    account_id, _, _, pin = account
    if not verify_pin(pin):
        return
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, account_id))
        cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'deposit', %s)",
                       (account_id, amount))
        conn.commit()
        print(Fore.GREEN + f"💰 Deposited ₹{amount:.2f} to {name}'s account.")
    except (InvalidOperation, ValueError):
        print(Fore.RED + "❌ Invalid amount.")

# Withdraw
def withdraw(name, amount):
    account = get_account(name)
    if not account:
        print(Fore.RED + "❌ Account not found.")
        return
    account_id, balance, overdraft_limit, pin = account
    if not verify_pin(pin):
        return
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError
        available = balance + overdraft_limit
        if available >= amount:
            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, account_id))
            cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'withdraw', %s)",
                           (account_id, amount))
            conn.commit()
            print(Fore.GREEN + f"💸 Withdrawn ₹{amount:.2f} from {name}'s account.")
            if balance - amount < 0:
                print(Fore.YELLOW + f"⚠️ You are using overdraft. Balance: ₹{balance - amount:.2f}")
        else:
            print(Fore.RED + f"❌ Insufficient funds. Available: ₹{available:.2f}")
    except (InvalidOperation, ValueError):
        print(Fore.RED + "❌ Invalid amount.")

# Transfer
def transfer(from_name, to_name, amount):
    if from_name == to_name:
        print(Fore.RED + "❌ Cannot transfer to the same account.")
        return
    from_acc = get_account(from_name)
    to_acc = get_account(to_name)
    if not from_acc:
        print(Fore.RED + f"❌ Sender account '{from_name}' not found.")
        return
    if not to_acc:
        print(Fore.RED + f"❌ Receiver account '{to_name}' not found.")
        return
    from_id, from_balance, from_overdraft, pin = from_acc
    to_id, _, _, _ = to_acc
    if not verify_pin(pin):
        return
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError
        available = from_balance + from_overdraft
        if available >= amount:
            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, from_id))
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, to_id))
            cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'transfer-out', %s)",
                           (from_id, amount))
            cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'transfer-in', %s)",
                           (to_id, amount))
            conn.commit()
            print(Fore.CYAN + f"🔁 Transferred ₹{amount:.2f} from {from_name} to {to_name}.")
            if from_balance - amount < 0:
                print(Fore.YELLOW + f"⚠️ {from_name} is using overdraft.")
        else:
            print(Fore.RED + f"❌ Transfer exceeds overdraft limit. Available: ₹{available:.2f}")
    except (InvalidOperation, ValueError):
        print(Fore.RED + "❌ Invalid amount.")

# Transaction History
def show_transactions(name):
    account = get_account(name)
    if account:
        account_id, _, _, _ = account
        cursor.execute("SELECT type, amount, timestamp FROM transactions WHERE account_id = %s ORDER BY timestamp DESC", (account_id,))
        transactions = cursor.fetchall()
        if transactions:
            formatted = [[t[2].strftime("%Y-%m-%d %H:%M:%S"), t[0].capitalize(), f"₹{Decimal(t[1]):.2f}"] for t in transactions]
            print(Fore.YELLOW + f"\n📜 Transaction History for {name}\n" + "-" * 40)
            print(tabulate(formatted, headers=["Timestamp", "Type", "Amount"], tablefmt="fancy_grid"))
        else:
            print(Fore.BLUE + "ℹ️ No transactions found.")
    else:
        print(Fore.RED + "❌ Account not found.")

# Account Summary
def account_summary(name):
    cursor.execute("SELECT name, balance, overdraft_limit, aadhar, account_type FROM accounts WHERE name = %s", (name,))
    account = cursor.fetchone()
    if account:
        name, balance, overdraft_limit, aadhar, acc_type = account
        table = [
            ["Name", name],
            ["Account Type", acc_type],
            ["Aadhar", aadhar],
            ["Balance", f"₹{balance:.2f}"],
            ["Overdraft Limit", f"₹{overdraft_limit:.2f}"],
            ["Total Available", f"₹{balance + overdraft_limit:.2f}"]
        ]
        print(Fore.CYAN + "\n📊 Account Summary\n" + "-" * 30)
        print(tabulate(table, tablefmt="fancy_grid"))
    else:
        print(Fore.RED + "❌ Account not found.")

# Main Menu
def main():
    while True:
        print("\n" + Fore.LIGHTGREEN_EX + "==== Mini Banking System ====")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. Transaction History")
        print("6. Account Summary")
        print("7. Exit")

        choice = input(Fore.LIGHTYELLOW_EX + "Enter your choice (1-7): ").strip()

        if choice == '1':
            name = input("Enter account holder name: ").strip()
            create_account(name)
        elif choice == '2':
            name = input("Enter account name: ").strip()
            deposit(name, input("Enter amount to deposit: "))
        elif choice == '3':
            name = input("Enter account name: ").strip()
            withdraw(name, input("Enter amount to withdraw: "))
        elif choice == '4':
            from_name = input("Sender name: ").strip()
            to_name = input("Receiver name: ").strip()
            transfer(from_name, to_name, input("Enter amount to transfer: "))
        elif choice == '5':
            name = input("Enter account name: ").strip()
            show_transactions(name)
        elif choice == '6':
            name = input("Enter account name: ").strip()
            account_summary(name)
        elif choice == '7':
            print(Fore.MAGENTA + "👋 Exiting. Thank you for using the Mini Banking System.")
            break
        else:
            print(Fore.RED + "❌ Invalid choice. Please select from 1-7.")

main()




