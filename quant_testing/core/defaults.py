def ib_comission(quantity):
    """
    Calculates the fees of trading based on an Interactive
    Brokers fee structure for API, in USD.

    This does not include exchange or ECN fees.

    Based on "US API Directed Orders":
    https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
    """
    full_cost = 1.3
    if quantity <= 500:
        full_cost = max(1.3, 0.013 * quantity)
    else:  # Greater than 500
        full_cost = max(1.3, 0.008 * quantity)
    return full_cost
