# Design Document: Trading Simulation Account Management System

This document outlines the design for a self-contained Python module named `accounts` that provides a simple account management system for a trading simulation platform.

## 1. Module Overview

The `accounts.py` module will contain all the necessary components to manage user trading accounts. It will be self-contained and have no external dependencies beyond the Python standard library. The core of the module is the `Account` class, which encapsulates all data and operations for a single user account.

## 2. Module Components

### 2.1. Helper Function: `get_share_price`

This standalone function will simulate fetching the current market price for a given stock symbol. For this simulation, it will return fixed prices for a predefined set of symbols.

**Function Signature:**
```python
def get_share_price(symbol: str) -> float:
```
**Description:**
- Takes a stock `symbol` (e.g., 'AAPL') as a string.
- Returns the current price of one share as a float.
- Raises an `InvalidSymbolError` if the symbol is not recognized.
- **Test Implementation:**
    - 'AAPL': 150.00
    - 'TSLA': 250.00
    - 'GOOGL': 130.00

### 2.2. Custom Exceptions

To handle specific error conditions gracefully, the module will define the following custom exception classes, all inheriting from `Exception`.

- `InsufficientFundsError`: Raised when a user tries to withdraw more cash than they have or buy shares they cannot afford.
- `InsufficientSharesError`: Raised when a user tries to sell shares they do not own.
- `InvalidSymbolError`: Raised by `get_share_price` for unknown stock symbols.

### 2.3. Data Structures

To ensure clean and structured data, we will use an `Enum` for transaction types and a `dataclass` for transaction records.

#### `TransactionType` (Enum)
```python
from enum import Enum, auto

class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAW = auto()
    BUY = auto()
    SELL = auto()
```
- Provides a clear and error-resistant way to classify transactions.

#### `Transaction` (dataclass)
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    timestamp: datetime
    type: TransactionType
    amount: float
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    share_price: Optional[float] = None
```
- `timestamp`: The date and time the transaction occurred.
- `type`: The type of transaction (from `TransactionType` enum).
- `amount`: The cash value of the transaction. Positive for deposits/sells, negative for withdrawals/buys.
- `symbol`: The stock symbol for BUY/SELL transactions.
- `quantity`: The number of shares for BUY/SELL transactions.
- `share_price`: The price per share at the time of a BUY/SELL transaction.

### 2.4. Main Class: `Account`

This class represents a single user's trading account and contains all the logic for managing funds, holdings, and transactions.

**Class Name:** `Account`

#### Constructor
**Method Signature:**
```python
def __init__(self, account_id: str, user_name: str):
```
**Description:**
- Initializes a new `Account` instance.
- **Parameters:**
    - `account_id`: A unique identifier for the account.
    - `user_name`: The name of the account holder.
- **Initial State:**
    - `self.account_id`: Stores `account_id`.
    - `self.user_name`: Stores `user_name`.
    - `self.cash_balance`: Initialized to `0.0`.
    - `self.total_deposits`: Initialized to `0.0`. Used for P/L calculation.
    - `self.holdings`: An empty dictionary to store shares, e.g., `{'AAPL': 10}`.
    - `self.transactions`: An empty list to store `Transaction` objects.

#### Public Methods

**1. `deposit(self, amount: float) -> None`**
- **Description:** Adds funds to the account's cash balance.
- **Parameters:**
    - `amount`: The amount of money to deposit. Must be a positive number.
- **Logic:**
    - Validates that `amount` is greater than zero.
    - Increases `self.cash_balance` by `amount`.
    - Increases `self.total_deposits` by `amount`.
    - Records a `DEPOSIT` transaction.

**2. `withdraw(self, amount: float) -> None`**
- **Description:** Withdraws funds from the account's cash balance.
- **Parameters:**
    - `amount`: The amount of money to withdraw. Must be a positive number.
- **Logic:**
    - Validates that `amount` is greater than zero.
    - Checks if `amount` is less than or equal to `self.cash_balance`.
    - If funds are insufficient, raises `InsufficientFundsError`.
    - If sufficient, decreases `self.cash_balance` by `amount`.
    - Records a `WITHDRAW` transaction.

**3. `buy(self, symbol: str, quantity: int) -> None`**
- **Description:** Buys a specified quantity of a stock.
- **Parameters:**
    - `symbol`: The stock symbol to buy (e.g., 'AAPL').
    - `quantity`: The number of shares to buy. Must be a positive integer.
- **Logic:**
    - Fetches the current price using `get_share_price(symbol)`.
    - Calculates the total cost (`price * quantity`).
    - Checks if `total_cost` is less than or equal to `self.cash_balance`.
    - If funds are insufficient, raises `InsufficientFundsError`.
    - If sufficient:
        - Decreases `self.cash_balance` by `total_cost`.
        - Updates `self.holdings`, adding the symbol if new or increasing the quantity if already owned.
        - Records a `BUY` transaction.

**4. `sell(self, symbol: str, quantity: int) -> None`**
- **Description:** Sells a specified quantity of a stock from the user's holdings.
- **Parameters:**
    - `symbol`: The stock symbol to sell.
    - `quantity`: The number of shares to sell. Must be a positive integer.
- **Logic:**
    - Checks if the `symbol` exists in `self.holdings` and if the holding quantity is greater than or equal to the `quantity` to be sold.
    - If shares are insufficient, raises `InsufficientSharesError`.
    - Fetches the current price using `get_share_price(symbol)`.
    - Calculates the total sale value (`price * quantity`).
    - If sufficient shares are held:
        - Increases `self.cash_balance` by `total_sale_value`.
        - Decreases the quantity of the `symbol` in `self.holdings`. If the quantity becomes zero, the symbol is removed from the dictionary.
        - Records a `SELL` transaction.

**5. `get_portfolio_value(self) -> float`**
- **Description:** Calculates the total current value of the account, including cash and the market value of all held shares.
- **Returns:** The total portfolio value as a float.
- **Logic:**
    - Starts with the `self.cash_balance`.
    - Iterates through `self.holdings`. For each symbol:
        - Gets the current price via `get_share_price(symbol)`.
        - Calculates the market value of that holding (`price * quantity`).
        - Adds it to the total value.
    - Returns the final sum.

**6. `get_profit_loss(self) -> float`**
- **Description:** Calculates the total profit or loss since the account was created.
- **Returns:** The profit (positive float) or loss (negative float).
- **Logic:**
    - Calculates the current total portfolio value using `self.get_portfolio_value()`.
    - Returns the result of `(portfolio_value - self.total_deposits)`.

**7. `get_holdings(self) -> dict[str, int]`**
- **Description:** Reports the current share holdings of the user.
- **Returns:** A copy of the `self.holdings` dictionary.

**8. `get_transactions(self) -> list[Transaction]`**
- **Description:** Reports the complete transaction history for the account.
- **Returns:** A copy of the `self.transactions` list.