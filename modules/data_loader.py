import yfinance as yf
import pandas as pd
import os

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

DEFAULT_TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "TSLA", "META", "AVGO", "AMD", "NFLX",
    "INTC", "ADBE", "PEP", "CSCO", "QCOM", "COST", "TMUS", "TXN", "AMAT", "HON",
    "INTU", "SBUX", "BKNG", "ISRG", "ADI", "MDLZ", "VRTX", "MU", "REGN", "GILD",
    "PDD", "LRCX", "KDP", "ASML", "ZM", "PANW", "CTSH", "MAR", "EXC", "CDNS",
    "ADP", "WDAY", "BIDU", "BIIB", "SNPS", "MNST", "EA", "ORLY", "DLTR", "ROST",
    "IDXX", "FAST", "TEAM", "CRWD", "OKTA", "ZS", "DDOG", "MRNA", "DOCU", "CHKP",
    "FTNT", "NXPI", "WBD", "ANSS", "PAYX", "VRSK", "ALGN", "SWKS", "NTES", "SIRI",
    "KLAC", "ILMN", "SGEN", "MELI", "JBHT", "PCAR", "XEL", "AEP", "EBAY", "CEG",
    "TTD", "FANG", "BKR", "ENPH", "DLR", "WBA", "CSGP", "LCID", "RIVN", "SPLK",
    "COIN", "ZS", "ABNB", "PLTR", "UPST", "SOUN", "CRSP", "SMCI", "CELH", "NVAX"
]

def fetch_stock_data(ticker, period="90d", interval="1d"):
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_{period}_{interval}.csv")
    if os.path.exists(cache_file):
        return pd.read_csv(cache_file, index_col=0, parse_dates=True)
    else:
        try:
            df = yf.download(ticker, period=period, interval=interval)
            if not df.empty:
                df.to_csv(cache_file)
            return df
        except Exception as e:
            print(f"Ошибка загрузки {ticker}: {e}")
            return pd.DataFrame()

def load_all_data(tickers=DEFAULT_TICKERS, period="90d", interval="1d"):
    data = {}
    for ticker in tickers:
        df = fetch_stock_data(ticker, period, interval)
        if not df.empty:
            data[ticker] = df
    return data
