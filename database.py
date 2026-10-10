import os
from decimal import Decimal

import mysql.connector
from dotenv import load_dotenv

from current_savings import validate_withdrawal

load_dotenv()


def get_connection():
    password = os.getenv("BANK_DB_PASSWORD")
    if password is None:
        raise RuntimeError(
            "BANK_DB_PASSWORD is missing. Add it to your .env file."
        )

    return mysql.connector.connect(
        host=os.getenv("BANK_DB_HOST", "localhost"),
        user=os.getenv("BANK_DB_USER", "root"),
        password=password,
        database=os.getenv("BANK_DB_NAME", "bank_management"),
    )


def create_account(name, dob, phone, address, account_type, balance):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        connection.start_transaction()

        cursor.execute(
            """
            INSERT INTO customers (name, dob, phone, address)
            VALUES (%s, %s, %s, %s)
            """,
            (name, dob, phone, address),
        )
        customer_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO accounts (customer_id, type, balance, status)
            VALUES (%s, %s, %s, 'ACTIVE')
            """,
            (customer_id, account_type, balance),
        )
        account_no = cursor.lastrowid

        if balance > 0:
            cursor.execute(
                """
                INSERT INTO transactions
                    (account_no, type, amount, balance_after)
                VALUES (%s, 'OPENING', %s, %s)
                """,
                (account_no, balance, balance),
            )

        connection.commit()
        return account_no

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_account(account_no):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT a.account_no, a.type, a.balance, a.status,
                   c.name, c.dob, c.phone, c.address
            FROM accounts AS a
            JOIN customers AS c ON a.customer_id = c.id
            WHERE a.account_no = %s
            """,
            (account_no,),
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def list_accounts():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT a.account_no, c.name, a.type, a.balance, a.status
            FROM accounts AS a
            JOIN customers AS c ON a.customer_id = c.id
            ORDER BY a.account_no
            """
        )
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def perform_transaction(account_no, operation, amount):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        cursor.execute(
            """
            SELECT account_no, type, balance, status
            FROM accounts
            WHERE account_no = %s
            FOR UPDATE
            """,
            (account_no,),
        )
        account = cursor.fetchone()

        if account is None:
            raise ValueError("Account not found")

        if account["status"] != "ACTIVE":
            raise ValueError("Account is not active")

        balance = Decimal(str(account["balance"]))

        if amount <= 0:
            raise ValueError("Amount must be positive")

        if operation == "DEPOSIT":
            new_balance = balance + amount
        elif operation == "WITHDRAWAL":
            new_balance = validate_withdrawal(account, amount)
        else:
            raise ValueError("Invalid transaction type")

        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_no = %s",
            (new_balance, account_no),
        )

        cursor.execute(
            """
            INSERT INTO transactions
                (account_no, type, amount, balance_after)
            VALUES (%s, %s, %s, %s)
            """,
            (account_no, operation, amount, new_balance),
        )

        connection.commit()
        return new_balance

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def close_account(account_no):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        connection.start_transaction()
        cursor.execute(
            """
            UPDATE accounts
            SET status = 'CLOSED'
            WHERE account_no = %s AND status = 'ACTIVE'
            """,
            (account_no,),
        )

        if cursor.rowcount == 0:
            raise ValueError("Active account not found")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_transactions(account_no):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT type, amount, balance_after, timestamp
            FROM transactions
            WHERE account_no = %s
            ORDER BY id
            """,
            (account_no,),
        )
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()
