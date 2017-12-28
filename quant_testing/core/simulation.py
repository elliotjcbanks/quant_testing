from . import events
import queue
import pandas as pd


class Simulator:

    def __init__(self, portfolio, strategy, datahandler, execution_handler):

        self.portfolio = portfolio
        self.strategy = strategy
        self.datahandler = datahandler
        self.execution_handler = execution_handler

        self.returns = []
        self.events = self.datahandler.events

        self.signal_count = 0
        self.order_count = 0
        self.fill_count = 0
        self.cumulative_comission = 0

    def backtest(self, finish):
        self._run_simulation(finish)
        eq_curve = self._generate_summary_stats()
        return eq_curve

    def _run_simulation(self, finish, output=False):
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
                            self.signal_count += 1
                            self.portfolio.generate_order(event)

                        elif isinstance(event, events.OrderEvent):
                            self.order_count += 1
                            self.execution_handler.fill_order(event)

                        elif isinstance(event, events.FillEvent):
                            self.fill_count += 1
                            self.cumulative_comission += event.commission
                            self.portfolio.update_portfolio(event)

            if not self.returns or self.datahandler.current_timestamp != self.returns[-1][0]:
                self.returns.append((self.datahandler.current_timestamp,
                                     self.portfolio.cash,
                                     self.portfolio.shares,
                                     self.portfolio.value,
                                     self.cumulative_comission))
            if output:
                print("cash: {}, shares: {}".format(self.portfolio.cash,
                                                    self.portfolio.shares))

            update_result = self.datahandler.update_bars()
            if update_result is False or self.datahandler.current_timestamp >= finish:
                break

    def _generate_summary_stats(self):
        """Generate a pandas dataframe of the results
        """

        eq_curve = pd.DataFrame(self.returns,
                                columns=['date', 'cash', 'shares',
                                         'value', 'cumulative_comission'])
        eq_curve.set_index('date')
        eq_curve['returns'] = eq_curve['value'].pct_change()
        return eq_curve
