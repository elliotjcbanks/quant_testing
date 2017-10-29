from events import ExecutionType

class Strategy:
    """Calculate the signal based on the data, determine whether to carry out the
    strategy. Implement the strategy to the appropriate portfolio if neccesary.

    """

    def generate_strategy(self):
        raise NotImplementedError

    def strategy_transaction_costs(self):
        raise NotImplementedError

    def implement_strategy(self):
        raise NotImplementedError


class BinaryStrategy(Strategy):
    """ Using data, buy if price is more than 2 std below mean. Sell if reverts
    back to within 2 std of mean.

    """

    def __init__(self, events, flat_commision,
                 percentage_comission, portfolio):

        self.events = events
        self.flat_cost = flat_commision
        self.percentage_comission = percentage_comission
        self.portfolio = portfolio

    def generate_strategy(self, event):
        """ Determine the strategy from the data for the portfolio. Returns
        and instruction whether or not to buy the stared

        """

        data = event.signal_data
        price_data = np.asarray(data['share_price'])
        current_price = price_data[-1]
        mean_price = np.mean(price_data)
        std_price = np.std(price_data)

        if current_price > mean_price - 2 * std_price:
            self.events.put(SignalEvent(None,
                                        event.timestamp,
                                        ExecutionType.sell)
        elif current_price < mean_price - 2 * std_price:
            self.events.put(SignalEvent(None,
                                        event.timestamp,
                                        ExecutionType.buy)
