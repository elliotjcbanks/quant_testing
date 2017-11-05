# ###########################################################################
# Portfolio classes

class Portfolio:
    pass


class SingleSharePortfolio(Portfolio):
    """Base class for a simple portfolio containing shares and cash

    """

    def __init__(self, events, portfolio_value, cash, shares, tick_data):
        self.events = events
        self.cash = cash
        self.shares = shares
        self.holdings = self.cash + self.shares
        self.tick_data = tick_data

    def determine_move(self, signal_event):
        # First we need the current share price
        current_data = self.tick_data.get_latest_bars(1)
        share_price = current_data['share_price']
        transaction_costs = self.strategy_transaction_costs(share_price)

        if signal_event.signal_type == ExecutionType.buy and self.shares == 0:
            # Get the number of shares we can buy, and send the order
            shares_to_buy = max(self.cash // share_price - transaction_costs, 0)
            return OrderEvent(None, 'MKT_ORDER', shares_to_buy, ExecutionType.buy)
        if signal_event.signal_type == ExecutionType.sell and self.shares > 0:
            return OrderEvent(None, 'MKT_ORDER', self.shares, ExecutionType.sell)

    def generate_order(self, signal_event):
        order_event = self.determine_move(signal_event)
        if order_event is not None:
            self.events.put(order_event)

    def strategy_transaction_costs(self, share_price):
        """Determine the transaction_costs associated with the strategy

        """
        floating_cost = share_price * self.percentage_comission
        return floating_cost + self.flat_cost

    def buy_instrument(self, number_shares, price_share, transaction_costs):

        total_cost = number_shares * share_price + transaction_costs

        if total_cost > self.cash:
            logger.warning("Not possible to execute stragety"
                           " - insufficient funds!")
            return

        self.cash -= total_cost
        self.shares += number_shares

    def sell_instrument(self, number_shares, price_share, transaction_costs):

        if number_shares > self.shares:
            logger.warning("Not possible to execute stragety"
                           " - insufficient shares!")
            return

        self.shares -= number_shares
        self.cash += number_shares * share_price - transaction_costs

    def update_portfolio(self, fill_order):
        """Update the portfolio
        """
        qnty = fill_order.quantity
        price = fill_order.price
        if fill_order.direction == ExecutionType.buy:
            self.buy_instrument(qnty, price, )


    @property
    def value(self, share_price):
        return self.cash + self.shares * share_price
