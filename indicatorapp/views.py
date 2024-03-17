import math

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView
from django_plotly_dash import DjangoDash
from dash import html, dcc, dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_ta import bbands
import numpy as np
import datetime
from scipy.stats import pearsonr
import yfinance as yf

from indicatorapp.models import Ohlcv, USBureauEvent, FinancialStatement
from pytz import timezone
from sklearn.preprocessing import StandardScaler

from indicatorapp.utils import get_fnMACD, get_stochastic, get_mfi, get_rsi, get_ADX, get_cci


def indexView(request):
    symbol_list = [
        'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'STETH-USD', 'XRP-USD', 'DOGE-USD',
        'ADA-USD', 'AVAX-USD', 'SHIB-USD', 'DOT-USD', 'TON11419-USD', 'LINK-USD', 'MATIC-USD',
        'WTRX-USD', 'TRX-USD', 'WBTC-USD', 'NEAR-USD', 'BCH-USD', 'UNI7083-USD', 'LTC-USD',
        'APT21794-USD', 'ICP-USD', 'LEO-USD', 'DAI-USD', 'FIL-USD', 'ATOM-USD', 'ETC-USD',
        'RNDR-USD', 'INJ-USD', 'OKB-USD', 'WHBAR-USD', 'HBAR-USD', 'XLM-USD', 'CRO-USD',
        'OP-USD', 'BTCB-USD', 'WBETH-USD', 'VET-USD', 'KAS-USD', 'THETA-USD', 'SEI-USD',
        'XMR-USD', 'MKR-USD', 'LDO-USD', 'FTM-USD', 'WIF-USD', 'ALGO-USD', 'RETH-USD',

        'MSFT', 'NVDA', 'AMZN', 'GOOG', 'GOOGL', 'META', 'BRK-A', 'BRK-B', 'LLY',
        'TSM', 'JPM', 'NONOF', 'NVO', 'V', 'AVGO', 'WMT', 'LVMHF', 'LVMUY', 'UNH',
        'MA', 'XOM', 'JNJ', 'PG', 'ASML', 'ASMLF', 'HD', 'LTMAY', 'BAC', 'ORCL', 'TCEHY',
        'TCTZF', 'JPM-PD', 'JPM-PC', 'COST', 'TM', 'TOYOF', 'ABBV', 'BAC-PK', 'BML-PG',
        'MRK', 'BML-PH', 'BAC-PE', 'BAC-PL', 'BML-PL', 'CVX', 'CRM', 'F', 'LTHM',
        'NSRGY', 'HESAF', 'HESAY', 'NFLX', 'LRLCY', 'LRLCF', 'KO', 'BML-PJ', 'BAC-PB',
        'IDCBY', 'ACN', 'FMXUF', 'FMX', 'IDCBF', 'PEP', 'LIN', 'ADBE', 'TMO', 'PCCYF',
        'SAPGF', 'SAP', 'SHEL', 'RHHVF', 'RHHBY', 'RYDAF', 'NVSEF', 'WFC', 'AZN', 'DIS',
        'AZNCF', 'MCD', 'RHHBF', 'ABT', 'NVS', 'WFC-PY', 'CSCO', 'ACGBY', 'TMUS', 'BABA',
        'WFC-PL', 'BABAF', 'QCOM', 'DHR', 'WFC-PR', 'AYAAY', 'GE', 'INTC', 'IBM', 'INTU',
        'CAT', 'CMCSA', 'VZ', 'C-PJ', 'AMAT', 'PDD', 'CHDRF', 'PROSF', 'SMAWF', 'TTFNF',
        'SIEGY', 'CICHF', 'CHDRY', 'TTE', 'PROSY', 'AXP', 'UBER', 'PFE', 'TXN', 'CICHY',
        'MS', 'IDEXY', 'NOW', 'BACHY', 'IDEXF', 'BX', 'NKE', 'BACHF', 'UNP', 'HBCYF', 'PM',
        'HSBC', 'GS', 'C', 'AMGN', 'BHP', 'COP', 'LOW', 'ISRG', 'BHPLF', 'EADSF', 'RY',
        'HDB', 'EADSY', 'CMWAY', 'SYK', 'SPGI', 'SBGSF', 'SBGSY', 'UPS', 'ARM', 'HON',
        'BUD', 'RTNTF', 'UL', 'WFC-PC', 'UNLYF', 'RTX', 'NEE', 'SCHW', 'T', 'SNYNF',
        'DTEGF', 'SNY', 'MUFG', 'PGR', 'BLK', 'ELV', 'PLD', 'LRCX', 'BUDFF', 'ETN', 'DTEGY',
        'MBFJF', 'BKNG', 'ALIZF', 'ALIZY', 'KYCCF', 'TOELY', 'TOELF', 'BA', 'TJX', 'TD',
        'AIQUY', 'MDT', 'AIQUF', 'SONY', 'SNEJF', 'CIHKY', 'DE', 'REGN', 'BMY', 'BP',
        'LMT', 'VRTX', 'BPAQF', 'CB', 'UBS', 'ESLOY', 'MU', 'CI', 'TSLA', 'AAPL', 'MARA',
        'SOFI', 'AMD', 'MIO', None,
    ]

    ticker = request.GET.get('ticker')
    if ticker not in symbol_list:
        context = {'ticker': ticker}
        return render(request, 'indicatorapp/error.html', context)

    usbe = pd.DataFrame(USBureauEvent.objects.all().values())

    def nearest(items, pivot):
        return min([i for i in items if i > pivot], key=lambda x: x - pivot)

    now = datetime.datetime.now(timezone('US/Eastern'))
    imminent_event = usbe[usbe['date'] == nearest(usbe['date'].tolist(), now)].iloc[0]

    context = {
        'symbol_list': symbol_list,
        'imminent_event': imminent_event,
    }
    return render(request, 'indicatorapp/index.html', context)


