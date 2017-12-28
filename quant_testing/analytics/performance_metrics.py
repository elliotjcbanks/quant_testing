import numpy as np


def sharpe_ratio(df, col_name=None, N=252, benchmark=0):
    """ Calculate the sharpe_ratio of a pandas dataframe.

    The dataframe must contain a column Returns

    Parameters
    ----------
    df: pandas.DataFrame
        pandas dataframe with a Returns column
    col_name: str, optional
        Name of the collumn to calculate. If None, defaults to Returns
    N: int, optional
        Number of trading periods. Defauts to 252 (daily returns data)
    benchmark: float, optional
        Benchmark return to use. Defaults to zero.

    Returns
    -------
    float
        Sharpe ratio of the returns

    """

    if col_name is None:
        if 'Returns' not in df.columns:
            raise ValueError("Returns not in columns {}".format(df.columns))
        col_name = 'Returns'

    returns = df[col_name] - benchmark

    return np.sqrt(N) * returns.mean() / returns.std()
