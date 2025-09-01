from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional

# Custom Exceptions
class InsufficientFundsError(Exception):
    """Raised when an operation cannot be completed due to lack of cash."""
    pass

class InsufficientSharesError(Exception):
    """Raised when trying to sell more shares than owned."""
    pass

class InvalidSymbolError(Exception):
    """Raised when a stock symbol is not found."""
    pass

# Helper Function
def get_share_price(symbol: str) -> float:
    """
    Simulates fetching the current market price for a given stock symbol.
    For this simulation, it returns fixed prices for a predefined set of symbols.
    """
    prices = {
        'AAPL': 150.00,
        'TSLA': 250.00,
        'GOOGL': 130.00,
    }
    price = prices.get(symbol)
    if price is None:
        raise InvalidSymbolError(f"Invalid symbol: {symbol}")
    return price

# Data Structures
class TransactionType(Enum):
    """Enum for transaction types."""
    DEPOSIT = auto()
    WITHDRAW = auto()
    BUY = auto()
    SELL = auto()

@dataclass
class Transaction:
    """Represents a single transaction in the account."""
    timestamp: datetime
    type: TransactionType
    amount: float
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    share_price: Optional[float] = None

# Main Class
class Account:
    """
    Represents a user's trading account, managing funds, holdings, and transactions.
    """

    def __init__(self, account_id: str, user_name: str):
        """
        Initializes a new Account instance.
        """
        self.account_id: str = account_id
        self.user_name: str = user_name
        self.cash_balance: float = 0.0
        self.total_deposits: float = 0.0
        self.holdings: dict[str, int] = {}
        self.transactions: list[Transaction] = []

    def _record_transaction(
        self,
        transaction_type: TransactionType,
        amount: float,
        symbol: Optional[str] = None,
        quantity: Optional[int] = None,
        share_price: Optional[float] = None
    ) -> None:
        """Helper method to create and record a transaction."""
        transaction = Transaction(
            timestamp=datetime.now(),
            type=transaction_type,
            amount=amount,
            symbol=symbol,
            quantity=quantity,
            share_price=share_price
        )
        self.transactions.append(transaction)

    def deposit(self, amount: float) -> None:
        """
        Adds funds to the account's cash balance.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.cash_balance += amount
        self.total_deposits += amount
        self._record_transaction(TransactionType.DEPOSIT, amount)

    def withdraw(self, amount: float) -> None:
        """
        Withdraws funds from the account's cash balance.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.cash_balance:
            raise InsufficientFundsError("Cannot withdraw more than the available cash balance.")
        self.cash_balance -= amount
        self._record_transaction(TransactionType.WITHDRAW, -amount)

    def buy(self, symbol: str, quantity: int) -> None:
        """
        Buys a specified quantity of a stock.
        """
        if quantity <= 0:
            raise ValueError("Quantity to buy must be a positive integer.")
        
        price = get_share_price(symbol)
        total_cost = price * quantity

        if total_cost > self.cash_balance:
            raise InsufficientFundsError(f"Insufficient funds to buy {quantity} shares of {symbol}.")

        self.cash_balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self._record_transaction(
            transaction_type=TransactionType.BUY,
            amount=-total_cost,
            symbol=symbol,
            quantity=quantity,
            share_price=price
        )

    def sell(self, symbol: str, quantity: int) -> None:
        """
        Sells a specified quantity of a stock from the user's holdings.
        """
        if quantity <= 0:
            raise ValueError("Quantity to sell must be a positive integer.")
        
        current_quantity = self.holdings.get(symbol, 0)
        if current_quantity < quantity:
            raise InsufficientSharesError(f"Not enough shares to sell {quantity} of {symbol}. You only have {current_quantity}.")

        price = get_share_price(symbol)
        total_sale_value = price * quantity

        self.cash_balance += total_sale_value
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]

        self._record_transaction(
            transaction_type=TransactionType.SELL,
            amount=total_sale_value,
            symbol=symbol,
            quantity=quantity,
            share_price=price
        )

    def get_portfolio_value(self) -> float:
        """
        Calculates the total current value of the account (cash + holdings).
        """
        holdings_value = 0.0
        for symbol, quantity in self.holdings.items():
            try:
                price = get_share_price(symbol)
                holdings_value += price * quantity
            except InvalidSymbolError:
                # In a real system, you might handle this differently,
                # e.g., use the last known price or log an error.
                # For this simulation, we'll assume prices are always available.
                pass
        return self.cash_balance + holdings_value

    def get_profit_loss(self) -> float:
        """
        Calculates the total profit or loss since the account was created.
        """
        current_value = self.get_portfolio_value()
        return current_value - self.total_deposits

    def get_holdings(self) -> dict[str, int]:
        """
        Reports the current share holdings of the user.
        """
        return self.holdings.copy()

    def get_transactions(self) -> list[Transaction]:
        """
        Reports the complete transaction history for the account.
        """
        return self.transactions.copy()