import logging
from abc import ABCMeta, abstractmethod
import pandas as pd
from datetime import datetime, timedelta
import events

logger = "AlgoTrading.log"

# DataHandler classes

class DataHandler:
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OLHCVI) for each symbol requested.

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self):
        """
        Returns the last N bars from the latest_symbol list before a certain timestamp,
        or fewer if less bars are available.
        """
        raise NotImplementedError("Should implement get_latest_bars()")


class DailyCsvHandler(DataHandler):

    def __init__(self, file_path, events, lookback=10, timestamp=None):

        self.read_file(file_path)
        self.events = events
        self.lookback = lookback
        if timestamp is not None:
            self.time = timestamp
        else:
            self.time = self.data['timestamp'].min()

    def get_data_points(self, timestamp, N=1):
        """Get the last N data points before a particular timestamp

        """
        relevant_data = self.data[self.data['timestamp'] < timestamp]
        return relevant_data.head(N)

    def get_latest_bars(self, N):
        return self.get_data_points(self.time, N)

    def update_bars(self):
        time = self.timestamp
        signal_bars = get_latest_bars(self.timestamp, lookback)
        last_bar = get_data_points(self.timestamp, 1)
        self.events.put(MarketEvent(time, last_bar, signal_bars))


class GoogleCSV(DailyCsvHandler):

    def read_file(self, file_path):
        self.data = pd.read_csv(file_path)
        self.data['timestamp'] = self.data.Date.apply(lambda x: datetime.strptime(x, '%d-%b-%y'))
        self.data['share_price'] = self.data['Close']

        # Convert data to a datetime format
        self.data.sort_values(['timestamp'], ascending=True)



# ###########################################################################
# Portfolio classes

class Portfolio:

    __metaclass__ = ABCMeta

    @abstractmethod
    def value():
        raise NotImplementedError

    @abstractmethod
    def buy_instrument():
        raise NotImplementedError

    @abstractmethod
    def sell_instrument():
        raise NotImplementedError


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

    @property
    def value(self, share_price):
        return self.cash + self.shares * share_price

def Executor(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def fill_order():
        raise NotImplementedError

def SingleShareExecutor(Executor):

    def __init__(self, portfolio, events, tick_data):

        self.portfolio = portfolio
        self.events = events
        self.tick_data = tick_data

    def fill_order(self, order):
        """Create a fill order that will update the portfolio object

        Naive implementation will do whatever we did before
        """
        # Get the latest price
        current_data = self.tick_data.get_latest_bars(1)
        share_price = current_data['share_price']
        transaction_costs = self.strategy_transaction_costs(share_price)