# https://songseungwon.tistory.com/147
# https://www.bls.gov/schedule/2024/02_sched_list.htm
# https://www.bls.gov/developers/api_signature_v2.htm#latest
def detailView(request):
    symbol_list = [
        'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'STETH-USD', 'XRP-USD', 'DOGE-USD',
        'ADA-USD', 'AVAX-USD', 'SHIB-USD', 'DOT-USD', 'TON11419-USD', 'LINK-USD', 'MATIC-USD',
        'WTRX-USD', 'TRX-USD', 'WBTC-USD', 'NEAR-USD', 'BCH-USD', 'UNI7083-USD', 'LTC-USD',
        'APT21794-USD', 'ICP-USD', 'LEO-USD', 'DAI-USD', 'FIL-USD', 'ATOM-USD', 'ETC-USD',
        'RNDR-USD', 'INJ-USD', 'OKB-USD', 'WHBAR-USD', 'HBAR-USD', 'XLM-USD', 'CRO-USD',
        'OP-USD', 'BTCB-USD', 'WBETH-USD', 'VET-USD', 'KAS-USD', 'THETA-USD', 'SEI-USD',
        'XMR-USD', 'MKR-USD', 'LDO-USD', 'FTM-USD', 'WIF-USD', 'ALGO-USD', 'RETH-USD',

        'MSFT', 'NVDA', 'AMZN', 'GOOG', 'GOOGL', 'META', 'BRK-A', 'BRK-B', 'LLY',
        'TSM', 'JPM', 'NONOF', 'NVO', 'V', 'AVGO', 'WMT', 'LVMHF', 'LVMUY', 'UNH',
        'MA', 'XOM', 'JNJ', 'PG', 'ASML', 'ASMLF', 'HD', 'LTMAY', 'BAC', 'ORCL', 'TCEHY',
        'TCTZF', 'JPM-PD', 'JPM-PC', 'COST', 'TM', 'TOYOF', 'ABBV', 'BAC-PK', 'BML-PG',
        'MRK', 'BML-PH', 'BAC-PE', 'BAC-PL', 'BML-PL', 'CVX', 'CRM', 'F', 'LTHM',
        'NSRGY', 'HESAF', 'HESAY', 'NFLX', 'LRLCY', 'LRLCF', 'KO', 'BML-PJ', 'BAC-PB',
        'IDCBY', 'ACN', 'FMXUF', 'FMX', 'IDCBF', 'PEP', 'LIN', 'ADBE', 'TMO', 'PCCYF',
        'SAPGF', 'SAP', 'SHEL', 'RHHVF', 'RHHBY', 'RYDAF', 'NVSEF', 'WFC', 'AZN', 'DIS',
        'AZNCF', 'MCD', 'RHHBF', 'ABT', 'NVS', 'WFC-PY', 'CSCO', 'ACGBY', 'TMUS', 'BABA',
        'WFC-PL', 'BABAF', 'QCOM', 'DHR', 'WFC-PR', 'AYAAY', 'GE', 'INTC', 'IBM', 'INTU',
        'CAT', 'CMCSA', 'VZ', 'C-PJ', 'AMAT', 'PDD', 'CHDRF', 'PROSF', 'SMAWF', 'TTFNF',
        'SIEGY', 'CICHF', 'CHDRY', 'TTE', 'PROSY', 'AXP', 'UBER', 'PFE', 'TXN', 'CICHY',
        'MS', 'IDEXY', 'NOW', 'BACHY', 'IDEXF', 'BX', 'NKE', 'BACHF', 'UNP', 'HBCYF', 'PM',
        'HSBC', 'GS', 'C', 'AMGN', 'BHP', 'COP', 'LOW', 'ISRG', 'BHPLF', 'EADSF', 'RY',
        'HDB', 'EADSY', 'CMWAY', 'SYK', 'SPGI', 'SBGSF', 'SBGSY', 'UPS', 'ARM', 'HON',
        'BUD', 'RTNTF', 'UL', 'WFC-PC', 'UNLYF', 'RTX', 'NEE', 'SCHW', 'T', 'SNYNF',
        'DTEGF', 'SNY', 'MUFG', 'PGR', 'BLK', 'ELV', 'PLD', 'LRCX', 'BUDFF', 'ETN', 'DTEGY',
        'MBFJF', 'BKNG', 'ALIZF', 'ALIZY', 'KYCCF', 'TOELY', 'TOELF', 'BA', 'TJX', 'TD',
        'AIQUY', 'MDT', 'AIQUF', 'SONY', 'SNEJF', 'CIHKY', 'DE', 'REGN', 'BMY', 'BP',
        'LMT', 'VRTX', 'BPAQF', 'CB', 'UBS', 'ESLOY', 'MU', 'CI', 'TSLA', 'AAPL', 'MARA',
        'SOFI', 'AMD', 'MIO',
    ]

    sector_stocks = {
        'Crypto': [
            'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'STETH-USD', 'XRP-USD', 'DOGE-USD',
            'ADA-USD', 'AVAX-USD', 'SHIB-USD', 'DOT-USD', 'TON11419-USD', 'LINK-USD', 'MATIC-USD',
            'WTRX-USD', 'TRX-USD', 'WBTC-USD', 'NEAR-USD', 'BCH-USD', 'UNI7083-USD', 'LTC-USD',
            'APT21794-USD', 'ICP-USD', 'LEO-USD', 'DAI-USD', 'FIL-USD', 'ATOM-USD', 'ETC-USD',
            'RNDR-USD', 'INJ-USD', 'OKB-USD', 'WHBAR-USD', 'HBAR-USD', 'XLM-USD', 'CRO-USD',
            'OP-USD', 'BTCB-USD', 'WBETH-USD', 'VET-USD', 'KAS-USD', 'THETA-USD', 'SEI-USD',
            'XMR-USD', 'MKR-USD', 'LDO-USD', 'FTM-USD', 'WIF-USD', 'ALGO-USD', 'RETH-USD',
        ],
        'Stock': [
            'MSFT', 'NVDA', 'AMZN', 'GOOG', 'GOOGL', 'META', 'BRK-A', 'BRK-B', 'LLY',
            'TSM', 'JPM', 'NONOF', 'NVO', 'V', 'AVGO', 'WMT', 'LVMHF', 'LVMUY', 'UNH',
            'MA', 'XOM', 'JNJ', 'PG', 'ASML', 'ASMLF', 'HD', 'LTMAY', 'BAC', 'ORCL', 'TCEHY',
            'TCTZF', 'JPM-PD', 'JPM-PC', 'COST', 'TM', 'TOYOF', 'ABBV', 'BAC-PK', 'BML-PG',
            'MRK', 'BML-PH', 'BAC-PE', 'BAC-PL', 'BML-PL', 'CVX', 'CRM', 'F', 'LTHM',
            'NSRGY', 'HESAF', 'HESAY', 'NFLX', 'LRLCY', 'LRLCF', 'KO', 'BML-PJ', 'BAC-PB',
            'IDCBY', 'ACN', 'FMXUF', 'FMX', 'IDCBF', 'PEP', 'LIN', 'ADBE', 'TMO', 'PCCYF',
             'SAPGF', 'SAP', 'SHEL', 'RHHVF', 'RHHBY', 'RYDAF', 'NVSEF', 'WFC', 'AZN', 'DIS',
            'AZNCF', 'MCD', 'RHHBF', 'ABT', 'NVS', 'WFC-PY', 'CSCO', 'ACGBY', 'TMUS', 'BABA',
            'WFC-PL', 'BABAF', 'QCOM', 'DHR', 'WFC-PR', 'AYAAY', 'GE', 'INTC', 'IBM', 'INTU',
            'CAT', 'CMCSA', 'VZ', 'C-PJ', 'AMAT', 'PDD', 'CHDRF', 'PROSF', 'SMAWF', 'TTFNF',
            'SIEGY', 'CICHF', 'CHDRY', 'TTE', 'PROSY', 'AXP', 'UBER', 'PFE', 'TXN', 'CICHY',
            'MS', 'IDEXY', 'NOW', 'BACHY', 'IDEXF', 'BX', 'NKE', 'BACHF', 'UNP', 'HBCYF', 'PM',
            'HSBC', 'GS', 'C', 'AMGN', 'BHP', 'COP', 'LOW', 'ISRG', 'BHPLF', 'EADSF', 'RY',
            'HDB', 'EADSY', 'CMWAY', 'SYK', 'SPGI', 'SBGSF', 'SBGSY', 'UPS', 'ARM', 'HON',
            'BUD', 'RTNTF', 'UL', 'WFC-PC', 'UNLYF', 'RTX', 'NEE', 'SCHW', 'T', 'SNYNF',
            'DTEGF', 'SNY', 'MUFG', 'PGR', 'BLK', 'ELV', 'PLD', 'LRCX', 'BUDFF', 'ETN', 'DTEGY',
            'MBFJF', 'BKNG', 'ALIZF', 'ALIZY', 'KYCCF', 'TOELY', 'TOELF', 'BA', 'TJX', 'TD',
            'AIQUY', 'MDT', 'AIQUF', 'SONY', 'SNEJF', 'CIHKY', 'DE', 'REGN', 'BMY', 'BP',
            'LMT', 'VRTX', 'BPAQF', 'CB', 'UBS', 'ESLOY', 'MU', 'CI', 'TSLA', 'AAPL', 'MARA',
            'SOFI', 'AMD', 'MIO',
        ],
    }

    ticker = request.GET.get('ticker')
    if ticker == None:
        ticker = 'BTC-USD'

    if ticker not in symbol_list:
        context = {'ticker': ticker}
        return render(request, 'indicatorapp/error.html', context)

    df_all = pd.DataFrame(Ohlcv.objects.all().values())
    df = pd.concat([df_all[df_all['symbol']==symbol].set_index('timestamp')['Close'].astype(float) for symbol in symbol_list], axis=1)
    df.columns = symbol_list
    df.interpolate(inplace=True)

    technical_analysis = df_all[df_all['symbol']==ticker]
    technical_analysis['day'] = technical_analysis['timestamp'].apply(lambda x: x.date()).astype(str)
    technical_analysis[['Close', 'High', 'Low', 'Open', 'Volume']] = technical_analysis[['Close', 'High', 'Low', 'Open', 'Volume']].astype(float)
    technical_analysis = get_rsi(technical_analysis)
    technical_analysis = get_cci(technical_analysis)
    technical_analysis = get_fnMACD(technical_analysis, 'Close')
    technical_analysis = get_stochastic(technical_analysis)
    technical_analysis = get_mfi(technical_analysis)
    technical_analysis = get_ADX(technical_analysis)
    technical_analysis.dropna(inplace=True)

    if len(technical_analysis) > 180:
        max_length = 180
    else:
        max_length = len(technical_analysis)-1

    result_score = 0
    rsi_num = technical_analysis.iloc[len(technical_analysis)-1]['RSI']
    if rsi_num > 80:
        rsi_content = 'Overbought'
        result_score -= 1
    elif rsi_num < 20:
        rsi_content = 'Oversold'
        result_score += 1
    else:
        rsi_content = 'Normal'

    cci_num = technical_analysis.iloc[len(technical_analysis)-1]['CCI']
    cci_num_delay = technical_analysis.iloc[len(technical_analysis) - 2]['CCI']
    if (cci_num > cci_num_delay) and (cci_num < -100):
        cci_content = 'Buy'
        result_score += 1
    elif (cci_num < cci_num_delay) and (cci_num > 100):
        cci_content = 'Sell'
        result_score -= 1
    else:
        cci_content = 'Normal'

    macd_num = technical_analysis.iloc[len(technical_analysis)-1]['MACD_Close']
    macd_sig_num = technical_analysis.iloc[len(technical_analysis)-1]['MACDSignal_Close']
    if (macd_num > macd_sig_num) and (macd_num > 0) and (macd_sig_num > 0):
        macd_content = 'Buy'
        result_score += 1
    elif (macd_num < macd_sig_num) and (macd_num < 0) and (macd_sig_num < 0):
        macd_content = 'Sell'
        result_score -= 1
    else:
        macd_content = 'Normal'

    fast_k_num = technical_analysis.iloc[len(technical_analysis)-1]['fast_k']
    if fast_k_num > 80:
        fast_k_content = 'Overbought'
        result_score -= 1
    elif fast_k_num < 20:
        fast_k_content = 'Oversold'
        result_score += 1
    else:
        fast_k_content = 'Normal'

    mfi_num = technical_analysis.iloc[len(technical_analysis)-1]['mfi']
    if mfi_num > 80:
        mfi_content = 'Overbought'
        result_score -= 1
    elif mfi_num < 20:
        mfi_content = 'Oversold'
        result_score += 1
    else:
        mfi_content = 'Normal'

    adx_num = technical_analysis.iloc[len(technical_analysis) - 1]['ADX']
    if adx_num > 25:
        adx_content = 'Strong trend'
        result_score += 2
    elif adx_num < 20:
        adx_content = 'Low trend'
        result_score -= 2
    else:
        adx_content = 'Normal trend'

    if result_score >= 3:
        summary_result = 'BUY (Maintain)'
    elif result_score <= -3:
        summary_result = 'SELL (Maintain)'
    else:
        summary_result = 'No Signal for Now...'

    technical_analysis_numbers = {
        'RSI': round(rsi_num, 2),
        'CCI': round(cci_num, 2),
        'MACD': round(macd_num, 2),
        'STOCHASTIC': round(fast_k_num, 2),
        'MFI': round(mfi_num, 2),
        'ADX': round(adx_num, 2),
    }
    technical_analysis_content = {
        'RSI': rsi_content,
        'CCI': cci_content,
        'MACD': macd_content,
        'STOCHASTIC': fast_k_content,
        'MFI': mfi_content,
        'ADX': adx_content,
    }

    technical_analysis_dataset = {
        'index': technical_analysis['day'].tolist()[-max_length:],
        'rsi': [
            {
                'label': 'Close',
                'data': technical_analysis['Close'].tolist()[-max_length:],
                'borderColor': ['black'],
                'backgroundColor': ['black'],
                'yAxisID': 'Close',
            }, {
                'label': 'RSI',
                'data': technical_analysis['RSI'].tolist()[-max_length:],
                'borderColor': ['#FF0000'],
                'backgroundColor': ['#FF0000'],
                'yAxisID': 'RSI',
            }
        ],
        'cci': [
            {
                'label': 'Close',
                'data': technical_analysis['Close'].tolist()[-max_length:],
                'borderColor': ['black'],
                'backgroundColor': ['black'],
                'yAxisID': 'Close',
            }, {
                'label': 'CCI',
                'data': technical_analysis['CCI'].tolist()[-max_length:],
                'borderColor': ['#FF0000'],
                'backgroundColor': ['#FF0000'],
                'yAxisID': 'CCI',
            }
        ],
        'macd': [
            {
                'label': 'Close',
                'data': technical_analysis['Close'].tolist()[-max_length:],
                'borderColor': ['black'],
                'backgroundColor': ['black'],
                'yAxisID': 'Close',
            }, {
                'label': 'MACD',
                'data': technical_analysis['MACD_Close'].tolist()[-max_length:],
                'borderColor': ['#FF0000'],
                'backgroundColor': ['#FF0000'],
                'yAxisID': 'macd',
            }, {
                'label': 'MACD signal',
                'data': technical_analysis['MACDSignal_Close'].tolist()[-max_length:],
                'borderColor': ['#80FF00'],
                'backgroundColor': ['#80FF00'],
                'yAxisID': 'macd',
            }
        ],
        'stochastic': [
            {
                'label': 'Close',
                'data': technical_analysis['Close'].tolist()[-max_length:],
                'borderColor': ['black'],
                'backgroundColor': ['black'],
                'yAxisID': 'Close',
            }, {
                'label': 'fast k',
                'data': technical_analysis['fast_k'].tolist()[-max_length:],
                'borderColor': ['#FF0000'],
                'backgroundColor': ['#FF0000'],
                'yAxisID': 'fast_k',
            }
        ],
        'mfi': [
            {
                'label': 'Close',
                'data': technical_analysis['Close'].tolist()[-max_length:],
                'borderColor': ['black'],
                'backgroundColor': ['black'],
                'yAxisID': 'Close',
            }, {
                'label': 'MFI',
                'data': technical_analysis['mfi'].tolist()[-max_length:],
                'borderColor': ['#FF0000'],
                'backgroundColor': ['#FF0000'],
                'yAxisID': 'mfi',
            }
        ],
        'adx': [
            {
                'label': 'Close',
                'data': technical_analysis['Close'].tolist()[-max_length:],
                'borderColor': ['black'],
                'backgroundColor': ['black'],
                'yAxisID': 'Close',
            }, {
                'label': 'ADX',
                'data': technical_analysis['ADX'].tolist()[-max_length:],
                'borderColor': ['#FF0000'],
                'backgroundColor': ['#FF0000'],
                'yAxisID': 'adx',
            }
        ],
    }

    scaler = StandardScaler()
    scaler.fit(df)
    scaled = scaler.transform(df)
    df_scaled = pd.DataFrame(data=scaled, columns=df.columns)
    df_scaled.index = df.index
    df_scaled.columns = symbol_list

    corr = df_scaled.corr(method='pearson').sort_values(ticker, ascending=False)

    with_t = corr[1:3].index.tolist()
    anti_t = corr[-7:-5].index.tolist()

    with_index = corr[1:11].index.tolist()
    with_value = corr[ticker][1:11].values.tolist()

    df_all['day'] = df_all['timestamp'].apply(lambda x: x.date())

    ticker_index = df_all[df_all['symbol']==ticker]['day'].astype(str).tolist()[-max_length:]
    ticker_value = df_scaled[ticker].astype(float).tolist()[-max_length:]
    with1_value = df_scaled[with_t[0]].astype(float).tolist()[-max_length:]
    with2_value = df_scaled[with_t[1]].astype(float).tolist()[-max_length:]
    anti1_value = df_scaled[anti_t[0]].astype(float).tolist()[-max_length:]
    anti2_value = df_scaled[anti_t[1]].astype(float).tolist()[-max_length:]

    dataset_for_with = [
        {
            'label': with_t[0],
            'data': with1_value,
            'borderColor': ['#80FF00'],
            'backgroundColor': ['#80FF00'],
        }, {
            'label': with_t[1],
            'data': with2_value,
            'borderColor': ['#D0F5A9'],
            'backgroundColor': ['#D0F5A9'],
        }, {
            'label': ticker,
            'data': ticker_value,
            'borderColor': ['black'],
            'backgroundColor': ['black'],
        }
    ]

    dataset_for_anti = [
        {
            'label': anti_t[0],
            'data': anti1_value,
            'borderColor': ['#F5A9A9'],
            'backgroundColor': ['#F5A9A9'],
        }, {
            'label': anti_t[1],
            'data': anti2_value,
            'borderColor': ['#FF0000'],
            'backgroundColor': ['#FF0000'],
        }, {
            'label': ticker,
            'data': ticker_value,
            'borderColor': ['black'],
            'backgroundColor': ['black'],
        }
    ]

    if ticker in sector_stocks['Stock']:
        financial_statement = pd.DataFrame(FinancialStatement.objects.all().values()).sort_values('year')
        financial_statement_index = financial_statement[financial_statement['symbol']==ticker]['year'].tolist()
        dataset_for_gross_profit = [
            {
                'label': with_t[0],
                'data': financial_statement[financial_statement['symbol']==with_t[0]]['gross_profit_ratio'].astype(float).tolist(),
                'borderColor': ['#F5A9A9'],
                'backgroundColor': ['#F5A9A9'],
            }, {
                'label': with_t[1],
                'data': financial_statement[financial_statement['symbol']==with_t[1]]['gross_profit_ratio'].astype(float).tolist(),
                'borderColor': ['#A9F5A9'],
                'backgroundColor': ['#A9F5A9'],
            }, {
                'label': ticker,
                'data': financial_statement[financial_statement['symbol']==ticker]['gross_profit_ratio'].astype(float).tolist(),
                'borderColor': ['#A9A9F5'],
                'backgroundColor': ['#A9A9F5'],
            }
        ]
        dataset_for_EBITDA = [
            {
                'label': with_t[0],
                'data': financial_statement[financial_statement['symbol'] == with_t[0]]['EBITDA_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#F5A9A9'],
                'backgroundColor': ['#F5A9A9'],
            }, {
                'label': with_t[1],
                'data': financial_statement[financial_statement['symbol'] == with_t[1]]['EBITDA_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#A9F5A9'],
                'backgroundColor': ['#A9F5A9'],
            }, {
                'label': ticker,
                'data': financial_statement[financial_statement['symbol'] == ticker]['EBITDA_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#A9A9F5'],
                'backgroundColor': ['#A9A9F5'],
            }
        ]
        dataset_for_operating_income = [
            {
                'label': with_t[0],
                'data': financial_statement[financial_statement['symbol'] == with_t[0]]['operating_income_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#F5A9A9'],
                'backgroundColor': ['#F5A9A9'],
            }, {
                'label': with_t[1],
                'data': financial_statement[financial_statement['symbol'] == with_t[1]]['operating_income_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#A9F5A9'],
                'backgroundColor': ['#A9F5A9'],
            }, {
                'label': ticker,
                'data': financial_statement[financial_statement['symbol'] == ticker]['operating_income_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#A9A9F5'],
                'backgroundColor': ['#A9A9F5'],
            }
        ]
        dataset_for_net_income = [
            {
                'label': with_t[0],
                'data': financial_statement[financial_statement['symbol'] == with_t[0]]['net_income_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#F5A9A9'],
                'backgroundColor': ['#F5A9A9'],
            }, {
                'label': with_t[1],
                'data': financial_statement[financial_statement['symbol'] == with_t[1]]['net_income_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#A9F5A9'],
                'backgroundColor': ['#A9F5A9'],
            }, {
                'label': ticker,
                'data': financial_statement[financial_statement['symbol'] == ticker]['net_income_ratio'].astype(
                    float).tolist(),
                'borderColor': ['#A9A9F5'],
                'backgroundColor': ['#A9A9F5'],
            }
        ]

        card_box = FinancialStatement.objects.filter(symbol__exact=ticker).order_by('year')

        context = {
            'symbol_list': symbol_list,
            'sector_stocks': sector_stocks['Stock'],
            'ticker': ticker,
            'with_t': with_t,
            'anti_t': anti_t,
            'ticker_index': ticker_index,
            'with_index': with_index,
            'with_value': with_value,
            'dataset_for_with': dataset_for_with,
            'dataset_for_anti': dataset_for_anti,
            'financial_statement': card_box,
            'financial_statement_index': financial_statement_index,
            'dataset_for_gross_profit': dataset_for_gross_profit,
            'dataset_for_EBITDA': dataset_for_EBITDA,
            'dataset_for_operating_income': dataset_for_operating_income,
            'dataset_for_net_income': dataset_for_net_income,
            'technical_analysis_numbers': technical_analysis_numbers,
            'technical_analysis_content': technical_analysis_content,
            'technical_analysis_dataset': technical_analysis_dataset,
            'summary_result': summary_result,
            'anti1_value': len(anti1_value),
        }
    else:
        context = {
            'symbol_list': symbol_list,
            'sector_stocks': sector_stocks['Stock'],
            'ticker': ticker,
            'with_t': with_t,
            'anti_t': anti_t,
            'ticker_index': ticker_index,
            'with_index': with_index,
            'with_value': with_value,
            'dataset_for_with': dataset_for_with,
            'dataset_for_anti': dataset_for_anti,
            'financial_statement_index': None,
            'dataset_for_gross_profit': None,
            'dataset_for_EBITDA': None,
            'dataset_for_operating_income': None,
            'dataset_for_net_income': None,
            'technical_analysis_numbers': technical_analysis_numbers,
            'technical_analysis_content': technical_analysis_content,
            'technical_analysis_dataset': technical_analysis_dataset,
            'summary_result': summary_result,
            'anti1_value': len(anti1_value),
        }

    return render(request, 'indicatorapp/detail.html', context)



