# ###########################################################################
# Portfolio classes
from .defaults import ib_comission
from quant_testing.core.events import ExecutionType, OrderEvent


import logging
logger = logging.Logger('portfolio.log')

class Portfolio:
    pass


class SingleSharePortfolio(Portfolio):
    """Base class for a simple portfolio containing shares and cash

    """

    def __init__(self, events, cash, shares, tick_data, commission_calc=ib_comission):
        self.events = events
        self.cash = cash
        self.shares = shares
        self.tick_data = tick_data
        self.commission = commission_calc

    def determine_move(self, signal_event):
        # First we need the current share price
        current_data = self.tick_data.get_latest_bars(1)
        share_price = current_data['share_price']

        # Get approximate transaction_costs - always buy roughly half the portfolio
        approx_shares = int(0.5*(self.cash // share_price))
        approx_costs = self.commission(approx_shares)

        if signal_event.signal_type == ExecutionType.buy and self.shares == 0:
            # Get the number of shares we can buy, and send the order
            shares_to_buy = max(int(self.cash // share_price - approx_costs), 0)
            return OrderEvent(None, 'MKT_ORDER', shares_to_buy, ExecutionType.buy)
        if signal_event.signal_type == ExecutionType.sell and self.shares > 0:
            return OrderEvent(None, 'MKT_ORDER', self.shares, ExecutionType.sell)

    def generate_order(self, signal_event):
        order_event = self.determine_move(signal_event)
        if order_event is not None:
            self.events.put(order_event)

    def buy_instrument(self, number_shares, share_price, transaction_costs):

        total_cost = number_shares * share_price + transaction_costs

        if total_cost > self.cash:
            logger.warning("Not possible to execute stragety"
                           " - insufficient funds!")
            return

        self.cash -= total_cost
        self.shares += number_shares

    def sell_instrument(self, number_shares, share_price, transaction_costs):

        if number_shares > self.shares:
            logger.warning("Not possible to execute stragety"
                           " - insufficient shares!")
            return
        elif transaction_costs > number_shares*share_price:
            logger.warning("Not possible to execute stragety"
                           " - insufficient funds!")
            return

        self.shares -= number_shares
        self.cash += number_shares * share_price - transaction_costs

    def update_portfolio(self, fill_order):
        """Update the portfolio
        """
        qnty = fill_order.quantity
        price = fill_order.price
        costs = fill_order.commission
        if fill_order.direction == ExecutionType.buy:
            self.buy_instrument(qnty, price, costs)
        elif fill_order.direction == ExecutionType.sell:
            self.sell_instrument(qnty, price, costs)
        else:
            raise ValueError("Unknown direction {}".format(fill_order.direction))

    @property
    def value(self, share_price):
        return self.cash + self.shares * share_price
