import .components
import .strategy


class Simulator:

    def __init__(self, portfolio, strategy, datahandler):

        self.portfolio = portfolio
        self.strategy = strategy
        self.datahandler = datahandler
        self.returns = []


    def run_simulation(self, start, finish, timestep):
        """ Run a share simulation from start to finish, at each timestep

        start_time: DatetimeObject
            Date and time to start the

        """

        current = start

        while current < finish:
            # Get the current price of the relevant events
            datapoints = self.datahandler.get_data_points(current,
                                                          self.strategy.lookback)

            current_share_price = self.datahandler.get_shareprice(current)

            # Determine if anything needs to be done
            strategy = self.strategy.generate_strategy(datapoints, self.portfolio)

            # Update the Portfolio
            self.strategy.apply_strategy(self.portfolio)

            # Get the current value of the portfolio
            self.returns.append(self.portfolio.value(current_share_price))

            current += timedelta(timestep)
