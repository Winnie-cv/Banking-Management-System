class insufficientFunds(Exception):
    """Raised when an account has insufficient funds for a transaction."""
    pass

class invalidTransaction(Exception):
    """Raised when a transaction is invalid."""
    pass

class accountNotFound(Exception):
    """Raised when an account is not found."""
    pass