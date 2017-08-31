import logging
from abc import ABCMeta, abstractmethod
import pandas as pd
from datetime import datetime, timedelta

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
    def get_data_points(self, symbol, timestamp, N=1):
        """
        Returns the last N bars from the latest_symbol list before a certain timestamp,
        or fewer if less bars are available.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_shareprice(self, symbol, timestamp, N=1):
        """
        Get the share price of the relevant share at a time
        """
        raise NotImplementedError("Should implement get_shareprice()")

    @abstractmethod
    def update(self, timestep, finish_point):
        raise NotImplementedError


class GoogleCsvHandler(DataHandler):

    def __init__(self, file_path):

        self.data = pd.read_csv(file_path)

        # Convert data to a datetime format
        self.data['timestamp'] = self.data.Date.apply(lambda x: datetime.strptime(x, '%d-%b-%y'))
        self.data['share_price'] = self.data['Close']
        self.data.sort_values(['timestamp'], ascending=True)

        self.time = self.data['timestamp'][0]


    def get_data_points(self, timestamp=None, N=1):
        if not timestamp:
            timestamp = self.time
        relevant_data = self.data[self.data['timestamp'] < timestamp]
        return relevant_data.tail(N)

    def get_shareprice(self, timestamp=None):
        if not timestamp:
            timestamp = self.time
        relevant_data = self.data[self.data['timestamp'] == timestamp]
        return relevant_data['share_price']

    def update(self, timestep):
        """ Update the time value by the number of days mentioned. If that is
        a weekend, move to the next available day

        """

        next_date = self.time + timedelta(timestep)
        self.time = self.data[self.data['timestamp'] >= next_date]['timestamp'].min()



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

    def __init__(self, cash, shares):

        self.cash = cash
        self.shares = shares

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

    def value(self, share_price):

        return self.cash + self.shares * share_price
