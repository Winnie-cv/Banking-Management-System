from decimal import Decimal, InvalidOperation

import database
from current_savings import (
    validate_account_type,
    validate_opening_balance,
)


def parse_money(value):
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid monetary amount")

    if not amount.is_finite():
        raise ValueError("Enter a finite monetary amount")

    if amount.as_tuple().exponent < -2:
        raise ValueError("Use at most two decimal places")

    return amount


def open_account(name, dob, phone, address, account_type, balance):
    if not name.strip() or not phone.strip() or not address.strip():
        raise ValueError("Name, phone and address are required")

    account_type = validate_account_type(account_type)
    balance = parse_money(balance)

    if account_type == "SAVINGS":
        validate_opening_balance(balance)
    elif not balance.is_finite() or balance < 0:
        raise ValueError("Opening balance cannot be negative")

    return database.create_account(
        name.strip(),
        dob.strip(),
        phone.strip(),
        address.strip(),
        account_type,
        balance,
    )


def deposit(account_no, amount):
    amount = parse_money(amount)
    return database.perform_transaction(account_no, "DEPOSIT", amount)


def withdraw(account_no, amount):
    amount = parse_money(amount)
    return database.perform_transaction(account_no, "WITHDRAWAL", amount)


def balance_enquiry(account_no):
    account = database.get_account(account_no)
    if account is None:
        raise ValueError("Account not found")
    return account


def display_accounts():
    return database.list_accounts()


def view_transactions(account_no):
    if database.get_account(account_no) is None:
        raise ValueError("Account not found")
    return database.get_transactions(account_no)


def close_account(account_no):
    database.close_account(account_no)
