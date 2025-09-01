import gradio as gr
from accounts import Account, InsufficientFundsError, InsufficientSharesError, InvalidSymbolError

# --- Backend Setup ---
# For this simple demo, we create a single, global account instance when the app starts.
# This simulates a single-user experience.
try:
    account = Account(account_id="user123", user_name="Demo User")
except Exception as e:
    # Handle potential import errors or initialization failures gracefully
    print(f"Failed to initialize Account: {e}")
    account = None

# --- UI Helper Functions ---

def get_all_reports():
    """Fetches and formats all account data for display in the UI."""
    if not account:
        return "$0.00", "$0.00", "$0.00", [], [], "Error: Account not initialized."

    # Format summary stats
    cash_str = f"${account.cash_balance:,.2f}"
    portfolio_val_str = f"${account.get_portfolio_value():,.2f}"
    pnl_str = f"${account.get_profit_loss():,.2f}"

    # Format holdings for DataFrame
    holdings_data = [[symbol, qty] for symbol, qty in account.get_holdings().items()]
    if not holdings_data:
        holdings_data = [[]] # Gradio needs a non-empty list to render headers

    # Format transactions for DataFrame
    transactions_data = []
    for t in reversed(account.get_transactions()): # Show most recent first
        transactions_data.append([
            t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            t.type.name,
            f"{t.amount:,.2f}",
            t.symbol or "N/A",
            t.quantity or "N/A",
            f"${t.share_price:,.2f}" if t.share_price is not None else "N/A"
        ])
    if not transactions_data:
        transactions_data = [[]]

    return cash_str, portfolio_val_str, pnl_str, holdings_data, transactions_data

def handle_money_op(operation_type, amount):
    """Handles deposit and withdraw operations."""
    if not account:
        return "Error: Account not initialized.", *get_all_reports()[0:5]

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be a positive number.")

        if operation_type == 'deposit':
            account.deposit(amount)
            message = f"Successfully deposited ${amount:,.2f}."
        elif operation_type == 'withdraw':
            account.withdraw(amount)
            message = f"Successfully withdrew ${amount:,.2f}."
        else:
            raise ValueError("Invalid operation")

    except (ValueError, InsufficientFundsError) as e:
        message = f"Error: {e}"

    cash, portfolio, pnl, holdings, transactions = get_all_reports()
    return message, cash, portfolio, pnl, holdings, transactions

def handle_trade_op(operation_type, symbol, quantity):
    """Handles buy and sell operations."""
    if not account:
        return "Error: Account not initialized.", *get_all_reports()[0:5]

    try:
        if not symbol:
            raise ValueError("Please select a stock symbol.")
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        if operation_type == 'buy':
            account.buy(symbol, quantity)
            message = f"Successfully bought {quantity} share(s) of {symbol}."
        elif operation_type == 'sell':
            account.sell(symbol, quantity)
            message = f"Successfully sold {quantity} share(s) of {symbol}."
        else:
            raise ValueError("Invalid operation")

    except (ValueError, InsufficientFundsError, InsufficientSharesError, InvalidSymbolError) as e:
        message = f"Error: {e}"

    cash, portfolio, pnl, holdings, transactions = get_all_reports()
    return message, cash, portfolio, pnl, holdings, transactions

def deposit_f(amount):
    return handle_money_op('deposit', amount)

def withdraw_f(amount):
    return handle_money_op('withdraw', amount)

def buy_f(symbol, quantity):
    return handle_trade_op('buy', symbol, quantity)

def sell_f(symbol, quantity):
    return handle_trade_op('sell', symbol, quantity)

# --- Gradio UI Definition ---
with gr.Blocks(theme=gr.themes.Soft(), title="Trading Account Simulator") as demo:
    gr.Markdown("# Trading Account Simulator")
    gr.Markdown("A simple UI to demonstrate the account management backend.")

    with gr.Row():
        cash_balance_out = gr.Textbox(label="Cash Balance", interactive=False)
        portfolio_value_out = gr.Textbox(label="Total Portfolio Value", interactive=False)
        pnl_out = gr.Textbox(label="Total Profit/Loss", interactive=False)

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.TabItem("Manage Funds"):
                    fund_amount_in = gr.Number(label="Amount", minimum=0.01)
                    with gr.Row():
                        deposit_btn = gr.Button("Deposit", variant="primary")
                        withdraw_btn = gr.Button("Withdraw")
                with gr.TabItem("Trade Shares"):
                    symbol_in = gr.Dropdown(['AAPL', 'TSLA', 'GOOGL'], label="Stock Symbol")
                    quantity_in = gr.Number(label="Quantity", minimum=1, precision=0)
                    with gr.Row():
                        buy_btn = gr.Button("Buy", variant="primary")
                        sell_btn = gr.Button("Sell")
            status_out = gr.Textbox(label="Status", interactive=False, lines=2)

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("Current Holdings"):
                    holdings_out = gr.DataFrame(
                        headers=["Symbol", "Quantity"],
                        datatype=["str", "number"],
                        row_count=(5, "fixed"),
                        col_count=(2, "fixed"),
                    )
                with gr.TabItem("Transaction History"):
                    transactions_out = gr.DataFrame(
                        headers=["Timestamp", "Type", "Amount ($)", "Symbol", "Quantity", "Share Price ($)"],
                        datatype=["str", "str", "str", "str", "str", "str"],
                        row_count=(10, "fixed"),
                    )

    # --- Component Connections ---
    outputs_list = [
        status_out,
        cash_balance_out,
        portfolio_value_out,
        pnl_out,
        holdings_out,
        transactions_out
    ]

    deposit_btn.click(fn=deposit_f, inputs=[fund_amount_in], outputs=outputs_list)
    withdraw_btn.click(fn=withdraw_f, inputs=[fund_amount_in], outputs=outputs_list)
    buy_btn.click(fn=buy_f, inputs=[symbol_in, quantity_in], outputs=outputs_list)
    sell_btn.click(fn=sell_f, inputs=[symbol_in, quantity_in], outputs=outputs_list)

    def load_initial_data():
        """Function to load initial data when the UI starts."""
        cash, portfolio, pnl, holdings, transactions = get_all_reports()
        return "Welcome to the trading simulator!", cash, portfolio, pnl, holdings, transactions

    demo.load(fn=load_initial_data, inputs=None, outputs=outputs_list)

if __name__ == "__main__":
    if account is None:
        print("Could not start the application because the account backend failed to initialize.")
    else:
        demo.launch()