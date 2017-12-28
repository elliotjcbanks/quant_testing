from . import events
import queue


class Simulator:

    def __init__(self, portfolio, strategy, datahandler, execution_handler):

        self.portfolio = portfolio
        self.strategy = strategy
        self.datahandler = datahandler
        self.execution_handler = execution_handler

        self.returns = []
        self.events = self.datahandler.events

    def run_simulation(self, start, finish, output=False):
        """ Run a share simulation from start to finish

        start_time: pd.Timestamp
            Timestamp to start the simulation
        end_time: pd.Timestamp
            timestamp to end the simulation
        output: bool, optional
            If True, print the portfolio after every event

        """
        while True:

            while True:

                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if isinstance(event, events.MarketEvent):
                            self.strategy.generate_strategy(event)

                        elif isinstance(event, events.SignalEvent):
                            self.portfolio.generate_order(event)

                        elif isinstance(event, events.OrderEvent):
                            self.execution_handler.fill_order(event)

                        elif isinstance(event, events.FillEvent):
                            self.portfolio.update_portfolio(event)

                if not self.returns or self.datahandler.current_timestamp != self.returns[-1][0]:
                    self.returns.append((self.datahandler.current_timestamp,
                                         self.portfolio.cash,
                                         self.portfolio.shares))
                if output:
                    print("cash: {}, shares: {}".format(self.portfolio.cash,
                                                        self.portfolio.shares))

            update_result = self.datahandler.update_bars()
            if update_result is False or self.datahandler.current_timestamp >= finish:
                break
