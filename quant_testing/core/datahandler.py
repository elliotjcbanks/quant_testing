from abc import ABCMeta, abstractmethod
import pandas as pd
import quandl
import configparser
from datetime import datetime
from .events import MarketEvent

logger = "AlgoTrading.log"
CONFIG_LOC = '/home/elliot/.config/personal/common.ini'


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


class DailyHandler(DataHandler):

    def __init__(self, file_path, events, max_timestamp=None, current_timestamp=None):

        self.read_file(file_path)
        self.symbol = file_path
        self.events = events

        if max_timestamp is not None:
            self.data = self.data[self.data.index <= max_timestamp]

        if current_timestamp is None:
            self.current_timestamp = self.data.index[0]
        else:
            self.current_timestamp = current_timestamp

        # This is the point to iterate through the data
        self.data_generator = self.data.iterrows()

    def get_data_points(self, timestamp, N=1):
        """Get the last N data points before a particular timestamp

        """
        relevant_data = self.data[self.data.index < timestamp]
        return relevant_data.tail(N).reset_index(drop=True)

    def get_latest_bars(self, N):
        return self.get_data_points(self.current_timestamp, N)

    def update_bars(self):
        """ Generator to get the next bar value, and update the current timestamp
        """
        next_step = next(self.data_generator)
        next_bar = next_step[1]
        if next_bar is None:
            return False

        self.current_timestamp = next_step[0]
        self.events.put(MarketEvent(self.current_timestamp, next_bar, self))

    def read_file(self, file_path):
        raise NotImplementedError("read_file must be implemented by inherited class")


class GoogleCSV(DailyHandler):
    """ Reader for google finance csv file

    """

    def read_file(self, file_path):
        self.data = pd.read_csv(file_path)
        self.data.index = self.data.Date.apply(lambda x: datetime.strptime(x, '%d-%b-%y'))
        self.data['share_price'] = self.data['Close']

        # Convert data to a datetime format
        self.data = self.data.sort_index(ascending=True)


class QuandlReader(DailyHandler):
    """ Reader for Quadl data.

    This requires the user to have an api key in the computer common.ini file

    """

    def __init__(self, symbol, events, lookback=10, max_timestamp=None, current_timestamp=None):
        # Get the config for quandl to read the data
        config = configparser.ConfigParser()
        config.read(CONFIG_LOC)
        quandl.ApiConfig.api_key = config.get('quandl', 'api_key')
        self.data = quandl.get(symbol)
        self.data['share_price'] = self.data['Price']
        self.symbol = symbol

        self.events = events
        self.lookback = lookback

        if max_timestamp is not None:
            self.data = self.data[self.data.index <= max_timestamp]

        if current_timestamp is None:
            self.current_timestamp = self.data.index[0]
        else:
            self.current_timestamp = current_timestamp

        # This is the point to iterate through the data
        self.data_generator = self.data.iterrows()
