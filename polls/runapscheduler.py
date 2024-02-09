import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from polls.models import Poll
import datetime

def updatePoll():
    question_data = Poll.objects.last().pub_date.strftime("%Y-%m-%d")
    # if question_data != datetime.datetime.today().strftime('%Y-%m-%d'):
        # q = Poll.objects.create(
        #     question_text=datetime.datetime.today().strftime("%d %b %Y")+" direction?",
        #     pub_date=datetime.datetime.now().strftime('%Y-%m-%d'),
        # )
        # q.save()

# https://pypi.org/project/django-apscheduler/
def handle():
    logger = logging.getLogger(__name__)
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        updatePoll,
        trigger=CronTrigger(day="*"),  # Every day
        id="updatePoll",  # The `id` assigned to each job MUST be unique
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'updatePoll'.")

    try:
        logger.info("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")