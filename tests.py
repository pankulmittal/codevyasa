import unittest
from mymodule import Case, Account


class TestCaseMethods(unittest.TestCase):

    def test_create_account(self):
        customer_id = "pankulmittal"
        new_account = Case.create_account(customer_id, "Pankul Mittal", "mittal.pankul@gmail.com", "9996360764")
        self.assertEqual(new_account.customer_id, customer_id)

        loaded_account = Account.load_by_account_id(new_account.account_id)
        self.assertEqual(new_account.__dict__, loaded_account.__dict__)

    def test_make_transaction(self):
        account_id = 288470
        account = Account.load_by_account_id(account_id)
        initial_balance = account.get_balance()
        Case.make_transaction(account_id, 20, "withdraw")
        Case.make_transaction(account_id, 50, "withdraw")
        Case.make_transaction(account_id, 20, "withdraw")
        Case.make_transaction(account_id, 10, "withdraw")
        Case.make_transaction(account_id, 30, "deposit")
        account = Account.load_by_account_id(account_id)
        self.assertEqual(account.get_balance(), initial_balance-20-50-20-10+30)


if __name__ == '__main__':
    unittest.main()
