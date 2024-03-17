# https://medium.com/@dorianszafranski17/create-a-news-platform-in-django-f7b66f69be95
import datetime

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from collections import Counter

from indicatorapp.models import Ohlcv
from .models import Article
import pandas as pd
from pytrends.request import TrendReq
from sklearn.preprocessing import StandardScaler


class NewsView(ListView):
    model = Article
    template_name = 'newsapp/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enddate = datetime.datetime.today()
        startdate = enddate - datetime.timedelta(days=7)
        article = Article.objects.filter(pub_date__range=[startdate, enddate]).order_by('-pub_date')
        context['article'] = article

        # ================= CHART 1 =================
        article = pd.DataFrame(list(article.values()))
        counts = Counter(sum(list(article['keywords'].apply(lambda x: [a['value'] for a in x.values()])), []))
        count_dic = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
        keyword = []
        count = []
        for key, value in count_dic:
            keyword.append(key)
            count.append(value)

        context['keyword'] = keyword[:10]
        context['count'] = count[:10]

        # ================= CHART 2 =================
        high_ranked = []
        neg_score = []
        neu_score = []
        pos_score = []
        article['keywords'] = article['keywords'].astype(str)
        for word in keyword:
            temp = article[article['keywords'].str.contains(word)]
            if len(temp) == 0:
                continue
            high_ranked.append(word)
            neg_score.append(round(temp['neg'].mean(), 3))
            neu_score.append(round(temp['neu'].mean(), 3))
            pos_score.append(round(temp['pos'].mean(), 3))

        context['high_ranked'] = high_ranked[:10]
        context['neg'] = neg_score[:10]
        context['neu'] = neu_score[:10]
        context['pos'] = pos_score[:10]

        # ================= CHART 3 =================
        context['news_desk_index'] = article['news_desk'].value_counts().index.tolist()
        context['news_desk_value'] = article['news_desk'].value_counts().values.tolist()

        # ================= CHART 4 =================
        ohlcv = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact="BTC-USD").values()))
        ohlcv['day'] = ohlcv['timestamp'].apply(lambda x: x.date())

        context['trend_index'] = ohlcv['day'].astype(str).tolist()[:52]
        context['trend_value'] = ohlcv['Close'].apply(lambda x: int(x)).tolist()[:52]

        return context


def crawler(request):
    from pynytimes import NYTAPI
    import datetime
    import pandas as pd
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

    nltk.download('vader_lexicon')

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

    # https://pynytimes.michadenheijer.com/search/article-search

    nyt = NYTAPI("THMTiNXu77eTwKywUupLcCGeDZBKwD2W", parse_dates=True)
    articles = nyt.article_search(
        #     query = "Obama", # Search for articles about Obama
        results=30,  # Return 30 articles
        # Search for articles in January and February 2019
        dates={
            "begin": datetime.datetime(2024, 3, 15),
            "end": datetime.datetime(2024, 3, 16)
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



    for index, row in df.iterrows():

        o = Article.objects.create(
            abstract = row['abstract'],
            web_url = row['web_url'],
            snippet = row['snippet'],
            lead_paragraph = row['lead_paragraph'],
            headline = row['headline'],
            keywords = {i+1:{'name':row['keywords'][i]['name'], 'value':row['keywords'][i]['value']} for i in range(len(row['keywords']))},
            pub_date = row['pub_date'],
            news_desk = row['news_desk'],
            section_name = row['section_name'],
            subsection_name = row['subsection_name'],
            word_count = row['word_count'],
            neg = row['neg'],
            neu = row['neu'],
            pos = row['pos'],
        )
        o.save()

    return render(request, 'newsapp/crawler.html')