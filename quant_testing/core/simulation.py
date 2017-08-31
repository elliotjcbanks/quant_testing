from . import components, strategy
from datetime import timedelta


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


        self.datahandler.time = start
        time = self.datahandler.time
        data = self.datahandler
        strat = self.strategy

        while time < finish:
            # Get the current price of the relevant events
            datapoints = data.get_data_points(strat.lookback)

            current_share_price = data.get_shareprice()

            # Determine if anything needs to be done
            strategy = strat.generate_strategy(datapoints, self.portfolio)

            # Update the Portfolio
            strat.apply_strategy(self.portfolio)

            # Get the current value of the portfolio
            self.returns.append(self.portfolio.value(current_share_price))

            # Use the datahandler to update to the next state to look at
            data.update(timestep)
