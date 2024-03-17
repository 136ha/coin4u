# https://fred.stlouisfed.org/docs/api/fred/#General_Documentation
# https://wooiljeong.github.io/python/pdr-fred-en/

import numpy as np
import pandas as pd
from PublicDataReader import Fred

service_key = "4882d2dc90465463751fdd851fd537a9"
api = Fred(service_key)

def CPI() -> pd.DataFrame:
    """Consumer Price Index (CPI) series data lookup function"""

    # series ID value
    series_id = "CPIAUCNS"

    # Get series data
    df = api.get_data(
        api_name="series_observations",
        series_id=series_id
    )

    # Convert value column to numeric type
    df['value'] = pd.to_numeric(df['value'], errors="coerce")
    # convert date column to date
    df['date'] = pd.to_datetime(df['date'])
    # set date column as an index
    df = df.set_index("date")

    # create a value last month column
    df['value_last_year'] = df['value'].shift(12)
    df['CPI(YoY)'] = (df['value'] - df['value_last_year']) / df['value_last_year'] * 100

    # Select only year-ago value columns
    df = df[['CPI(YoY)']]
    return df


def PCE() -> pd.DataFrame:
    """Personal Consumption Expenditures (PCE) series data lookup function"""

    # series ID value
    series_id = "PCEPI"

    # Get series data
    df = api.get_data(
        api_name="series_observations",
        series_id=series_id
    )

    # Convert value column to numeric type
    df['value'] = pd.to_numeric(df['value'], errors="coerce")
    # convert date column to date
    df['date'] = pd.to_datetime(df['date'])
    # set date column as an index
    df = df.set_index("date")

    # create a value last month column
    df['value_last_year'] = df['value'].shift(12)
    df['PCE(YoY)'] = (df['value'] - df['value_last_year']) / df['value_last_year'] * 100

    # Select only year-ago value columns
    df = df[['PCE(YoY)']]
    return df


def PPI() -> pd.DataFrame:
    """Producer Price Index (PPI) series data lookup function"""

    # series ID value
    series_id = "PPIFID"

    # Get series data
    df = api.get_data(
        api_name="series_observations",
        series_id=series_id
    )

    # Convert value column to numeric type
    df['value'] = pd.to_numeric(df['value'], errors="coerce")
    # convert date column to date
    df['date'] = pd.to_datetime(df['date'])
    # set date column as an index
    df = df.set_index("date")

    # create a value last month column
    df['value_last_year'] = df['value'].shift(12)
    df['PPI(YoY)'] = (df['value'] - df['value_last_year']) / df['value_last_year'] * 100

    # Select only year-ago value columns
    df = df[['PPI(YoY)']]
    return df


def FED_RATE() -> pd.DataFrame:
    """Function to fetch the target series data for Federal Funds Rate"""

    # Series ID value
    series_id = "DFEDTARU"

    # Retrieve series data
    df = api.get_data(
        api_name="series_observations",
        series_id=series_id
    )

    # Create a column by converting the 'value' column to numeric
    df['FED RATE'] = pd.to_numeric(df['value'], errors="coerce")
    # Convert the 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Set the 'date' column as index
    df = df.set_index('date')
    # Select only the Federal Funds Rate column
    df = df[['FED RATE']]

    return df


def CS() -> pd.DataFrame:
    """Function to retrieve the Case-Shiller National Home Price Index series data"""

    # Series ID value
    series_id = "CSUSHPISA"

    # Retrieve series data
    df = api.get_data(
        api_name="series_observations",
        series_id=series_id
    )

    # Convert 'value' column to numeric
    df['value'] = pd.to_numeric(df['value'], errors="coerce")
    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    # Set 'date' column as index
    df = df.set_index("date")

    # Generate column for same month value of last year
    df['value_last_year'] = df['value'].shift(12)
    df['CS(YoY)'] = (df['value'] - df['value_last_year']) / df['value_last_year'] * 100

    # Select only the column with YoY changes
    df = df[['CS(YoY)']]

    return df


def GDP() -> pd.DataFrame:
    """Function to fetch the US GDP growth rate (annualized QoQ) series data"""

    # Series ID value
    series_id = "A191RL1Q225SBEA"

    # Retrieve series data
    df = api.get_data(
        api_name="series_observations",
        series_id=series_id
    )

    # Convert 'value' column to numeric
    df['GDP RATE'] = pd.to_numeric(df['value'], errors="coerce")
    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    # Set 'date' column as index
    df = df.set_index("date")
    # Select only the GDP growth rate column
    df = df[['GDP RATE']]

    return df

def get_cci(df, period=20):
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['sma'] = df['TP'].rolling(period).mean()
    df['mad'] = df['TP'].rolling(period).apply(lambda x: (pd.Series(x) - pd.Series(x).mean()).abs().mean())
    df['CCI'] = (df['TP'] - df['sma']) / (0.015 * df['mad'])
    del df['TP']
    del df['sma']
    del df['mad']
    return df