# FinancialStatement
def crawler(request):
    from financetoolkit import Toolkit

    API_KEY = "gCBxDtKx26xBXWD9iULeQboBZNAKaiCK"
    # API_KEY = 'bb5b19dd01ac8ec7f418bd292a002013'
    symbol_list = [
        'PM',
        'HSBC', 'GS', 'C', 'AMGN', 'BHP', 'COP', 'LOW', 'ISRG', 'BHPLF', 'EADSF', 'RY',
        'HDB', 'EADSY', 'CMWAY', 'SYK', 'SPGI', 'SBGSF', 'SBGSY', 'UPS', 'ARM', 'HON',
        'BUD', 'RTNTF', 'UL', 'WFC-PC', 'UNLYF', 'RTX', 'NEE', 'SCHW', 'T', 'SNYNF',
        'DTEGF', 'SNY', 'MUFG', 'PGR', 'BLK', 'ELV', 'PLD', 'LRCX', 'BUDFF', 'ETN', 'DTEGY',
        'MBFJF', 'BKNG', 'ALIZF', 'ALIZY', 'KYCCF', 'TOELY', 'TOELF', 'BA', 'TJX', 'TD',
        'AIQUY', 'MDT', 'AIQUF', 'SONY', 'SNEJF', 'CIHKY', 'DE', 'REGN', 'BMY', 'BP',
        'LMT', 'VRTX', 'BPAQF', 'CB', 'UBS', 'ESLOY', 'MU', 'CI',
    ]

    for symbol in symbol_list:
        companies = Toolkit([symbol], api_key=API_KEY)

        # Obtain the balance sheets from each company
        balance_sheet_statement = companies.get_balance_sheet_statement()
        income_statement = companies.get_income_statement()
        cashflow_statement = companies.get_cash_flow_statement()
        # enterprise = companies.get_enterprise()

        year_list = set(list(set(balance_sheet_statement.columns.tolist()).intersection(income_statement.columns.tolist()))).intersection(cashflow_statement.columns.tolist())
        for year in year_list:
            o = FinancialStatement.objects.create(
                symbol=symbol,
                year=year,
                # market_cap=enterprise.loc[year]['Market Capitalization'],
                revenue=income_statement.loc['Revenue'][year],
                net_income=income_statement.loc['Net Income'][year],
                net_debt=balance_sheet_statement.loc['Net Debt'][year],
                EBITDA=income_statement.loc['EBITDA'][year],
                cost_and_expenses=income_statement.loc['Cost and Expenses'][year],
                depreciation_and_amortization=income_statement.loc['Depreciation and Amortization'][year],
                total_current_assets=balance_sheet_statement.loc['Total Current Assets'][year],
                total_current_liabilities=balance_sheet_statement.loc['Total Current Liabilities'][year],
                total_non_current_liabilities=balance_sheet_statement.loc['Total Non Current Liabilities'][year],
                cash_flow_from_operations=cashflow_statement.loc['Cash Flow from Operations'][year],
                cash_flow_from_investing=cashflow_statement.loc['Cash Flow from Investing'][year],
                cash_flow_from_financing=cashflow_statement.loc['Cash Flow from Financing'][year],
                cash_beginning_of_period=cashflow_statement.loc['Cash Beginning of Period'][year],
                cash_end_of_period=cashflow_statement.loc['Cash End of Period'][year],
                gross_profit_ratio=income_statement.loc['Gross Profit Ratio'][year],
                EBITDA_ratio=income_statement.loc['EBITDA Ratio'][year],
                operating_income_ratio=income_statement.loc['Operating Income Ratio'][year],
                net_income_ratio=income_statement.loc['Net Income Ratio'][year],
                # earnings_yield=round(income_statement.loc['EBITDA'][year] / (enterprise.loc[year]['Market Capitalization'] + balance_sheet_statement.loc['Net Debt'][year]), 6),
                # return_on_capital=round(income_statement.loc['EBITDA'][year] / (
                #         (balance_sheet_statement.loc['Total Current Assets'][year]-balance_sheet_statement.loc['Total Current Liabilities'][year]) + \
                #         (balance_sheet_statement.loc['Total Non Current Liabilities'][year] - income_statement.loc['Depreciation and Amortization'][year])), 6),
            )
            o.save()

    return render(request, 'indicatorapp/crawler.html')


