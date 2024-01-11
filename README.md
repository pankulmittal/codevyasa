
# Code Vyasa Assignment

For code testing

    from mymodule import Case

    # Create Account
    customer_id = "pankulmittal"
    account = Case.create_account(customer_id, "Pankul Mittal", "mittal.pankul@gmail.com", "9996360764")

    # Make Transaction 
    Case.make_transaction(account.account_id, 2000, "deposit")
    Case.make_transaction(account.account_id, 50, "withdraw")
    Case.make_transaction(account.account_id, 20, "withdraw")
    <!-- Case.make_transaction(account.account_id, 10, "withdraw") -->
    Case.make_transaction(account.account_id, 30, "deposit")

    # Generate Statement
    statement = Case.generate_account_statement(account.account_id)
    print(statement)