def get_rsi(df, period=14):
    U = np.where(df['Close'].diff(1) > 0, df['Close'].diff(1), 0)
    D = np.where(df['Close'].diff(1) < 0, df['Close'].diff(1) *(-1), 0)
    AU = pd.DataFrame(U, index=df.index).rolling(window=period).mean()
    AD = pd.DataFrame(D, index=df.index).rolling(window=period).mean()
    RSI = AU / (AD+AU) *100
    df['RSI'] = RSI
    return df

# MACD
def get_fnMACD(m_Df, column, m_NumFast=12, m_NumSlow=26, m_NumSignal=9):
    m_Df['EMAFast'] = m_Df[column].ewm(span = m_NumFast, min_periods = m_NumFast - 1).mean()
    m_Df['EMASlow'] = m_Df[column].ewm(span = m_NumSlow, min_periods = m_NumSlow - 1).mean()
    m_Df[f'MACD_{column}'] = m_Df['EMAFast'] - m_Df['EMASlow']
    m_Df[f'MACDSignal_{column}'] = m_Df[f'MACD_{column}'].ewm(span = m_NumSignal, min_periods = m_NumSignal-1).mean()
    m_Df[f'MACDDiff_{column}'] = m_Df[f'MACD_{column}'] - m_Df[f'MACDSignal_{column}']
    del m_Df['EMAFast']
    del m_Df['EMASlow']
    return m_Df

# stochastic
def get_stochastic(df, n=15):
    df['fast_k'] = ((df['Close'] - df['Low'].rolling(n).min()) / (df['High'].rolling(n).max() - df['Low'].rolling(n).min())) * 100
    df['slow_k'] = df['fast_k'].rolling(n).mean()
    df['slow_d'] = df['slow_k'].rolling(n).mean()
    df['stochasticDiff'] = df['slow_k'] - df['slow_d']
    return df

# MFI 구하기 : https://sjblog1.tistory.com/45
def get_mfi(df, period=14):
    df['ma20'] = df['Close'].rolling(window=20).mean() # 20일 이동평균
    df['stddev'] = df['Close'].rolling(window=20).std() # 20일 이동표준편차
    df['upper'] = df['ma20'] + 2*df['stddev'] # 상단밴드
    df['lower'] = df['ma20'] - 2*df['stddev'] # 하단밴드
    df['PB'] = (df['Close'] - df['lower']) / (df['upper'] - df['lower'])
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['PMF'] = 0
    df['NMF'] = 0
    for i in range(len(df['Close'])-1):
        if df.TP.values[i] < df.TP.values[i+1]:
            df.PMF.values[i+1] = df.TP.values[i+1] * df.Volume.values[i+1]
            df.NMF.values[i+1] = 0
        else:
            df.NMF.values[i+1] = df.TP.values[i+1] * df.Volume.values[i+1]
            df.PMF.values[i+1] = 0
    df['MFR'] = (df.PMF.rolling(window=period).sum() / df.NMF.rolling(window=period).sum())
    df['mfi'] = 100 - 100 / (1 + df['MFR'])
    del df['ma20']
    del df['stddev']
    del df['upper']
    del df['lower']
    del df['PB']
    del df['TP']
    del df['PMF']
    del df['NMF']
    del df['MFR']
    return df


def get_ADX(data: pd.DataFrame, period=14):
    """
    Computes the ADX indicator.
    """
    df = data.copy()
    alpha = 1 / period

    # TR
    df['H-L'] = df['High'] - df['Low']
    df['H-C'] = np.abs(df['High'] - df['Close'].shift(1))
    df['L-C'] = np.abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
    del df['H-L'], df['H-C'], df['L-C']

    # ATR
    df['ATR'] = df['TR'].ewm(alpha=alpha, adjust=False).mean()

    # +-DX
    df['H-pH'] = df['High'] - df['High'].shift(1)
    df['pL-L'] = df['Low'].shift(1) - df['Low']
    df['+DX'] = np.where(
        (df['H-pH'] > df['pL-L']) & (df['H-pH'] > 0),
        df['H-pH'],
        0.0
    )
    df['-DX'] = np.where(
        (df['H-pH'] < df['pL-L']) & (df['pL-L'] > 0),
        df['pL-L'],
        0.0
    )
    del df['H-pH'], df['pL-L']

    # +- DMI
    df['S+DM'] = df['+DX'].ewm(alpha=alpha, adjust=False).mean()
    df['S-DM'] = df['-DX'].ewm(alpha=alpha, adjust=False).mean()
    df['+DMI'] = (df['S+DM'] / df['ATR']) * 100
    df['-DMI'] = (df['S-DM'] / df['ATR']) * 100
    del df['S+DM'], df['S-DM']

    # ADX
    df['DX'] = (np.abs(df['+DMI'] - df['-DMI']) / (df['+DMI'] + df['-DMI'])) * 100
    df['ADX'] = df['DX'].ewm(alpha=alpha, adjust=False).mean()
    del df['DX'], df['ATR'], df['TR'], df['-DX'], df['+DX'], df['+DMI'], df['-DMI']

    return df
