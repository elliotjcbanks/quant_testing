def Executor(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def fill_order():
        raise NotImplementedError

def NaiveSimulationExecutor(Executor):

    def __init__(self, portfolio, events, tick_data):

        self.portfolio = portfolio
        self.events = events
        self.tick_data = tick_data

    def fill_order(self, order_event):
        """Create a fill order that will update the portfolio object

        Naive implementation will do whatever we did before, and pass the fill back to the
        portfolio object
        """
        # Print the order
        order_event.print_order

        # Get the latest price
        lastest_bars = self.tick_data.get_latest_bars(1)
        price = lastest_bars['share_price']

        # Get the transaction_costs
        num_shares = order_event.quantity
        commission = self.portfolio.strategy_transaction_costs(num_shares)

        # Naive implementation will just execute the same order
        fill = FillEvent(None, None, None, num_shares,
                         order_event.direction, price, commission=commission)
        self.events.put(fill)
