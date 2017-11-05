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

    def __init__(self, file_path, events, lookback=10, timestamp=None, max_timestamp):

        self.read_file(file_path)
        self.events = events
        self.lookback = lookback
        self.max_timestamp = max_timestamp
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
        """Go to the next timestamp, and calculate the
        """
        last_bar = get_data_points(self.time, 1)
        next_bar = last_bar
        while last_bar == next_bar:
            self.time += timedelta(days=1)
            next_bar = get_data_points(self.time, 1)
            if self.time = self.max_timestamp:
                return False
        signal_bars = get_latest_bars(lookback)
        last_bar = next_bar
        self.events.put(MarketEvent(time, last_bar, signal_bars))


class GoogleCSV(DailyCsvHandler):

    def read_file(self, file_path):
        self.data = pd.read_csv(file_path)
        self.data['timestamp'] = self.data.Date.apply(lambda x: datetime.strptime(x, '%d-%b-%y'))
        self.data['share_price'] = self.data['Close']

        # Convert data to a datetime format
        self.data.sort_values(['timestamp'], ascending=True)
