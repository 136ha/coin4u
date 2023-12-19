from django.urls import path

from polls import views
from polls.views import PollsIndexView, PollsDetailView, PollsResultsView, vote
from profileapp.views import ProfileCreateView, ProfileUpdateView

app_name = "polls"

urlpatterns = [
    # path('create/', ProfileCreateView.as_view(), name='create'),
    # path('update/<int:pk>', ProfileUpdateView.as_view(), name='update'),
    path("", PollsIndexView.as_view(), name="index"),
    path("detail/<int:question_id>/", PollsDetailView.as_view(), name="detail"),
    path("results/<int:question_id>/", PollsResultsView.as_view(), name="results"),
    path("vote/<int:question_id>/", vote, name="vote"),
]