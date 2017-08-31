class Strategy:

    def generate_strategy(self):
        raise NotImplementedError

    def apply_strategy(self):
        raise NotImplementedError

    def strategy_transaction_costs(self):
        raise NotImplementedError


class BinaryStrategy(Strategy):
    """ Using data, buy if price is more than 2 std below mean. Sell if reverts
    back to within 2 std of mean.

    """

    def __init__(self, number_shares, flat_commision, percentage_comission):

        self.shares_bought = False
        self.should_buy = False
        self.should_sell = False
        self.strategy_number_shares = number_shares
        self.flat_cost = flat_commision
        self.percentage_comission = percentage_comission


    def strategy_transaction_costs(self, share_price):
        """Determine the transaction_costs associated with the strategy

        """

        floating_cost = share_price * self.percentage_comission
        return floating_cost + self.flat_cost


    def generate_strategy(self, data, portfolio):
        """ Determine the strategy from the data for the portfolio

        """
        if self.should_buy or self.should_sell:
            # Already an order in place so don't regenerate_strategy
            return

        price_data = np.asarray('share_price')
        current_price = price_data[-1]
        mean_price = np.mean(price_data)
        std_price = np.std(price_data)

        if self.shares_bought:
            if current_price > mean_price - 2 * std_price:
                self.should_sell = True
        else:
            if current_price < mean_price - 2 * std_price:
                self.should_buy = True


    def apply_strategy(self):
        """Apply the relevant strategy

        """

        self.strategy_transaction_costs()
