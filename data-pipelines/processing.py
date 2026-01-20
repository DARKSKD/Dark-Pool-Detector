"""
Processing Layer

This module represents the transformation and enrichment stage
between ingestion and detection.

In MVP:
- Processing is minimal and inline
- Data is already structured for detection engines

Future Scope:
- Feature engineering
- Trade aggregation
- Windowing logic
"""

import pandas as pd


def prepare_trade_dataframe(trades: list) -> pd.DataFrame:
    """
    Converts trade log into a Pandas DataFrame.

    Parameters:
    trades (list): List of trade dictionaries

    Returns:
    pd.DataFrame: Structured trade data
    """

    if not trades:
        return pd.DataFrame()

    df = pd.DataFrame(trades)

    # Ensure correct data types
    df["price"] = df["price"].astype(float)
    df["quantity"] = df["quantity"].astype(int)

    return df
