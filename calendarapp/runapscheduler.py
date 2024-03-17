import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from calendarapp.models import Event
import requests
import pandas as pd
import datetime


def get_earning_data(headers, url, params, date):
    query = {
        "entityIdType": "earnings",
        "includeFields": [
            "ticker",
            "companyshortname",
            "startdatetime",
            "epsestimate",
            "epsactual",
            "epssurprisepct",
        ],
        "offset": 0,
        "query": {
            "operands": [
                {"operands": ["startdatetime", (date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')],
                 "operator": "gte"},
                {"operands": ["startdatetime", date.strftime('%Y-%m-%d')],
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

def updateEvent():
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",}
    url = "https://query2.finance.yahoo.com/v1/finance/visualization"
    params = {
        "crumb": "EwuCwsPbKM2",
        "lang": "en-US",
        "region": "US",
        "corsDomain": "finance.yahoo.com",
    }

    now = datetime.datetime.today()
    df = get_earning_data(headers, url, params, now)

    df['companyshortname'] = df['companyshortname'].apply(lambda x: x[:50] if len(x) > 50 else x)
    df['startdatetime'] = df['startdatetime'].apply(lambda x: x[:10])
    df = df[(df['epsestimate'] // 10 < 4) & (df['epsactual'] // 10 < 4) & (df['epssurprisepct'] // 10 < 6)]
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


# https://pypi.org/project/django-apscheduler/
def handle():
    logger = logging.getLogger(__name__)
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        updateEvent,
        trigger=CronTrigger(day="*", hour=0, minute=1),  # Every day
        id="updateEvent",  # The `id` assigned to each job MUST be unique
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