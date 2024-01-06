from django.urls import path, include
from django.views.generic import TemplateView

from polls import views
from polls.views import PollsIndexView, PollsDetailView, PollsResultsView, vote, LineChartJSONView, send_data
from profileapp.views import ProfileCreateView, ProfileUpdateView

app_name = "polls"

urlpatterns = [
    # path('create/', ProfileCreateView.as_view(), name='create'),
    # path('update/<int:pk>', ProfileUpdateView.as_view(), name='update'),
    path("", PollsIndexView.as_view(), name="index"),
    path("detail/<int:question_id>/", PollsDetailView.as_view(), name="detail"),
    path("results/<int:question_id>/", PollsResultsView.as_view(), name="results"),
    path("vote/<int:question_id>/", vote, name="vote"),
    path('chart/', TemplateView.as_view(template_name='polls/line_chart.html'), name='line_chart'),
    path('chartJSON/', LineChartJSONView.as_view(), name='line_chart_json'),
    path('chartJSON2/', send_data, name='line_chart_json2'),
    path('population-chart/', views.population_chart, name='population-chart'),
]