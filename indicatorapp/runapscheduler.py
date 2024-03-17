import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from calendarapp.models import Event
import requests
import pandas as pd
import datetime
import math
import yfinance as yf

from indicatorapp.models import Ohlcv


def digit_length(n):
    return int(math.log10(n)) + 1 if n else 0

def updateOhlcv():
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

    for sc in symbol_list:
        try:
            time_list = pd.DataFrame(Ohlcv.objects.filter(symbol__exact=sc).values())['timestamp'].tolist()
            tick = yf.Ticker(sc)
            df = tick.history(period="3mo")
            for index, row in df.iterrows():
                digit = digit_length(row['Open'])
                if index not in time_list:
                    o = Ohlcv.objects.create(
                        symbol=sc,
                        interval='1d',
                        timestamp=index,
                        Open=round(row['Open'], 8 - digit),
                        High=round(row['High'], 8 - digit),
                        Low=round(row['Low'], 8 - digit),
                        Close=round(row['Close'], 8 - digit),
                        Volume=row['Volume'],
                    )
                    o.save()
        except:
            pass


# https://pypi.org/project/django-apscheduler/
def handle():
    logger = logging.getLogger(__name__)
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        updateOhlcv,
        trigger=CronTrigger(day="*", hour=0, minute=10),  # Every day
        id="updateOhlcv",  # The `id` assigned to each job MUST be unique
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'updateEvent'.")

    try:
        logger.info("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")