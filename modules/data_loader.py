
import pandas as pd

def load_data(cache_file):
    def custom_date_parser(x):
        try:
            return pd.to_datetime(x, format="%Y-%m-%d")
        except:
            return pd.to_datetime(x)

    return pd.read_csv(
        cache_file,
        index_col=0,
        parse_dates=["Date"],
        date_parser=custom_date_parser
    )