'''

# USBureauEvent
def crawler(request):
    df = pd.read_csv('CSV.CSV', encoding="UTF-8")
    df['start_time'] = df['start_time'].apply(lambda x: x[1:] if '\x08' in x else x)
    df['end_time'] = df['end_time'].apply(lambda x: x[1:] if '\x08' in x else x)
    for index, row in df.iterrows():
        o = USBureauEvent.objects.create(
            name=row['event'],
            date=datetime.datetime.strptime(row['start_date'] + ' ' + row['start_time'], '%Y-%m-%d %H:%M:%S'),
            value=None,
        )
        o.save()
    return render(request, 'crawler.html')


# Ohlcv
def crawler(request):
    symbol_list = [
        'LTHM',
        'NSRGY',
        'PFE',
    ]

    for sc in symbol_list:
        try:
            tick = yf.Ticker(sc)
            df = tick.history(period='1y')
            for index, row in df.iterrows():
                digit = digit_length(row['Open'])
                o = Ohlcv.objects.create(
                    symbol=sc,
                    interval = '1d',
                    timestamp = index,
                    Open = round(row['Open'], 8-digit),
                    High = round(row['High'], 8-digit),
                    Low = round(row['Low'], 8-digit),
                    Close = round(row['Close'], 8-digit),
                    Volume = row['Volume'],
                )
                o.save()
        except:
            pass

    return render(request, 'indicatorapp/crawler.html')

def digit_length(n):
    return int(math.log10(n)) + 1 if n else 0

'''