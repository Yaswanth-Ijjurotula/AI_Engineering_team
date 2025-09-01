import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from accounts import (
    Account,
    Transaction,
    TransactionType,
    InsufficientFundsError,
    InsufficientSharesError,
    InvalidSymbolError,
    get_share_price,
)

class TestHelperFunctions(unittest.TestCase):
    """Tests for helper functions in the accounts module."""

    def test_get_share_price_valid(self):
        """Test get_share_price with valid symbols."""
        self.assertEqual(get_share_price('AAPL'), 150.00)
        self.assertEqual(get_share_price('TSLA'), 250.00)
        self.assertEqual(get_share_price('GOOGL'), 130.00)

    def test_get_share_price_invalid(self):
        """Test get_share_price with an invalid symbol raises InvalidSymbolError."""
        with self.assertRaises(InvalidSymbolError):
            get_share_price('INVALID')

class TestAccount(unittest.TestCase):
    """Test suite for the Account class."""

    def setUp(self):
        """Set up a new account for each test."""
        self.account = Account(account_id="12345", user_name="Test User")

    def test_initialization(self):
        """Test that an account is initialized with correct default values."""
        self.assertEqual(self.account.account_id, "12345")
        self.assertEqual(self.account.user_name, "Test User")
        self.assertEqual(self.account.cash_balance, 0.0)
        self.assertEqual(self.account.total_deposits, 0.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])

    def test_deposit_positive_amount(self):
        """Test depositing a positive amount correctly updates balances and logs transaction."""
        self.account.deposit(500.0)
        self.assertEqual(self.account.cash_balance, 500.0)
        self.assertEqual(self.account.total_deposits, 500.0)
        self.assertEqual(len(self.account.transactions), 1)
        
        transaction = self.account.transactions[0]
        self.assertEqual(transaction.type, TransactionType.DEPOSIT)
        self.assertEqual(transaction.amount, 500.0)

    def test_deposit_multiple(self):
        """Test multiple deposits accumulate correctly."""
        self.account.deposit(100.0)
        self.account.deposit(200.0)
        self.assertEqual(self.account.cash_balance, 300.0)
        self.assertEqual(self.account.total_deposits, 300.0)
        self.assertEqual(len(self.account.transactions), 2)

    def test_deposit_zero_or_negative_amount(self):
        """Test depositing zero or a negative amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.deposit(0)
        with self.assertRaises(ValueError):
            self.account.deposit(-100.0)
        self.assertEqual(self.account.cash_balance, 0.0)
        self.assertEqual(len(self.account.transactions), 0)

    def test_withdraw_valid_amount(self):
        """Test withdrawing a valid amount updates balance and logs transaction."""
        self.account.deposit(500.0)
        self.account.withdraw(200.0)
        self.assertEqual(self.account.cash_balance, 300.0)
        self.assertEqual(self.account.total_deposits, 500.0) # Should not change
        self.assertEqual(len(self.account.transactions), 2)

        transaction = self.account.transactions[1]
        self.assertEqual(transaction.type, TransactionType.WITHDRAW)
        self.assertEqual(transaction.amount, -200.0)

    def test_withdraw_insufficient_funds(self):
        """Test withdrawing more than the balance raises InsufficientFundsError."""
        self.account.deposit(100.0)
        with self.assertRaises(InsufficientFundsError):
            self.account.withdraw(150.0)
        self.assertEqual(self.account.cash_balance, 100.0)

    def test_withdraw_zero_or_negative_amount(self):
        """Test withdrawing zero or a negative amount raises ValueError."""
        self.account.deposit(100.0)
        with self.assertRaises(ValueError):
            self.account.withdraw(0)
        with self.assertRaises(ValueError):
            self.account.withdraw(-50.0)
        self.assertEqual(self.account.cash_balance, 100.0)

    def test_buy_valid_transaction(self):
        """Test a valid stock purchase."""
        self.account.deposit(1000.0)
        # Price of AAPL is 150.00
        self.account.buy('AAPL', 5)
        self.assertAlmostEqual(self.account.cash_balance, 1000.0 - (150.00 * 5))
        self.assertEqual(self.account.holdings['AAPL'], 5)
        self.assertEqual(len(self.account.transactions), 2)

        buy_transaction = self.account.transactions[1]
        self.assertEqual(buy_transaction.type, TransactionType.BUY)
        self.assertEqual(buy_transaction.symbol, 'AAPL')
        self.assertEqual(buy_transaction.quantity, 5)
        self.assertEqual(buy_transaction.share_price, 150.00)
        self.assertAlmostEqual(buy_transaction.amount, -(150.00 * 5))

    def test_buy_multiple_stocks(self):
        """Test buying multiple different stocks."""
        self.account.deposit(10000.0)
        self.account.buy('AAPL', 10) # 10 * 150 = 1500
        self.account.buy('TSLA', 5)  # 5 * 250 = 1250
        self.assertAlmostEqual(self.account.cash_balance, 10000.0 - 1500 - 1250)
        self.assertEqual(self.account.holdings, {'AAPL': 10, 'TSLA': 5})
        
    def test_buy_add_to_existing_holding(self):
        """Test buying more shares of an existing holding."""
        self.account.deposit(5000.0)
        self.account.buy('GOOGL', 10) # 10 * 130 = 1300
        self.account.buy('GOOGL', 5)  # 5 * 130 = 650
        self.assertAlmostEqual(self.account.cash_balance, 5000.0 - 1300 - 650)
        self.assertEqual(self.account.holdings['GOOGL'], 15)

    def test_buy_insufficient_funds(self):
        """Test buying stock with insufficient funds."""
        self.account.deposit(100.0)
        with self.assertRaises(InsufficientFundsError):
            self.account.buy('AAPL', 1) # Costs 150.00
        self.assertEqual(self.account.cash_balance, 100.0)
        self.assertEqual(self.account.holdings, {})

    def test_buy_invalid_symbol(self):
        """Test buying stock with an invalid symbol."""
        self.account.deposit(500.0)
        with self.assertRaises(InvalidSymbolError):
            self.account.buy('INVALID', 2)

    def test_buy_zero_or_negative_quantity(self):
        """Test buying zero or a negative quantity of stock."""
        self.account.deposit(500.0)
        with self.assertRaises(ValueError):
            self.account.buy('AAPL', 0)
        with self.assertRaises(ValueError):
            self.account.buy('AAPL', -2)
            
    def test_sell_valid_transaction(self):
        """Test a valid stock sale."""
        self.account.deposit(1500)
        self.account.buy('AAPL', 10)
        self.account.sell('AAPL', 4)
        
        # Initial cash: 1500. After buy: 1500 - (10*150) = 0. After sell: 0 + (4*150) = 600
        self.assertAlmostEqual(self.account.cash_balance, 600.0)
        self.assertEqual(self.account.holdings['AAPL'], 6)
        self.assertEqual(len(self.account.transactions), 3)

        sell_transaction = self.account.transactions[2]
        self.assertEqual(sell_transaction.type, TransactionType.SELL)
        self.assertEqual(sell_transaction.symbol, 'AAPL')
        self.assertEqual(sell_transaction.quantity, 4)
        self.assertEqual(sell_transaction.share_price, 150.00)
        self.assertAlmostEqual(sell_transaction.amount, 4 * 150.00)
        
    def test_sell_all_shares(self):
        """Test selling all shares of a particular stock."""
        self.account.deposit(1500)
        self.account.buy('AAPL', 10)
        self.account.sell('AAPL', 10)
        self.assertAlmostEqual(self.account.cash_balance, 1500)
        self.assertNotIn('AAPL', self.account.holdings)

    def test_sell_insufficient_shares(self):
        """Test selling more shares than owned."""
        self.account.deposit(1500)
        self.account.buy('AAPL', 5)
        with self.assertRaises(InsufficientSharesError):
            self.account.sell('AAPL', 6)
        self.assertEqual(self.account.holdings['AAPL'], 5)

    def test_sell_stock_not_owned(self):
        """Test selling a stock that is not in the holdings."""
        self.account.deposit(1000)
        with self.assertRaises(InsufficientSharesError):
            self.account.sell('TSLA', 1)

    def test_sell_zero_or_negative_quantity(self):
        """Test selling zero or a negative quantity of stock."""
        self.account.deposit(1500)
        self.account.buy('AAPL', 5)
        with self.assertRaises(ValueError):
            self.account.sell('AAPL', 0)
        with self.assertRaises(ValueError):
            self.account.sell('AAPL', -2)

    def test_get_portfolio_value(self):
        """Test the calculation of total portfolio value."""
        # Initial value is 0
        self.assertEqual(self.account.get_portfolio_value(), 0.0)
        
        # Value with only cash
        self.account.deposit(1000.0)
        self.assertEqual(self.account.get_portfolio_value(), 1000.0)
        
        # Value with cash and holdings
        # cash is now 1000 - (2*150) = 700
        # holdings are 2 * 150 = 300
        self.account.buy('AAPL', 2) 
        self.assertAlmostEqual(self.account.get_portfolio_value(), 700.0 + 300.0)
        
        # Value with multiple holdings
        # cash is now 700 - (3*250) = -50 (oops, let's start over)
        self.setUp()
        self.account.deposit(2000)
        self.account.buy('AAPL', 5) # 5 * 150 = 750. Cash = 1250
        self.account.buy('TSLA', 2) # 2 * 250 = 500. Cash = 750
        # Holdings value = 750 (AAPL) + 500 (TSLA) = 1250
        # Total value = 750 (cash) + 1250 (holdings) = 2000
        self.assertAlmostEqual(self.account.get_portfolio_value(), 2000.0)

    def test_get_profit_loss(self):
        """Test the calculation of profit and loss."""
        # Initial P/L is 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)

        self.account.deposit(2000)
        # P/L should be 0 if portfolio value equals deposits
        self.assertEqual(self.account.get_profit_loss(), 0.0)
        
        # Mock get_share_price to simulate price changes
        with patch('accounts.get_share_price') as mock_get_price:
            # Setup initial prices
            mock_get_price.side_effect = lambda symbol: {'AAPL': 150.0, 'TSLA': 250.0}[symbol]
            
            self.account.buy('AAPL', 10) # Cost: 10 * 150 = 1500. Cash left: 500.
            
            # P/L should still be 0 as prices haven't changed
            self.assertAlmostEqual(self.account.get_profit_loss(), 0.0)
            
            # Simulate a price increase for AAPL (profit)
            mock_get_price.side_effect = lambda symbol: {'AAPL': 160.0, 'TSLA': 250.0}[symbol]
            # Portfolio value = 500 (cash) + 10 * 160 (holdings) = 2100
            # P/L = 2100 (value) - 2000 (deposits) = 100
            self.assertAlmostEqual(self.account.get_profit_loss(), 100.0)

            # Simulate a price decrease for AAPL (loss)
            mock_get_price.side_effect = lambda symbol: {'AAPL': 140.0, 'TSLA': 250.0}[symbol]
            # Portfolio value = 500 (cash) + 10 * 140 (holdings) = 1900
            # P/L = 1900 (value) - 2000 (deposits) = -100
            self.assertAlmostEqual(self.account.get_profit_loss(), -100.0)
            
    def test_get_holdings_returns_copy(self):
        """Test that get_holdings returns a copy, not a reference."""
        self.account.deposit(500)
        self.account.buy('AAPL', 2)
        holdings_copy = self.account.get_holdings()
        self.assertEqual(holdings_copy, {'AAPL': 2})
        
        # Modify the copy
        holdings_copy['AAPL'] = 99
        
        # Check that the original holdings are unchanged
        self.assertEqual(self.account.holdings['AAPL'], 2)

    def test_get_transactions_returns_copy(self):
        """Test that get_transactions returns a copy, not a reference."""
        self.account.deposit(100)
        transactions_copy = self.account.get_transactions()
        self.assertEqual(len(transactions_copy), 1)
        
        # Modify the copy
        transactions_copy.append("a fake transaction")
        
        # Check that the original transactions list is unchanged
        self.assertEqual(len(self.account.transactions), 1)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
