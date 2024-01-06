from datetime import time

from apscheduler.schedulers.background import BackgroundScheduler
from chartjs.views.lines import BaseLineChartView
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView

from polls.models import Question, Choice

from polls.utils import get_data
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
import pandas as pd
from math import pi
import datetime
import json


class PollsIndexView(ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]


class PollsDetailView(DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_object(self):
        object = get_object_or_404(Question, id=self.kwargs['question_id'])
        return object


class PollsResultsView(DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_object(self):
        object = get_object_or_404(Question, id=self.kwargs['question_id'])
        return object

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        # return HttpResponseRedirect(reverse("polls:index", args=(question.id,)))
        return HttpResponseRedirect(reverse("polls:index"))


class LineChartJSONView(BaseLineChartView):
    df = get_data('BTC-USD', '15mo')[400:]

    def get_labels(self):
        # index
        return self.df.index.tolist()

    def get_providers(self):
        # column
        return ["open", "close", "high", "low"]

    def get_data(self):
        # data
        return [self.df["open"].tolist(), self.df["close"].tolist(), self.df["high"].tolist(), self.df["low"].tolist()]

def send_data(request):
    # https://stackoverflow.com/questions/59881433/how-do-i-return-data-from-pandas-dataframe-to-be-returned-by-djangos-jsonrespon
    df = get_data('BTC-USD', '15mo')
    result = df.to_json(orient='records')
    return JsonResponse(json.loads(result), safe=False)


# def btcusdt_15m():
#     sched = BackgroundScheduler()
#     # interval - 일정주기로 수행(테스트용 10초)
#     # sched.add_job(job, 'interval', seconds=900, id='get_data')
#     sched.add_job(job, 'cron', minute="15", second='5', id="btcusdt_15m")
#     sched.add_job(job, 'cron', minute="30", second='5', id="btcusdt_15m")
#     sched.add_job(job, 'cron', minute="45", second='5', id="btcusdt_15m")
#     sched.add_job(job, 'cron', minute="0", second='5', id="btcusdt_15m")
#
#     sched.start()

# https://simpleisbetterthancomplex.com/tutorial/2020/01/19/how-to-use-chart-js-with-django.html
def population_chart(request):
    df = get_data('BTC-USD', '15mo')
    labels = df['date'].tolist()
    data = df['close'].tolist()
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })
