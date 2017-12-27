from abc import ABCMeta, abstractmethod
import pandas as pd
from datetime import datetime
from .events import MarketEvent

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

    def __init__(self, file_path, events, lookback=10, max_timestamp=None, current_timestamp=None):

        self.read_file(file_path)
        self.events = events
        self.lookback = lookback

        if max_timestamp is not None:
            self.data = self.data[self.data['timestamp'] <= max_timestamp]

        if current_timestamp is None:
            self.current_timestamp = self.data.iloc[0]['timestamp']
        else:
            self.current_timestamp = current_timestamp

        # This is the point to iterate through the data
        self.data_generator = self.data.iterrows()

    def get_data_points(self, timestamp, N=1):
        """Get the last N data points before a particular timestamp

        """
        relevant_data = self.data[self.data['timestamp'] < timestamp]
        return relevant_data.tail(N).reset_index(drop=True)

    def get_latest_bars(self, N):
        return self.get_data_points(self.current_timestamp, N)

    def update_bars(self):
        """ Generator to get the next bar value, and update the current timestamp
        """
        next_bar = next(self.data_generator)[1]
        if next_bar is None:
            return False

        self.current_timestamp = next_bar['timestamp']
        signal_bars = self.get_latest_bars(self.lookback)
        self.events.put(MarketEvent(self.current_timestamp, next_bar, signal_bars))

    def read_file(self, file_path):
        raise NotImplementedError("read_file must be implemented by inherited class")


class GoogleCSV(DailyCsvHandler):

    def read_file(self, file_path):
        self.data = pd.read_csv(file_path)
        self.data['timestamp'] = self.data.Date.apply(lambda x: datetime.strptime(x, '%d-%b-%y'))
        self.data['share_price'] = self.data['Close']

        # Convert data to a datetime format
        self.data = self.data.sort_values(['timestamp'], ascending=True)
