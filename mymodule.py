import pandas as pd
import uuid

from random import randint


ACCOUNT_FILE = "account_data.xlsx"
CUSTOMER_FILE = "customer_data.xlsx"
TRANSACTION_FILE = "transaction_data.xlsx"


def main_save(df, filename):
    df.to_excel(filename, index=False)


def main_load(filename):
    return pd.read_excel(filename)  


def save_accounts(accounts):
    main_save(accounts, ACCOUNT_FILE)


def load_accounts():
    return main_load(ACCOUNT_FILE)


def save_customers(customers):
    main_save(customers, CUSTOMER_FILE)


def load_customers():
    return main_load(CUSTOMER_FILE)


def save_transactions(transactions):
    main_save(transactions, TRANSACTION_FILE)


def load_transactions():
    return main_load(TRANSACTION_FILE)


class Account:

    def __init__(self, account_id, customer_id, account_number, balance):
        self.account_id = account_id
        self.customer_id = customer_id
        self.account_number = account_number
        self.balance = balance

    def __update(self):
        accounts = load_accounts()
        accounts.loc[accounts["account_id"] == self.account_id, "balance"] = self.balance
        save_accounts(accounts)

    def deposit(self, amount):
        self.balance += amount
        self.__update()

    def withdraw(self, amount):
        if self.balance < amount:
            raise Exception("insufficient funds")
        self.balance -= amount
        self.__update()

    def get_balance(self):
        return self.balance

    @classmethod
    def create(cls, account_id, customer_id, account_number, balance):
        accounts = load_accounts()
        filtered_account = accounts.loc[accounts["account_id"] == account_id]
        if not filtered_account.empty:
            raise Exception("Acount already exists!")
        account = cls(account_id=account_id, customer_id=customer_id, account_number=account_number, balance=balance)
        accounts = pd.concat([accounts, pd.DataFrame(data=account.__dict__, index=[0])], ignore_index=True)
        save_accounts(accounts)
        return account

    @classmethod
    def load_by_account_id(cls, account_id):
        accounts = load_accounts()
        filtered_account = accounts.loc[accounts["account_id"] == account_id]
        if filtered_account.empty:
            raise Exception("Account not found!")
        return cls(**filtered_account.to_dict('records')[0])

    @classmethod
    def list_by_customer_id(cls, customer_id):
        accounts = load_accounts()
        filtered_accounts = accounts.loc[accounts["customer_id"] == customer_id]
        return [cls(account_id=filtered_account["account_id"],
                    customer_id=filtered_account["customer_id"],
                    account_number=filtered_account["account_number"],
                    balance=filtered_account["balance"]) for index, filtered_account in filtered_accounts.iterrows()]


class Customer:

    def __init__(self, customer_id, name, email, phone_number):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone_number = phone_number

    @classmethod
    def create(cls, customer_id, name, email, phone_number):
        customers = load_customers()
        filtered_customer = customers.loc[customers["customer_id"] == customer_id]
        if not filtered_customer.empty:
            raise Exception("Customer already exists!")
        customer = cls(customer_id=customer_id, name=name, email=email, phone_number=phone_number)
        customers = pd.concat([customers, pd.DataFrame(data=customer.__dict__, index=[0])], ignore_index=True)
        save_customers(customers)
        return customer

    @classmethod
    def load_by_customer_id(cls, customer_id):
        customers = load_customers()
        filtered_customer = customers.loc[customers["customer_id"] == customer_id]
        if filtered_customer.empty:
            raise Exception("Customer not found!")
        return cls(customer_id=filtered_customer.at[0, "customer_id"],
                   name=filtered_customer.at[0, "name"],
                   email=filtered_customer.at[0, "email"],
                   phone_number=filtered_customer.at[0, "phone_number"])


class Transaction:
    transaction_type_allowed = ["deposit", "withdraw"]

    def __init__(self, transaction_id, account_id, amount, transaction_type, status, comment=""):
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.status = status
        self.comment = comment

    def execute(self):
        account = Account.load_by_account_id(self.account_id)
        if self.transaction_type == "deposit":
            account.deposit(self.amount)
            self.status = "success"
        elif self.transaction_type == "withdraw":
            try:
                account.withdraw(self.amount)
                self.status = "success"
            except Exception as exc:
                self.status = "failed"
                self.comment = "insufficient funds"

        transactions = load_transactions()
        transactions.loc[transactions["transaction_id"] == self.transaction_id, "status"] = self.status
        transactions.loc[transactions["transaction_id"] == self.transaction_id, "comment"] = self.comment
        save_transactions(transactions)
        
    @classmethod
    def create(cls, account_id, amount, transaction_type):
        account = Account.load_by_account_id(account_id)

        if transaction_type not in cls.transaction_type_allowed:
            raise Exception("Invalid transaction_type!")

        transaction_id = str(uuid.uuid1())

        transactions = load_transactions()
        transaction = cls(transaction_id=transaction_id, 
                          account_id=account_id, 
                          amount=amount, 
                          transaction_type=transaction_type, 
                          status="created")
        transactions = pd.concat([transactions, pd.DataFrame(data=transaction.__dict__, index=[0])], ignore_index=True)
        save_transactions(transactions)
        transaction.execute()
        return transaction

    @classmethod
    def list_by_account_id(cls, account_id):
        transactions = load_transactions()
        filtered_transactions = transactions.loc[transactions["account_id"] == account_id]
        return [cls(transaction_id=filtered_transaction["transaction_id"],
                    account_id=filtered_transaction["account_id"],
                    amount=filtered_transaction["amount"],
                    transaction_type=filtered_transaction["transaction_type"],
                    status=filtered_transaction["status"],
                    comment=filtered_transaction["comment"]) for index, filtered_transaction in filtered_transactions.iterrows()]


class AccountRepository:

    def find_account_by_id(account_id):
        return Account.load_by_account_id(account_id)

    def find_accounts_by_customer_id(customer_id):
        return Account.load_by_customer_id(customer_id)


class Case:

    @staticmethod
    def generate_account_id():
        account_id = randint(10**(5), (10**6)-1)
        try:
            account = Account.load_by_account_id(account_id)
        except:
            return account_id
        return generate_account_id()

    @staticmethod
    def create_account(customer_id, name, email, phone_number):
        try:
            customer = Customer.load_by_customer_id(customer_id)
        except Exception:
            customer = Customer.create(customer_id, name, email, phone_number)

        account_id = Case.generate_account_id()
        account_number = randint(10**(9), (10**10)-1) 
        balance = 0

        return Account.create(account_id, customer_id, account_number, balance)

    @staticmethod
    def make_transaction(account_id, amount, transaction_type):
        Transaction.create(account_id, amount, transaction_type)

    @staticmethod
    def generate_account_statement(account_id):
        transactions = Transaction.list_by_account_id(account_id)
        string = ""
        for transaction in transactions:
            string += " | ".join(list(map(str, transaction.__dict__.values())))
            string += "\n"
        return string