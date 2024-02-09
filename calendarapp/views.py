from datetime import datetime, date, timedelta

from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.generic import ListView

from calendarapp.models import Event
from calendarapp.utils import Calendar

import calendar

import finnhub
import pandas as pd

from indicatorapp.models import Ohlcv


def TestView(request):
    event_data = Event.objects.last()
    return render(request, 'calendarapp/test.html', {'event_data': event_data})

# https://velog.io/@2hey9/Project-%ED%94%8C%EB%A0%88%EC%9D%B4%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%9E%A5%EA%B3%A0-%EB%AF%B8%EB%8B%88%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%EC%BA%98%EB%A6%B0%EB%8D%94-%EC%95%B1-%EA%B5%AC%EB%8F%99%ED%95%98%EA%B8%B0
class CalendarView(ListView):
    model = Event
    template_name = 'calendarapp/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ohlcv = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact="BTC-USD").values()))

        # =================== DATA FOR CALENDAR ===================
        d = get_date(self.request.GET.get('day', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(ohlcv, withyear=True)
        context['calendar'] = mark_safe(html_cal)

        # Get previous and next month
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        # =================== DATA FOR BAR CHART ===================
        ohlcv['day'] = ohlcv['timestamp'].apply(lambda x: f'{x.year}{x.month}{x.day}')
        ohlcv['volatility'] = ohlcv['High'] - ohlcv['Low']
        ohlcv['volatility_mean'] = ohlcv['volatility'].rolling(window=30, min_periods=1).mean()
        ohlcv['e_count'] = ohlcv.apply(lambda x: 1 if x['volatility'] > x['volatility_mean'] else 0, axis=1)
        ohlcv['n_count'] = ohlcv.apply(lambda x: 1 if x['volatility'] < x['volatility_mean'] else 0, axis=1)

        ev = pd.DataFrame(list(Event.objects.all().values()))
        ev['day'] = ev['date'].apply(lambda x: f'{x.year}{x.month}{x.day}')

        df = pd.merge(ev, ohlcv, how='left', on='day')
        df = df.groupby('symbol_x').agg({'e_count':'sum', 'n_count':'sum'}).sort_values(by=['e_count'], ascending=False)
        context['symbol_list'] = df.index.tolist()[:15]
        context['e_count_list'] = df['e_count'].tolist()[:15]
        context['n_count_list'] = df['n_count'].tolist()[:15]

        return context


def get_date(req_day):
    try:
        if req_day:
            year, month, day = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
    except (ValueError, TypeError):
        pass
    return datetime.today().date()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    a = 'day=' + str(prev_month.year) + '-' + str(prev_month.month) + '-' + str(prev_month.day)
    return a


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    a = 'day=' + str(next_month.year) + '-' + str(next_month.month) + '-' + str(next_month.day)
    return a


# def crawler(request):
#
#     finnhub_client = finnhub.Client(api_key="cmpn2s1r01qg7bboc3r0cmpn2s1r01qg7bboc3rg")
#     df = finnhub_client.earnings_calendar(_from="", to="", symbol="", international=False)
#     df = pd.DataFrame(df['earningsCalendar'])
#     df.dropna(inplace=True)
#
#     for index, row in df.iterrows():
#         o = Event.objects.create(
#             date = row['date'],
#             epsActual = round(row['epsActual'], 4),
#             epsEstimate = round(row['epsEstimate'], 4),
#             hour = row['hour'],
#             quarter = row['quarter'],
#             revenueActual = round(row['revenueActual'], 1),
#             revenueEstimate = round(row['revenueEstimate'], 1),
#             symbol = row['symbol'],
#         )
#         o.save()
#
#     return render(request, 'calendarapp/crawler.html')

def crawler(request):
    import requests
    import pandas as pd
    import datetime
    import time
    import random

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    }

    url = "https://query2.finance.yahoo.com/v1/finance/visualization"

    params = {
        "crumb": "EwuCwsPbKM2",
        "lang": "en-US",
        "region": "US",
        "corsDomain": "finance.yahoo.com",
    }

    def get_earning_data(headers, url, params, date):
        query = {
            "entityIdType": "earnings",
            "includeFields": [
                "ticker",
                "companyshortname",
                # "eventname",
                "startdatetime",
                # "startdatetimetype",
                "epsestimate",
                "epsactual",
                "epssurprisepct",
                # "timeZoneShortName",
                # "gmtOffsetMilliSeconds",
            ],
            "offset": 0,
            "query": {
                "operands": [
                    {"operands": ["startdatetime", date.strftime('%Y-%m-%d')], "operator": "gte"},
                    {"operands": ["startdatetime", (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')],
                     "operator": "lt"},
                    {"operands": ["region", "us"], "operator": "eq"},
                ],
                "operator": "and",
            },
            "size": 100,
            "sortField": "companyshortname",
            "sortType": "ASC",
        }

        # this changes in time ?
        cookie = "d=AQABBK8KXmQCEA8-VE0dBLqG5QEpQ7OglmEFEgABCAHCeWWpZfNtb2UB9qMAAAcIqgpeZJj7vK8&S=AQAAAqhyTAOrxcxONc4ktfzCOkg"

        with requests.session() as s:
            s.headers.update(headers)
            s.cookies["A3"] = cookie

            data = s.post(url, params=params, json=query).json()

        return pd.DataFrame(data=data['finance']['result'][0]['documents'][0]['rows'],
                            columns=[n['id'] for n in data['finance']['result'][0]['documents'][0]['columns']]).dropna()

    now = datetime.datetime(2024, 2, 2)
    today = datetime.datetime(2024, 2, 3)
    df = get_earning_data(headers, url, params, now)
    now = now + datetime.timedelta(days=1)

    while now != today:
        temp = get_earning_data(headers, url, params, now)
        if len(temp) != 0:
            df = pd.concat([df, temp], axis=0)
        now = now + datetime.timedelta(days=1)
        time.sleep(random.uniform(1, 4))

    df['companyshortname'] = df['companyshortname'].apply(lambda x: x[:50] if len(x) > 50 else x)
    df['startdatetime'] = df['startdatetime'].apply(lambda x: x[:10])
    df = df[(df['epsestimate']//10 < 4) & (df['epsactual']//10 < 4) & (df['epssurprisepct']//10 < 6)]
    df = df.drop_duplicates(['ticker', 'companyshortname', 'startdatetime'], keep='first')
    df.reset_index(drop=True, inplace=True)

    for index, row in df.iterrows():
        o = Event.objects.create(
            date=row['startdatetime'],
            epsActual=round(row['epsactual'], 2),
            epsEstimate=round(row['epsestimate'], 2),
            epsSurprisePct=round(row['epssurprisepct'], 2),
            symbol=row['ticker'],
            name=row['companyshortname'],
        )
        o.save()

    return render(request, 'calendarapp/crawler.html')