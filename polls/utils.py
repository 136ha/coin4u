import yfinance as yf
import pandas as pd

def get_data(symbol, period):
    data = yf.Ticker(symbol)
    df = data.history(period=period)
    df.columns = ['open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits']
    df['date'] = pd.to_datetime(df.index)
    return df