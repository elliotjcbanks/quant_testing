from . import components, strategy
from datetime import timedelta
import Queue as queue


class Simulator:

    def __init__(self, portfolio, strategy, datahandler, execution_handler):

        self.portfolio = portfolio
        self.strategy = strategy
        self.datahandler = datahandler
        self.execution_handler = execution_handler

        self.returns = []
        self.events = queue.Queue()


    def run_simulation(self, start, finish, timestep):
        """ Run a share simulation from start to finish, at each timestep

        start_time: DatetimeObject
            Date and time to start the

        """

        while True:

            while True:

                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if isinstance(event, MarketEvent):
                            self.strategy.generate_strategy(event)

                        elif isinstance(event, SignalEvent):
                            self.portfolio.generate_order(event)

                        elif isinstance(event, OrderEvent):
                            self.execution_handler.fill_order(event)

                        elif isinstance(event, FillEvent):
                            self.portfolio.update_portfolio(event)

            update_result = self.datahandler.update_bars()
            if update_result is False:
                break
