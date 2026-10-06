from abc import ABC, abstractmethod
class account:
    def __init__(self, account_id, account_name):
        self.account_id = account_id
        self.account_name = account_name

    def display_account_info(self):
        print(f"Account ID: {self.account_id}, Account Name: {self.account_name}")