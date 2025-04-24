
import pandas as pd

def generate_targets(df, horizon=3):
    df = df.copy()
    df.loc[:, "target_1d"] = df["Close"].shift(-1) > df["Close"]
    df.loc[:, "target_3d"] = df["Close"].shift(-horizon) > df["Close"]
    return df
