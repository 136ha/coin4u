import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from calendarapp.models import Event
import finnhub
import pandas as pd

def updateEvent():
    # 여기에 작업 내용을 작성합니다.
    # event_data = Event.objects.last().date.strftime("%Y-%m-%d")
    event_data = Event.objects.all()
    finnhub_client = finnhub.Client(api_key="cmpn2s1r01qg7bboc3r0cmpn2s1r01qg7bboc3rg")
    df = finnhub_client.earnings_calendar(_from="", to="", symbol="", international=False)
    df = pd.DataFrame(df['earningsCalendar'])
    df.dropna(inplace=True)

    for index, row in df.iterrows():
        if row in event_data:
            break
        # o = Event.objects.create(
        #     date=row['date'],
        #     epsActual=round(row['epsActual'], 4),
        #     epsEstimate=round(row['epsEstimate'], 4),
        #     hour=row['hour'],
        #     quarter=row['quarter'],
        #     revenueActual=round(row['revenueActual'], 1),
        #     revenueEstimate=round(row['revenueEstimate'], 1),
        #     symbol=row['symbol'],
        # )
        # o.save()

# https://pypi.org/project/django-apscheduler/
def handle():
    logger = logging.getLogger(__name__)
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        updateEvent,
        trigger=CronTrigger(day="*"),  # Every day
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