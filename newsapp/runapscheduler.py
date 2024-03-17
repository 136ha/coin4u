import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from pynytimes import NYTAPI
import datetime
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .models import Article
nltk.download('vader_lexicon')

def updateArticle():
    # New words and values
    new_words = {
        'crushes': 10,
        'beats': 5,
        'misses': -5,
        'trouble': -10,
        'falls': -100,
    }
    # Instantiate the sentiment intensity analyzer with the existing lexicon
    vader = SentimentIntensityAnalyzer()
    # Update the lexicon
    vader.lexicon.update(new_words)
    now = datetime.datetime.now()

    # https://pynytimes.michadenheijer.com/search/article-search

    nyt = NYTAPI("THMTiNXu77eTwKywUupLcCGeDZBKwD2W", parse_dates=True)
    articles = nyt.article_search(
        #     query = "Obama", # Search for articles about Obama
        results=30,  # Return 30 articles
        # Search for articles in January and February 2019
        dates={
            "begin": now - datetime.timedelta(days=1),
            "end": now,
        },
        options={
            "sort": "oldest",  # Sort by oldest options
            # Only get information from the Politics desk
            "news_desk": [
                "Business Day",
                "Business",
                "Market Place",
                "Politics"
            ]
        }
    )

    df = pd.DataFrame(articles)
    # Iterate through the headlines and get the polarity scores
    scores = [vader.polarity_scores(headline + lead_paragraph + headline) for abstract, lead_paragraph, headline in
              zip(df['abstract'].values, df['lead_paragraph'].values, df['headline'].astype('str'))]
    scores_df = pd.DataFrame(scores)
    # Join the DataFrames
    df = pd.concat([df, scores_df], axis=1)
    df.dropna(subset=['abstract', 'web_url', 'lead_paragraph', 'headline', 'keywords'], inplace=True)

    headline_list = pd.DataFrame(Article.objects.all().values())['headline'].tolist()[-10:]
    for index, row in df.iterrows():
        if row['headline'] not in headline_list:
            o = Article.objects.create(
                abstract=row['abstract'],
                web_url=row['web_url'],
                snippet=row['snippet'],
                lead_paragraph=row['lead_paragraph'],
                headline=row['headline'],
                keywords={i + 1: {'name': row['keywords'][i]['name'], 'value': row['keywords'][i]['value']} for i in
                          range(len(row['keywords']))},
                pub_date=row['pub_date'],
                news_desk=row['news_desk'],
                section_name=row['section_name'],
                subsection_name=row['subsection_name'],
                word_count=row['word_count'],
                neg=row['neg'],
                neu=row['neu'],
                pos=row['pos'],
            )
            o.save()


# https://pypi.org/project/django-apscheduler/
def handle():
    logger = logging.getLogger(__name__)
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        updateArticle,
        trigger=CronTrigger(day="*", hour="*", minute=5),  # Every day
        id="updateArticle",  # The `id` assigned to each job MUST be unique
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