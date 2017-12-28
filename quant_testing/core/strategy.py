import numpy as np

from .events import ExecutionType, MarketEvent, SignalEvent


class Strategy:
    """Calculate the signal based on the data, determine whether to carry out the
    strategy. Implement the strategy to the appropriate portfolio if neccesary.

    """

    def __init__(self, events, portfolio):

        self.events = events
        self.portfolio = portfolio

    def generate_strategy(self):
        raise NotImplementedError


class MovingAverageCrossStrategy(Strategy):
    """ Class for moving average crossing strategy.

    Buy stocks when the short term moving average is greater than the long term
    moving order. Exit when the long term average is greater than the short term.

    """

    def __init__(self, events, portfolio, short_window=10, long_window=30):
        super().__init__(events, portfolio)
        self.short_window = short_window
        self.long_window = long_window

    def generate_strategy(self, event):
        """ Get the long and short moving averages
        """

        if not isinstance(event, MarketEvent):
            return

        tick_data = event.signal_data
        price_bars = tick_data.get_latest_bars(self.long_window)
        if len(price_bars) < self.long_window:
            return

        price_data = np.asarray(price_bars['share_price'])

        short_sma = np.mean(price_data[-self.short_window:])
        long_sma = np.mean(price_data[-self.long_window:])

        if short_sma > long_sma and self.portfolio.shares == 0:
            self.events.put(SignalEvent(tick_data.symbol,
                                        event.timestamp,
                                        ExecutionType.buy))
        elif short_sma < long_sma and self.portfolio.shares > 0:
            self.events.put(SignalEvent(tick_data.symbol,
                                        event.timestamp,
                                        ExecutionType.sell))


class BinaryStrategy(Strategy):
    """ Using data, buy if price is more than 2 std below mean. Sell if reverts
    back to within 2 std of mean.

    """
    def __init__(self, events, portfolio, lookback=10):
        super().__init__(events, portfolio)
        self.lookback = lookback

    def generate_strategy(self, event):
        """ Determine the strategy from the data for the portfolio. Returns
        and instruction whether or not to buy the stared

        """
        tick_data = event.signal_data
        data = tick_data.get_latest_bars(self.lookback)
        if any((data is None, data.empty)):
            # Can occasionally get none if this is the start of a cycle
            return None
        price_data = np.asarray(data['share_price'])
        current_price = price_data[-1]
        mean_price = np.mean(price_data)
        std_price = np.std(price_data)

        if current_price > mean_price - 2 * std_price:
            self.events.put(SignalEvent(tick_data.symbol,
                                        event.timestamp,
                                        ExecutionType.sell))

        elif current_price < mean_price - 2 * std_price:
            self.events.put(SignalEvent(tick_data.symbol,
                                        event.timestamp,
                                        ExecutionType.buy))

        else:
            return None
