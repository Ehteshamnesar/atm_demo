import sqlite3
from datetime import datetime, timedelta

# ================= DATABASE SETUP =================
DB_NAME = "atm.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            card_number TEXT PRIMARY KEY,
            pin INTEGER,
            balance INTEGER,
            wrong_attempts INTEGER,
            locked_until TEXT
        )
    """)
    conn.commit()
    conn.close()

# ================= ACCOUNT MODEL =================
class Account:
    def __init__(self, card_number, pin, balance, wrong_attempts, locked_until):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance
        self.wrong_attempts = wrong_attempts
        self.locked_until = locked_until

    @staticmethod
    def get(card_number):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE card_number=?", (card_number,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Account(*row)
        return None

    def save(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO accounts
            VALUES (?, ?, ?, ?, ?)
        """, (self.card_number, self.pin, self.balance, self.wrong_attempts, self.locked_until))
        conn.commit()
        conn.close()

# ================= ATM MACHINE =================
class ATM:
    def authenticate_pin(self, account, entered_pin):
        if account.locked_until:
            if datetime.now() < datetime.fromisoformat(account.locked_until):
                print("Account locked. Try after 24 hours")
                return False

        if entered_pin != account.pin:
            account.wrong_attempts += 1
            print("Wrong PIN")
            if account.wrong_attempts == 3:
                account.locked_until = (datetime.now() + timedelta(hours=24)).isoformat()
                print("Account locked for 24 hours")
            account.save()
            return False

        account.wrong_attempts = 0
        account.locked_until = None
        account.save()
        return True

    def menu(self, account):
        while True:
            print("\n1. Check Balance\n2. Deposit\n3. Withdraw\n4. Exit")
            choice = input("Choose option: ")

            if choice == '1':
                pin = int(input("Enter PIN: "))
                if self.authenticate_pin(account, pin):
                    print("Balance:", account.balance)

            elif choice == '2':
                pin = int(input("Enter PIN: "))
                amt = int(input("Enter amount: "))
                if self.authenticate_pin(account, pin):
                    account.balance += amt
                    account.save()
                    print("Amount deposited")

            elif choice == '3':
                pin = int(input("Enter PIN: "))
                amt = int(input("Enter amount: "))
                if self.authenticate_pin(account, pin):
                    if amt > account.balance:
                        print("Insufficient balance")
                    else:
                        account.balance -= amt
                        account.save()
                        print("Collect cash")

            elif choice == '4':
                break

            else:
                print("Invalid option")

# ================= MAIN FLOW =================
def run_atm():
    init_db()

    # demo accounts (run once)
    demo = Account.get("1111-2222-3333")
    if not demo:
        Account("1111-2222-3333", 1234, 5000, 0, None).save()
        Account("4444-5555-6666", 4321, 8000, 0, None).save()

    atm = ATM()

    while True:
        card = input("\nInsert ATM Card (or 'exit'): ")
        if card == 'exit':
            print("ATM shut down")
            break

        account = Account.get(card)
        if not account:
            print("Invalid card")
            continue

        atm.menu(account)


run_atm()
